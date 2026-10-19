# Hydraulic circuits and cylinder connections

## Sources and verified findings

Sources: paired `vehicle.data / vehicle.meta` from Workshop creation `3809467608` and matching `bin/game.gcl`. Inputs were read-only; saves were not overwritten and the game was not launched. Eleven selected function records, definition hashes, constant addresses, and sample fingerprints are in [hydraulic evidence](evidence/hydraulic-connections.json). Recorded GCL: 81,870,449 bytes, SHA-256 `d9725681f1b0bff321c58fcadc0d2e12104919a541eef074cf12945b283edb75`. Do not reuse offsets for other versions.

Sample vehicle 2168 has 105 components, 58 nodes, 77 beams, 11 plates; links: electric 3, mechanical 16, liquid 22, gas 10, belt 5, data 0. It has no external cylinder base/rod ends and no `hydraulic_links` array.

Components 26/27 are `wheel_c`, class `wheel_hydraulic`. Original logic nodes 0/1 are liquid steering interfaces; node 2 is gas braking. Liquid valves 36–39 form four steering circuits to the wheels through existing `liquid_links`. Each wheel's `hydraulic_cylinder` stores two-chamber fluid state. Use the UI's liquid-line option for pump/valve/tank/hydraulic supply ports.

## External-cylinder game rules

External cylinders are constraint connections across physical subgrids, restored through endpoint component references. Do not invent a `hydraulic_links` array or force both anchors to coincide as for hinges.

| Size | Base definition | Rod-end definition | Logic node size |
| --- | --- | --- | --- |
| 1×1 | hydraulic_cylinder_connector_base | hydraulic_cylinder_connector | 0 |
| 2×2 | hydraulic_cylinder_connector_base_2_2 | hydraulic_cylinder_connector_2_2 | 1 |
| 3×3 | hydraulic_cylinder_connector_base_3_3 | hydraulic_cylinder_connector_3_3 | 2 |

- Base original nodes 0/1 are `liquid`, node 2 `hydraulic_base`; rod-end node 0 is `hydraulic`. Preserve original indexes after UI filtering.
- Connect equal-size base/rod ends only, with no duplicate occupancy. Save base -> rod regardless of click order.
- For odd size, `logic_node.get_size_offset` adds half a cell on both axes perpendicular to the normal, after `center_stretch` extension. Thus a 2×2 base `[0,1,0]` anchor becomes `[.5,1,.5]`; rod anchor becomes `[.5,0,.5]`.
- Game dragging computes `length_max = round(distance / 0.08)` from world anchors; a new link has `extension_factor = 1`. Native omitted defaults are 8 and 0 respectively. Editor limits are 1–10000 cells and extension 0–1; these are input limits, not verified game maxima.
- Both endpoints save `connected_vehicle`, `connected_component`, `connected_node_index`. Base also saves `length_max`, `extension_factor`, `hydraulic_cylinder` state.

Evidence follows `vehicle_editor_hydraulic.state_edit_hydraulic_nodes_drag.tick`, `can_add_hydraulic_link`, both endpoints' `parse_save_data / post_load`, and base `connect_multibody`. The summary excludes full decompilation and binaries.

## Editor implementation

Choose Hydraulic cylinder in the connection tool, then click matching base/rod ends. UI shows port roles, preview, and selectable diagnostic cylinder geometry. Size mismatch, occupied ports, nonnative scale, and invalid distance produce localized errors. Supply circuits still use the separate Liquid line option.

`src/editor/hydraulic-connections.js` validates endpoints, normalizes direction, calculates initial length, and restores references. `scripts/extract-hydraulic-profiles.mjs` generates minimal profiles for six endpoints from published definitions, keeping runtime independent of the installation. Picking synchronizes world matrices immediately after port refresh, preventing missed rapid clicks before the next render frame.

Project `topology.links` stores `kind: "hydraulic"`, base/rod references, `lengthMax`, `extensionFactor`, empty `points`. Selection, delete, undo/redo, and independent visibility are reused without welding subgrids. Viewport cylinders follow endpoints without pressure/constraint simulation.

Native export reuses rigid-structure partitioning for separate endpoint vehicles and reciprocal component/node references. It preserves fluid state and rebuilds relationship fields. Deletion omits stale references/length. Import reads reciprocal references/defaults, preserves endpoint distance, and rejects missing/contradictory references or invalid lengths. Export rejects reflected cylinders, endpoints on one rigid structure, and other ordinary cross-body networks under existing adapter limits.

## Checks and unaccepted behavior

Run from repository root:

```powershell
node scripts/extract-hydraulic-profiles.mjs
node scripts/check-hydraulic-evidence.mjs <game.gcl> [vehicle.data]
npm run check
npm run test:browser:editor
```

Evidence checking read-only verifies GCL fingerprint, bodies/signatures/constants, and published definitions. Optional sample input requires adjacent `vehicle.meta`. It checks 105 components, structure counts, every network count, 22 liquid paths/port indexes, four steering circuits, and fluid-state export/reimport, with unchanged input hashes. Because it has no external cylinders, three minimal assemblies in `tests/hydraulic-fixtures.js` cover those separately.

`tests/hydraulic.test.js` is explicitly included by the unit entry point, covering three sizes, half-cell offsets, original indexes, reciprocal relations, omitted length defaults, invalid references, occupancy, state preservation, and independent subgrids. Browser workflows cover real clicks, localization, duplicate occupancy, visibility, undo/redo, paired downloads, distance-preserving native reimport, and deletion.

Actual game loading, dynamics, pressure/flow simulation, arbitrary simulation poses, and cylinder Mesh/material comparison remain unaccepted. Intermediate XML still omits connections and is not lossless hydraulic-project exchange.
