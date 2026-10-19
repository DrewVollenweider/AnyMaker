# XML, project JSON, and native-file boundaries

## Current project JSON

Browser schema: `anymaker-web-project` v1:

```json
{
  "format": "anymaker-web-project",
  "version": 1,
  "projectName": "anymaker-vehicle",
  "grids": [{"id": "grid-1"}],
  "objects": [
    {
      "id": "instance-uuid",
      "type": "engine",
      "position": {"x": 0, "y": 0, "z": 0},
      "rotation": {"x": 0, "y": 0, "z": 0},
      "localMirrorAxes": ["x"],
      "scale": {"x": 1, "y": 1, "z": 1}
    }
  ]
}
```

`projectName` is saved in history/local recovery and becomes the basename for `.data`, `.meta`, project JSON, and intermediate XML. Invalid filename characters are replaced; empty names fall back to `anymaker-vehicle`. It is not currently written into native vehicle fields.

Optional `grids` is an editor subgrid catalog. Each has a unique alphanumeric/`_`/`-` `id` and optional `name` up to 80 characters. Rename through the subgrid list; JSON, project code, history, and recovery preserve names. Older unnamed grids use default labels. Empty manually created grids persist. Components/nodes/beams/plates may share `gridId`; legacy missing membership defaults to `grid-1`. This editor catalog does not establish native subgrid-export semantics.

Native import groups editor membership by physical `vehicle`: all mounting `grids[]` in a vehicle share the first mounting grid's editor `gridId`, while each component retains its own mounting-frame projection and source-grid instance ID. Door handles/dashboard instruments do not become separate physical groups merely from different mounting coordinates. Connectivity checks may split/merge membership without moving world coordinates or equating `gridId` with a native mounting frame.

Optional `nativeProperties` stores serializable Properties Tool fields: finite numbers, booleans, text, and bounded-size/depth JSON state. It excludes component/vehicle relationship references. Import retains safely validated properties. Inspector edits existing fields and defaults confirmed through game descriptions/GCL symbols, such as gear-lever gear counts, gearbox ratios, mechanical offset/scale. Paired export writes them into component records. Complex runtime state is read-only; game loading remains unverified.

The `microcontroller` class uses observed `script`, `global_inputs`, `global_outputs`, `global_private` from `test-vehicle/vehicle.data`. Variables are `{ name, data_value }`; samples currently support `f64` and `bool`, with native `type: "type_bool"` for booleans. Inspector provides dedicated editors. The browser never parses/executes scripts or simulates data networks/game runtime. Field write-back is format research, without game-loading acceptance.

Import validates version, unique IDs, definition existence, finite numbers, transform bounds, positive scale. Projects contain no local absolute paths or selected File objects.

Editor lattice: `1 cell = 8 cm = 0.08` world units. Ordinary `objects[].position`, `mirror.offset`, and manual `topology.nodes[].position` world X/Y/Z must be whole cells; reject off-grid input, normalizing only floating-point residuals of 8 cm multiples. Native `nativeProjected` objects and valid `surfaceMount` components may retain fractional world positions. Beams reference nodes; plates reference nodes only. `scale` is dimensionless, not a cell count.

On 2026-09-28, optional `surfaceMount: { dir: [0,1,-2], position: [66,0,131] }` was added without changing v1. Each field has three integers with absolute value ≤1000000. `dir` has at least two nonzero components, representing a native inclined normal. `position` is integer mounting-frame position, distinct from world `position`. Validation, JSON, adapters, and history preserve it; older projects need no migration, but older editors may discard it.

Native export reconstructs integer mounting `origin` from world position, transforms orientation back to integer local `rot`, and groups by `origin/dir` into multiple `grids[]` within one physical vehicle. Inclined mounting grids are not new physical bodies. Whole-cell moves/copies retain fractional positions. Noninteger origins, nonlocal-90° rotations, and reflected geometry explicitly fail native export. See [inclined placement](12_INCLINED_PLACEMENT.md). Intermediate XML omits `surfaceMount` and is neither lossless nor game-compatible.

`topology.nodes[].standalone: true` marks explicitly created nodes to retain even without beams/plates. Structural commits remove unreferenced editor leftovers unless standalone or native-projected. Hidden state never implies deletion; referenced hidden nodes remain.

Optional `topology.edges[].color`, `topology.plates[].color_front`, and `topology.plates[].color_back` are editor `#RRGGBB` paint/render fields. Imported `col`, `col_front/col_back` remain optional native indexes 0–255 with unverified color semantics at that research stage. `topology.plates[].normalOffset` is finite world units: its absolute value supplies support offset for every nonzero normal axis; typical new value 0.04, three-cell beam 0.12, zero on node plane. Optional `surfaceDirection` chooses front/back; new plates save oriented unit normals. Old camera vectors remain readable but no longer shift outlines tangentially. This is not game plate thickness; see [Plate review](15_PLATES.md). These editor fields were not encoded by intermediate XML/current experimental native write-back at this checkpoint; do not infer compatibility.

`topology.links` stores `id`, `kind`, `from/to` component endpoints (optional `port` 0–255), and `points`. Six networks `electric / mechanical / liquid / gas / belt / data` permit up to 256 integer-cell path points. Additional `hydraulic` means external cylinder, requiring empty points, integer `lengthMax` 1–10000 cells, finite `extensionFactor` 0–1. No duplicate cylinder-port occupancy; tool/export also validate matching-size base/rod and original scale. Base original port index is 2, rod 0.

This retains v1; existing cylinder-free projects need no migration. Older editors reject the new kind. Validation/snapshots/JSON retain lengths; XML still omits links. Native cylinders write both endpoints' `connected_vehicle / connected_component / connected_node_index` and base `length_max / extension_factor`, preserving `hydraulic_cylinder` fluid state without inventing `hydraulic_links`. Supply and wheel steering use `liquid_links`. See [hydraulics](11_HYDRAULIC_CONNECTIONS.md) for omitted defaults/size offsets/evidence. This supports undoable editing/diagnostic rendering, not accepted game loading.

`topology.mechanicalConnections` separately stores physical mates: `id`, `type` (`hinge`, `latch`, `mounting`, `rail`, `rail_ballscrew`, `tow`), instance IDs `from/to`, shared anchor `position`, optional `axis`, hinge `limits`, mounting-pin `orientationIndices: [a, b]` (integers 0–31). Optional fields retain v1 compatibility; legacy missing orientation indexes recalculate from geometry. Import/commits rebuild from definitions/mating frames, independently of the six network kinds. Native export separates rigid endpoints and writes reciprocal `connected_vehicle / connected_component`, orientation indexes, or rail lists. Game `post_load` needs explicit references, not overlapping Meshes alone. See [mechanical mates](10_MECHANICAL_MATES.md).

Optional `visibilityGroups` stores editor transparency groups: stable `id`, user name, component/edge/plate IDs in `components`, `edges`, `plates`. They support bulk visibility only, not XML/native serialization. References must exist; commits prune deleted members.

Project JSON references stable definition IDs, not Mesh/material/lazy URLs. Published indexes/bindings/manifests reconstruct assets on GitHub Pages without the installed game.

Current editor limits: 2000 components, position/rotation absolute values ≤10000, scale `(0,100]`. These are input boundaries, not verified game limits. Rotations are Three.js XYZ Euler radians. The broad editor/game lattice mapping statement here predates the specific mounting/X-reflection evidence below; full game validation remains incomplete.

### Track and belt connections

Ordinary belts use `topology.links(kind: belt)` / native `belt_links`, distinguished from `belt_track*` by port type `belt`. Pulley/three engine-wheel radii come from `get_belt_data`; component `reverse` persists. Closed surfaces/original texture are derived displays, not serialized geometry. Two-wheel single edges or multiwheel loops render static solids; links/properties retain export rules. See [belts](14_BELTS.md) for the real six-wheel sample/limits.

Tracks also retain v1 links/native `vehicles[].belt_links`. Three `belt_track*` types select width; ports retain original `logic_nodes` indexes. Native edges contain `p0/p1.comp/pos`, omit default port 0, and exclude derived links/path samples/diagnostic colors. Two wheels need one edge, larger networks branch-free closure. Open valid references remain editable/saveable. Real centers/radii/pitches/32-direction tangents generate static geometry: [tracks](13_TRACKS.md). No real track-save or game-loading acceptance was available.

## Current intermediate XML

`anymaker-intermediate.xml` is for debugging/tool exchange:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!-- EDITOR INTERCHANGE ONLY. Not a verified Anymaker vehicle save. -->
<anymaker-web-project version="1" name="anymaker-vehicle" game-compatible="false" coordinate-unit="world" grid-cell-size-cm="8">
  <component instance="instance-uuid" definition="engine">
    <position x="0.000000" y="0.000000" z="0.000000"/>
    <rotation-radians-xyz x="0.000000" y="0.000000" z="0.000000"/>
    <scale x="1.000000" y="1.000000" z="1.000000"/>
  </component>
</anymaker-web-project>
```

Escape attributes and text. It lacks native nodes/beams/plates/paint/component grids/networks/runtime state and cannot be claimed game-readable.

| XML | Source | Meaning |
| --- | --- | --- |
| version | Project schema | Currently 1 |
| game-compatible | Fixed false | No game-readability claim |
| coordinate-unit / grid-cell-size-cm | Fixed `world` / `8` | Editor 8 cm integer lattice, not a game-unit compatibility claim |
| component.instance | objects[].id | Editor instance ID, not native integer ID |
| component.definition | objects[].type | Definition ID, not native def index |
| position | objects[].position | Editor world coordinates; manual whole cells, nativeProjected/surfaceMount may be fractional |
| rotation-radians-xyz | objects[].rotation | XYZ Euler radians |
| scale | objects[].scale | Editor transform, not native ext/stretch |

JSON still serves validation/history/local recovery but is no longer the visible Save/Open exchange. No XML importer exists. Six-decimal output rounds values and is not lossless read-back.

## Native fields and target mappings

| Observed path | Shape | Mapping needing verification |
| --- | --- | --- |
| definitions.components | Definition ID strings | Integer `grids[].components[].def` indexing |
| vehicles.vehicles[].transform | Nine m and three t numbers | Row/column order, handedness, units |
| grids[].origin / dir | Optional number arrays | Basis/defaults/local relationships |
| grids[].components[] | def/id/pos/rot/colors, sometimes ext/state | Matrices, color slots, stretch/state defaults |
| nodes / edges / plates | IDs/references | Coincidence, connectivity, winding, membership |
| plate_paint | plate_id, front/back chunks | filled/pixels, grid_pos, color indexes |
| *_links | p0/p1, points, color, etc. | comp/pos encoding and cross-grid coordinates |
| .meta bounds | min/max arrays | Necessity/recalculation timing |

Preserve omitted/unknown fields. Do not force editor scale/Euler data into native files without evidence.

Palette source is ROM `textures/color_palette.txtr`: TXTR v2, 256×1 RGBA8; first 85 slots (0–84) opaque, remaining alpha-zero placeholders. `scripts/extract-color-palette.mjs` validates layout and generates self-contained `src/editor/game-palette.js`. Source SHA-256 `ed7f5ca7a55ab5e71769298b5d523d9f81d98563755845968dc684932160027e`. Export maps editor RGB to nearest opaque slot by squared 8-bit RGB distance, ties to lowest index, writing component `colors`, beam `col`, plate `col_front/col_back`, connection `color`. Unpainted native indexes survive. Palette RGB does not reproduce game lighting/materials.

On 2026-09-25, GCL bodies corrected grid projection: [transform evidence](evidence/native-grid-transform.json), [reverse engineering](06_REVERSE_ENGINEERING.md). Omitted `origin` is `[0,0,0]`; omitted `dir` `[0,1,0]`. Only their combined match uses identity base grid. Otherwise `Y = normalize(dir)`; world Y reference up, except world Z when dir parallels Y; `X = normalize(dir × up)`, `Z = normalize(X × Y)`. Earlier world-X projection rotated in-plane door axes incorrectly.

Effective origin in cells: `origin + 0.5 * sign(dir) + 0.5 * normalize(dir)`. Per-axis sign comes from node-cube face center/edge midpoint/corner; the latter term is half-cell component-base normal displacement. Rotation alone omits essential translations. Compose component `pos` and native column-major `rot` with full frame, then convert positions by 0.08. Nodes/beams/plates/path points stay in vehicle coordinates despite temporary storage in first-grid editor projection.

Editor/native X axes oppose. Import completes native grid/accessory transforms, then reflects positions across YZ. Rotations use `S R S`, `S = diag(-1, 1, 1)`. Mesh local geometry/ports reflect too; reverse plate node order to preserve front/back. Export applies inverse to components/nodes/paths; recompute native `.meta` bounds. Asymmetric automated round trips exist; matched-camera/game-loading acceptance remains required.

Vehicle relationship-anchor corrections use multibody pivot differences after grid projection. `hinge_knuckle.constraint_position` is supported; `tow_hitch` surface/logic positions are not substituted for pivots. All recorded anchors for a child vehicle must imply one offset, otherwise projection stops. `nativeProjected` retains fractional world cells on inclined grids. These frame rules have static code evidence; arbitrary dynamic poses, full write-back, and game loading remain unaccepted.

## Final export goal

The goal is native paired `.data/.meta`; XML remains a development interchange. `toNativePairFromEditor` generates paired JSON from the scene and recalculates meta bounds; experimental independent-domain write-back is another entry point. Paired generation does not prove compatibility: unknowns/defaults/full state/game loading remain open.

Before body partition, export cleans redundant collinear nodes and adds missing boundary beams adjacent to beamless plate corners in a temporary copy. Deduplicate unordered pairs, preserve corners/outlines, avoid adding every triangulation edge. Run the same structural-island preflight as the button, rejecting degenerate/duplicate beams, invalid plates, cross-island references, dangling links. Revalidate per-body references and a beam for every exported node after splitting. Failures write no files; normalization never changes current project/original saves. See [islands](16_NATIVE_ISLANDS.md).

## Native Anymaker questions still requiring confirmation

Evidence identifies `.data/.meta` JSON, not XML. Before formal compatibility, obtain real exports or controlled tests for:

1. Root/vehicle ID generation.
2. Matrices, translations, grid coordinates, unit conversion.
3. Definition-array and component `def` indexing.
4. Relationships among nodes/edges/plates/components.
5. Electrical/mechanical/liquid/gas/belt/data endpoints.
6. Dynamic state, colors, plate paint, buoyancy.
7. Unknown-field retention, migration, loading diagnostics.

Keep UI wording Intermediate XML, never Game-compatible XML, until these are resolved.

## Current read-only native adapter

`src/native/anymaker-data.js` parses native JSON into domain data and retains paired meta. Import local vehicle and Select paired .data/.meta share pairing: exactly one of each, matching basenames. Single files, duplicate extensions, differing names, oversized files, nonobject meta fail. After local read/validation, import the most-component main vehicle and related children, replacing the scene. Save vehicle requires no original files: generate components/nodes/beams/plates/links and meta identity transform/current bounds from the current editor project. Loading semantics, all state, complex child hierarchies remain unverified, so do not label game-compatible. XML additionally retains `component.grid` and optional `<mirror axis="x|y|z" offset="..."/>`, still nonnative schema.

### Removing nonplanar plates on native import

Native saves can contain plates failing editor coplanarity. Normal/subgrid import both use `src/native/import-document.js` `prepareNativeImport`: project into editor coordinates, remove only `nonplanar-plate` failures, then validate the full project. Retain components/nodes/beams/valid plates without moving nodes or modifying raw native-domain data/disk originals. Subsequent native export uses the cleaned scene without restoring removed plates.

This tolerance is native-import-only. Project JSON/manual creation still rejects nonplanarity; duplicate/unknown nodes, self-intersection, other errors remain fatal. Successful cleanup reports count in localized viewport messages. Parse/validation failure reports specifics and preserves loaded project.

2026-09-28 `981.1.data/.meta`: six components, 91 nodes, 161 beams, 56 plates; removes 11 nonplanar plates, retaining 45 plus all components/nodes/beams. Browser verified geometry, undo/redo, save/reimport, unchanged original SHA-256. This is not game-loading acceptance. Portable fixture/unit assertions: `tests/native-import-fixtures.js`, `tests/native-import.test.js`; browser cases in `tests/browser/editor.spec.js` accept local basename without extension through `ANYMAKER_NATIVE_IMPORT_SAMPLE`.
