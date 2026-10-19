# Component Mesh splitting plan

## Goal

Status at the initial design: index/detail/binding extraction exists; published Mesh/material conversion and independent deployment assets were incomplete. The later implementation section below records subsequent progress. The game directory is offline input, never an online dependency.

Components must not remain in one enormous module or hand-maintained array. Maintain definitions, binary parsing, assembly, and category metadata separately for per-class validation, lazy loading, and possible future GLB conversion.

## Target directories

```text
src/components/
  registry.js              Register assemblers; no complete definitions/vertices
  types.ts                 Proposed ComponentDefinition / ComponentInstance types
  common/
    static.js              Generic assembler for ordinary static components
    ports.js               surfaces / logic_nodes handling
    transforms.js          Axes, rotation matrices, dynamic Mesh pivots
  engine/
    engine.js              Engine-specific assembly only if special behavior warrants it
  wheel/
    wheel.js               Wheel component
    landing_gear.js        Landing gear
  building/
    building_b_door.js     Door component
public/data/
  component-index.json     Lightweight search/version/count/source-hash index
  definitions/
    engine.json            One complete original definition per file
    wheel.json
    building_b_door.json
  bindings/
    engine.json            One Mesh-reference list per component
    wheel.json             Static/dynamic reference roles and transforms
```

These are target paths, not claims that TypeScript or all modules exist. `src/assets/mesh.js` parses binary data; `src/assets/library.js` handles local files and Three.js lifetimes. Component rules do not belong in the asset parser.

Possible later splits: `assets/mesh.js` into `mesh/reader.js`, `mesh/v5.js`, and `mesh/layouts.js`; geometry creation, material mapping, and caches into separate library modules. Do not duplicate parsers per component: many components share one format.

Category files should be indexes or small shared rules. Create component modules only for distinct behavior; ordinary components use separate JSON plus a generic assembler, not hundreds of identical empty modules.

Detail files use stable definition IDs; indexes explicitly list relative URLs. Extractors validate safe filenames, unique IDs, and references. Deterministic key/field ordering enables per-component diffs/incremental updates. Retain old catalogs as migration inputs until consumers switch, then avoid maintaining two complete authoritative copies.

## Mesh file organization

Publish separate converted files by original path, never one giant combined GLB:

```text
public/assets/meshes/
  components/engine_block_a_0_0_0.glb
  components/car_wheel.glb
  components/manifold_pipe_a_straight.glb
  buildings/wall_b.glb
public/assets/materials/<texture-id>.ktx2
public/assets/manifests/mesh-manifest.json
```

Each manifest entry should include original `.mesh` path, SHA-256, vertex/triangle counts, submesh names, material slots, bounds, coordinates, and converter version. Resolve component references through the manifest; show a missing-resource marker on failure.

Default to one file per original Mesh and deduplicate shared references. Component bindings and dynamic assemblies reference those files. Preserve original parts as named child nodes; split parts into files only when independent loading/replacement warrants it, recording original part indexes so material relationships survive.

## Submesh rules

- Preserve every static named part as a Three.js child and manifest entry.
- `meshes_dynamic[]` are not static submeshes: preserve each `path/pos/preview_rot` and pivot without welding during conversion.
- Derive boundaries from file structure, definitions, or reproducible experiments, not material color guesses.
- Track low-detail, collision, preview, and final render geometry separately without overwriting original paths.
- Category files describe connection/occupancy/interaction rules without duplicating vertices.

## Lazy loading

The target first screen loads only definition indexes and thumbnail manifest. Selecting/placing a component loads its GLB by ID. Cache by File object/asset URL; dispose Geometry, Material, and Texture when replacing projects/local resources.

GLB/compressed glTF was the planned publishing path. Production must not read local original `.mesh` files; local reads belong to development/audit. Loaders may share binding interfaces, but production reads `public/assets` and manifests without requiring a conversion backend.

## Complete independent publication

For every promised component, manifest entries must cover static Mesh, `meshes_dynamic[]`, material slots, textures, color/alpha/emissive parameters, and coordinates. Publishing only 15 popular models and requiring local imports for the rest is insufficient.

Compression may use:

- Draco, Meshopt, or equivalent geometry compression, recording original vertex/index hashes, compressed hash, version, and quantization.
- KTX2/Basis or browser-compatible textures, recording channels, color space, transparency, and mipmaps.
- Preserved topology, coordinates, normals, UVs, part names, material slots, and building bounds. Lossy quantization requires error limits and screenshot/material acceptance.
- Independent original-Mesh assets with shared-dependency deduplication, not one complete giant package.

Lazy loading changes when download/decompression/GPU upload occurs: index first; details/bindings on selection/placement; Mesh/materials when visible or about to be visible; LRU cache eviction. Already deployed/cached components should remain usable offline. First opening must not access the installation.

## Acceptance criteria

- 598 stable definitions retain original fields; 794 resource references remain locatable and shared references deduplicated.
- Initial network requests only `index.json`; viewing a component requests only its details/binding/necessary models.
- Per-component edits affect only corresponding details, bindings, and dependencies, not a complete giant catalog.
- Filenames trace to component ID/original mesh_path without cross-category collisions.
- Local import, missing-resource reporting, cache disposal, and existing file tests do not regress.
- Production contains no local absolute paths; static checks resolve every binding, dynamic part, material, and manifest URL.
- A clean GitHub Pages browser can search all components and place/display every promised real Mesh without choosing local files or encountering missing assets.
- Network tests show index-first lazy requests and no repeated requests for shared assets.

## Implemented publication (2026-09-22)

`scripts/build-published-assets.mjs` reads the 794 Meshes referenced by ROM bindings, uses the shared v5 parser to preserve positions, normals, UVs, color bytes, indexes, part names, metadata, and bounds, and writes `public/assets/meshes/*.json.gz` plus `public/assets/manifests/mesh-manifest.json`. The package is about 6.6 MiB; entries record source/compressed hashes, bytes, parts, and vertex/triangle counts. This is the implemented format, superseding the earlier GLB proposal.

`src/assets/published-library.js` initially requests only the manifest. `ComponentCatalog` lazily requests details/bindings; Meshes load/decompress at instantiation. Promise caches deduplicate URLs. Production never reads the installation; `AssetLibrary` remains a development/audit local-file fallback. `npm run check:assets` checks binding references, file existence, and output hashes.

One `blade_blurred/blade.mesh` uses an undecoded native variant. Complete original bytes are compressed and marked `opaque` in the manifest; the page shows a diagnostic marker. Decoding remains unfinished P5 work, not 1:1 rendering acceptance.
