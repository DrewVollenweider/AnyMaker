# Automatic mechanical mates and native multibody connections

## Problem and verified findings

In `981.1.data`, hinge pin (native component 4) and hinge knuckle (5) have matching constraint anchors/orientations, but neither has `connected_vehicle / connected_component`. Both, the chassis, and door structure are in one vehicle. The old exporter also flattened everything into one vehicle without references.

Contrary to the earlier format description, loading does not automatically recover every hinge merely from Mesh positions. Static analysis of matching-version GCL confirms `hinge_pin.post_load` reads saved vehicle/component IDs, locates the other endpoint, and calls multibody connection code. That function uses both vehicles' physics objects to create a constraint and reciprocal references. Editor diagnostic records or `mechanical_links` alone are insufficient.

Source fingerprints, signatures/offsets/sizes/hashes for 37 functions, and sample summaries: [mechanical mate evidence](evidence/mechanical-mates.json). Conclusions are tied to its GCL SHA-256; offsets cannot be reused across versions. Original game files, saves, and full decompilation are excluded from Git.

## Implementation

| Mate | Alignment rule | Native fields |
| --- | --- | --- |
| Hinge pin / knuckle | Coincident constraint anchors and matching `constraint_orientations` | Reciprocal `connected_vehicle / connected_component` |
| Latch pin or handle / knuckle | Defined constraint anchors/orientations | Same |
| Mounting pin / knuckle | Anchors and discrete orientations on both endpoints | Reciprocal references; each endpoint's `con_orient_index` |
| Rail / slider | Coaxial, slider within current extended length | Rail `connected_components` list and each slider's reverse reference |
| Ballscrew rail / slider | Coaxial, valid length including center extension | Same |
| Tow bar / hitch, truck kingpin / hitch | Coincident anchors; mating-axis angle meets both `dot_min` values | Reciprocal references |

Client discrete mounting computes `Rb = Ra × Ca[i] × Cb[j]`, then makes transformed `constraint_position` values coincide. Native matrices are column-major. The editor also handles X reflection, XYZ Euler radians, and 0.08 units per cell.

Tow hitches cannot reuse ordinary interface orientation defaults: `vehicle_component_definition.parse_json` defaults `tow_hitch_dir` to 3 (+Y) and `tow_hitch_dot_min` to 0. `tow_bar.tick_multibody` compares each endpoint's world mating axis, requiring both dot thresholds; rotation around that axis is unconstrained. The editor handles coincident-anchor building states, not simulation snapping within less than one cell.

- `src/editor/mechanical-connections.js` recalculates on import, move, rotate, copy, delete, undo/redo, and save. Separation clears references; realignment restores them. Hidden objects still participate.
- `src/editor/mechanical-mate-profiles.js` holds only compact profiles for 15 mate classes generated from published definitions. Runtime needs no ROM/installation/conversion service; complete definitions remain lazy-loaded.
- Inspector displays automatic-connection counts in English and optional Chinese localization. Multiple candidates occupying one pin/slider produce explicit native-export errors rather than arbitrary selection. Rails permit multiple sliders at distinct positions.
- `src/editor/mechanical-bodies.js` derives rigid membership from nodes/beams/plates and component mounting surfaces, exporting actual mates into separate vehicles. Structures group with components; `gridId` is not a physics-body identifier, and render-bounds overlap does not weld mate endpoints.
- Native export reallocates/rebuilds relationship IDs and clears stale rail lists/orientation indexes. Nodes/edges/plates/network lines remain with their body; meta writes separate transform/bounds per body.
- Root-vehicle import traverses singular references and rail-slider lists. Generic anchor alignment does not reset longitudinal slider position to zero.

## Validation and limits

Read-only original-sample regression: chassis exports 84 nodes, 153 beams, 54 plates, four components; door exports seven nodes, eight beams, two plates, two components. Pin references vehicle 2/component 5; knuckle references vehicle 1/component 4. Root-only reimport retains six components, 91 nodes, 161 beams, 56 plates, one hinge, and unchanged component positions. Original file hashes remain identical.

Unit tests cover every mate class, orientation indexes, axis mismatch, positional error, towing tolerances, multiple sliders, copy rebuilding, native grouping, invalid/ambiguous references, rigidly welded endpoints, cross-body lines, and independent snapshots. Browser tests cover Inspector edits, both localized counts, undo/redo, paired downloads, and reciprocal references.

No actual game loading/dynamics validation has occurred, so this is not accepted arbitrary-save compatibility. Editor rigid membership is derived from known mounts/structure, not all game attachment rules. Complex slopes, beam/plate intersections, special dynamic parts, and arbitrary simulation poses need samples/runtime comparison. Export explicitly rejects, rather than silently discards: endpoints on the same rigid structure, ambiguous mates, scaled mates, unrepresentable reflected mates, and cross-body network lines. Cross-body network interfaces remain separate work; hinge motion is not simulated.

Rebuild profiles without game reads or Mesh regeneration:

```sh
node scripts/extract-mechanical-mate-profiles.mjs
npm run check
npm run test:browser:editor
```

Read-only game-evidence check:

```sh
node scripts/check-mechanical-mate-evidence.mjs <game.gcl>
```

The check stops on a version-fingerprint mismatch. To review decompilation, use recorded signatures, codeOffset/codeSize, and existing `ExportAnymakerGclFunction.java`; reimport the same-hash GCL into Ghidra rather than applying new offsets to an old project.
