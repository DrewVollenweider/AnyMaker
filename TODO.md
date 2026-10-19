# Anymaker Web Builder phased TODO

Updated 2026-09-28. Complete requirements/design before dependent implementation. Checkmarks mean only the stated scope, never final game compatibility/1:1 visuals. This is a historical roadmap: later documents supersede older implementation descriptions where explicitly evidenced; unchecked items are not silently promoted by translation.

## Scope and priorities

- Drive implementation/configuration: [Drive archives](doc/17_GOOGLE_DRIVE_ARCHIVES.md). Real OAuth/account login/upload/download acceptance remains open; mocks are not service acceptance.
- Goal: Three.js desktop Web builder, real game Meshes, ultimately verified vehicle exports, static GitHub Pages hosting.
- Mouse/keyboard desktop only this phase; touch/phone/tablet/mobile layouts/tests deferred.
- Final exports are paired native `.data/.meta`, not XML. XML is development interchange; experimental write-back is not formal export. Do not implement/claim final compatibility without complete mapping/reference/game-loading evidence.
- Current work is resource research/editor prototype. Complete materials/dynamic assembly/topology/subgrid editing/native export remain unfinished.
- Production must be independently static: no installation/game files/game.exe dependency; ship all supported definitions/Meshes/materials/conversion manifests.
- Lossless or validated lossy compression may save space, with auditable topology/coordinates/normals/UVs/material slots/bounds. Lazy loading must not sacrifice completeness.
- All 794 component references are published: 793 decoded v5 static layouts, one blurred native variant retained as complete raw bytes/opaque pending decoder/render support.
- Mirror/split/copy/move/merge are core requirements, not just Three.js Groups/negative scale.
- Entry: [documentation](doc/README.md).

## P0 · Requirements and documentation baseline

- [x] Desktop-first; remove touch/mobile scope.
- [x] Current/target module boundaries: [architecture](doc/01_SYSTEM_ARCHITECTURE.md).
- [x] Definitions/topology/resources/unknowns: [Anymaker architecture](doc/02_ANYMAKER_ARCHITECTURE.md).
- [x] Separate JSON/XML/native: [formats](doc/03_XML_AND_NATIVE_FORMAT.md).
- [x] Per-component/multi-Mesh/lazy conventions: [split plan](doc/04_COMPONENT_MESH_SPLIT.md).
- [x] Mirror/subgrid semantics, boundaries, undo, acceptance: [operations](doc/05_BUILD_OPERATIONS.md).
- [x] Move old docs/reports from docs/ to doc/, update output paths/links.
- [x] Extend .gitignore for Node/Vite/Playwright, local resources/research outputs while retaining lockfiles/fixtures/selected evidence.
- [ ] Manual game baseline: version string, export entry, same-vehicle reference screenshots. At this roadmap date only EXE hash/static ROM evidence existed.

Acceptance: every implementation traces to fields/design/checks; no guessed completion.

## P1 · Prototype and resource research

- [x] Drive belts: pulley/three engine wheels, mixed radii/reverse idlers, continuous 56 mm × 12 mm surface, real texture, tools/whole-loop refresh, real six-wheel sample. [Belts](doc/14_BELTS.md). Dynamic speed/phase, matched-camera visuals/game loading unaccepted.
- [x] Automatic hinge/latch/mounting/rail/ballscrew/tow recalculation on commits; export multivehicle membership/references. Read-only 981.1 export/reimport: [mates](doc/10_MECHANICAL_MATES.md).
- [ ] Actual game loading/dynamics, complex rigid attachment/cross-body network acceptance.
- [x] Vite/Three.js, static build; Pages workflow was recorded as configured but not published at this historical stage. Inspect current workflow existence before use.
- [x] 598 real definitions with optional Chinese-name search, original fields/hashes; compact square cards, 22 local SVG category icons/localized filters.
- [ ] Local `.mesh` is development/audit only; paired `.data/.meta` import also must not become production prerequisite.
- [x] Mesh v5 16/28/36-byte multipart decoding retaining vertices/normals/UVs/packed bytes/indexes.
- [x] ROM audit: 3230/3333 Meshes parse; 793/794 component references supported, none missing.
- [x] Explicit unsupported/truncated/out-of-bounds/trailing-data errors.
- [ ] Neutral real-static-Mesh preview and explicit missing-model diagnostic markers (development).
- [x] Select/place/delete/move/rotate/scale, Inspector, focus/grid.
- [x] Inclined plate snapping through native normal/canonical origin, local cells, preview/click/J/K/L 90° consistency, fractional world coordinates, whole-cell moves/history/native frames. Based on five gauges/GCL, no unsupported arbitrary angles. Inclined mirroring/all collisions/game loading open: [placement](doc/12_INCLINED_PLACEMENT.md).
- [x] Project JSON validation/history/XML download; JSON internal recovery, top Save/Open paired-native workflow.
- [x] Paired starter_vehicle JSON validation; require one same-name data/meta, import components while domain retains topology not yet fully displayed at this initial stage.
- [x] Read-only native-domain mapping with raw/unknown retention and diagnostic experimental JSON write-back, no game round-trip claim.
- [x] Historical 37 unit/20 browser tests passed: editing/localization/XYZ/grid/node preferences, component/topology recovery, corruption/quota/multitab guards, 8 cm lattice in persistence, planar oblique beam orientation, rulers/axis snapping, closed plates/colors, pairing, real-reference fingerprints/full structure/black-background helper-free screenshot. Not visual parity. Routine `npm run check`, affected browser/assets, pre-release `npm run check:full`. Environment bulk-delete protection required temporary Vite `emptyOutDir: false`, restored afterward; clean-output rebuild was not verified.
- [ ] Add real-Mesh render/handle-camera interaction regressions; existing tests do not establish game materials/visuals.

## P2 · File separation, domain model, commands

Depends on P0; precedes mirror/subgrid business logic.

- [x] Lightweight component-index.json + definitions/<component-id>.json; no full data/vertices in index.
- [x] Stable `index.json` with schema/resource version/manifest; legacy migration input retained.
- [x] Separate bindings/<component-id>.json; one shared resource per original Mesh.
- [x] Publish static/dynamic conversions in public/assets/meshes with hash/size/parts/compression/coordinates/bounds; `npm run check:assets` verifies.
- [ ] Complete materials/textures in public/assets/materials, no online local-txtr prerequisite.
- [x] Index/UI first; lazy details/bindings/gzip Meshes by component/visibility; published manifest, development local fallback.
- [ ] Draco/Meshopt/KTX2/equivalent compression with hashes/vertex/image error/bounds/browser checks; reject unproven loss/error tolerance.
- [ ] Special assembly modules per component, category indexes only; no giant switch/factory/vertex file.
- [x] Separate reading/parsing/Three.js geometry/disposal.
- [x] Separate dynamic assembly/published loader/disposal; materials open.
- [ ] Split main.js composition/viewport/selection/tools/Inspector/I/O/native diagnostics.
- [x] Three.js-independent Project/Vehicle/Grid/Component/Node/Edge/Plate/Link, separate native fields/adapters.
- [x] Domain classes/migrations: known v0 retained, unknown versions rejected, native unknown fields preserved.
- [x] Explicit gridId/local/parent frames, units/evidence; interval is not component size.
- [ ] Full command transactions: validation/single undo/batch component actions implemented, atomic beam drafts/prepared restores and mixed transforms implemented; generic previews/all failure rollback still incomplete.
- [x] ID allocator/basic whole-graph mapping shared by copy/mirror; complete port/reference mapping pending domain work at this stage.

Acceptance: cached deployed Pages needs no installation, index-first lazy assets/materials, resource disposal on delete/project switch, lossless fields/parsing across split.

## P3 · Building tools and structural topology

- [x] 3D parsing sidebar: GLB/OBJ/STL, background envelopes/filtering, 13 targets 30–250 emphasizing 70–250, quad preference, optional centered X/Y/Z symmetry, scale/grid footprint/counts/wireframe, beams/optional normal plates, one undo. [Model import](doc/07_MODEL_IMPORT.md), not game acceptance.
- [ ] Preserve deep concavity/separate pieces optionally, error controls/more real samples; compressed GLB/complex concavity/skinning unsupported.

Implemented: component placement/delete/transform; Shift batch copy/mirror/split/delete; merge prototype; node tools/beam create/split/delete/plate overlays; mixed whole-cell move/90° rotation/manual mirror. Components/topology share atomic snapshots; full native round trip unaccepted. Depends on P2; nodes/beams/plates must be modeled alongside components.

- [x] Node create/select/move/delete/snap/merge/IDs: independent topology, accessible projected labels/highlight, frozen-plane movement, atomic merge/reference cleanup, helper visibility/delete/save/history verified.
- [ ] Full beam tool: point/continuous building, insert/split, length constraints, dependent-plate prompts. Implemented two-click camera-plane beams, automatic endpoints, one-cell 8 cm/0.08 cross-section, half-cell visual extension, axis-aligned faces/light-gray solids/transparent preview, integer-cell/cm rulers, persistent A-axis snap, cancel/atomic undo, legal interior Alt splits, hidden-node building.
- [ ] Complete plate rendering/validity. Historical ordered-chain/early coplanar-convex-size-membership implementation later relaxed per [Plate review](doc/15_PLATES.md). Occlusion, closure/history, normal offsets, intersections/deduplication/concave triangulation fixed; thickness/outer/glass frames/game acceptance remain.
- [ ] Full paint: component slots/beam/front-back/per-cell, original indexes/defaults. At this historical stage beam col/plate `col_front`/`col_back` diagnostic painting existed; full palette/material semantics incomplete.
- [ ] Placement: surfaces/ports, axis locks, preview rotation, continuous placement, occupancy diagnostics.
- [ ] Selection: single/add/remove/box, vehicle/grid/type filters, lock/hide/isolate. Shift components implemented.
- [ ] Editing: batch delete/copy/cut/paste/repeat/arrays/local-world/pivot/measure. Batch delete/copy/X-mirror/split implemented.
- [ ] Weld/cut with explicit structure/grid/vehicle semantics, never just Three.js merging.
- [ ] Network tools for pairing/path/reconnect/delete and electric/mechanical/liquid/gas/belt/data views.
- [x] Cylinders: three base/rod sizes, raw indexes, size/occupancy/length validation, diagnostics/delete/history, code-derived native references. Read-only Workshop 3809467608 round trip: 22 liquid lines/four steering circuits. [Hydraulics](doc/11_HYDRAULIC_CONNECTIONS.md).
- [ ] Cylinder game loading/dynamics/arbitrary pose/pressure-flow/Mesh-material acceptance.
- [x] Track endpoints/static rendering: 18 wheels, three real widths, two-wheel edge/multiwheel loops, cache/localized diagnostics; code/synthetic evidence [tracks](doc/13_TRACKS.md).
- [ ] Real track saves/game loading/dynamic suspension/motion/collision/material comparison.

Acceptance: minimal node-beam-plate frame editable/saveable without dangling references; cancel/history restores fully.

Implemented structural tools: separate Split beam (I)/Alt inserts affected plate nodes; Glass (J) uses closed beam rings/native-observed `type: "window"`; six networks retain endpoints/optional ports/grid paths/render/delete/history/native import. Inner faces use normal support/depth bias; thickness/outer edges unfinished. Duplicate plates/windows on one loop rejected. Port compatibility/glass damage/full write-back require game evidence.

## P4 · Mirror and subgrid core operations

Depends on P2/P3 topology/remapping; includes components/nodes/beams/plates/links.

### P4.1 Mirror

Manual mirror copies selected components/nodes/beams/plates/internal links across world X/Y/Z integer-offset plane, retaining originals/selecting copies. Continuous supports placement/delete/paint/paired-component transforms/node moves/complete paired structures. Local/multiplane/handed/port semantics unfinished.

- [x] Whole beam/plate transforms/manual mirror: pure transactions, shared-node splitting, shape/front-back retention, endpoint mapping, handles/Inspector/cancel/single undo/deduplication. [Operations](doc/05_BUILD_OPERATIONS.md#whole-transforms-of-beams-plates-and-mixed-selections). 90° structure steps; inclined component whole rotation/mirror/game loading unaccepted.
- [ ] X/Y/Z/combined world/local planes/offsets.
- [ ] One-shot and continuous building fully; current placement/delete/paired moves/rotation/paint work, relationship preview/complex topology open.
- [ ] Synchronized pivots/axes/normals/winding/front-back paint/ports.
- [ ] Handed door/bracket/joint maps; reject unsupported equivalents.
- [ ] Cross-grid links/dynamic constraints, not scale.x=-1.
- [ ] On-plane/multiplane deduplication without merging different structures/ports by position alone.
- [ ] Persist settings; one undo per mirror transaction.

### P4.2 Split

Prototype single/Shift component new-grid membership saves/undoes; boundary structures/links open.

- [x] Connectivity check repartitions all entities with world pose/cross-links/stable IDs/history, mounting-frame handles in physical subgrids; partial cuts/game physics open.
- [ ] Selected split with new origin/pivot/world-pose preservation.
- [ ] Whole versus partial topology; explicit keep/copy-boundary/cancel policy.
- [ ] Explicit network keep/reconnect/disconnect; list changed endpoints/constraints.
- [ ] Valid IDs/ports/nodes/references; no accidental dynamic-Mesh splitting into game grids.

### P4.3 Copy

Prototype independent IDs/offset/one undo for component selections; full subtree/internal/external candidate support open.

- [ ] Complete grid/subtree transforms/nodes/beams/plates/paint/links.
- [ ] New IDs/remapped internal refs; external excluded by default with reconnection candidates.
- [ ] Preview/snap/repeat/whole undo, independent mutable copies.

### P4.4 Move

Prototype single-component transforms; reparent/pivot/joints open.

- [ ] Whole translation/rotation/pivot, local/world/numeric/grid/port snap.
- [ ] Reparent/vehicle conversion with preserved world pose and previewed constraints/links.
- [ ] Joint freedoms/ranges; no scaling bypass.

### P4.5 Merge

Prototype membership-ID merge retains components; deduplication/compatibility/welding/conflicts open.

- [ ] Destination-frame conversion and lattice/rotation/port validation.
- [ ] ID remapping and explicit node/beam/plate tolerances/property conflicts.
- [ ] Precommit occupancy/paint/boundary/joint diagnostics; no silent loss.
- [ ] Rebuild all references without welding hinge/suspension endpoints.
- [ ] Split/move/copy/merge save/load/history topology consistency.

Acceptance: same test vehicle, unique IDs/full references/transform tolerances/normals/ports/paint, unsupported combinations rejected before modification.

## P5 · Component types and real visuals

Depends on P2, may proceed modularly with P3/P4.

| Group | Classes/examples | Special work |
| --- | --- | --- |
| Structure/decor | building/furniture/weight_block/nodes/beams/plates | zones/tile/stretch/thickness/holes/front-back |
| Powertrain | engine/gearbox/torque/motor | Axes/lengths/ports/static-dynamic assembly |
| Ground/air | wheel/tracks/landing gear/aircraft | Suspension/hubs/rotors/control surfaces/pivots |
| Fluid/hydraulic | gas/liquid/hydraulic | Tanks/pumps/valves/manifolds/pistons/ports |
| Electric/logic | electric/data/sensor/interface | Ports/types/property schemas/controllers |
| Controls/mates | control/mechanical/connector | Joints/rails/latches/seats/mechanisms |
| Equipment | storage/light/sound/radio/weapon | Inventory/light/audio-radio/ammo/mounting |

- [ ] Per-class coverage of definitions/Meshes/dynamic parts/occupancy/ports, not searchable-catalog counts alone.
- [ ] Dynamic pos/preview_rot/hierarchy/pivots, matrix order/units.
- [ ] Decode the one opaque component Mesh with minimal fixture; skeleton/animation tails separately.
- [ ] txtr/material slots/packed colors/palette/shaders; neutral preview is not final.
- [ ] Per-Mesh GLB/compressed glTF retaining names/material boundaries/shared deduplication/full dependency manifest (original proposal; current gzip implementation documented separately).
- [ ] Coordinates/two-sided/alpha/emissive/shadows; no DoubleSide masking winding errors.
- [ ] Matched-camera screenshots/vertices/indexes/bounds/material comparison table with explained differences.
- [ ] Lazy cache limits/disposal/thumbnails/instancing/LOD/cutaway/wireframe/desktop benchmarks without reducing asset coverage.

### Designated reference rendering

- [x] Register `test-vehicle/vehicle.data`, `vehicle.meta`, `vehicle.png`; [fingerprints/counts](doc/evidence/vehicle-reference.json). Distinct from starter: 48 definitions/four vehicles/nine grids/159 components/271 nodes/493 beams/138 plates, 512×512 reference.
- [ ] Use red-body reference as visual target. Vehicle 553 resolves cross-vehicle ID conflicts/8 cm/initial collinear plate nodes/triangulation, retains native colors/glass. Automatic black helper-free preview/screenshots exist. Full parent transforms/matched camera/light/materials/outlines/dynamic assembly remain unproven; no pixel pass.
- [ ] Calibrate camera/projection/light/exposure/background/resource version, helpers off, record geometry/image error; no handpicked angle/tolerance acceptance without evidence.
- [ ] Real 3D reconstruction from native data, never reference-image-on-canvas substitution.

Acceptance: geometry/dynamic assembly/materials all match before component visual completion.

## P6 · Native paired .data/.meta export

`src/native/anymaker-data.js` maps vehicle transform/grid origin-dir/component definition-pos-rot/structure/six networks into domain data, retaining unknowns. Initially read-only evidence, no compatibility claim. Depends on stable P2–P5 model/[formats](doc/03_XML_AND_NATIVE_FORMAT.md).

- [x] Starter root/JSON counts: 112 nodes/181 beams/27 plates/two grids/39 components.
- [x] Native-only nonplanar cleanup shared by normal/subgrid import, retaining valid entities/rejecting other errors. Real 981.1 browser removed 11 plates/save-reimported; originals untouched/no game acceptance. [Cleanup](doc/03_XML_AND_NATIVE_FORMAT.md#removing-nonplanar-plates-on-native-import).
- [ ] Complete origin/dir/m/t/pos/rot/ext/definition-index/omitted-default mapping.
- [ ] Paint/endpoints/constraints/state, unknown fields/array order preserved.
- [ ] Confirm paired schema/generation/loading from samples, not other games or XML delivery.
- [ ] Formal edited-project export with IDs/indexes/structures/networks/frames/units/colors/state/unknowns/defaults/meta bounds. Historical requirement only: incomplete mapping/no loading evidence must not become fake-compatible export.
- [ ] Import/edit/export round trip, independent validator/field diffs, game loading for at least three vehicle classes.
- [ ] Extend project/XML domain data with migrations/unknown-field policy.
- [ ] Reject unsupported mirror/rotation/scale/grid relationships with entity diagnostics.

Acceptance: game-compatible means actual game-loading evidence, not downloaded/parseable XML.

## P7 · Advanced desktop and publication

- [ ] Blueprints/templates/selection sets/tree/hide-lock/parameters/command palette/shortcut settings.
- [x] 60-second committed-snapshot recovery, hidden/leaving saves, previous backup, corruption/disabled/quota/multitab protection; subinterval crash loss possible.
- [x] Versioned settings for language/grid/node/snap/panels/drawers/search/tool/camera/target.
- [x] English default/optional Chinese switch, floating toolbar/middle-side handles.
- [x] Camera-following XYZ/six axes/isometric/focus; perspective at this historical stage, orthographic separate.
- [ ] Complete migration/missing-resource diagnostics/formal export checklist.
- [ ] Three-axis orthographic/measure/cutaway/mass-center estimates; evidenced buoyancy/thrust formulas only.
- [ ] Keyboard accessibility/recovery/WebGL2 fallback; no mobile.
- [x] Relative Pages base/subpath browser tests.
- [ ] Reproducible local prebuild unit/browser/assets/budget guide; Pages hosts committed `main /docs`, no Actions build.
- [ ] Complete manifests/reachable references/hashes/size/lazy checks; never publish partial assets after failure.
- [ ] Desktop Chrome/Edge/Firefox/low-GPU benchmarks.
- [ ] Actual Pages/root/subpath acceptance; no online URL record at this roadmap date.
- [ ] Clear import/formats/asset version/visual/native acceptance status.

## Implementation order and gates

1. P0 documentation/ignore baseline.
2. P2 per-component details/bindings/Meshes/domain/transactions.
3. P3 structure -> complete P4 operation chains.
4. Evidence-led P5/P6 before declaring 1:1 or game-loadable.
5. P7 desktop publication acceptance; mobile/touch remain outside scope.
