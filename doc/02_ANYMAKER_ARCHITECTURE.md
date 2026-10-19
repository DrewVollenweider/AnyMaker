# Anymaker resource and vehicle architecture

This document separates observed resource fields from unverified runtime semantics. Stormworks analysis directories offer scanning/decompilation methods, not evidence of Anymaker's formats.

## Verified resource layout

```text
Anymaker/
  game.exe
  rom/
    data/vehicle_component_definitions.json
    data/buildings/starter_vehicle.data
    data/buildings/starter_vehicle.meta
    meshes/components/*.mesh
    meshes/buildings/*.mesh
    textures/**/*.txtr
    languages_components.tsv
```

The installation version audited here has 10,713 ROM files, including 598 component definitions, 3,333 `.mesh`, 115 `.txtr`, 204 `.data`, and 204 `.meta`. Full hashes/scan results: [asset audit](evidence/asset-audit.json).

## Component definitions

`vehicle_component_definitions.json` has a top-level `definitions` array. The editor must retain:

| Fields | Purpose |
| --- | --- |
| `id`, `name`, `class`, `category` | Stable identity, search, categorization, display |
| `mesh_static.mesh_path` | Static Mesh reference |
| `meshes_dynamic[]` | Dynamic sub-Meshes, positions, preview rotations; recorded here but not yet automatically assembled at this stage |
| `zones`, `interval`, `mode_x/y/z` | Candidate occupied regions, spacing, tile/stretch modes; units/defaults/exact building rules need verification |
| `surfaces` | Structural, mechanical, torque, fluid, and other connection surfaces, including `pos/dir/gender/type` |
| `logic_nodes`, `data_descriptors` | Logic ports and data inputs/outputs |
| `density`, `tech_tier`, `spawn_probability` | Mass estimation, technology tier, game-logic parameters |

Definitions are data-driven. Do not guess dimensions from names or equate visual Mesh bounds with building occupancy.

## Native vehicle structure

Despite its extension, `data/buildings/starter_vehicle.data` is JSON. Observed fields:

- `definitions.components`: definitions used by the vehicle.
- `vehicles.vehicles[]`: vehicle instances.
- `transform`: 3×3 matrix `m` and translation `t`.
- `nodes`, `edges`: structural nodes/beams.
- `plates`, `plate_paint`: plate polygons and per-cell paint.
- `grids[].components[]`: instances, definition indexes, grid positions, rotation matrices, component state.
- `electric_links`, `mechanical_links`, `liquid_links`, `gas_links`, `belt_links`, `data_links`: distinct network connections.
- `buoyancy_fill`, `loot_locations`, `creature_locations`: runtime or scene-associated data.

`src/native/anymaker-data.js` maps these read-only structures to an independent domain model. Vehicle-level nodes/beams/plates/links attach only to the first grid in the editor projection, avoiding duplicated topology from component-grid grouping. Definition indexes, rotation matrices, color slots, states, and unknown fields remain in `extras.native`; original JSON is in project `extras.native.raw`. Safe reading does not establish game-compatible write-back after editing.

Observed colors: beams use `edges[].col`; plates use `plates[].col_front`, sometimes `col_back`; components use `grids[].components[].colors` slot arrays. Editor painting uses separate Hex RGB fields `color`, `color_front`, `color_back`. Imported native indexes remain preserved as fallback diagnostic previews. The full native palette, component-slot mapping, `plate_paint`, and shaders need verification. Rotation matrices retain their original 3×3 arrays and convert to XYZ radians in the browser projection; matrix conventions still require game screenshot/read-back validation.

The sample has one vehicle, 112 nodes, 181 beams, 27 plates, two grids, and 39 components. `.meta` contains matching transform/bounds summaries.

A vehicle is therefore more than components plus XYZ. Native import/export must handle matrices, grid coordinates, beams, plate paint, and multiple networks. Until evidence is complete, intermediate project XML remains explicitly incompatible with game saves.

## Editor connection projection

The six native link arrays map to project `topology.links`. Editor endpoints use `{ componentId, port? }`; path points use world grid coordinates. Import maps `p0/p1.comp` to instance IDs, retains `pos` as port index, and converts `points` using 0.08 world units. Visualization/undo cover all six kinds, but port compatibility, belt/pipe-specific constraints, and game write-back are not established by this sample.

## Mesh v5 observations

Binary checks of component Meshes confirmed `mesh` magic, version 5, one or more named submeshes, three vertex strides (16/28/36 bytes), triangle index buffers, and an eight-byte zero terminator. The parser checks truncation, vertex buffers, index bounds, and unknown trailing content, explicitly failing unsupported layouts.

This is not complete rendering recovery. Packed vertex colors, material slots, `.txtr` compression, dynamic assembly, skeletons/animation, and game shaders remain partly unknown. The browser currently uses real static geometry with neutral diagnostic materials.
