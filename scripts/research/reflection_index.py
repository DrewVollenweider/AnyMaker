"""Recover bounded GCL structure/enum reflection descriptors after indexed code.

Supports observed descriptor kinds 13/14 with a zero unknown-list count.
This is a partial structural parser, not complete loader/type/ABI recovery.
Uninterpreted flags, unresolved lifecycle methods and duplicate names survive.
"""
import argparse
from collections import Counter
from contextlib import closing
import hashlib,json,re,sqlite3,struct
from pathlib import Path

from baseline import sha,write
from gcl_index import valid_signature

VERSION='1.0.0'


class Cursor:
    def __init__(self,data,offset):self.data,self.offset=data,offset
    def u32(self):
        if not 0<=self.offset<=len(self.data)-4:raise ValueError('Truncated descriptor integer')
        result=struct.unpack_from('<I',self.data,self.offset)[0];self.offset+=4;return result
    def text(self,empty=False):
        size=self.u32()
        if not (0 if empty else 1)<=size<=65536 or self.offset+size>len(self.data):
            raise ValueError('Invalid descriptor text length')
        raw=self.data[self.offset:self.offset+size];self.offset+=size
        if any(value<32 for value in raw):raise ValueError('Control character in descriptor text')
        return raw.decode('utf-8')
    def count(self):
        result=self.u32()
        if result>4096:raise ValueError('Unbounded descriptor count')
        return result


def type_name(name):
    return bool(name) and not any(char in name for char in '()\\/\r\n')


def parse(data,offset):
    c=Cursor(data,offset);kind=c.u32()
    if kind not in (13,14):raise ValueError('Unsupported descriptor kind')
    name=c.text();base=c.text(empty=True)
    if not type_name(name) or base and not type_name(base):raise ValueError('Invalid descriptor type name')
    size,alignment,flags=c.u32(),c.u32(),c.u32()
    if size>64*1024**2 or not 1<=alignment<=4096 or alignment&(alignment-1) or size%alignment or flags>65535:
        raise ValueError('Unsupported size/alignment/flag shape')
    enum_names=[c.text() for _ in range(c.count())]
    if kind==13 and enum_names:raise ValueError('Enum values in structure descriptor')
    virtuals=[c.text() for _ in range(c.count())]
    lifecycle=[c.text(empty=True) for _ in range(4)]
    if any(not valid_signature(value.encode()) for value in virtuals+lifecycle if value):
        raise ValueError('Invalid reflected function signature')
    unknown=c.u32()
    if unknown!=0:raise ValueError('Unsupported nonzero unknown-list count')
    fields=[]
    for _ in range(c.count()):
        field_type,field_name,field_offset=c.text(),c.text(),c.u32()
        if not type_name(field_type) or not re.fullmatch(r'[A-Za-z_$][A-Za-z0-9_$]*',field_name):
            raise ValueError('Invalid reflected field')
        if field_offset>size:raise ValueError('Reflected field starts outside object')
        fields.append(dict(type=field_type,name=field_name,offset=field_offset))
    if len({field['name'] for field in fields})!=len(fields):raise ValueError('Duplicate reflected field name')
    if kind==14 and (base or size!=4 or alignment!=4 or virtuals or fields or any(lifecycle)):
        raise ValueError('Unsupported enum descriptor layout')
    return dict(kind=kind,name=name,base=base,size=size,alignment=alignment,flags_uninterpreted=flags,
                enum_labels=enum_names,duplicate_enum_labels={key:count for key,count in Counter(enum_names).items() if count>1},
                virtual_methods=virtuals,lifecycle=lifecycle,
                unknown_list_count=unknown,fields=fields,offset=offset,length=c.offset-offset,
                descriptor_sha256=hashlib.sha256(data[offset:c.offset]).hexdigest())


def parse_table(data,offset):
    c=Cursor(data,offset);count=c.u32()
    if not 1<=count<=100000 or count*48>len(data)-c.offset:
        raise ValueError('Unbounded reflection table count')
    rows=[]
    for _ in range(count):
        row=parse(data,c.offset);rows.append(row);c.offset+=row['length']
    if c.offset!=len(data):raise ValueError('Reflection table does not end at EOF')
    return rows


def locate_table(data,start):
    rejected=Counter()
    for candidate in re.finditer(rb'[\x0d\x0e]\x00\x00\x00',data[start+4:min(start+65536,len(data))]):
        offset=start+candidate.start()
        try:return offset,parse_table(data,offset),dict(rejected)
        except (ValueError,UnicodeDecodeError) as error:rejected[str(error)]+=1
    raise ValueError('No bounded EOF-terminated reflection table in search window')


def build(source,index,output):
    if output.exists():raise FileExistsError(output)
    raw=source.read_bytes();digest=hashlib.sha256(raw).hexdigest()
    with closing(sqlite3.connect(index.resolve().as_uri()+'?mode=ro',uri=True)) as db:
        expected=json.loads(db.execute("SELECT value FROM provenance WHERE key='source_sha256'").fetchone()[0])
        if expected!=digest:raise ValueError('Reflection/index source mismatch')
        final=json.loads(db.execute('SELECT record FROM functions ORDER BY code_offset DESC LIMIT 1').fetchone()[0])
        start=final['code_offset']+final['serialized_size']
        methods={s:o for s,o in db.execute('SELECT signature,min(code_offset) FROM functions GROUP BY signature HAVING count(*)=1')}
    table_offset,rows,rejected=locate_table(raw,start)
    counts=Counter(row['name'] for row in rows)
    output.mkdir(parents=True)
    with closing(sqlite3.connect(output/'types.sqlite')) as db:
        db.executescript('CREATE TABLE metadata(key TEXT PRIMARY KEY,value TEXT);'
                         'CREATE TABLE types(offset INTEGER PRIMARY KEY,name TEXT,kind INTEGER,record TEXT);'
                         'CREATE INDEX names ON types(name);')
        for row in rows:
            row['same_name_records']=counts[row['name']]
            row['lifecycle_record_candidates']=[methods.get(value) if value else None for value in row['lifecycle']]
            row['virtual_record_candidates']=[methods.get(value) for value in row['virtual_methods']]
            db.execute('INSERT INTO types VALUES(?,?,?,?)',(row['offset'],row['name'],row['kind'],json.dumps(row)))
        report=dict(schema=1,tool_version=VERSION,tool_sha256=sha(Path(__file__)),source_sha256=digest,
                    scan_start=start,table_offset=table_offset,table_end=len(raw),
                    table_bytes=len(raw)-table_offset,prefix_bytes_unparsed=table_offset-start,
                    descriptors=len(rows),structures=sum(row['kind']==13 for row in rows),
                    enums=sum(row['kind']==14 for row in rows),ambiguous_names={k:v for k,v in counts.items() if v>1},
                    fields_starting_at_reported_size=[dict(type=row['name'],field=field['name'],field_type=field['type'],offset=field['offset'])
                        for row in rows for field in row['fields'] if field['offset']==row['size']],
                    complete_storage_widths_checked=False,
                    rejected_candidates=rejected,
                    limits='Observed kinds 13/14 only; flags and unknown zero-list meaning unresolved. Descriptor vtable/lifecycle names are declarations, not executed runtime calls or complete ABI recovery.')
        if sha(source)!=digest:raise ValueError('Source changed during descriptor indexing')
        db.execute('INSERT INTO metadata VALUES(?,?)',('provenance',json.dumps(report)));db.commit()
    write(output/'summary.json',report)
    print(json.dumps({key:report[key] for key in ['descriptors','structures','enums','ambiguous_names','scan_start']}))
    return report


def lookup(database,name):
    with closing(sqlite3.connect(database.resolve().as_uri()+'?mode=ro',uri=True)) as db:
        rows=db.execute('SELECT record FROM types WHERE name=?',(name,)).fetchall()
    if len(rows)!=1:raise ValueError('Missing or ambiguous reflected type')
    return json.loads(rows[0][0])


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);sub=parser.add_subparsers(dest='command',required=True)
    command=sub.add_parser('build')
    for name in ('source','index','output'):command.add_argument(name,type=Path)
    command=sub.add_parser('show');command.add_argument('database',type=Path);command.add_argument('name')
    command.add_argument('--section',choices=['header','fields','methods','enum'],default='header')
    args=parser.parse_args()
    if args.command=='build':build(args.source,args.index,args.output)
    else:
        result=lookup(args.database,args.name)
        if args.section=='fields':result=result['fields']
        elif args.section=='methods':result=result['virtual_methods']
        elif args.section=='enum':result=result['enum_labels']
        else:result={key:value for key,value in result.items() if key not in ('fields','virtual_methods','virtual_record_candidates')}
        print(json.dumps(result,indent=2))
