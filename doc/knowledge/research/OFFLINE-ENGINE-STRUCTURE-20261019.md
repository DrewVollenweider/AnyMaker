# Engine, edge, and plate implementation follow-up

Date: 2026-10-19, America/New_York. The user requested broader systems coverage, specifically engines, edges, and plates. This continues the offline investigation using the actual code and existing structural/engine research. No game session or creation edit was required.

## Version and coverage

Build 25904830; `bin/game.gcl`, 82,528,301 bytes; SHA-256 `626a994be960b7218409d9ca416d2664450231d1fc3295036fc77c81b8449355`. The installed file was rechecked and still matched the analysis snapshot. Decimal offsets below apply to this exact file.

Two bounded exports added **27 functions**, with **11,186 instructions / 68,043 instruction bytes** checked against the source. The combined reader now holds 92 functions, 25,041 instructions / 145,322 instruction bytes, 1,203 local slot-derived call dependencies and 935 unresolved indirect call sites. These are selected exports, not 92 fully understood functions or a resolved runtime call graph.

[Evidence](versions/build-25904830/offline-engine-structure-20261019/evidence.json) contains 27 function identities, 24 typed constants, 14 strings, and 15 call-instruction examples. The independent checker successfully re-parsed identities and verified selected bytes. [Verification](versions/build-25904830/offline-engine-structure-20261019/verification.json) records the checks. Full native C/assembly/p-code and databases remain local.

## Combustion engine: gates, controls, and damage

Scope: `server_scene.vehicle_component.engine`, including its create, parse, manifold registration, data binding, tooltip, and tick paths. This does not establish the behavior of jet, steam, or other engine classes.

| Function | Offset | Reviewed role |
| --- | --- | --- |
| `engine.tick` | 54501350 | Speed coupling, manifold inputs, fuel/air use, combustion, temperature, lubricant aging, damage stages and drive feedback |
| `engine.create` | 54469900 | Creates the lubricant and coolant volumes |
| `engine.parse_save_data` | 54476812 | Binds saved speed, temperature, damage, damage factor and fluid contents |
| `engine.add_mating_component` | 54454733 | Registers gearboxes/wheels/manifolds/data port; connects oil manifolds to one lubricant volume and coolant manifolds to one coolant volume |
| `engine.get_data_f64` / `build_tooltip_data` | 54471463 / 54461074 | Establish channel fields and distinguish raw values from displayed rates/power |

Static findings from the reviewed tick:

- Fuel demand is set to zero when the cached engine speed is **below 6 RPS** or **above 8,000 / 60 RPS** (approximately 133.333 RPS). Equality at either threshold passes these speed gates. Other prerequisites still apply. This is a fuel cutoff path, not a hard mechanical speed clamp or proof of successful ignition exactly at 6 RPS.
- Gearbox and engine-wheel shaft speeds participate in a signed, mass-weighted coupling. Starter pulley speed is therefore not automatically the engine's speed. This supports the earlier successful starter investigation without replacing its user-run evidence.
- Each intake-manifold mechanical input is combined with the current throttle using `max`, then clamped to [0,1]. Multiple throttle inputs do not average down: the largest positive request wins in this path.
- Intake pressure is averaged across intake manifolds, clamped to native values [1,10], then remapped to a factor [1,2]. Exhaust reduction is full below native pressure 4, falls across 4..20, and reaches zero at 20. These are native pressure quantities; this report does not assign new SI pressure conversions.
- Fuel consumption and available-air factors participate in computed combustion energy. Saved damage stage **1** multiplies that energy by **0.5**; stage **2** sets it to zero. The fuel/air consumption operations precede this damage adjustment, so a damaged engine's fuel use is not by itself proof of useful output.
- Oil aging transfers quantity from lubricant species entry 2 to entry 3, with coefficient **0.00001** times a clamped speed fraction based on 8,000 RPM. This transfer preserves the lubricant total while changing its composition. Keep species-name recovery separate from these verified numeric indices.
- The lubrication damage term uses `clamp(2 * remaining_entry_2 / lubricant_capacity, 0, 1)`, then accumulates a deficit term proportional to speed and **0.0001**. Quantity and quality both matter; this is not simply a test for an empty reservoir. For ordinary positive-capacity states, at least half-capacity in entry 2 makes this particular deficit term zero.
- Engine, coolant and lubricant temperatures are blended using the quantities/engine thermal term in the reviewed tick, followed by an ambient-temperature blend. A temperature strictly above **160 C** increments the damage accumulator. These paths do not establish a complete radiator, heat-transfer, or endurance model.

The code increments damage stages through its accumulator/event path and separately handles repair requests. Damage also triggers small fluid-removal operations. Structural damage and engine wear are different investigations; do not infer edge-breaking forces from these engine thresholds.

### Raw channels versus dashboard values

The native getter binds these exact names:

| Channel | Component offset | Interpretation boundary |
| --- | --- | --- |
| `rps` | +0x590 | Cached engine speed |
| `throttle` | +0x5c0 | Combined/clamped intake request |
| `temperature` | +0x598 | Engine temperature |
| `fuel_flow` | +0x5e8 | Quantity consumed in this update; tooltip multiplies by server tick rate before flow formatting |
| `air_flow` | +0x5d0 | Intake quantity for this update; tooltip likewise multiplies by tick rate |
| `torque` | +0x600 | Field assigned computed combustion energy in the tick; tooltip multiplies it by tick rate and uses power formatting |

The `torque` channel name is not sufficient evidence that its raw unit is N m. The same applies to assuming that the two raw flow channels already equal the dashboard's per-second values. Any future controller or telemetry tool must preserve these conversions and verify the actual update cadence rather than hardcoding a guessed tick rate.

## Edges and rigid structural attachment

Current-build exports confirm the earlier [structural-island research](../../16_NATIVE_ISLANDS.md):

- `vehicle._flood_islands` for an edge at 52539235 follows other edges registered at both endpoint nodes, registered plates, and attached components. A crossing or coordinate overlap alone is not a substitute for those references.
- The plate overload at 52543833 follows actual boundary-edge references and attached components. It does not weld every edge that happens to share any corner coordinate.
- The component overload and island rebuild paths traverse registered component/edge/plate relationships. Signal connections and mounting-grid count do not directly define rigid-body count.
- `vehicle_component.create_island_links` at 54223153 first calls the attachment tester, then records reciprocal component/edge, component/plate and component/component links for returned hits. An unmounted control can remain electrically connected while belonging to a separate structural island.
- Edge and plate link-creation paths at 58207708 and 59065172 register adjacency and query nearby components to refresh their attachment links. These broad spatial queries are candidate collection, not proof that every nearby component attaches.

This is useful for future generation/auditing: validate the saved reference graph and successful attachment conditions separately from pipe/wire/control connectivity. Existing cardinal mounting audits remain conservative approximations; these exports do not make them a complete destruction or inclined-contact solver. The historical beamless-node crash remains version-labeled in the earlier report; this checkpoint did not re-prove that old crash at the current split implementation.

## Plates: facing, support offset, and thickness

The server attachment tester `vehicle_util.test_component_attaches_to_vehicle<server_scene>` at 65662243 has separate component, edge and plate paths. In the reviewed base-grid plate branch, it requires the component surface direction and plate-facing vector to be opposite, checks the surface's distance from the plate's frame plane/size, then tests projected rectangle/triangle overlap. Inclined/equivalent-grid handling has a separate transform path and is not covered by a universal cardinal rule here.

Consequently, a component overlapping the visible back of a plate need not be attached. Normal/facing metadata is functional, in addition to affecting appearance. A generator must keep node order, normal/facing and surface placement coherent; moving rendered vertices alone does not prove an attachment.

Exact static geometry findings:

| Quantity | Value | Evidence |
| --- | --- | --- |
| Native grid unit | **0.08 m** | `G_VEHICLE_GRID_SIZE.$ctor`, 271602 |
| Plate thickness | **0.01 m** | `G_VEHICLE_PLATE_THICKNESS.$ctor`, 275805 |
| Ordinary cardinal support offset | **0.04 m** from frame/node plane | Grid * 0.5 * multiplier 1 in `get_plate_node_surface_offset`, 63455641 |
| Support offset for size selector 1 | **0.12 m** for cardinal normals | Same helper uses multiplier 3 for this selector |

Support offset and plate thickness are separate terms. `add_static_geometry` at 63375987 obtains the support offset, computes an opposite-normal thickness displacement, dispatches solid/window/opening/hatch inner geometry, then adds outer geometry. A panel is not simply a zero-thickness polygon centered on its nodes.

For normals with two nonzero axes, the support helper selects the two best-aligned cube corners and uses their midpoint; with three, it uses the best-aligned corner. For cardinal normals it uses half the grid along the normal. This is consistent with placing the surface on the frame's supported side. Full outer strips, every slope, all pane states, and collision geometry remain separate work.

The type-only `get_is_physics_plate` at 63404453 rejects plate type **2**, which the geometry dispatch identifies as Opening. The glass-state overload has an additional exclusion. This classifier alone is not proof of player passage, complete window collision, or water sealing; the existing [Opening/Hatch investigation](SEALING.md) covers the separate buoyancy path.

Practical deduction for cabin walls: one 8 cm node/frame move does not directly describe the visible gap between skins. Compute each face's support offset, normal and thickness, then verify its attachment side. This gives a better basis for wall cavities and hidden wiring than comparing node coordinates alone. No existing cabin was changed in this investigation.

## Checks and next targets

Every new exported instruction was checked against the original bounded record and paired assembly by the reader; the selected evidence checker also passed. No research implementation changed, so the previously passing 51-test tool/model suite was not repeated as a new result. This checkpoint's new checks are source-byte audits, selected evidence, and documentation validation. No frontend acceptance or gameplay test is claimed.

Next targets: the full vehicle collision-shape builder and player collision; plate creation/facing serialization and all edge widths/slopes; structural strength/destruction thresholds; complete engine fuel/thermal calibration and other engine classes. Reuse the reader and existing mounting/geometry tools before writing new approximations. Continue offline without requiring user-run game tests.
