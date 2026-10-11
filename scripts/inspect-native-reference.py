#!/usr/bin/env python3
"""Read-only native snapshot inventory; not a physics or connectivity validator."""
import argparse
import hashlib
import json
from pathlib import Path


def inspect(path):
    raw = Path(path).read_bytes()
    data = json.loads(raw)
    definitions = data['definitions']['components']
    vehicles = data['vehicles']['vehicles']
    result = {'source': Path(path).name, 'sha256': hashlib.sha256(raw).hexdigest(),
              'validation_scope': 'saved-snapshot inventory only', 'vehicles': []}
    for vehicle in vehicles:
        components = [c for g in vehicle['grids'] for c in g['components']]
        controllers = []
        state = []
        for component in components:
            definition = definitions[component['def']]
            if definition == 'microcontroller':
                controllers.append({'id': component['id'], 'script': component.get('script', '')})
            keys = [k for k in component if k.startswith('content') or k == 'acc']
            if keys:
                state.append({'id': component['id'], 'definition': definition,
                              'fields': {k: component[k] for k in keys}})
        result['vehicles'].append({'id': vehicle['id'], 'grids': len(vehicle['grids']),
            'components': len(components), 'nodes': len(vehicle.get('nodes', [])),
            'edges': len(vehicle.get('edges', [])), 'plates': len(vehicle.get('plates', [])),
            'links': {k: len(vehicle.get(k, [])) for k in
                      ('electric_links', 'mechanical_links', 'liquid_links', 'gas_links', 'belt_links', 'data_links')},
            'controllers': controllers, 'saved_state': state})
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('file')
    args = parser.parse_args()
    print(json.dumps(inspect(args.file), ensure_ascii=False, indent=2))
