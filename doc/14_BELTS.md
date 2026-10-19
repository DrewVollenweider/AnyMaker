# Ordinary drive belts

## Scope and evidence

On 2026-09-28, read-only inputs were local `bin/game.gcl`, four wheel definitions, `textures/belt.txtr`, and vehicle 553's six-wheel circuit in `test-vehicle/vehicle.data`. [Evidence](evidence/belts.json) records game fingerprint, nine function signatures/offsets/code hashes, ten constants, definitions, and texture hashes.

Belts and tracks share `vehicle_belt.rebuild` but generate differently: belts are continuous procedural geometry; [tracks](13_TRACKS.md) instance individual Mesh links. This investigation uses long `rebuild(vehicle_belt, vehicle)` at `0xf39fcf`; network collection is in overload `rebuild(vehicle)` at `0xf486e8`.

| Component | Radius, world units | Original port |
| --- | ---: | ---: |
| `pulley_wheel` | 0.04 | 0 |
| `engine_wheel` | 0.10 | 0 |
| `engine_wheel_b` | 0.155 | 0 |
| `engine_wheel_c` | 0.267 | 0 |

All four use `logic_nodes[].type: belt`. Center is the logic node's extended position transformed by the component, not the protruding port point. First-wheel local +Z gives the axle. Game tangent search uses 32 directions, angle `-2π × index / 32`, signed-distance threshold 0.0001. `reverse` is a saved boolean; opposite adjacent wheel directions flip contact by half a turn and reversed idlers wrap oppositely.

Cross-section width is 0.056, thickness 0.012 world units (56 mm × 12 mm): eight vertices/four independently normaled faces per section. Game UV V is 0; target U density is 16. Original allocation gives one chord-length step at both arc ends plus straight distance, then adjusts to integer repeats. The editor preserves this allocation/closing seam.

Original TXTR v2 is RGBA8, 32×32, six mip levels. `scripts/build-belt-texture.mjs` validates all mip sizes/lengths and deterministically converts first-layer RGBA to PNG, retaining source/output SHA-256. Published `public/assets/textures/belt.png` is 109 bytes; no installation dependency. Three.js generates mips from PNG; lighting/material parameters are not full game-shader recovery.

## Current behavior

- Imported ordinary `belt_links` generate continuous solids. Belt tool needs one edge for two wheels; larger branch-free loops follow saved order, including concave reversed idlers.
- Mix all four radii with parallel axles/coplanar centers. Scaled wheels, wrong ports, belt/track mixing, branches, and impossible tangents produce explicit diagnostics. Valid open references remain lines for later completion.
- Move/rotate/mirror or edit any wheel's `reverse` to rebuild the complete loop, including nonadjacent wheels. Property/link edits retain complete undo/redo.
- Belt visibility controls editing solids; native-reference previews retain them. Hiding any wheel hides the loop.
- Endpoints preserve original logic-node indexes; definition overrides cannot redefine their meaning. Projects/native files store links/wheel properties, not derived geometry/GPU objects. No schema change.
- Caps: 64 tangent-search iterations and 16384 scene sections, both editor allocation limits rather than verified game maxima.

## Implementation and lifetimes

- `src/editor/belt-profiles.js`: four radii, ports, cross-section constants.
- `src/editor/belt-path.js`: pure-data networks/tangents/sampling without DOM/Three.js.
- `src/editor/belt-view.js`: closed BufferGeometry, normals/winding, texture loading.
- `src/main.js`: incremental view cache, tools, localized diagnostics, lazy texture. Application owns the shared texture; rebuild/delete disposes per-belt geometry/material without destroying it. Render-context teardown handles page-end recovery.
- `tests/belts.test.js`, `tests/belt-fixtures.js`: radii/ports, real circuit, reversal/mirroring/rotation, dimensions/winding/UVs, invalid networks, caps, native read-back, history, texture pixels.
- `tests/browser/editor.spec.js`: real six-wheel import, reverse/move refresh, undo/redo, visibility/reference preview, export/reimport, tool creation, localized diagnostics.

Real circuit: `27 → 30 → 14 → 29 → 31 → 28 → 27`; 14 is the engine wheel, 31 reversed idler. Current output: 60 sections, perimeter approximately 1.8470701731 world units. Tests read-only extract those six wheels/edges without altering the sample.

Reproduction from repository root:

```powershell
node scripts/check-belt-evidence.mjs <game.gcl> <Anymaker/rom>
node scripts/build-belt-texture.mjs <Anymaker/rom>
npm run check:assets
npm run check
npm run test:browser:editor
```

## Unverified scope

This is a static building-pose belt. Runtime speed, moving texture phase, dynamic engine/wheel rotation, tension, and dynamics are unimplemented. Game shaders, matched-camera visuals, and exported-file game loading remain unaccepted. Geometry/texture fingerprints and passing tests are not game compatibility or overall visual parity.

## Actual historical validation (2026-09-28)

- Belt unit tests 8/8 passed, including original RGBA pixel hash. Evidence check matched nine functions, ten constants, four definitions, texture, real-save fingerprint.
- Three belt browser workflows passed; six-wheel frontal/angled and mixed-radius screenshots were viewed. First complete editor run: 71/72, failing subgrid-name undo. An isolated rerun with the three belt cases passed 4/4. Initial failure retained, no assertions removed/skipped.
- Asset checks passed: 800 references, 868 Mesh entries, one existing opaque variant, and new PNG dimensions/size/hash.
- First full unit run passed 199/199. Other plate-construction work changed concurrently; final `npm run check` was 196/199, all three failures in `plateSurfaceBoundary`. This task did not change/revert that parallel code. Belt-specific rerun passed 8/8.
- Separate `npm run build` then succeeded to `docs/`, restoring relative base. No `test-vehicle/` or local game files changed.
