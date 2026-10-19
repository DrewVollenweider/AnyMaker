# 3D model parsing

## Interaction and implementation

Right sidebar Resources and validation -> 3D model parsing accepts local GLB/OBJ/STL, reports source vertices/triangles, simplification/uniform scale, resulting nodes/beams/plates/footprint. Confirm replaces the vehicle; one undo restores it. Cancel, parse errors, parameter adjustments do not change the project.

- Thirteen target-vertex levels: **250,230,210,190,170,150,130,110,90,70,50,40,30**, default about 150. First ten emphasize 70–250; final three reduce cross-sections for coarse outlines. UI distinguishes target, simplified vertices, final grid nodes. Eight vertices per section, merging/degeneracy cleanup changes counts; simple planes do not gain artificial points.
- Intersect first/last depths on three axes for a solid envelope, at fixed longest-axis resolution 56 voxels and two low-pass passes. Remove tiny islands/fill closed cavities; interior seats/chassis do not generate separate structures, small protrusions disappear.
- Volume models sample convex octagonal cross-sections along longest axis, join with coplanar quads, cap ends. First ten levels retain at least ten sections; targets 50/40/30 permit six/five/four. Consistent edge directions/grid reconstruction; sufficiently wide models retain at least six-cell thin end widths/two-cell corners to prevent collapsed faces/short beams. Envelope merges grooves/holes/separate cross-sectional pieces/gaps, preserving major outline only.
- Open coplanar models, including inclined ones, retain open planar decimation. Cluster dense input to ≤2,048 vertices, then edge-collapse. Merge adjacent triangles only if coplanar/convex/aligned, permitting ≤one-cell per-axis adjustment when necessary. Lock accepted quads; neighbors cannot flip/collapse. Otherwise retain triangles.
- Symmetry defaults off; X/Y/Z reflect through source-bounds-center YZ/XZ/XY respectively. Snap center plane to nearest 8 cm grid plane; Y uses model midpoint, not ground. Average shell sections with reflections, fit paired ranges/corners/positions. Open planes retain positive half and mirror; result may differ from source. Disabling restores original simplification without mutating worker cache.
- Symmetry constrains final scaled/snapped nodes; disable individual quad adjustments. Prefer valid quads but do not guarantee symmetric face/beam subdivision. Recalculate counts/footprint; open-plane clipping may add seam nodes.
- Scale 0.01×–100×, default 1×. **1× normalizes transformed GLB longest dimension to 4 m**, not a verified file-to-game-unit mapping. All levels use original bounds; center X/Z and minimum Y; snap final coordinates to 8 cm cells.
- Footprint uses remaining nodes' X×Z and separate Y height, adding one cell per span for beam thickness. Thus 4 m source span may produce 4.08 m footprint. Main HUD currently uses node span without this extra cell; definitions differ.
- Shared vertices become nodes, final triangle/quad perimeters become beams, **no quad triangulation diagonals**. Plates default on, normals follow shell winding with global flip. Quads remain four-node records; no schema/coplanarity relaxation.
- SVG wireframe shows final grid centerlines, draggable/arrow-key rotation; not beam thickness/material/plate shading.
- Optional UI localization follows editor settings. Files, parsed meshes, worker caches, temporary controls never enter snapshots; only generated standard topology persists.

## Modules and format boundaries

| Module | Responsibility |
| --- | --- |
| `src/assets/model-import.js` | GLB scenes/geometry, Three.js OBJ/STL, input bounds |
| `src/assets/model-shell.js` | Depth envelope, filtering, cavities/islands, open-plane decimation |
| `src/editor/model-shell-sections.js` | Sections/coplanar quad shell |
| `src/editor/model-symmetry.js` | Reflected averaging, clipping, winding reflection |
| `src/editor/model-quads.js` | Grid-coplanar quad merging/neighbor protection |
| `src/editor/model-mesh.js` | Bounds/normals/vertex-face remapping |
| `src/editor/model-import-settings.js` | Thirteen budgets/default |
| `src/editor/model-conversion.js` | Grid merging/deduplication/normals/footprint/topology |
| `src/editor/model-import-worker.js` | Background parsing/simplification; at most three levels cached |
| `src/editor/model-import-tool.js` | Sidebar, request versions/cancel, preview/commit |
| `src/locales/model-import-en.js` | Tool localization mappings |
| `src/main.js` | Validation/prepared scene replacement/history/focus |

GLB supports glTF 2.0 embedded BIN, default static scene hierarchy, matrix/TRS, repeated Mesh instances, Float32 POSITION, interleaved bufferViews, 8/16/32-bit indexes, unindexed triangles, strip/fan. Ignore materials/textures/cameras/animation without fetching URLs. Reject external buffers, sparse accessors, compressed/extension geometry, skinning, morph targets, nonface primitives. Initial version has no Draco/Meshopt decoder.

OBJ uses Three.js without MTL/textures, supports positive/negative indexes and parser fan triangulation; triangulate complex concavity beforehand. STL supports ASCII/binary and vertex winding, without repairing it from normal fields.

Limits: 32 MiB file, 500,000 vertex records/triangles, including expanded OBJ/STL vertices. Generated limits: 5,000 nodes, 10,000 beams, 4,000 faces. Show excess counts/block confirmation pending stronger simplification. These are memory/interaction budgets, not game limits or low-end FPS promises.

Validate lengths/counts/finite coordinates/indexes/hierarchy cycles. New file/cancel terminates old worker; disable confirmation while calculating and discard stale parameter results. All code ships statically; Vite worker URLs honor subpaths.

## Validation

- Historical `npm run check`: 116 tests/build passed. Coverage includes hierarchy/reflection, invalid GLB, negative OBJ indexes, both STL formats, interior/protrusion removal, inclined planes, budgets, quads/closed boundaries/no diagonal beams, lattice/footprint/normals, narrow ends/native winding. Also asymmetric shells on three axes, X/Y/Z symmetry, half-cell rounding, levels/scales, seams, open-plane normals, restoring symmetry-off state.
- Three 3D-model browser workflows passed within editor testing: formats, scale, plate toggles/flip, symmetry, confirm/history/language/cancel/bad files, external real sample. Target with `-- --grep "3D model"`.
- External sample remains outside Git:

```powershell
$env:ANYMAKER_MODEL_SAMPLE = '<local-model-path>'
npm run test:browser:editor -- --grep '3D model'
```

[model-import-sample.json](evidence/model-import-sample.json) retains input fingerprints/old section counts before narrow-end treatment. Same GLB retest, level 13/1×/X symmetry: 32 nodes, 60 beams, 30 quads, zero triangles; eight former beams below 12 cm reduced to zero. Ignored screenshots: `test-results/model-sample-preview.png`, `test-results/model-sample-vehicle.png`. Game visuals not rechecked.

Earlier same-Porsche symmetry audit: 13 levels × three axes × scales 1/1.02/1.37 = 117 cases. Historical counts are not post-narrow-end counts. New isolated default-level/1×/X result: 152 nodes, 144 quads, 12 triangles. Browser checks off-by-default, axes, preview restoration, rapid changes during work, localization, symmetry/history.

This change passed 116 tests/build and three sample-bearing targeted browser cases covering eight levels/scales/generation/history. The old 117-case audit was not regenerated. Earlier complete editor suite with sample: 33/37 passed, four failed, not rerun completely here. All four reproduced on unchanged separate `8671728` worktree without deleting/relaxing assertions:

| Existing case | Failure |
| --- | --- |
| extendable components | Linear size Z expected 0, got 1 |
| registered reference vehicle | Relative-handle coordinate sign opposite assertion |
| favorite stars | Favorites hidden after refresh |
| XYZ rulers | New grids/projectName absent from old field-set assertion |

Historical logs: ignored `local-data/model-levels-check.log`, `local-data/model-levels-browser.log`; old 117-case data `local-data/model-symmetry-audit.json`. Full suite had four existing failures and was not rerun here. No asset/settings-specific checks, game load, or publication.

Game loading, physical connectivity, driveability, material recovery, native compatibility remain unverified. Generated editor structures do not automatically receive engines/wheels/controls.
