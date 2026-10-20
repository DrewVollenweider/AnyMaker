"""Recheck selected reflected declarations against an exact local GCL copy."""
import argparse
from collections import Counter
import hashlib,json
from pathlib import Path

from baseline import sha,write
from reflection_index import parse_table


def check(source,evidence,output=None):
    raw=source.read_bytes();claims=json.loads(evidence.read_text(encoding='utf-8'))
    if claims.get('schema')!=1:raise ValueError('Unknown reflection evidence schema')
    digest=hashlib.sha256(raw).hexdigest()
    if digest!=claims['source_sha256']:raise ValueError('Reflection evidence/source mismatch')
    table=claims['table'];rows=parse_table(raw,table['offset'])
    if len(rows)!=table['records'] or len(raw)!=table['end'] or hashlib.sha256(raw[table['offset']:]).hexdigest()!=table['sha256']:
        raise ValueError('Changed reflection table identity')
    counts=Counter(row['name'] for row in rows)
    by_name={row['name']:row for row in rows if counts[row['name']]==1}
    selected={}
    for identity in claims['types']:
        row=by_name.get(identity['name'])
        if row is None or any(row[key]!=value for key,value in identity.items()):
            raise ValueError('Changed or ambiguous reflected type '+identity['name'])
        selected[row['name']]=row
    for item in claims['enums']:
        if selected[item['type']]['enum_labels']!=item['labels']:
            raise ValueError('Changed enum labels '+item['type'])
    for item in claims['fields']:
        if item['field'] not in selected[item['type']]['fields']:
            raise ValueError('Changed reflected field '+item['type'])
    for item in claims['virtuals']:
        methods=selected[item['type']]['virtual_methods'];slot=item['slot']
        if type(slot) is not int or not 0<=slot<len(methods) or methods[slot]!=item['signature']:
            raise ValueError('Changed reflected method declaration '+item['type'])
    report=dict(schema=1,source_sha256=digest,tool_sha256=sha(Path(__file__)),
                table_records_checked=len(rows),selected_type_identities_checked=len(selected),
                enum_label_lists_checked=len(claims['enums']),fields_checked=len(claims['fields']),
                virtual_declarations_checked=len(claims['virtuals']),
                limits='Static descriptor declarations and identities only. Not executed dispatch, full storage ABI, units, lifecycle semantics or whole-game understanding.')
    if output:write(output,report)
    print(json.dumps(report,indent=2));return report


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source',type=Path);parser.add_argument('evidence',type=Path)
    parser.add_argument('--output',type=Path)
    args=parser.parse_args();check(args.source,args.evidence,args.output)
