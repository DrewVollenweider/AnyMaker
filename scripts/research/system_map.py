"""Generate measurable topic leads, not claims of system understanding."""
import argparse
from collections import Counter
import json
from pathlib import Path
import re
import sqlite3
from baseline import write

TOPICS = [
 ('building','Building, grids, welding, structures and islands',r'grid|vehicle_edge|vehicle_plate|island|weld', ['Mounting transform defaults and supported directions','Attachment versus network connection','Island splitting and update order']),
 ('components','Components, interfaces, properties and accessories',r'component_definition|vehicle_component|logic_node|interface|accessor', ['Class-to-definition binding','Omitted defaults and compatibility by variant','Fitted accessories and saved endpoint ordinals']),
 ('physics','Physics, collisions, damage, destruction and repair',r'physics|collision|constraint|damage|repair|destroy', ['Collision versus buoyancy geometry','Constraint units and break thresholds','Damage propagation and repair state']),
 ('powertrain','Combustion, torque, gears, clutches, wheels, belts and tracks',r'engine|torque|gearbox|differential|clutch|wheel|belt|track', ['Complete torque sign and ratio path','Combustion and fluid dependency thresholds','Unchecked size and steering variants']),
 ('electric','Electrical generation, storage, networks and loads',r'electric|battery|alternator|generator|relay', ['Voltage/current/power conventions','Network solve order and overload behavior','Storage limits and disconnected defaults']),
 ('fluids','Liquids, gases, flow, pressure, temperature and cooling',r'liquid|gas_|pressure|temperature|pump|coolant|radiator|valve', ['Native volume and pressure conversions','Conservation and timestep integration','Pump direction and port-to-chamber mapping']),
 ('doors','Doors, openings, hatches, latches, sealing, rails and actuators',r'hatch|opening|hinge|latch|rail|actuator|ballscrew', ['Geometric seal conditions and collision separation','Latch state versus alignment','Tolerance and moving-body seal transitions']),
 ('controls','Mechanical controls, sensors, data, displays and microcontrollers',r'mechanical|sensor|data_node|display|microcontroller|junction', ['Signal types, defaults and hysteresis','Network discovery and alias scope','Controller scheduling and power-loss behavior']),
 ('scripts','Script grammar, types, bindings, execution and persistence',r'script|lexer|token|parser|on_tick|global_private|binding', ['Grammar and operator round-trip','Type conversions and API bindings','Instruction budget, scheduling and persistent state']),
 ('survival','Inventory, progression, loot, survival, weather, combat and AI',r'inventory|loot|craft|survival|weather|zombie|creature|weapon|projectile|progress', ['Discover whether crafting/progression exists','Loot and survival update paths','AI authority, sensing and combat damage']),
 ('world','World generation, buildings, bunkers and environment',r'world|tile_|dungeon|bunker|building|terrain|environment', ['Seed and tile assembly rules','Building asset serialization','Environmental interaction and persistence']),
 ('saves','Save/load, creations, metadata and version migration',r'save_data|save_|load_|parse_json|serialize|clipboard', ['Creation versus world schema','Omitted defaults and migration policy','Unknown fields and ID remapping']),
 ('multiplayer','Multiplayer authority, synchronization, ownership and persistence',r'replication|network|authority|ownership|peer|multiplayer', ['Client/server ownership and validation','Replication ordering and loss recovery','Join/leave persistence']),
 ('rendering','Rendering, meshes, textures, materials and animation',r'graphics|mesh|texture|material|animation|render|geometry', ['Mesh variants and dynamic assembly','Collision/render mesh relationship','Animation state and material parameters']),
 ('input_audio_ui','Input, audio, UI, localization and journal',r'input|action_digital|audio|sound|language|journal|ui_', ['Digital versus analog paths','Audio event and spatialization bindings','Journal/localization completeness'])
]


def build(database, catalog, output):
    if output.exists():raise FileExistsError(output)
    db=sqlite3.connect(database.resolve().as_uri()+'?mode=ro',uri=True)
    rows=[json.loads(x[0]) for x in db.execute('SELECT record FROM functions')]
    cat=sqlite3.connect(catalog.resolve().as_uri()+'?mode=ro',uri=True)
    defs=cat.execute('SELECT source,pointer,id,class,name,description FROM definitions').fetchall()
    result=[]
    for ident,title,pattern,questions in TOPICS:
        regex=re.compile(pattern,re.I)
        # Templates and generated helpers are retained in counts. A count does
        # not pretend to measure distinct mechanics or user-facing features.
        hits=[r for r in rows if regex.search(r['signature'])]
        dhits=[d for d in defs if regex.search(' '.join(d))]
        ranked=sorted(hits,key=lambda r:(any(t in r['signature'] for t in ('operator_',' ctor ',' dtor ','replication.','vector<')),r['code_offset']))
        result.append({'id':ident,'title':title,'lead_pattern':pattern,
            'function_record_keyword_hits':len(hits),'definition_keyword_hits':len(dhits),
            'implementation_explained':False,'runtime_tests_this_session':0,
            'function_leads':[{k:r[k] for k in ('signature','code_offset','code_size','code_sha256')} for r in ranked[:8]],
            'definition_leads':[{'source':d[0],'pointer':d[1],'id':d[2],'class':d[3]} for d in dhits[:8]],
            'next_questions':questions,
            'required_trace':['Inputs/outputs and units','Defaults/limits/state transitions','Update order and dependencies','Serialization and omitted values','Failure modes','Implementation and callers','Runtime ambiguity and controls']})
    provenance={k:json.loads(v) for k,v in db.execute('SELECT key,value FROM provenance') if k in ('source_sha256','tool_version')}
    output.parent.mkdir(parents=True,exist_ok=True)
    write(output,{'schema':1,'provenance':provenance,'topics':result,
        'limits':'Keyword leads overlap and include templates. A hit is not an explained system; zero hits do not establish absence.'})
    print(f'Mapped {len(result)} topics with versioned leads and explicit open questions')


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('database',type=Path);p.add_argument('catalog',type=Path);p.add_argument('output',type=Path)
    a=p.parse_args();build(a.database,a.catalog,a.output)
