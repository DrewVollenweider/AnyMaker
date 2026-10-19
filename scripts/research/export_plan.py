"""Create a deterministic Ghidra export plan from indexed records on a matching copy."""
import argparse
from contextlib import closing
import hashlib
import json
from pathlib import Path
import re
import sqlite3

from baseline import sha, write


def plan(source, database, output, terms):
    if output.exists():
        raise FileExistsError(output)
    with closing(sqlite3.connect(database.resolve().as_uri() + '?mode=ro', uri=True)) as db:
        expected = json.loads(db.execute("SELECT value FROM provenance WHERE key='source_sha256'").fetchone()[0])
        index_tool = json.loads(db.execute("SELECT value FROM provenance WHERE key='tool_sha256'").fetchone()[0])
        if index_tool != sha(Path(__file__).with_name('gcl_index.py')):
            raise ValueError('Index parser version/hash differs; rebuild index before reuse')
        if sha(source) != expected:
            raise ValueError('Index/source version mismatch')
        b = source.read_bytes()
        rows = {}
        for term in terms:
            for row in db.execute('SELECT record FROM functions WHERE instr(signature,?)>0', (term,)):
                r = json.loads(row[0])
                if r['same_signature_records'] != 1:
                    raise ValueError('Ambiguous function: '+r['signature'])
                rows[r['code_offset']] = r
    if not rows:
        raise ValueError('No matching functions')
    output.mkdir()
    lines = []
    for offset, r in sorted(rows.items()):
        if hashlib.sha256(b[offset:offset+r['code_size']]).hexdigest() != r['code_sha256']:
            raise ValueError('Code hash mismatch')
        short = r['signature'].split(') ', 1)[-1].split(' (', 1)[0]
        name = 'f_' + str(offset) + '_' + re.sub('[^a-zA-Z0-9_]', '_', short)[-85:]
        r['export_name'] = name
        lines.append(f"F\t{offset}\t{r['code_size']}\t{name}\t{r['signature']}")
        for ref in r['references']:
            symbol = ref['symbol'] or 'numeric_' + str(ref.get('operand_u32'))
            label = 'ref_' + str(offset) + '_' + str(ref['slot_offset']) + '_' + re.sub('[^a-zA-Z0-9_]', '_', symbol)[:100]
            lines.append(f"R\t{offset+ref['slot_offset']}\t{ref['kind']}\t{label}\t{symbol}")
    (output/'plan.tsv').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    write(output/'records.json', {'source_sha256':expected,'records':list(rows.values()),
          'limits':'Raw pointers remain unresolved. Labels annotate slots; no original bytes are patched.'})
    print(f'Prepared {len(rows)} functions')


if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('source',type=Path)
    ap.add_argument('database',type=Path)
    ap.add_argument('output',type=Path)
    ap.add_argument('terms',nargs='+')
    a=ap.parse_args()
    plan(a.source,a.database,a.output,a.terms)
