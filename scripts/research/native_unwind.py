"""Resolve bounded x64 PE runtime ranges linked by chained unwind metadata.

Decodes version-1 chained links only. Nonchained version-2 headers can be opaque
roots; unwind operations, handlers, register ABI and complete CFG are not decoded.
No executable is loaded or run. Microsoft x64 exception-handling layout:
https://learn.microsoft.com/en-us/cpp/build/exception-handling-x64
"""
import argparse
from collections import defaultdict
import hashlib
import json
from pathlib import Path
import struct

from native_image import Image

VERSION = '1.0.0'


def _key(row):
    return row['begin_rva'],row['end_rva'],row['unwind_rva']


class UnwindGroups:
    def __init__(self,image):
        self.image = image
        self.rows = {}
        self.metadata = {}
        for row in image.runtime_functions:
            key = _key(row)
            if key in self.rows:
                raise ValueError('Ambiguous duplicate runtime entry')
            self.rows[key] = row
            self.metadata[key] = self._metadata(row)
        self.roots = {}
        for key in self.rows:
            path = []
            current = key
            seen = set()
            while current not in self.roots:
                if current in seen:
                    raise ValueError('Cyclic chained unwind metadata')
                if current not in self.rows:
                    raise ValueError('Chained target is not one exact runtime entry')
                seen.add(current)
                path.append(current)
                parent = self.metadata[current]['parent']
                if parent is None:
                    root = current
                    break
                current = tuple(parent)
            else:
                root = self.roots[current]
            for item in path:
                self.roots[item] = root
        self.members = defaultdict(list)
        for key,root in self.roots.items():
            self.members[root].append(key)

    def _metadata(self,row):
        rva = row['unwind_rva']
        if not rva:
            return dict(unwind_rva=0,version=None,flags=None,parent=None,bytes='')
        if rva%4:
            raise ValueError('Unaligned unwind metadata')
        at = self.image.file_offset(rva,4)
        raw = self.image.raw
        version,flags = raw[at]&7,raw[at]>>3
        count = raw[at+2]
        if version not in (1,2) or flags&~7 or flags&4 and flags&3:
            raise ValueError('Unsupported unwind header/flag combination')
        parent = None
        if version==2:
            if flags&4:
                raise ValueError('Version-2 chained decoding is outside this tool')
            width = 4
        else:
            width = 4+((count+1)&~1)*2
            if flags&4:
                link_at = self.image.file_offset(rva+width,12)
                parent = list(struct.unpack_from('<III',raw,link_at))
                width += 12
            elif flags&3:
                width += 4
        at = self.image.file_offset(rva,width)
        data = raw[at:at+width]
        return dict(unwind_rva=rva,version=version,flags=flags,code_slots=count,
                    parent=parent,bytes=data.hex(),sha256=hashlib.sha256(data).hexdigest())

    def group(self,rva):
        found = self.image.containing_runtime_ranges(rva)
        if len(found)!=1:
            raise ValueError('Select one unambiguous declared runtime range')
        root = self.roots[_key(found[0])]
        members = sorted(self.members[root])
        ranges = [self.rows[k] for k in members]
        if any(a['end_rva']>b['begin_rva'] for a,b in zip(ranges,ranges[1:])):
            raise ValueError('Overlapping chained ranges')
        return dict(primary=dict(self.rows[root]),ranges=[dict(r) for r in ranges],
                    unwind=[dict(self.metadata[k]) for k in members],
                    contiguous=all(a['end_rva']==b['begin_rva'] for a,b in zip(ranges,ranges[1:])),
                    limits='Metadata-linked ranges only; not all code, leaf functions, ABI, operations, handler semantics or a complete CFG.')


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('source',type=Path);p.add_argument('rva',type=lambda x:int(x,0))
    a=p.parse_args();raw=a.source.read_bytes()
    print(json.dumps(dict(source_sha256=hashlib.sha256(raw).hexdigest(),
                          group=UnwindGroups(Image(raw)).group(a.rva)),indent=2))
