"""Read-only static inspection of explicitly named installed Anymaker binaries."""
import archive_paths as ap
import hashlib
import json
from pathlib import Path
import re
import struct
import anymaker as am

ROOT=ap.install('')


def inspect(path):
    raw=path.read_bytes()
    result={'file':str(path),'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest(),'first_16_bytes_hex':raw[:16].hex()}
    if raw[:2]==b'MZ':
        offset=struct.unpack_from('<I',raw,0x3c)[0]
        if raw[offset:offset+4]!=b'PE\0\0': raise ValueError('Invalid PE signature')
        machine,count,timestamp,_,_,optional_size,flags=struct.unpack_from('<HHIIIHH',raw,offset+4)
        optional=offset+24; magic=struct.unpack_from('<H',raw,optional)[0]
        result.update(machine=hex(machine),architecture='x64' if machine==0x8664 else 'other',pe_optional_magic=hex(magic),sections=[])
        section_start=optional+optional_size
        sections=[]
        for i in range(count):
            at=section_start+i*40
            name=raw[at:at+8].rstrip(b'\0').decode('ascii','replace')
            virtual_size,rva,size,file_offset=struct.unpack_from('<IIII',raw,at+8)
            sections.append((rva,max(virtual_size,size),file_offset,size))
            result['sections'].append({'name':name,'virtual_bytes':virtual_size,'file_bytes':size})
        def physical(rva):
            for start,span,file_offset,size in sections:
                if start<=rva<start+span and rva-start<size: return file_offset+rva-start
            raise ValueError('Unmapped RVA')
        def cstring(at):
            return raw[at:raw.index(b'\0',at)].decode('ascii','replace')
        dirs=optional+(112 if magic==0x20b else 96)
        imports_rva,imports_size=struct.unpack_from('<II',raw,dirs+8)
        imports=[]
        if imports_rva:
            at=physical(imports_rva)
            while True:
                lookup,stamp,forwarder,name_rva,first=struct.unpack_from('<IIIII',raw,at)
                if not any((lookup,stamp,forwarder,name_rva,first)): break
                imports.append(cstring(physical(name_rva))); at+=20
        result['imported_libraries']=imports
    needles=('game.gcl','on_tick','microcontroller','WinHttp','WinInet','CreateFile','WriteFile','LoadLibrary','GetProcAddress','WSAStartup','SteamAPI','telemetry')
    found=set()
    for match in re.finditer(rb'[\x20-\x7e]{5,}',raw):
        text=match.group().decode('ascii')
        for needle in needles:
            if needle.lower() in text.lower(): found.add(needle)
    result['targeted_readable_markers']=sorted(found)
    result['hash_unchanged_after_read']=hashlib.sha256(path.read_bytes()).hexdigest()==result['sha256']
    return result


if __name__=='__main__':
    report=[inspect(ROOT/name) for name in ('game.exe','steam_api64.dll','bin/game.gcl')]
    print(am.save('installed-binaries.json',report))
    print(json.dumps(report,indent=2))
