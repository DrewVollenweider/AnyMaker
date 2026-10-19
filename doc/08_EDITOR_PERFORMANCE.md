# Editing performance and render quality

This records implementation/automated checks, not hardware FPS guarantees from resource reuse. Main code: `src/editor/visual-cache.js`, `render-quality.js`, `render-quality-ui.js`, and `src/main.js` coordination.

## Editing

- Process only latest mouse/attached-preview sample each render frame. TransformControls still receives input directly; release synchronously flushes final transform, committing final state only. Skip unrelated hover rays during component drags, retain picking during camera interaction with current camera/mouse.
- Remove fixed 30 FPS drag cap; use configured global cap. Lower canvas resolution proportionally during interaction, restore afterward. Default to cached preinteraction shadows without changing light casting flags/recompiling shader variants.
- Compare normalized component data to reuse unchanged render objects. Linear-size edits instantiate changed components only. Prepare all replacements before swap; failure disposes new objects and preserves scene. Explicit local-Mesh reimport forces component rebuilding.
- Rebuild nodes/beams/plates/links only for changed entities/dependencies. New structure preserves unrelated geometry/material/objects; node dragging updates connected structures, path dragging changed links only.
- Same-cell beam previews retain geometry. Reapplying same depth layer no longer triggers material compilation. Cache component/plate bounds for rays.
- Beam placement sphere radius reduced 0.07 -> 0.035, halving diameter without changing snapping/beam rules. Cache real Mesh world bounds, cull misses, query nearest actual surface by distance; outlines do not collide. Nearby fallback shares cache, invalidated by edits/transforms/tool switches.
- Reuse node screen projections until camera/viewport/node changes. Avoid unchanged DOM text rewrites and repeated traversal/temporary allocations/layout.
- Camera inertia requests preview refresh only without pending mouse input, never overwriting fresh coordinates. Record raw mouse positions immediately, including during orbit; synchronize camera matrix before picking to avoid old-view cursor positions. Inertia stays enabled.
- Skip grid/axis-indicator updates when camera unchanged. Disabled beam labels create no DOM; enabled labels reuse/project/style only when needed.

## Editor settings -> render quality

Persist `renderQuality` in existing path-isolated localStorage v1, never project/schema. Missing/invalid values use:

| Parameter | Range/options | Default/effect |
| --- | --- | --- |
| Preset | Performance/Balanced/High/Custom | Balanced; changed details identify Custom |
| Render scale | 50%–150% | 100%; canvas pixels |
| Pixel ratio cap | 1–3 | 1.5, capped by device ratio |
| Interaction scale | 35%–100% | 75% of normal resolution while dragging/camera interaction |
| Frame cap | 30/60/120/display | 60 FPS cap, not guarantee |
| Multisample antialias | On/off | On; WebGL initialization, reload required; prompt to save |
| Shadows | On/off | On |
| Shadow map | 512/1024/2048/4096 | 1024, GPU-limited; dispose old map on size change |
| Shadow filter | Basic/PCF/Soft PCF | Soft PCF; softness adjusts radius only under PCF |
| Shadow updates | Scene changes/every frame | Scene changes; committed edits/light settings refresh |
| Update during interaction | On/off | Off; reuse old shadows until release |
| Tone mapping | None/Linear/Reinhard/ACES Filmic | None; diagnostic-material display |
| Exposure | 0.1–3 | 1, active with tone mapping |
| Statistics | On/off | Off; frame interval/draw calls/triangles/effective ratio |

Except antialias, apply immediately. Restore current configured resolution after interaction without persisting temporary scale. Disable shadow details when off/exposure when no tone mapping.

## Evidence and limits

- Unit tests cover bounds/legacy settings, shadow freeze/restore, old-map disposal, coalescing/cancel, dependency invalidation, geometry reuse.
- 100 pending mouse samples cause one preview update; 50 identical beam previews never replace/dispose geometry. Deterministic workload checks, not hardware timing.
- Browser imports 60 shafts, edits one size, asserts other 59 Three.js UUIDs unchanged and undo/redo data correct.
- Real closed-loop plate creation/undo retains existing node/beam UUIDs.
- Actual move/rotate handle drags verify camera stays still, pixel ratio restores, components not rebuilt, one history record per drag.
- Settings browser tests cover localization/reload, actual renderer values, antialias context recreation, camera downsampling, static shadow cache, using Three.js devtools events without exposing application test-control APIs.
- Chromium/SwiftShader establishes automated behavior/reuse only. Real GPU P95 input latency/frame time, complex native scenes, cross-browser experience, game visual parity need separate measurement.

Normally run `npm run check`, then affected editor/preferences suites. Preserve uncommitted `docs/` using `--outDir dist` with matching preview output and `/anymaker-builder/` base.

### Actual historical checks

- `npm test`: 130 passed.
- Editor/preferences Playwright: 51 passed with temporary inherited config changing only output/preview to dist; Chromium/SwiftShader/one worker/1500×960/Pages subpath unchanged.
- Service build `npm run build -- --outDir dist --base=/anymaker-builder/` succeeded.
- Quality-panel screenshot inspected; controls/localization/reload/interaction resolution browser-checked.
- Initial regression calibrated old tests: native X reflection, new grids/projectName, refresh fixtures must not clear settings on every navigation. Linear-size test follows base-size display/ext-as-increment. Precise assertions retained plus settings-exclusion check; no skipped failures or coordinate/schema changes to satisfy tests.
- No asset regeneration/game loading/real-GPU FPS/P95 measurements.

### Beam placement sphere regressions

- 133 unit tests passed, adding cache invalidation, nearest solids, rotation/size, rays inside bounds, nearby snapping, projection reuse.
- Deterministic 100-model/50-pointer case computes each bound once and performs 50 actual Mesh raycasts, excluding outlines.
- Browser with 60 shafts verifies radius 0.035 and reused geometry as position changes. Warm empty-region movement causes no bound recalculation/distant Mesh raycasts/repeated status text. Beam creation/undo works.
- Editor 46 cases: first 45 passed, one `download.createReadStream: canceled`. Isolated rerun passed without app/assertion changes; first failure `tmp/beam-hover-first-run.txt` retained.
- dist service build succeeded; no docs/assets regeneration or GPU FPS measurement.

### Cursor after orbit

- Real right-button orbit then mouse movement during inertia reproduced cursor drift before fix. Input-overwrite fix alone left one-frame camera lag; matrix synchronization resolved it.
- Per-frame exact cell checks cover stationary mouse after release and immediately continued movement. Neither inertia disablement nor relaxed assertions hid errors.
- 134 unit tests, 47 editor cases, dist build passed. Before/after failures retained in `tmp/orbit-cursor-before`, `tmp/orbit-cursor-after`; final `tmp/orbit-cursor-regression`.
- Checks timing/position consistency, not GPU FPS/P95.

### Placement collision and snapping

- Keep nearest-real-triangle -> nearby-bounds -> Y=0 plane ordering. Fallback uses each Mesh local bounds/transform, not gaps between parts or empty corners of rotated world boxes. Cache inverse/normal matrices with bounds; invalidate together on edits.
- Honor ray near/far/layers. Starting inside bounds must not flip far exit into mouse-facing contact. Inclined lattice searches preserve outside-surface condition, reuse vectors, stabilize near-equal rounding candidates.
- Existing-node beam/node placement first validates integer cells, then tests occlusion along node projection. Perspective/orthographic exclude blocked nodes; hidden helpers do not invalidate unobstructed logical endpoints. Stop at camera-facing node-cube surface to avoid self-occlusion; cube size follows visible one-/three-cell beams.
- Exclude beams/plates containing that node so oblique beam sides/offset plate faces do not obscure their own endpoints. Unrelated solids still occlude; helper visibility/history do not change this.
- Rotating/mirroring pending components refreshes preview immediately using new bounds. Save click ray, recheck actual bounds after asynchronous creation. If mouse leaves while loading, preview stays hidden until return at current position.
- Unit coverage: gaps, rotated/nonuniform scale, ray ranges/layers, far exits, perspective/orthographic occlusion, inclined rounding. Browser uses real published assets to check changed-view node access, rotated preview/save agreement, delayed loading/leave/return.
- Nearby fallback remains per-Mesh box approximation, not exact arbitrary cavities, full assembly interference, or interface mating. No hardware latency claim.

Actual checks:

- 143 unit tests, 51 editor cases, five targeted beam/plate/occlusion cases passed using existing browser settings.
- dist service build/`git diff --check` passed, no docs/assets overwritten.
- Initial self-occluding beam-end logic duplicated nodes. Corrected cube boundaries/owned-structure exclusions retained node-count/loop/undo assertions. Added one-/three-cell, oblique, unrelated-front-occluder units and real three-cell front/back browser tests.
- Initial four failures and later one oblique failure retained at `tmp/placement-snapping-regression`, `tmp/placement-snapping-final`; final success `tmp/placement-snapping-complete`. No GPU FPS/P95 measurement.

### Overlapping-beam click and automatic split occlusion

- Separate click-to-split entry used screen centerline priority, missing the node occlusion filter and selecting rear beams.
- Now visible existing nodes first, nearest real hit next to decide beam splitting. Only with no solid hit use original 24-pixel tolerance, rechecking split-point occlusion. Endpoint protection/integer splits retained.
- Alt split also obeys nearest solid; foreground plates block rear beams. Click-path cache reuse adds no per-frame split-candidate enumeration.
- Three new browser cases cover perspective/orthographic, front/back, rear-beam-first array order, hidden helpers, undo, normal/Alt plate occlusion, using exact IDs/counts/coordinates.
- 143 unit/54 editor cases and dist build passed with unchanged browser settings, no docs/assets regeneration.
- Before failure `tmp/overlapping-beams-before`; five targeted passes `tmp/overlapping-beams-after`; complete suite `tmp/overlapping-beams-regression`. Behavioral checks only, no hardware timing.

### Unified picking during camera orbit/pan

- Previous shared mouse-handler return paused all previews/highlights during camera motion; release cancelled queued final refresh. Now process latest sample once per frame, retain release refresh, and follow inertia without new events.
- Synchronize picking camera matrices and transform-handle orientation/world matrices before hover. Hover is not pointermove-only; pointerdown capture synchronizes view before TransformControls. Component drags still disable camera and commit once.
- Captured right-button movement can arrive outside canvas: clear previews/highlights, restore on reentry instead of showing stale off-canvas points.
- New browser checks compare actual tool rays/render camera every frame for all 13 tools, perspective/orthographic orbit, middle-pan, release inertia. Also extension/move/rotate/scale handle rays/axes. Beam cursor exactness includes held-right-button and captured leave/return.
- Handle pre-fix stale-origin evidence: `tmp/gizmo-orbit-before`; first three shared-picking checks `tmp/all-tools-orbit-after`; six handle targeted checks `tmp/all-tools-orbit-targeted`. 144 unit tests passed.
- Complete editor suite 57 passed in 2.7 minutes, `tmp/all-tools-orbit-regression`; dist service build and changed-file diff check passed, unchanged Chromium/SwiftShader/one-worker/Pages settings.
- This validates input/camera/ray/display timing, not real-GPU FPS, frame time, or P95 input latency.
