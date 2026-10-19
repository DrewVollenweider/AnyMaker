# Plate rendering and edge-selection review

Reviewed 2026-09-28 from source, native samples, read-only GCL machine code, and selected decompilation. No game run or matched-camera screenshot acceptance.

## Review findings

| Priority | Finding | Current treatment |
| --- | --- | --- |
| P1 | Full camera direction selected node-cube corners, expanding frontal outlines and translating oblique plates; identical node loops produced view-dependent geometry. | Inner faces use uniform normal-derived surface offset; camera only selects front/back. |
| P1 | Convexity/coplanarity/size/endpoint-continuity checks on unfinished drafts blocked valid boundary selection. | User-requested arbitrary beam order, collinear segments, mixed widths, temporarily disconnected edges. Validate coplanarity, one subgrid, valid boundary only after one closed loop; no four-beam cap. |
| P1 | Beam-only raycasts selected through foreground plates/components. | Hover/click share nearest solid hit before candidate checks; complete game raycast filters remain unrecovered. |
| P1 | Single-layer polygons lack native thickness, outer strips, glass inner frames. | **Unfinished**. Only inner outline/surface placement corrected; not complete native plate geometry. |
| P2 | No self-intersection check; coplanarity tolerance varied with cross-product length; fans filled some concave gaps. | Unit-normal distance, reject closed self-crossing/backtracking boundaries; ear clipping for new/existing/imported simple concave plates. |
| P2 | Cyclic starting-index error missed duplicate boundaries when starting from another beam. | Deduplicate cyclic shifts and reversed winding. |
| P2 | Structural surfaces mixed Plate/Panels terminology across import/painting. | Structural objects use Plate/plates; mathematical plane and settings panel remain distinct. |

## Verified static code

[Evidence](evidence/plates.json) records 11 function signatures, code/allocation ranges, hashes, and relocation lists. Input `bin/game.gcl`: 81,870,449 bytes, SHA-256 `d9725681f1b0bff321c58fcadc0d2e12104919a541eef074cf12945b283edb75`. This differs from old `native-grid-transform.json`'s `32c138…`; records and following owner names were reparsed, never old offsets reused.

Selection concerns **beam-chain node topology and candidate rules**, not proof of arbitrary independent-node selection:

- `state_add_plate.tick` starts from a hit beam and stores both endpoint IDs.
- `state_add_plate_select_edges.get_is_edge_visible` checks endpoint connection to chain ends and calls `_get_is_planar`, `_get_is_convex`.
- `state_add_plate_select_edges.tick` inserts at either end; closing calls `client_scene.vehicle.can_add_plate`, then sends nodes, orientation flag, plate type.
- `_get_is_convex` passes positions to `vehicle_util.test_is_convex`. This is game static evidence. The editor intentionally removes such preliminary filters per user request rather than imposing the game's candidate rules.

Rendering: `add_static_geometry` calls `get_plate_node_surface_offset`, uses `G_VEHICLE_PLATE_THICKNESS` for backside offset, dispatches solid/window/opening/hatch, then calls `add_geometry_outer`. `add_geometry_inner_solid` adds one shared node-surface offset to each node and submits front/back triangles. Offset depends on nonzero normal axes: cube face center for one, outer-edge midpoint for two, outer corner for three; no camera tangential component.

Complete `add_geometry_outer_1_axis/2_axis` strips/frames/window holes/thickness were not implemented. A game fan for convex polygons does not prove safety for arbitrary concavity. Diagnostic materials/glass alpha/lighting differ from the game.

## Implementation and data boundaries

- [plate-selection.js](../src/editor/plate-selection.js) collects a beam set using shared hover/click logic. Reclick cancels one beam; Esc clears. Disconnected, collinear, mixed-width, noncoplanar, cross-grid drafts remain editable without premature polygon validation. Only a single closed loop is ordered/validated for coplanarity and same-subgrid beams/explicitly owned nodes, then creates a plate/window. Branches/multiple disconnected loops do not commit. Self-crossing/backtracking/degenerate loops report errors and retain draft/project. Intermediate collinear nodes stay in project references; triangulation may omit redundant points. Drafts are not saved; closure makes one undoable operation. Hiding node helpers preserves drafts.
- [plate-polygon.js](../src/editor/plate-polygon.js) shares planar projection, self-intersection checks, triangulation without Three.js in domain code.
- Temporarily nonplanar/self-crossing node drags hide only invalid previews; valid outlines restore them. Collinearity-driven triangle-count changes refresh normals/front/back material groups. Commit still runs domain validation.
- `construction-view.js` renders inner faces from node loops plus uniform support offset. Axial outlines no longer expand by half a cell. More exposed outer beams reflect the still-missing independent outer strips.
- Project schema remains v1. Existing `surfaceDirection` is preserved but only chooses normal sign; new plates save an oriented unit normal. Old fields need not be deleted, though corrected rendering changes outlines.
- Optional `normalOffset` remains in world units. Here its absolute value supplies support offset for each nonzero normal axis. Typical new value 0.04, three-cell beams 0.12; mixed widths use maximum selected width, independent of click order. Zero stays on node plane. This is not native plate thickness.
- New plates follow selected-chain ownership rather than incorrectly using active grid. Here grid is editor physical grouping, not an independent body for each native mounting grid.
- Native export retains existing X reflection/node-winding mappings for front/back. Rendering fixes do not establish game-save loading acceptance.

## Review procedure

From repository root:

~~~powershell
node scripts/check-plate-evidence.mjs <game.gcl>
npm test
npm run test:browser:editor
npm run build
~~~

The read-only evidence script checks version, headers, owners, hashes, relocations. [Targeted tests](../tests/plates.test.js) are explicitly loaded by the unit entry point. Browser coverage: arbitrary-order beams, eight collinear segments, mixed widths, occlusion, plates/windows, cancel, ownership, camera rotation, undo/redo. Paint/delete overlap tests use actual snapped nodes rather than old artificially expanded pixel positions.

Logs/screenshots remain ignored in `tmp/plate-review/`. To preserve existing uncommitted `docs/`, this review built with `--outDir tmp/plate-review/production-dist`. Browser settings remained Chromium, one worker, 1500×960, SwiftShader, `/anymaker-builder/`, with outputs redirected there. Complete editor regression used 4173. Final targeted reruns found 4173/4187 occupied, used temporary port 8753 without stopping/reusing services, and did not change committed config.

## Relaxed beam-selection validation (2026-09-28)

- `npm test`: 224/224 passed, including nine Plate tests for eight collinear segments, unordered/cancelled selection, mixed widths, concavity, atomic closed-loop coplanarity/ownership failure, multiple loops not committing. Log `tmp/plate-selection-unit.log`.
- Editor browser suite: 92/92 passed. New real-mouse eight-beam plate/window loops check no draft history commits, single-edge cancellation, rendering, undo/redo, save/reload. Log `tmp/plate-selection-editor.log`.
- `npm run build` passed to normal `docs/`; log `tmp/plate-selection-build.log`.
- No game run; arbitrary concavity/mixed-width game loading and native thickness/outer edges remain unaccepted.

## Earlier rendering-review validation

- Evidence script matched 11 functions' version/owner/hash/relocations: `tmp/plate-review/evidence-final.log`. This checks inputs/records, not gameplay.
- Final `npm test`: 218/218, seven plate cases, `tmp/plate-review/unit-final.log`. Other functions' tests also use this entry point and are not plate changes.
- Complete editor browser suite then passed 74/74, `tmp/plate-review/browser-editor.log`, before the final drag-preview fix/additional cases; not a rerun of all final-workspace cases.
- Final targeted browser tests: 5/5 covering ordered chains, occlusion/cancel, invalid/collinear drags and front/back groups, glass paint, overlapping plate/beam deletion. Log `tmp/plate-review/browser-final-isolated-port.log`, including final Pages-subpath build.
- Separate build passed to `tmp/plate-review/production-dist`: `tmp/plate-review/build-final.log`; changed-file `git diff --check` passed.
- Early failures/port-conflict logs remain. Final drag test was corrected to trigger actual TransformControls dragging and start at an outline point eliminating collinear vertices, then passed without deleting normal/material-group assertions.
- Settings/recovery suites, asset checks, and `check:full` were not run; no published assets/settings persistence changed.

Still unverified: actual game selection interaction, all `can_add_plate` blockers, full outer/thickness/window geometry, all native edge sizes/dynamic poses, game loading, matched-camera pixels. Passing tests do not establish visual parity.
