"""Index a local x64 PE image and conservative native-signature reference leads.

Reads bytes only; never loads/executes the executable. Exception-directory
ranges omit leaf functions and are not a complete native function inventory.
Relative-displacement matches are byte-pattern leads, not decoded instructions
or proven signature/function bindings. Full native code/indexes stay local.
"""
import argparse,hashlib,json,re,sqlite3,struct
from contextlib import closing
from pathlib import Path
from baseline import sha,write
from gcl_index import valid_signature

VERSION='1.0.0'


class Image:
    def __init__(self,raw):
        self.raw=raw
        def integer(at,fmt):
            size=struct.calcsize(fmt)
            if not 0<=at<=len(raw)-size:raise ValueError('Truncated PE field')
            return struct.unpack_from(fmt,raw,at)[0]
        if len(raw)<64 or raw[:2]!=b'MZ':raise ValueError('Missing DOS header')
        pe=integer(0x3c,'<I')
        if pe<64 or raw[pe:pe+4]!=b'PE\0\0':raise ValueError('Missing bounded PE header')
        coff=pe+4;opt=coff+20
        if integer(coff,'<H')!=0x8664:raise ValueError('Only x64 PE supported')
        count=integer(coff+2,'<H');optional_size=integer(coff+16,'<H')
        if not 1<=count<=96 or optional_size<112 or opt+optional_size>len(raw):
            raise ValueError('Invalid PE header bounds')
        if integer(opt,'<H')!=0x20b:raise ValueError('Only PE32+ supported')
        self.image_base=integer(opt+24,'<Q');self.image_size=integer(opt+56,'<I')
        self.headers_size=integer(opt+60,'<I');directories=integer(opt+108,'<I')
        if not 0<self.headers_size<=len(raw) or self.image_size<self.headers_size:
            raise ValueError('Invalid image/header size')
        if directories>16 or optional_size<112+directories*8:raise ValueError('Invalid directory bounds')
        section_at=opt+optional_size
        if section_at+count*40>self.headers_size:raise ValueError('Sections extend beyond headers')
        self.sections=[]
        for i in range(count):
            at=section_at+i*40;name=raw[at:at+8].split(b'\0')[0].decode('ascii')
            virtual_size,rva,size,offset=struct.unpack_from('<IIII',raw,at+8)
            flags=integer(at+36,'<I');mapped=max(virtual_size,size)
            if not name or not mapped or rva<self.headers_size or rva+mapped>self.image_size:
                raise ValueError('Invalid section virtual bounds')
            if size and (offset<self.headers_size or offset+size>len(raw)):
                raise ValueError('Invalid section file bounds')
            self.sections.append(dict(name=name,rva=rva,virtual_size=virtual_size,
                                      raw_size=size,raw_offset=offset,flags=flags))
        for first,second in zip(sorted(self.sections,key=lambda x:x['rva']),sorted(self.sections,key=lambda x:x['rva'])[1:]):
            if first['rva']+max(first['virtual_size'],first['raw_size'])>second['rva']:
                raise ValueError('Overlapping virtual sections')
        backed=sorted((s for s in self.sections if s['raw_size']),key=lambda x:x['raw_offset'])
        for first,second in zip(backed,backed[1:]):
            if first['raw_offset']+first['raw_size']>second['raw_offset']:raise ValueError('Overlapping file sections')
        self.runtime_functions=[]
        if directories>3:
            rva,size=struct.unpack_from('<II',raw,opt+112+8*3)
            if bool(rva)!=bool(size) or size%12 or size>16*1024**2:raise ValueError('Invalid exception-directory bounds')
            if size:
                offset=self.file_offset(rva,size)
                for i in range(0,size,12):
                    begin,end,unwind=struct.unpack_from('<III',raw,offset+i)
                    if not begin<end:raise ValueError('Empty/reversed runtime-function range')
                    code=self.file_offset(begin,end-begin)
                    if not self.section_for_rva(begin)['flags']&0x20000000:
                        raise ValueError('Runtime range outside executable section')
                    if unwind:self.file_offset(unwind,1)
                    self.runtime_functions.append(dict(begin_rva=begin,end_rva=end,unwind_rva=unwind,
                        file_offset=code,code_sha256=hashlib.sha256(raw[code:code+end-begin]).hexdigest()))
        self.runtime_functions.sort(key=lambda x:(x['begin_rva'],x['end_rva']))
        self.starts=[x['begin_rva'] for x in self.runtime_functions]

    def section_for_rva(self,rva):
        found=[s for s in self.sections if s['rva']<=rva<s['rva']+max(s['virtual_size'],s['raw_size'])]
        if len(found)!=1:raise ValueError('RVA is not in one mapped section')
        return found[0]

    def file_offset(self,rva,width=1):
        if type(rva) is not int or type(width) is not int or rva<0 or width<=0:raise ValueError('Invalid RVA span')
        if rva<self.headers_size:
            if rva+width<=self.headers_size:return rva
            raise ValueError('RVA span crosses header boundary')
        s=self.section_for_rva(rva)
        if rva+width>s['rva']+s['raw_size']:raise ValueError('RVA span is not completely file backed')
        return s['raw_offset']+rva-s['rva']

    def rva_for_offset(self,offset,width=1):
        if type(offset) is not int or type(width) is not int or offset<0 or width<=0:raise ValueError('Invalid file span')
        if offset+width<=self.headers_size:return offset
        found=[s for s in self.sections if s['raw_offset']<=offset and offset+width<=s['raw_offset']+s['raw_size']]
        if len(found)!=1:raise ValueError('File span is not in one backed section')
        s=found[0];return s['rva']+offset-s['raw_offset']

    def containing_runtime_ranges(self,rva):
        # Preserve overlapping/duplicate entries instead of assuming uniqueness.
        return [r for r in self.runtime_functions if r['begin_rva']<=rva<r['end_rva']]

    def signatures(self):
        rows=[]
        for s in self.sections:
            if s['flags']&0x20000000:continue
            raw=self.raw[s['raw_offset']:s['raw_offset']+s['raw_size']]
            for m in re.finditer(rb'[ -~]{8,1024}\x00',raw):
                value=m.group()[:-1]
                if valid_signature(value):
                    at=s['raw_offset']+m.start()
                    rows.append(dict(signature=value.decode('ascii'),file_offset=at,rva=self.rva_for_offset(at,len(value)+1)))
        return rows

    def relative_signature_leads(self,signatures):
        targets={r['rva']:r for r in signatures};leads=[]
        for s in self.sections:
            if not s['flags']&0x20000000:continue
            start=s['raw_offset'];end=start+s['raw_size']
            for at in range(start,end-3):
                rva=s['rva']+at-start
                target=rva+4+struct.unpack_from('<i',self.raw,at)[0]
                if target in targets:
                    leads.append(dict(displacement_file_offset=at,displacement_rva=rva,
                        target_rva=target,signature=targets[target]['signature'],
                        containing_runtime_begin_rvas=[r['begin_rva'] for r in self.containing_runtime_ranges(rva)],
                        status='byte_pattern_candidate_not_decoded_or_bound'))
        return leads


def build(source,output):
    if output.exists():raise FileExistsError(output)
    raw=source.read_bytes();digest=hashlib.sha256(raw).hexdigest();image=Image(raw)
    signatures=image.signatures();leads=image.relative_signature_leads(signatures)
    output.mkdir(parents=True)
    report=dict(schema=1,tool_version=VERSION,tool_sha256=sha(Path(__file__)),source_sha256=digest,
        source_bytes=len(raw),image_base=image.image_base,image_size=image.image_size,sections=image.sections,
        runtime_function_records=len(image.runtime_functions),signature_strings=len(signatures),relative_signature_leads=len(leads),
        limits=['Exception-directory records omit leaf functions and do not recover all native functions.',
                'Relative byte patterns can be false positives; decode and trace before asserting a binding.',
                'No native execution, ABI recovery or complete PE loader/relocation proof.'])
    with closing(sqlite3.connect(output/'native.sqlite')) as db:
        db.executescript('CREATE TABLE metadata(key TEXT PRIMARY KEY,value TEXT);'
            'CREATE TABLE ranges(id INTEGER PRIMARY KEY,begin_rva INTEGER,end_rva INTEGER,record TEXT);'
            'CREATE TABLE signatures(id INTEGER PRIMARY KEY,rva INTEGER,signature TEXT,record TEXT);'
            'CREATE TABLE leads(id INTEGER PRIMARY KEY,displacement_rva INTEGER,target_rva INTEGER,signature TEXT,record TEXT);'
            'CREATE INDEX signature_names ON signatures(signature);')
        db.executemany('INSERT INTO ranges(begin_rva,end_rva,record) VALUES(?,?,?)',
                       [(r['begin_rva'],r['end_rva'],json.dumps(r)) for r in image.runtime_functions])
        db.executemany('INSERT INTO signatures(rva,signature,record) VALUES(?,?,?)',
                       [(r['rva'],r['signature'],json.dumps(r)) for r in signatures])
        db.executemany('INSERT INTO leads(displacement_rva,target_rva,signature,record) VALUES(?,?,?,?)',
                       [(r['displacement_rva'],r['target_rva'],r['signature'],json.dumps(r)) for r in leads])
        if sha(source)!=digest:raise ValueError('Source changed during native indexing')
        db.execute('INSERT INTO metadata VALUES(?,?)',('provenance',json.dumps(report)));db.commit()
    write(output/'summary.json',report)
    print(json.dumps({k:report[k] for k in ['runtime_function_records','signature_strings','relative_signature_leads']}))
    return report


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('source',type=Path);p.add_argument('output',type=Path)
    a=p.parse_args();build(a.source,a.output)
