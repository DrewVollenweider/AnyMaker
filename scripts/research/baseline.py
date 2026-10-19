"""Read-only installation inventory and selective, independently verified snapshot.

Standard-library only. Single worker, below-normal priority on Windows. Never
opens a process or save folder. JSON records contain relative paths only.
"""
import argparse
from collections import Counter
import codecs
import ctypes
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import platform
import re
import shutil
import struct
import time

VERSION = '1.1.0'


def sha(path):
    before = path.stat()
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    after = path.stat()
    if (before.st_size, before.st_mtime_ns) != (after.st_size, after.st_mtime_ns):
        raise ValueError('File changed while hashing: ' + path.name)
    return h.hexdigest()


def resources(path):
    r = {'disk_free_bytes': shutil.disk_usage(path).free}
    if os.name == 'nt':
        class Memory(ctypes.Structure):
            _fields_ = [('length', ctypes.c_ulong), ('load', ctypes.c_ulong)] + [
                (x, ctypes.c_ulonglong) for x in ('total', 'available', 'page',
                    'available_page', 'virtual', 'available_virtual', 'extended')]
        m = Memory()
        m.length = ctypes.sizeof(m)
        if not ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m)):
            raise OSError('Cannot establish memory headroom')
        r.update(memory_total_bytes=m.total, memory_available_bytes=m.available)
        if not ctypes.windll.kernel32.SetPriorityClass(ctypes.c_void_p(-1), 0x4000):
            raise OSError('Cannot set below-normal priority')
    return r


def classify(path):
    with path.open('rb') as f:
        b = f.read(4096)
    if b.startswith(b'MZ') and len(b) >= 64:
        off = struct.unpack_from('<I', b, 60)[0]
        with path.open('rb') as f:
            f.seek(off)
            header = f.read(26)
        if header[:4] == b'PE\0\0':
            return 'pe-x64' if struct.unpack_from('<H', header, 4)[0] == 0x8664 else 'pe-other'
    for sig, fmt in [(b'\x89PNG\r\n\x1a\n', 'png'), (b'OggS', 'ogg'),
                     (b'RIFF', 'riff'), (b'DDS ', 'dds'), (b'\x1f\x8b', 'gzip'),
                     (b'PK\x03\x04', 'zip'), (b'OTTO', 'opentype'),
                     (b'\x00\x01\x00\x00', 'sfnt-candidate')]:
        if b.startswith(sig):
            return fmt
    # These labels distinguish header recognition from a complete format parse.
    if len(b) >= 16:
        if b[:4] in (b'mesh', b'TXTR', b'ATLA'):
            version = struct.unpack_from('<I', b, 4)[0]
            return b[:4].decode('ascii') + '-v' + str(version) + '-header'
        n, ident, size = struct.unpack_from('<III', b)
        if 0 < n < 10000 and 0 < size < 2048 and b[12:12+size].endswith(b'.gc'):
            return 'gcl-source-table-header'
    if not b:
        return 'empty'
    try:
        # A 4096-byte prefix may end inside a multibyte UTF-8 character.
        t = codecs.getincrementaldecoder('utf-8-sig')().decode(b, final=False)
    except UnicodeDecodeError:
        return 'binary-unresolved'
    if t.lstrip().startswith(('{', '[')):
        try:
            # Validate full JSON, not just its leading punctuation.
            json.loads(path.read_text(encoding='utf-8-sig'))
            return 'json'
        except (ValueError, UnicodeDecodeError):
            return 'text-json-like-invalid'
    if '\0' not in t and all(c.isprintable() or c in '\r\n\t' for c in t):
        return 'utf8-tabular' if '\t' in t else 'utf8-text'
    return 'binary-unresolved'


def selected(rel):
    return (rel in ('game.exe', 'steam_api64.dll', 'bin/game.gcl')
            or rel.startswith('rom/data/') or rel.startswith('AnymakerWorkshopVehicle/')
            or (rel.startswith('rom/audio/') and rel.endswith('.slib'))
            or (rel.startswith('rom/') and '/' not in rel[4:] and rel.endswith('.tsv')))


def write(path, value):
    with path.open('x', encoding='utf-8', newline='\n') as f:
        json.dump(value, f, ensure_ascii=False, indent=2)
        f.write('\n')


def baseline(root, out, manifest=None):
    root, out = root.resolve(), out.resolve()
    if out == root or out.is_relative_to(root):
        raise ValueError('Snapshot must be outside installation')
    if out.exists():
        raise FileExistsError(out)
    out.parent.mkdir(parents=True, exist_ok=True)
    budget = resources(out.parent)
    if budget.get('memory_available_bytes', 10**10) < 4 * 1024**3:
        raise MemoryError('Require at least 4 GiB available before analysis')
    paths = sorted(root.rglob('*'))
    if any(p.is_symlink() or p.is_junction() for p in paths):
        raise ValueError('Refuse redirected installation paths')
    paths = [p for p in paths if p.is_file()]
    required = sum(p.stat().st_size for p in paths if selected(p.relative_to(root).as_posix()))
    if budget['disk_free_bytes'] < required + 20 * 1024**3:
        raise OSError('Require snapshot plus 20 GiB free')
    out.mkdir()
    start = datetime.now(timezone.utc).isoformat()
    rows = []
    for i, p in enumerate(paths):
        rel = p.relative_to(root).as_posix()
        before = p.stat()
        row = {'path': rel, 'bytes': before.st_size, 'sha256': sha(p),
               'format': classify(p), 'snapshot': selected(rel)}
        if (before.st_size, before.st_mtime_ns) != (p.stat().st_size, p.stat().st_mtime_ns):
            raise ValueError('Source changed during classification: ' + rel)
        if row['snapshot']:
            dest = out / 'snapshot' / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(p, dest)
            if sha(dest) != row['sha256'] or sha(p) != row['sha256']:
                raise ValueError('Source/snapshot mismatch: ' + rel)
        rows.append(row)
        if i % 1000 == 0:
            print(f'Inventoried {i}/{len(paths)}', flush=True)
        if i % 100 == 0:
            time.sleep(.02)
    # Independent second complete pass catches additions, removals and changes.
    now = sorted(p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_file())
    if set(now) != {r['path'] for r in rows}:
        raise ValueError('Installation membership changed')
    for r in rows:
        if sha(root / r['path']) != r['sha256']:
            raise ValueError('Installation changed on second pass: ' + r['path'])
    steam = {}
    if manifest:
        text = manifest.read_text(encoding='utf-8')
        # Deliberately whitelist fields; never retain LastOwner/account data.
        for key in ('appid', 'name', 'buildid', 'TargetBuildID', 'StateFlags', 'lastupdated'):
            match = re.search(r'"' + key + r'"\s+"([^"\n]+)"', text, re.I)
            steam[key] = match.group(1) if match else None
    report = {'schema': 1, 'tool_version': VERSION, 'tool_sha256': sha(Path(__file__)),
              'python': platform.python_version(), 'started_utc': start,
              'completed_utc': datetime.now(timezone.utc).isoformat(),
              'resources_before': budget, 'steam': steam, 'file_count': len(rows),
              'total_bytes': sum(r['bytes'] for r in rows),
              'snapshot_count': sum(r['snapshot'] for r in rows),
              'snapshot_bytes': required, 'formats': dict(Counter(r['format'] for r in rows)),
              'consistency': 'all files identical on independent second hash pass; selected copies hash matched',
              'limits': 'Not an atomic filesystem snapshot. No claim about changes after final pass.',
              'files': rows}
    write(out / 'inventory.json', report)
    print(json.dumps({k: v for k, v in report.items() if k != 'files'}, indent=2))


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('installation', type=Path)
    ap.add_argument('output', type=Path)
    ap.add_argument('--steam-manifest', type=Path)
    a = ap.parse_args()
    baseline(a.installation, a.output, a.steam_manifest)
