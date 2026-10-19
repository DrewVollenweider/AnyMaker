# Track import, rendering, and export

## Scope and sources

Read-only research covered the then-current local `bin/game.gcl` and ROM: six each of sprockets, fixed rollers, suspension rollers (18 definitions), and three real link Meshes for narrow/standard/wide tracks. Version fingerprints, function signatures/offsets/hashes, constant addresses, and definition/Mesh fingerprints: [evidence](evidence/tracks.json).

Inspected paths include track-link parsing, wheel-center/radius queries, network traversal, 32-direction tangent search, path rebuilding, and instance transforms. No real vehicle sample containing track wheels was found. Tests use synthetic native-format vehicles based on real definitions, not game-loading or 1:1 visual acceptance.

## Native format and networks

- Tracks reuse `vehicles[].belt_links`. Each edge has `p0 / p1`; endpoints contain component ID `comp` and original `logic_nodes` index `pos` (0 may be omitted).
- `belt_track_narrow / belt_track / belt_track_wide` determine width. Editor uses the existing `belt` network but rejects mixing with drive belts or different track widths.
- One edge between two wheels produces a closed loop. Three or more require a branch-free closed sequence. Follow connection order, preserving concave rollers rather than substituting a convex hull.
- Project v1 `topology.links` is unchanged. Links are derived render data, not project/native components. Native edges contain endpoints only, without sampled paths or diagnostic paint.
- Export remaps component IDs while preserving port indexes. Ordinary belts retain their behavior. Valid open multiwheel connections can be saved without solid track rendering.

## Geometry

| Component suffix | Original radius | Link pitch |
| --- | ---: | ---: |
| small_narrow / large_narrow | 0.08 / 0.16 | 0.08 × π / 4 |
| small / large | 0.18 / 0.34 | 0.16 × π / 4 |
| small_wide / large_wide | 0.23 / 0.43 | 0.24 × π / 4 |

Values are world units (one cell = 0.08). Game radius quantization uses `pitch / (2π)`: 0.01/0.02/0.03; wide radii 0.23/0.43 become 0.24/0.42. Tangents use 32 directions. Arc/straight sections calculate whole-link counts separately; straight allocated length is adjusted before sampling the closed path. Concave entry/exit angles converge to their bisector without an extra revolution.

Sprocket centers are component origins; fixed rollers use first dynamic Mesh `pos`; suspension rollers use second dynamic Mesh `pos`. Logic ports are not wheel centers. This is the static building pose with suspension displacement and track phase both zero.

Game transforms sample by pitch to the actual allocated path end. With mixed radii, a final interval shorter than one pitch can still generate a link, yielding one more rendered instance than the rounded nominal rebuild count. The editor preserves this and caps actual instance counts.

Mesh X follows track, Y radius, Z axle, preserving native axial offset. Use one `InstancedMesh` per loop/part, lazy resources, atomic replacement, and GPU disposal on edits/undo/deletion. Negative-determinant transforms clone and reflect vertices/normals/winding instead of applying negative instance scale.

## Editor behavior and limits

- Choose Belt and click same-width track-wheel ports. Axles must point the same way and centers be coplanar; scaled track wheels are unsupported.
- Any wheel move invalidates the whole loop cache, including wheels not adjacent to its first edge. Undo/redo restores full connections/shape.
- Belt visibility controls solids in editing; native-reference previews retain solids.
- Open/branched/mismatched-width/nonplanar/no-tangent/oversized networks do not produce invented solids. Valid references remain diagnostic lines; localized resource/validation diagnostics explain failure.
- Tangent search caps at 64 iterations; scene cap is 8192 links. These are editor allocation limits, not game limits.
- Neutral materials, fixed centers/phase do not simulate game materials, dynamics, pressure/tension, collision, wear, or dynamic suspension.

## Implementation and validation

- `src/editor/track-profiles.js`: component/radius/center/pitch/resource mapping.
- `src/editor/track-path.js`: pure-data network/geometry without DOM/Three.js.
- `src/editor/track-view.js`: real Mesh instancing/coordinate reflection.
- `tests/tracks.test.js`, `tests/track-fixtures.js`: three widths, 18 definitions, loops, concavity, mixed radii, invalid networks, rotation, Meshes, endpoints, history round trips.
- `tests/browser/editor.spec.js`: native import, solids, nonadjacent wheel edits, undo/redo, visibility/reference preview, export/reimport, tool use, localized diagnostics.

Read-only evidence check:

    node scripts/check-track-evidence.mjs <game.gcl> <Anymaker/rom>

Offline update of only three track-link assets, preserving other manifest entries:

    node scripts/build-published-assets.mjs <Anymaker/rom> --tracks-only
    npm run check:assets

Frontend never reads the local installation. Published resources total 868, including one unchanged opaque native variant.

Actual 2026-09-28 validation: `npm run check` passed 183 unit tests/build; 67 editor browser cases passed, then three track-specific workflows passed again after terminal-sampling correction. Asset checks passed (800 references, 868 entries). Evidence checks covered 22 functions, 13 constants, three source/output Mesh hash pairs, 18 definitions. Four-wheel frontal and three-width angled screenshots were visually inspected. Production relative base was restored. No game-loading acceptance.
