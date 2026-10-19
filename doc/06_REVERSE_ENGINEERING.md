# Local decompilation analysis

Later mechanical research: [automatic mates](10_MECHANICAL_MATES.md), [function/sample fingerprints](evidence/mechanical-mates.json). That evidence records a separate GCL hash, 37 ranges, saved references, and tow-hitch defaults. Never mix offsets across versions. Read-only check: `node scripts/check-mechanical-mate-evidence.mjs <game.gcl>`. No game-loading acceptance.

`game.exe`/installation are local read-only inputs, never committed, copied to `public/`, or required by the website.

`scripts/Invoke-AnymakerGhidraAnalysis.ps1` calls the installed Ghidra workspace, which retains large products. This repository stores selected reviewable findings/small evidence summaries only.

```powershell
./scripts/Invoke-AnymakerGhidraAnalysis.ps1 `
  -GameExe 'I:\SteamLibrary\steamapps\common\Anymaker\game.exe' `
  -AnalysisWorkspace 'D:\00Data00\Stormworks\analysis' `
  -FullAnalysis -LightAnalysis
```

Exports: PE information, imports, function lists, definition strings, string xrefs, call graph, relevance-selected C pseudocode. `-LightAnalysis` disables known memory-intensive constant propagation. Pseudocode alone is not verified game behavior.

Connection/port/subgrid findings need Ghidra run ID, product path, reproducible experiments. Distinguish verified facts, editor implementation, and unverified behavior.

## Existing evidence

Read-only local run `20260923_213555` (2026-09-23), `D:\00Data00\Stormworks\analysis\artifacts\ghidra\20260923_213555\game`: 9,787 functions, 2,123 string xrefs, 358 C files. EXE is x86-64 PE with Jolt physics/hinge/constraint symbols/strings.

Unverified: these products did not directly connect `.data` fields such as `electric_links`/`connected_vehicle` to runtime ports/parent transforms. Following `connected_vehicle` / `connected_component` references and displaying definition `logic_nodes` are auditable editor implementations, not proof of complete game connection/rotation/constraint equivalence.

### Child-vehicle constraints (2026-09-24)

Sample fact: vehicles 551/552/554 each have hinge and tow records. Comparing component origins gives one-cell errors. Transforming `constraint_position: [0, 0, -1]` from `public/data/definitions/hinge_knuckle.json` by column-major rotation makes seven records agree on each child's rigid offset. `tow_hitch` `surface.pos`/`logic_nodes.pos` are not pivots: substituting them contradicts hinge offsets in the same sample.

Read-only GCL export `server_scene.vehicle_component.hinge_knuckle.connect_multibody.c`, run `20260924_202337`, under `D:\00Data00\Stormworks\analysis\artifacts\anymaker-gcl\20260924_202337`, delegates to the base class. `server_scene.vehicle_component.tow_bar.connect_multibody.c`, run `20260924_202458` in the corresponding directory, references both `get_transform`, grid conversions, `physics.scene.create_constraint_point`, without surface/logic port reads. This supports separating ports from multibody pivots, not complete connector/pose semantics from pseudocode alone.

Editor implementation pairs published `*_definition_id_other` fields and coincident `constraint_position` (component origin if omitted), producing separate `topology.mechanicalConnections` for hinge/latch/mounting/rail/ballscrew/tow/truck hitch. These are neither six-network links nor verified physics simulation.

### Door handles and mounting grids (2026-09-25)

Static evidence: read-only `bin/game.gcl`, SHA-256 `32c1389e6bbc49aeae5a7eff93f2f580fed78ec453a69e6a491c014253e4ae09`, cross-checked records, relocation symbols, machine code, constants. Ignored local Ghidra run `tmp/door-grid/DoorGridVerified`; C output `tmp/door-grid/`; committed summary [native-grid-transform.json](evidence/native-grid-transform.json). No game launch/modification.

Old script target `0x126C738 / 0x78` actually belongs to `client_scene.vehicle_grid.get_transform`. Its final relocation references `vehicle_util.grid_origin_dir.get_transform`; that final referenced signature is not the subsequent code owner. Checking the following owner corrected the script and established:

| Function | Offset / size | Static evidence |
| --- | --- | --- |
| `vehicle_util.grid_origin_dir.get_transform` | `0x3C4E8EC / 0x500` | Nonbase orientation/origin/node-surface/half-normal combination |
| `vehicle_grid_util.get_grid_axis_normals` | `0x3BD9834 / 0x348` | Y reference, Z when parallel; normalize X=dir×up, Y=dir, Z=X×Y |
| `vehicle_util.grid_origin_dir.get_orientation` | `0x3C4E16F / 0x130` | Three axes to mat33 constructor |
| `vehicle_plate_util.get_plate_node_surface_offset` | `0x3C198C9 / 0x900` | One axis face center; two outer-corner midpoint; three outer corner; get_transform passes edge_size=0 |
| `vehicle_plate_util._g_plate_node_corners.$ctor` | `0x3BE0721 / 0x280` | Eight corners, components ±0.5 cell |
| `vehicle_util.grid_origin_dir.get_is_base_grid` | `0x3C4DBB3 / 0x160` | Only origin=0 and dir=(0,1,0) |
| `vehicle_util.grid_origin_dir.parse_json` | `0x3C4F332 / 0x230` | Defaults origin=(0,0,0), dir=(0,1,0) |

Nonbase effective origin: `origin + sign(dir) * 0.5 + normalize(dir) * 0.5`, per-axis sign. Earlier code correctly used local Y=dir but projected world X for in-plane orientation and omitted offsets. Door normals `(±6, ±1, 0)` exposed major errors. Dashboard `(0,1,-2)` happened to have correct orientation but also lacked offsets.

`nativeGridFrame` now shares these rules across component position/rotation, anchors, inverse edit displacement, restores omitted dir, rejects zero/invalid direction. Vehicle-level structures/paths do not receive mounting transforms. Evidence JSON records independently computed positions/normals for handles 551:5/6 and 552:3/8, used by unit/browser snapshots; after whole-vehicle centering compare relative to chassis hinge.

Read-only checks with authorized local inputs:

```powershell
node scripts/check-native-grid-evidence.mjs 'I:\SteamLibrary\steamapps\common\Anymaker\bin\game.gcl'
./scripts/Invoke-AnymakerGclAnalysis.ps1 `
  -GameGcl 'I:\SteamLibrary\steamapps\common\Anymaker\bin\game.gcl' `
  -AnalysisWorkspace 'D:\00Data00\Stormworks\analysis' `
  -KnownFunction vehicle_util.grid_origin_dir.get_transform
```

First command checks full GCL fingerprint, seven records' signatures/sizes/owners/relocations/hashes, eight constants, vehicle fingerprint. Static evidence is not runtime acceptance. Matched-camera pixels, moving doors, complete materials, arbitrary native export loading remain unverified.

Actual historical checks: `npm run check` passed 71 unit tests/build and the evidence command passed. Initial browser suite: 14 passed/six failed. Handle assertions ignored whole-car centering; relative-position correction passed targeted tests. History-panel timeout passed isolated rerun. Four others (single-component native import, toolbar occlusion, old catalog DOM, glass painting) also reproduced in a copy retaining user changes but removing this transform fix; not repaired as regressions. Logs `tmp/door-grid/{check,browser,browser-reference,browser-history,browser-baseline}.log`, screenshot `tmp/door-grid/reference-vehicle-door-handles.png`. Do not call the complete suite passed.

### Plate winding and export (2026-09-26)

Read-only same-GCL exports located `client_scene.vehicle_plate.add_static_geometry` (`0x13346BA`) and `vehicle_plate_util.add_static_geometry` (`0x3C05CEC`). Latter branches on `vehicle_plate_util.calculate_plate_normal`: `calculate_plate_dir` anchors at first node, scans pairs for first noncollinear cross product, normalizes it. Thus ordered `plates[].nodes` determines front/back, not an unordered boundary.

Editor X reflection requires reversing export node order. If `surfaceDirection` exists, reflect it into native coordinates, compare with game normal, reverse again if needed so saved front faces the creation-time camera side. Native-plate export tests in `tests/unit.test.js` cover this. Complete materials/window frames/runtime loading still require game screenshots/acceptance.

### Beam geometry (2026-09-23)

GCL contains signatures and x86-64 code, not just assets. `scripts/Invoke-AnymakerGclAnalysis.ps1` and `scripts/ExportAnymakerGclFunction.java` import Raw Binary into Ghidra and disassemble/export registered ranges only. Inputs/large output stay in local analysis workspace.

Run `20260923_234711`, `client_scene.vehicle_edge.debug_render_geometry.c`, under `D:\00Data00\Stormworks\analysis\artifacts\anymaker-gcl\20260923_234711`, with symbol records establishes:

- Static entry `vehicle_edge_util.add_static_geometry(vec3_s32, vec3_s32, s32, s32, vehicle_plates_edges_builder)`.
- Converts endpoints to world grid points, computes nonzero difference-axis count/min/max, calls `add_edge_quad`/`add_edge_triangle`.
- Client debug geometry also branches by axis count; three-axis case creates eight grid corners/six quads, others triangles/quads.

Evidence rejects octagonal/general arbitrary-axis cylindrical beams. Editor BoxGeometry/node overlays remain temporary projections, not native beam recovery. Next: recover relocations and each branch's quad/triangle vertex order, compare with screenshots/runtime.

```powershell
./scripts/Invoke-AnymakerGclAnalysis.ps1 `
  -GameGcl 'I:\SteamLibrary\steamapps\common\Anymaker\bin\game.gcl' `
  -AnalysisWorkspace 'D:\00Data00\Stormworks\analysis' `
  -KnownFunction client_scene.vehicle_edge.debug_render_geometry
```
