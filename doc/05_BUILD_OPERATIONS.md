# Mirror and subgrid operation design

Status: primarily requirements/design. Component operations/basic topology prototypes exist; complete P2–P4 acceptance remains unfinished. Dependencies are in TODO P2–P4. Later sections record implemented extensions, including some superseded rendering approaches.

## Three distinct subdivisions

| Concept | Meaning | Editing behavior |
| --- | --- | --- |
| Mesh part / render submesh | Geometry/material fragment in a model | Preserve boundaries; not a vehicle/grid |
| Dynamic mesh | Moving geometry referenced by meshes_dynamic, e.g. hubs/pistons | Assemble by definition; do not arbitrarily split into components |
| Vehicle Grid / building subgrid | Building coordinate system for components; native origin/dir | Target of planned split/copy/move/merge operations |

Known native nodes/beams/plates live at vehicle level, not within each grid array. Explicitly maintain structural operation sets and let native adapters map them. Do not assume intrinsic grid ownership. Exact joint/cross-grid game semantics still need verification. Later physical-subgrid conventions below distinguish mounting grids from bodies.

## Common command protocol

Commands accept selected entities, source/target frames, pivot, boundary policy; return preview, errors, ID map, change set.

1. Read domain data; compute entities, internal/external links, affected plates.
2. Build read-only previews of additions/removals/disconnections/reconnections/conflicts.
3. Validate numbers, lattice, definitions, constraints, duplicate occupancy, references.
4. Commit once atomically; failure preserves project, cancel removes preview only.
5. One undo restores IDs, membership, coordinates, paint, links.

Three.js displays results but is not the sole source of topology/IDs.

## Mirroring

Choose world/grid-local plane, X/Y/Z normal, offset, one-shot/continuous mode. With unit normal n and offset d:

p′ = p − 2n(n · p − d)

Reflection determinant is −1, not ordinary rotation. Neither a rotation alone nor stored negative scale represents valid component semantics. Treat non-mirror-symmetric geometry, left/right paired definitions, and missing mirrored definitions separately.

- Deduplicate on-plane entities and multiplane combinations with stable maps.
- Copies allocate IDs, remap internal Links, and apply boundary policy externally.
- Keep triangle winding, normals, plate front/back, paint UV/pixel orientation consistent.
- Transform port positions/directions/genders, joint axes/limits, dynamic pivots.
- Continuous mode retains correspondence so delete/move/paint acts as one command.
- Missing handedness mappings/unrepresentable export must identify objects and reject compatible commit.

## Splitting subgrids

Create new gridId for selected components/explicit structures. For source/target world frames Ws/Wt and local transform L, preserve world pose with:

L′ = inverse(Wt) × Ws × L

Do not cut boundary beams/plates by deleting references. Preview dependencies and offer valid complete-structure, copied-boundary-node, or cancel strategies. Reject unsupported partial cuts instead of inventing caps. Whether continuous-structure splitting creates vehicles is separate game behavior to verify.

## Copying subgrids

Copy grid/subtree with relative transforms, structure, paint, properties. Allocate all unique node/plate/component/grid/Link IDs; internal references target copies. Default to no external links, showing reconnectable endpoints. Mutable property objects cannot be shared.

## Moving subgrids

Distinguish:

- Whole transforms change grid frame, preserving local layout.
- Pivot edits compensate local positions, preserving world poses.
- Reparenting/vehicle transfer uses frame conversion and recalculates structure/link/constraint membership.

Reject results unrepresentable by native lattice/rotations. Do not merge moving-joint endpoints or bypass constraints through scaling.

## Merging subgrids

Choose destination, transform sources into it, validate IDs/occupancy/connectivity/constraints. Distinguish:

- **Membership merge**: common grid, unchanged world positions.
- **Structural welding**: merge nodes/edges under verified rules, changing connectivity.
- **Render batching**: draw-call optimization without domain changes.

Set deduplication tolerance from unit/lattice evidence. Report paint/material conflicts, incompatible genders, overlaps, joint conflicts; never silently discard source information.

## Acceptance matrix

| Operation | Cases | Invariants |
| --- | --- | --- |
| Mirror | Offset/local planes, handed parts, multiple planes, on-plane coincidence | Correct normals/ports/paint; unique IDs |
| Split | Rotated source, boundary beams/plates, cross-grid Links | World pose/reference integrity |
| Copy | Dynamic parts, multigrid subtrees, internal/external Links | Independent copies; internal references target copies |
| Move | World/local axes, pivot, reparenting, limited joints | Relative structure/valid constraints |
| Merge | Different frames, ID conflicts, off-grid points, paint conflicts | No lost entities/fields/dangling endpoints |
| Combined | Split -> copy -> move -> merge -> save -> load -> undo/redo | Atomic, reproducible results |

Do not promise fabricated precision before verifying tolerances/lattice/native mapping. Record editor tests separately from game tests.

## UI preferences and local recovery

- `selection-filter-toolbar` has a collapsible Hide by type list below Selectable objects. Check to hide components/nodes/beams/plates/links; Structures groups nodes/beams/plates. Link filtering covers ordinary lines, cylinders, belts/tracks and combines with network visibility settings.
- Type hiding is `hiddenKinds` display preference, not object `hidden`, history, or export omission. Individually hidden objects stay hidden when filters clear. New/imported/undo-restored content uses current filters. Localization and selectability remain independent; Move can pick logical nodes even with helpers hidden.
- Top-left language switch offers English/optional Chinese; first use defaults English. Tooltips/counts/catalog/Inspector update immediately; IDs/project content are not translated.
- Editing tools form a single floating row below topbar/above workspace. Mid-side vertical handles toggle panels; left width is draggable, viewport Tab toggles it.
- XYZ indicator follows camera; ±X/±Y/±Z choose six views, with isometric/focus controls. These are perspective-camera axial views, not implemented orthographic projection.
- Grid color/alpha/solid-dash apply immediately. Snap step, grid/node visibility, panel sizes/toggles, drawers, filters/search, tool, camera/target persist separately in `localStorage`, outside schema.
- Keys isolate site origin/pathname and version settings/project separately. Localhost writes only current browser; ports/browsers/paths do not share records.
- Startup loads definitions, validates/recovers project, then saves committed component/topology snapshots every 60 seconds and attempts additional saves on hiding/leaving. Beam drafts, intermediate TransformControls states, File objects, local bytes are excluded.
- Keep previous valid backup; recover it on corruption. If both fail, retain originals and stop overwrites. Another tab's save also pauses overwrites until explicit project choice. Disabled/full storage reports failure without clearing projects or claiming success.
- Clearing site data deletes recovery. Autosave is not an external backup/game save; periodically download project JSON. Changes since last interval may be lost on crash.

## Implemented state

`src/editor/operations.js` supplies rendering-independent copy/move/mirror-copy/grid-split/merge primitives returning new snapshots/IDs/maps without mutating input. `validateDocument` checks `gridId` and explicit `mirror`. Toolbar single-component copy/X-mirror/split/merge use one `restore + History.commit`. Continuous mirroring supports world X/Y/Z integer-offset planes. Paired component drag/rotation/Inspector edits and corresponding node moves update both sides in one history commit. Pairing uses current plane/position/metadata; switching planes does not automatically rematch old objects.

`src/editor/topology.js` supplies node deduplication, atomic move/merge, node/beam/plate deletion, beam creation/split, coplanarity and initially fan triangulation (later replaced as documented in Plate review). Reject unknown nodes, duplicate/zero-length beams, collinear/nonplanar plates. Full node editing is wired to viewport; batch/constraint interactions were initially incomplete.

Topbar `node`, `edge`, `plate`: Node selects a node, clicking another merges; blank clicks move on its frozen camera plane with snapping/coincidence merge; Delete removes it/direct dependencies. Beam clicks start/end, automatically creating/reusing nodes. Plate/window drafts select beams with blue center-line highlight and commit upon a single closed loop; Esc cancels. Delete picks visible nodes/solid beams/plates. Selection/delete/paint share hover highlighting: thick beam center, actual inset plate boundary, component bounds. Paint priority is plate, beam, component even at support intersections. Shift component selection supports batch copy/mirror/split/delete in one undo. Mixed structural transforms/box selection are implemented below. Topology and components save/undo atomically.

Plate/window drafts are sets: arbitrary order, collinear segments, mixed widths, no four-beam cap or preliminary convexity/continuity filter. Reclick removes one; Esc clears. On a single closed loop, validate coplanarity, ownership, non-self-intersection; order boundary while retaining collinear nodes. See [Plate selection](15_PLATES.md) for distinction from game rules.

### Whole transforms of beams, plates, and mixed selections

`src/editor/selection-transform.js` provides pure-data expansion/whole transforms/manual mirror transactions. Shift mixes components/nodes/beams/plates. Beam/plate selections receive shared move/rotate handles and relative XYZ cell/90° Inspector inputs. Hidden node helpers do not disable whole transforms; explicit single-node editing retains its own workflow.

- Expand selected beam endpoints, plate boundary nodes, and internal links whose components are both selected. Selecting a plate does not automatically select boundary beams; select both to move both.
- Handle/Inspector rotation uses nearest whole-cell point to selection-bounds center; manual rotation uses actual unrounded center. One matrix transforms shared nodes once. Whole-cell displacement/90° steps retain fractional native projection, without per-node rounding.
- Clone nodes shared with unselected structures, remap selected references, preserve untouched structure. Retain membership/colors/glass/offset, rotate `surfaceDirection`. Components may transform with structures; internal paths follow.
- Drag replaces preview only; release commits once. Esc/pointer cancellation/invalid transforms roll back. No-op does not split nodes/add history. Undo/redo/save include full topology.
- Continuous mirror identifies complete matching same-subgrid beams/plates. Coincident isolated nodes do not pull unrelated structures into selection. If crossing-plane structure cannot stay rigid/symmetric, request disabling mirror, never stretch beams/plates to fake symmetry.

`rotate-toolbar` separates Manual rotation and Mirror, visible for rotate tool/continuous mirror. Manual XY/XZ/YZ with 90°/180°/270° (default 90°) rotates around world +Z/+Y/+X and current center, supporting mixed selections. Valid half-cell-center 180° rotations retain center. Reject off-lattice ordinary nodes without changing center/rounding vertices. One history record per application.

Mirror section: continuous toggle, world X/Y/Z plane/offset, Mirror selection. Manual mirror does not require continuous mode: **copy reflected selection and retain originals**. Select copies; undo once. Components keep positive scale/explicit reflection metadata; remapped structural nodes, reversed winding/reflected directions, preserved front/back colors. Reuse on-plane nodes/existing counterparts; repeated clicks do not stack duplicates. Internal endpoints remap, external unselected links are excluded. Component deduplication checks orientation/dimensions/native stretch, not origin-on-plane alone for asymmetric geometry.

`tests/selection-transform.test.js`: shared-node separation, rigidity/direction, X/Y/Z offset mirrors, deduplication, on-plane points, component geometry/internal links, native structural round trips/history. `tests/browser/editor.spec.js` `structural selection` cases cover real picking, drag, Inspector, cancel, undo/redo, mixed mirrors/save. Editor-only validation, no new game acceptance. `surfaceMount` components may translate; whole rotation/mirroring explicitly rejects unrepresentable native grids. Arbitrary structure angles/local mirror planes/all joint/handedness mappings remain unfinished.

### Subgrid structural integrity

Player-facing subgrid means an independently moving physical structure. Native `grids[]` inside one vehicle are mounting frames, grouped into one editor subgrid while IDs retain source grid and mounting transforms/metadata. See [mechanical mates](10_MECHANICAL_MATES.md).

`analyzeSubgridIntegrity` in `src/editor/subgrid-connectivity.js` derives connected sets from mounting surfaces/nodes/beams/plates, using native units, X reflection, rotations, stretch, half-cell support offsets. It checks beam-interior/plate-interior contact, avoiding orphan handles merely distant from corners. Dedicated surfaces also participate, e.g. tow-hitch mechanical handles/engine pulleys. Signal lines/hoses/belts/cylinders do not create rigidity. Explicit mate endpoints and incidental contact across known joint-side subgrids do not weld. Geometry does not replace network/port validation. Legacy calls without definitions may use occupancy/bounds diagnostics; UI supplies full definitions rather than render bounds.

When valid, Subgrid check calls `src/editor/subgrid-partition.js` to update component/node/beam/plate `gridId`, merge connected sets/split disconnected ones. Largest fragment preferentially retains each old ID; others get unique IDs; manual empty grids persist. Positions/rotations/paint/instance IDs/visibility groups/endpoints stay unchanged; cross-group lines remain. One undo transaction; repeat no-op adds no history. Missing refs/incomplete coverage/cut structural refs reject partition and preserve project.

Traversal follows game checks dated 2026-09-28: beams connect through shared endpoints; plates through actual boundary-beam references, never arbitrary beams at every corner. Node membership comes from beams. Beamless corners, cross-island plates, duplicate IDs, degenerate/duplicate beams, invalid plates are errors. Partial missing boundaries, unused orphan nodes, cross-grid structures remain diagnostics; multiple independent subgrids are not inherently errors. Failure applies no partition. Independent node-ID lists prevent confusing equal plate/node IDs during location.

Valid component-free shells are not errors. `tests/subgrids.test.js` splits 159 components in real `test-vehicle/vehicle.data` into four physical groups without orphaning door/tow handles/pulleys. Synthetic tests cover mounting surfaces, independent shells, stable IDs, atomic failure/history. `tests/native-export.test.js` adds beamless-node, real-boundary, cross-island rejection/general-repair coverage. Browser checks ownership/location/localization/save/reload/undo. See [islands](16_NATIVE_ISLANDS.md) for fingerprints/traversal/crash instructions. Contact registration is still approximate, not accepted 1:1 game partition/loading.

### Projected beam construction and node helpers

- Screen position determines camera ray. Without an existing endpoint, intersect camera-facing plane through camera target. First click freezes plane direction/depth at start; later camera rotation does not change that beam's plane. Front/top/oblique views work.
- Global lattice is one 8 cm/0.08 cell. Ordinary component/node/beam-end/plate-node positions, mirror offsets, copy/move displacements are integer world XYZ cells. Project/autosave/XML reject real off-grid data, normalizing floating error only. Scale is dimensionless. Native projection exceptions are documented in the format guide.
- Free mode prioritizes logical nodes even hidden. Surface hits use one-cell node-cube boundary along outward normal, then global integer XYZ quantization. Only empty-space hits use construction/work planes; quantized positions may slightly leave plane. Existing nodes can connect different depths.
- Axis snap button or `A` toggles persistent single-axis mode, default off. From start choose world X/Y/Z nearest the ray, with integer displacement on that axis only. Collinear nodes retain coordinates and priority; off-axis nodes do not override. Exclude nearly camera-aligned axes to avoid depth degeneracy.
- First click creates draft only; movement previews transparent solid beam; second click atomically commits endpoints/beam. `src/editor/edge-ruler.js` shows XYZ whole-cell and cm components, including zeros, following camera/viewport. Preview/ruler/commit share endpoint resolution. SVG/DOM helpers are excluded from picking/history/export/recovery.
- Esc/tool switch/pointer cancel/project restore clears draft/ruler without orphan nodes. Leaving canvas hides preview, returning resumes. Coincident/duplicate/invalid/off-grid beams do not commit.
- `src/editor/construction-view.js` shares grid sizing `20 / 250 = 0.08`. Each end has a world-aligned one-cell cube; connections use its eight real corners. One-axis beams use four facing-face corners; two-axis beams use four real projected silhouette corners; general three-axis beams use all six silhouette corners and six side faces. Width follows cube edge/diagonal and may exceed one cell; no rescaled cross-sections, interpolated face points, forced four-corner reduction. This screenshot-derived rule is not full game implementation: targeted `bin/game.gcl` decompilation located `vehicle_edge_util.add_static_geometry`, `vehicle_plates_edges_builder.add_edge_quad` and `vehicle_plates_edges_builder.add_edge_triangle`, and axis-count branches in debug geometry. Evidence rejects octagonal/generic-cylinder assumptions; exact static-render branches/face order remain open. Connections retain original path points and render cylinder segments with spheres at bends; dimensions differ diagnostically by kind. Default beams/plates are `#cccccc`, plates opaque diagnostic material. Old `{id,a,b}` beams need no migration.
- Historical plate projection selected camera-facing corners on each axis-aligned node cube, then inward half-planes of adjacent beams, triangulating in loop order. `normalOffset` sign retained creation side so camera motion did not flip it. This screenshot-derived method was not exact native topology; later uniform normal-support rendering in [Plate review](15_PLATES.md) supersedes it.
- Alt-click beam chooses closest center-line point among legal interior lattice candidates derived from integer-vector GCD; reject if none.
- Nodes are topology, not catalog components. Visible nodes have projected DOM ID labels and selected labels/spheres. Node spheres/ports use fixed-color overlays above Meshes without depth testing; paint/subgrid view cannot recolor them. Labels are derived, excluded from JSON/count/history. Hide/Show nodes toggles labels/spheres only, outside history. Move still picks logical nodes by selectability with helpers hidden; Node tool needs helpers visible. Beam creation/snap/split/delete is independent of helpers.
- Initial node selection freezes a camera-facing plane through it. Blank click snaps/moves on that plane. Coincidence invokes `moveNodeAndMerge` atomically to rewrite references/remove self-loops/duplicates/validate; failure preserves state.
- Move (`G`) picks logical positions regardless of helper display if Structures/Nodes selectability is enabled. Toggling helpers preserves selection/handle; disabling selectability clears it. Individually hidden/reference-preview nodes are excluded. Selecting one node then G uses same operation. Drag retains IDs/references, updates beams/plates, undoable. Hover/click share screen tolerance and permit node picking through thick beams/body plates. Beam selectability is independent; beam-body clicks still move whole beams. Beam construction retains solid occlusion checks. Node (`N`) click movement/merge remains.
- Move/Node tools keep nodes visible at long camera distances, updating immediately on tool switch while honoring explicit hiding/reference preview. Other tools/grid helpers retain distance thresholds. Browser `node movement`, `node overlay`, `node editing` cover entry, beam/plate occlusion, distance, explicit hiding, shared refs/merge/history. `native node overlays` uses synthetic saves by default; `ANYMAKER_NODE_SAMPLE` may point to paired basename for read-only real-sample tests, never overwriting originals.
- Restore/topology commands validate complete candidates and prepare geometry before replacing scene. Legacy no-topology loads clear current structure. Focus supports structure-only projects.

Mirror previews clone each geometry in `src/assets/geometry-ops.js`, reflecting positions/normals/winding while keeping positive object scale. Native definition adapters remain responsible for port/joint/handedness mappings.

This remains a prototype. Paired components/nodes/complete beams/plates support corresponding mirrored transforms and copied internal references, but all port/dynamic-joint/left-right semantics are incomplete. Metadata and reflected Three.js previews do not establish that arbitrary mirrored results export valid game semantics. No game-loading acceptance.
