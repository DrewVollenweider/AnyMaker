# Component snapping on inclined plates

Reviewed 2026-09-28. This applies only to an inclined structural plate actually hit by the ray. Axial faces, beams, component Meshes, and curved surfaces retain existing placement logic.

## Game and dashboard evidence

Read-only inputs: `bin/game.gcl` and repository `test-vehicle/vehicle.data`. Fingerprints, selected functions, constants, and sample summaries are in the [evidence record](evidence/inclined-placement.json). Original game files, full decompilation, and temporary output stay outside Git.

Sample vehicle 553, `grids[1]`, is a dashboard mounting grid:

- `origin = [0, -90, 183]`, `dir = [0, 1, -2]`.
- Two `circular_dial_a` (180,181) and three `circular_dial_small_a` (217,218,219), all with integer local `pos`.
- First three column-major `rot` arrays: `[-1,0,0,0,1,0,0,0,-1]`; last two: `[0,0,1,0,1,0,-1,0,0]`.
- Supporting plates 45,46,52 have nodes satisfying `y - 2*z = -456`. Applying the game's origin normalization to any of these nodes produces that `origin`.

Inclination comes from grid `dir`, not fractional angles in local component `rot`. `state_add_component.tick` (`0x84880f`) calls `mat33_s32.rotation_angle_axis` with step constants `1` and `-1`, dispatching to integer `rotation_x_axis/y_axis/z_axis`. Placement network events also transmit `grid_origin_dir`, `vec3_s32`, `mat33_s32`. No arbitrary local-angle placement evidence was found in these paths, so local steps remain 90° without adding arbitrary-angle subpanels. Integer-axis rotation bodies remain undecoded; names/indirect references are not full implementation proof.

## Implemented coordinates

`src/native/grid-frame.js` shares transforms between import and new inclined mounting. In native cells:

1. Derive an integer plane normal from real nodes and reduce by greatest common divisor. Use click ray to choose front/back. Accept only coplanar inclined faces with integer nodes.
2. Use world Y as reference `up` (Z when normal parallels Y): `X = normalize(dir × up)`, `Y = normalize(dir)`, `Z = normalize(X × Y)`.
3. Following `get_consistent_grid_origin_and_dir`, separately reduce integer X/Z basis vectors and compute `origin = p - X * floor(dot(p,X)/dot(X,X)) - Z * floor(dot(p,Z)/dot(Z,Z))`. X/Z here are reduced integer axes. Negative values also use floor, never truncation; the first plate node is not necessarily the origin.
4. Effective mounting origin is `origin + 0.5 * sign(dir) + 0.5 * normalize(dir)`. Snap in-plane X/Z to local integer cells; determine local Y from occupancy and current local rotation.
5. Compose mounting frame and local rotation. Reflect X between editor/game with `S R S`. Final world coordinates may be fractional and must not be rounded again by world XYZ.

`src/editor/inclined-placement.js` handles rays, plates, and preview orientation. Commit recomputes using the saved click ray, preventing mouse movement during asynchronous resource loading from changing the result. Placement J/K/L rotate 90° around mounting-frame X/Y/Z.

## Project and native export

Project v1 adds optional `surfaceMount: { dir: [0,1,-2], position: [66,0,131] }`: native integer normal and mounting-grid integer coordinates. Object `position/rotation` remain world position/XYZ Euler radians. Validation, domain adapters, snapshots, copy, history, and JSON preserve it. Old projects without it need no migration; older editors may not preserve it.

Do not store an origin that can become stale. Export reconstructs integer `origin` from current world/local position, recovers integer local `rot`, and groups by `origin + dir` into native `grids[]` within one physical vehicle. Mounting grids are not independent physics bodies. Import restores mounting metadata. Whole-cell moves, centering, and copies retain fractional mounting offsets. Move controls round displacement, preserving fractional position remainder.

Native export rejects noninteger-cell displacement, rotations not representable as local 90° mounting rotations, and reflected geometry. Inclined placement with mirroring rejects before commit and requests disabling mirror. Generic rotation Inspector does not thereby gain arbitrary-angle native compatibility. Intermediate XML omits `surfaceMount` and remains a non-game debug format.

## Checks and limits

From repository root, with local game input:

```powershell
node scripts/check-inclined-placement-evidence.mjs <game.gcl>
npm run check
npm run test:browser:editor
```

- Evidence checking covers game version, nine function signatures/code hashes, two rotation constants, three dashboard plates, and coordinate/orientation round trips for five gauges, with unchanged source sample.
- `tests/inclined.test.js`, explicitly loaded by the unit entry point, covers canonical origin/negative floor, in-plane cells, local rotation, backside/three-axis slopes, ordinary-surface exclusions, format validation, move/copy, and dashboard sample.
- Browser tests cover actual hover/click, K rotation, preview/commit, Y dragging with fractional-position preservation, undo/redo, native download/reimport. Other editor workflows cover ordinary placement/related edits.

Actual historical results: evidence check passed; `npm run check` passed 171 unit tests and production build; editor browser suite passed 64 tests; `git diff --check` passed. Production `docs/` relative paths were restored. Full settings/recovery browser suites and asset regeneration were not run.

Unverified: game loading, all component occupancy/collision rules, arbitrary dynamic-subvehicle poses, and matched-camera visuals. Snapping does not reproduce all game placement-validity checks. Save/build success is not game acceptance.
