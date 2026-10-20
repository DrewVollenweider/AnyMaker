"""Trace component constructor initialization prefixes in verified x64 exports.

This narrow analysis follows entry RCX (object), entry RSP, operand-slot
provenance and private stack spills. It stops at the first control-flow branch.
It identifies same-address initializer calls and type-tag stores, not complete
runtime inheritance, vtables, calling conventions or component behavior.
"""
import argparse
from contextlib import closing
import json
from pathlib import Path
import re
import sqlite3

from baseline import sha, write
from trace_code import audit, checked_nodes

VERSION = '1.0.0'
COMPONENT = 'server_scene.vehicle_component'
CTOR = re.compile(r'^\(\) ctor \((' + re.escape(COMPONENT) + r'(?:\.[a-zA-Z0-9_]+)?)\)$')


def trace_prefix(instructions, references):
    """Ghidra x86-64 register offsets: RCX=8, RSP=32; no cross-branch joins."""
    registers = {(8, 8): ('this', 0), (32, 8): ('stack', 0)}
    memory, calls, tags = {}, [], []
    slots = {ref['address']: ref for ref in references}
    stopped = 'end_of_export'
    expected_next = None
    for instruction in instructions:
        if expected_next is not None and int(instruction['address']) != expected_next:
            return dict(initializers=calls, type_stores=tags, stopped_at='instruction_gap')
        expected_next = int(instruction['fallthrough']) if instruction.get('fallthrough') is not None else None
        temporary = {}
        entry_sp = registers.get((32, 8))

        def get(node):
            if node.get('constant'):
                return ('constant', int(node['offset']))
            if node['space'] == 'ram' and node['size'] == 8 and int(node['offset']) in slots:
                return ('slot', int(node['offset']))
            key = (int(node['offset']), node['size'])
            return (registers if node.get('register') else temporary).get(key)

        def assign(node, value):
            if node is None:
                return
            env = registers if node.get('register') else temporary
            start, size = int(node['offset']), node['size']
            for key in list(env):
                if start < key[0] + key[1] and key[0] < start + size:
                    del env[key]
            if value is not None and size == 8:
                env[(start, size)] = value

        for op in instruction['pcode']:
            checked_nodes(op)
            name, nodes, value = op['opcode'], op['inputs'], None
            args = [get(node) for node in nodes]
            if name in ('BRANCH', 'CBRANCH', 'BRANCHIND', 'RETURN'):
                return dict(initializers=calls, type_stores=tags, stopped_at=name)
            if name == 'COPY' or name == 'CAST':
                if nodes and op.get('output') and nodes[0]['size'] == op['output']['size']:
                    value = args[0]
            elif name in ('INT_ADD', 'INT_SUB') and len(args) == 2:
                a, b = args
                if name == 'INT_ADD' and a and a[0] == 'constant':
                    a, b = b, a
                if a and b and a[0] in ('this', 'stack', 'constant') and b[0] == 'constant':
                    value = (a[0], a[1] + (b[1] if name == 'INT_ADD' else -b[1]))
            elif name == 'LOAD' and len(args) == 2:
                address = args[1]
                if address and address[0] == 'slot':
                    value = address
                elif address and address[0] == 'stack':
                    value = memory.get((address[1], op['output']['size']))
            elif name == 'STORE' and len(args) == 3:
                address, stored = args[1:]
                width = nodes[2]['size']
                if address and address[0] == 'stack':
                    for key in list(memory):
                        if address[1] < key[0] + key[1] and key[0] < address[1] + width:
                            del memory[key]
                    if stored is not None:
                        memory[(address[1], width)] = stored
                elif address is None:
                    memory.clear()
                if address == ('this', 0) and width == 8 and stored and stored[0] == 'slot':
                    ref = slots[stored[1]]
                    if ref['kind'] == 5:
                        tags.append(dict(instruction=int(instruction['address']), bytes=instruction['bytes'],
                                         slot_address=stored[1], symbol=ref['symbol']))
            elif name in ('CALL', 'CALLIND'):
                target = args[0] if args else None
                if target and target[0] == 'slot':
                    ref = slots[target[1]]
                    match = CTOR.fullmatch(ref.get('symbol') or '')
                    if ref['kind'] == 4 and match and registers.get((8, 8)) == ('this', 0):
                        calls.append(dict(instruction=int(instruction['address']), bytes=instruction['bytes'],
                                          slot_address=target[1], kind=4, symbol=ref['symbol'],
                                          initialized_type=match[1], object_offset=0))
                # A returning x64 CALL's stack push is undone by the callee's
                # return. Preserve only private spills outside the shadow area.
                # If a stack pointer is passed, an unknown callee may mutate it.
                pointer_args = [registers.get((offset, 8)) for offset in (8, 16, 128, 136)]
                if any(arg and arg[0] == 'stack' for arg in pointer_args):
                    memory.clear()
                if entry_sp and entry_sp[0] == 'stack':
                    for key in list(memory):
                        if key[0] < entry_sp[1] + 32 and entry_sp[1] < key[0] + key[1]:
                            del memory[key]
                registers.clear()
                if entry_sp:
                    registers[(32, 8)] = entry_sp
                temporary.clear()
            assign(op.get('output'), value)
    return dict(initializers=calls, type_stores=tags, stopped_at=stopped)


def build(source, index, folder, output):
    if output.exists():
        raise FileExistsError(output)
    output.mkdir(parents=True)
    audit(source, index, folder, output / 'instruction-audit.json')
    records = json.loads((folder / 'records.json').read_text(encoding='utf-8'))['records']
    with closing(sqlite3.connect(index.resolve().as_uri() + '?mode=ro', uri=True)) as db:
        known = {sig: offset for sig, offset in db.execute(
            'SELECT signature,min(code_offset) FROM functions GROUP BY signature HAVING count(*)=1')}
    results = []
    for record in records:
        match = CTOR.fullmatch(record['signature'])
        if not match:
            continue
        facts = json.loads((folder / 'ghidra' / (record['export_name'] + '.facts.json')).read_text())
        refs = [dict(address=record['code_offset'] + ref['slot_offset'], **ref)
                for ref in record['references']]
        result = trace_prefix(facts['instructions'], refs)
        for call in result['initializers']:
            call['target_record_candidate'] = known.get(call['symbol'])
        results.append(dict(component_type=match[1], function={key:record[key] for key in
            ('signature','signature_offset','code_offset','code_size','code_sha256')}, **result))
    report = dict(schema=1, tool_version=VERSION, tool_sha256=sha(Path(__file__)),
                  source_sha256=sha(source), constructors=results,
                  limits=['Straight-line constructor-prefix analysis only, using the x64 Windows ABI model.',
                          'Same-address initialization calls and type-tag writes are not a recovered vtable or full runtime inheritance proof.',
                          'Unresolved or absent observations stay explicit; no game execution.'])
    write(output / 'constructors.json', report)
    print(json.dumps(dict(constructors=len(results), same_address_initializers=sum(len(r['initializers']) for r in results),
                          matching_type_stores=sum(any(t['symbol']==r['component_type'] for t in r['type_stores']) for r in results))))
    return report


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ('source','index','folder','output'):
        parser.add_argument(name,type=Path)
    args=parser.parse_args()
    build(args.source,args.index,args.folder,args.output)
