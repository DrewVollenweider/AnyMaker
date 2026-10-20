"""Audit Ghidra machine facts and trace proven local uses of GCL operand slots.

This is conservative static dataflow, not game execution or a complete call graph.
Register provenance is discarded at branches, joins, gaps and every call. COPY,
same-width CAST, addition and pointer-load ancestry are followed. A slot-derived
call proves a local data dependency, not that its named candidate is the bound
callee: kind 6 operands, for example, occur in multi-load virtual dispatch.
"""
import argparse
from collections import Counter
from contextlib import closing
import hashlib
import json
from pathlib import Path
import re
import sqlite3
import struct

from baseline import sha, write
from gcl_index import record as parse_record

VERSION = '1.0.0'


def node_key(node):
    return node['space'], int(node['offset']), node['size']


def checked_nodes(op):
    if not isinstance(op.get('opcode'), str):
        raise ValueError('Invalid p-code opcode')
    for n in [op.get('output'), *op.get('inputs', [])]:
        if n is None:
            continue
        if not isinstance(n, dict) or not isinstance(n.get('space'), str):
            raise ValueError('Invalid p-code varnode')
        if not 0 <= int(n['offset']) < 2**64 or type(n.get('size')) is not int or not 1 <= n['size'] <= 256:
            raise ValueError('Unbounded p-code varnode')


def interpret(instructions, slots):
    """Return auditable call-site/slot-read records; never speculate across CFG joins."""
    regs, calls, reads = {}, [], []
    branch_targets = set()
    for ins in instructions:
        for op in ins['pcode']:
            if op['opcode'] in ('BRANCH', 'CBRANCH') and op['inputs']:
                dest = op['inputs'][0]
                if dest['space'] == 'ram':
                    branch_targets.add(int(dest['offset']))
    previous_fallthrough = None
    for ins in instructions:
        address = int(ins['address'])
        if address in branch_targets or address != previous_fallthrough:
            regs.clear()
        local = {}

        def slot_read(slot):
            reads.append({'instruction': address, 'slot_address':slot, **slots[slot]})
            return ('operand-slot', slot, address, [{'instruction':address, 'operation':'read-slot'}])

        def value(n):
            if n is None:
                return None
            if n.get('constant'):
                return ('integer', int(n['offset']), None)
            if n['space'] == 'ram' and n['size'] == 8 and int(n['offset']) in slots:
                return slot_read(int(n['offset']))
            return (regs if n.get('register') else local).get(node_key(n))

        def assign(n, val):
            if n is None:
                return
            key = node_key(n)
            env = regs if n.get('register') else local
            # A write to EAX/AX/AL invalidates an earlier RAX pointer, and vice versa.
            if n.get('register'):
                for k in list(env):
                    if k[0] == key[0] and max(k[1], key[1]) < min(k[1]+k[2], key[1]+key[2]):
                        del env[k]
            if val is not None:
                env[key] = val

        has_call, transfer = False, False
        for op in ins['pcode']:
            checked_nodes(op)
            code, inputs, output = op['opcode'], op['inputs'], op.get('output')
            values = [None if i==0 and code in ('CALL','BRANCH','CBRANCH') else value(n)
                      for i,n in enumerate(inputs)]
            result = None
            if code in ('COPY', 'CAST') and inputs and output and inputs[0]['size'] == output['size']:
                result = values[0]
            elif code in ('INT_ADD', 'INT_SUB') and len(values) == 2 and output:
                if all(v is not None and v[0] == 'integer' for v in values):
                    number = values[0][1] + (1 if code == 'INT_ADD' else -1)*values[1][1]
                    result = ('integer', number % (1 << (output['size']*8)), None)
                elif code == 'INT_ADD' and output['size'] == 8:
                    tagged = [v for v in values if v is not None and v[0] == 'operand-slot']
                    if len(tagged) == 1:
                        t = tagged[0]
                        result = (*t[:3], t[3]+[{'instruction':address,'operation':'INT_ADD'}])
            elif code == 'LOAD' and len(values) == 2:
                pointer = values[1]
                if pointer is not None and pointer[0] == 'integer' and pointer[1] in slots and output and output['size'] == 8:
                    result = slot_read(pointer[1])
                elif pointer is not None and pointer[0] == 'operand-slot' and output and output['size'] == 8:
                    result = (*pointer[:3],pointer[3]+[{'instruction':address,'operation':'LOAD'}])
            elif code in ('CALL', 'CALLIND'):
                call = {'instruction': address, 'bytes': ins['bytes'], 'instruction_text': ins['text'],
                        'opcode': code, 'resolution': 'unresolved-indirect'}
                if code == 'CALLIND' and values and values[0] is not None and values[0][0] == 'operand-slot':
                    _, slot, loaded, steps = values[0]
                    call.update(resolution='slot-derived-in-local-block', slot_address=slot,
                                loaded_at=loaded, dependency_steps=steps, **slots[slot])
                elif code == 'CALL' and inputs and inputs[0]['space'] == 'ram':
                    call.update(resolution='direct-address', target_address=int(inputs[0]['offset']))
                calls.append(call)
                has_call = True
            if code in ('BRANCH', 'CBRANCH', 'BRANCHIND', 'RETURN'):
                transfer = True
            assign(output, result)
        # No assumption that the GCL compiler follows a particular volatile-register ABI.
        if has_call or transfer:
            regs.clear()
        fallthrough = ins.get('fallthrough')
        previous_fallthrough = int(fallthrough) if fallthrough is not None else None
    return calls, reads


def validate_instructions(facts, rec, source, assembly):
    if facts.get('schema') != 1:
        raise ValueError('Unsupported machine-facts schema')
    for k in ('signature', 'code_offset', 'code_size', 'export_name'):
        if facts.get(k) != rec[k]:
            raise ValueError('Machine-facts header mismatch: '+k)
    if facts.get('decompile_completed') is not True:
        raise ValueError('Decompiler did not complete')
    instructions = facts.get('instructions')
    if not isinstance(instructions, list) or not instructions or len(instructions) > rec['code_size']:
        raise ValueError('Invalid instruction count')
    expected = []
    for line in assembly.splitlines():
        if line.startswith('#'):
            continue
        address, raw, text = line.split('\t', 2)
        expected.append((int(address, 16), raw, text))
    actual, end = [], rec['code_offset']
    for ins in instructions:
        address, raw = int(ins['address']), bytes.fromhex(ins['bytes'])
        if not raw or len(raw) > 15 or address < end or address+len(raw) > rec['code_offset']+rec['code_size']:
            raise ValueError('Instruction outside record or overlapping')
        if source[address:address+len(raw)] != raw:
            raise ValueError('Machine-facts bytes differ from snapshot')
        end = address+len(raw)
        actual.append((address, ins['bytes'], ins['text']))
        if len(ins['pcode']) > 1024:
            raise ValueError('Unbounded instruction p-code')
        for op in ins['pcode']:
            checked_nodes(op)
    if actual != expected:
        raise ValueError('Machine-facts and assembly export disagree')
    return instructions


def embedded_reads(instructions, rec, source):
    """Report literal raw reads in the declared code area, excluding decoded instructions.

    Values are interpretations of bytes, not assertions about field types/units.
    """
    spans = [(int(i['address']), int(i['address'])+len(bytes.fromhex(i['bytes']))) for i in instructions]
    result = []
    seen = set()
    for ins in instructions:
        for op in ins['pcode']:
            candidates = []
            if op['opcode'] == 'LOAD' and op.get('output') and len(op['inputs']) == 2:
                ptr = op['inputs'][1]
                if ptr.get('constant'):
                    candidates.append((int(ptr['offset']),op['output']['size']))
            if op['opcode'] not in ('CALL','BRANCH','CBRANCH','RETURN'):
                candidates.extend((int(n['offset']),n['size']) for n in op['inputs'] if n['space']=='ram')
            for offset, width in candidates:
                if not rec['code_offset'] <= offset < offset+width <= rec['code_offset']+rec['code_size']:
                    continue
                if any(max(offset, lo) < min(offset+width, hi) for lo, hi in spans):
                    continue
                k = int(ins['address']), offset, width
                if k in seen:
                    continue
                seen.add(k)
                data = source[offset:offset+width]
                row = {'instruction': k[0], 'offset': offset, 'width': width, 'bytes': data.hex(),
                       'unsigned_le': int.from_bytes(data, 'little')}
                if width in (4, 8):
                    f = struct.unpack('<f' if width == 4 else '<d', data)[0]
                    row['ieee_float_interpretation'] = f if abs(f) <= 1.7976931348623157e308 else str(f)
                result.append(row)
    return result


def literal_strings(instructions, rec, source):
    spans = [(int(i['address']),int(i['address'])+len(bytes.fromhex(i['bytes']))) for i in instructions]
    result = []
    for match in re.finditer(rb'[\x20-\x7e]{3,256}',source[rec['code_offset']:rec['code_offset']+rec['code_size']]):
        lo,hi=rec['code_offset']+match.start(),rec['code_offset']+match.end()
        if not any(max(lo,a)<min(hi,b) for a,b in spans):
            result.append({'offset':lo,'text':match[0].decode('ascii'),
                           'classification':'printable-data-candidate'})
    return result


def address_literals(instructions,rec,source):
    """Preview in-record addresses passed onward; unlike embedded_reads this is not a read claim."""
    spans=[(int(i['address']),int(i['address'])+len(bytes.fromhex(i['bytes']))) for i in instructions]
    result=[];seen=set();end=rec['code_offset']+rec['code_size']
    for ins in instructions:
        for op in ins['pcode']:
            for n in op['inputs']:
                if not n.get('constant'):continue
                at=int(n['offset']);k=int(ins['address']),at
                if k in seen or not rec['code_offset']<=at<end or any(a<=at<b for a,b in spans):continue
                seen.add(k);raw=source[at:min(at+16,end)]
                preview=source[at:min(at+128,end)].split(b'\0',1)[0]
                row={'instruction':k[0],'address':at,'preview_bytes':raw.hex(),
                     'classification':'address-reference-not-proven-read'}
                if len(raw)>=8:
                    f=struct.unpack('<d',raw[:8])[0]
                    row['preview_f64']=f if abs(f)<=1.7976931348623157e308 else str(f)
                if preview and all(32<=b<127 for b in preview):row['ascii_prefix']=preview.decode('ascii')
                result.append(row)
    return result


def audit(source, database, folder, output):
    if output.exists():
        raise FileExistsError(output)
    raw = source.read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    meta = json.loads((folder/'records.json').read_text(encoding='utf-8'))
    with closing(sqlite3.connect(database.resolve().as_uri()+'?mode=ro', uri=True)) as db:
        expected = json.loads(db.execute("SELECT value FROM provenance WHERE key='source_sha256'").fetchone()[0])
        if expected != digest or meta['source_sha256'] != digest:
            raise ValueError('Index/export/source mismatch')
        if not 0 < len(meta['records']) <= 256:
            raise ValueError('Select at most 256 functions per evidence bundle')
        results = []
        for rec in meta['records']:
            name = rec['export_name']
            if not re.fullmatch(r'[A-Za-z0-9_]+', name):
                raise ValueError('Unsafe export name')
            reparsed = parse_record(raw, rec['signature_offset'])
            if any(rec.get(k) != v for k, v in reparsed.items()):
                raise ValueError('Export record disagrees with original GCL metadata')
            factpath = folder/'ghidra'/(name+'.facts.json')
            facts = json.loads(factpath.read_text(encoding='utf-8'))
            instructions = validate_instructions(facts, rec, raw,
                (folder/'ghidra'/(name+'.asm.tsv')).read_text(encoding='utf-8'))
            slots = {rec['code_offset']+r['slot_offset']:dict(r) for r in rec['references']}
            calls, reads = interpret(instructions, slots)
            for call in calls:
                symbol = call.get('symbol')
                rows = db.execute('SELECT code_offset,code_size FROM functions WHERE signature=?', (symbol,)).fetchall() if symbol else []
                if len(rows) == 1 and call.get('kind') in (4, 6):
                    call['target_record_candidate'] = {'code_offset':rows[0][0], 'code_size':rows[0][1]}
                elif symbol:
                    call['target_record_candidate'] = None
            results.append({'signature':rec['signature'], 'code_offset':rec['code_offset'],
                'code_sha256':rec['code_sha256'], 'export_name':name, 'facts_sha256':sha(factpath),
                'instructions_byte_checked':len(instructions), 'call_sites':calls,
                'slot_reads':reads, 'embedded_reads':embedded_reads(instructions, rec, raw),
                'literal_strings':literal_strings(instructions, rec, raw),
                'address_literals':address_literals(instructions,rec,raw)})
    if sha(source) != digest:
        raise ValueError('Source changed during analysis')
    counts = Counter(c['resolution'] for r in results for c in r['call_sites'])
    report = {'schema':1, 'tool_version':VERSION, 'tool_sha256':sha(Path(__file__)),
        'source_sha256':digest, 'functions':results, 'call_site_resolution_counts':dict(counts),
        'instruction_count':sum(r['instructions_byte_checked'] for r in results),
        'limits':['A resolved call site is a static CALL/CALLIND instruction, not an observed execution.',
                  'Slot-derived virtual calls prove operand dependency; the matching signature is a candidate, not a proven bound dispatch target.',
                  'Register provenance is reset at every call and control-flow boundary; unresolved sites are retained.',
                  'P-code comes from Ghidra; exact original instruction bytes and paired assembly are checked.',
                  'Embedded scalar interpretations are raw bytes, not recovered type or unit assertions.',
                  'No game process is launched, attached to, modified, or required.']}
    write(output, report)
    print(json.dumps({'functions':len(results), 'instructions_byte_checked':report['instruction_count'],
                      'call_sites':dict(counts)}, indent=2))
    return report


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    for name in ('source', 'database', 'export_folder', 'output'):
        p.add_argument(name, type=Path)
    args = p.parse_args()
    audit(args.source, args.database, args.export_folder, args.output)
