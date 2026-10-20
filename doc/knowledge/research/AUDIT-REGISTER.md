# Full-game audit register

Scope expanded on 2026-10-19: research every game system and revisit earlier work. This register is a work queue, not a completion certificate. Research stays offline; no new gameplay test is required from the user. Build 25904830 and source hashes remain mandatory boundaries.

Start with the [latest findings](FULL-AUDIT-20261019.md), [scope accounting](versions/build-25904830/full-audit-20261019/scope-summary.json), and [every component class group](versions/build-25904830/full-audit-20261019/component-audit.json). Full local method indexes retain all 37,082 indexed functions, including 15,049 unclassified name leads. Names and export counts cannot establish implementation behavior.

## Required review for every component and mechanic

1. Bind shipped definitions and variants to actual implementations, including inherited/generic implementations. A matching class name is only a candidate.
2. Read creation and parse/save paths for explicit and omitted defaults; retain unknown fields and version boundaries.
3. Trace mounting, grids, bodies, moving joints, compatible interfaces, gender, ordinals, placement and facing separately from network connections.
4. Establish inputs, outputs, units, limits, hysteresis, state transitions, update order and dependencies.
5. Follow power loss, empty supplies, damage, repair, disconnected conditions, serialization and recovery.
6. Separate render geometry, collision, structural connectivity and buoyancy. Record counterexamples and incomplete paths.
7. Reconcile older claims with matching-build evidence. Preserve user observations at their actual scope; never convert an old successful snapshot into endurance proof.

All 207 named component classes and the omitted-class group remain individually reviewable. The public component audit deliberately leaves semantic status pending even when selected methods were exported. Counts do not silently promote a whole class to understood.

## Systems and dependencies

| Area | Current evidence | Required continuation |
| --- | --- | --- |
| Coordinates, nodes, edges, plates, grids and islands | Current 8 cm grid, support offsets, thickness, graph traversal and attachment tests; historical native tools | Full inclined/equivalent-grid cases, split/merge/weld scheduling, strength, destruction, topology mutation and graph rebuilding |
| Components, accessories and interfaces | All 598 definitions indexed; exact-owner name candidates for 203 classes; fitted-item oil filter and battery paths sampled | Resolve omitted/generic/inherited classes, every variant's parser defaults, interface compatibility and mounting/accessory behavior |
| Physics, collision, constraints and damage | Current vehicle compound-shape builder exported; selected actor impact arithmetic; historical constraint leads | Complete shapes/material flags, player capsule interaction, mass/inertia, constraints, friction, breakage, repair and collision scheduling |
| Combustion and drivetrain | Current engine gates/thermal/oil paths; gearboxes, discrete clutch and positive-only shift correction | Full torque solver, ratios and losses, loads, all engine sizes, wheels, hydraulic truck wheels, belts, tracks, differentials and brakes |
| Flight, jets, rotors and marine propulsion | Jet combustion/compressor exports; collective input, control-surface and propeller branches sampled | Complete jet assembly/start/thrust, rotor force/torque/axis behavior, swashplate, aerodynamic calibration and water/air transitions |
| Electrical generation and distribution | Ordered consumption, deferred source debit, relay hysteresis and battery accessory synchronization | Stable ordering after load/split, generators, storage/charging losses, redistribution, all loads, power-loss behavior and overload cases |
| Liquids, gases and heat | Pump sign, native capacities, direct conservation, liquid head, gas quantity/capacity pressure, filter and radiator branches | All species/units, gas conservation and thermal coupling, sources/sinks/leaks, valves, vents, manifolds, exchangers, compressibility and multiple-source constraints |
| Hatches, latches, doors and actuation | Current sealing evidence re-exported; hydraulic pressure-to-control hysteresis; historical mates | Initial/loaded seal state, scheduling, player passage, latches under motion, hydraulic cylinders, hinges, rails, ballscrews, tow links and winches |
| Controls, sensors, data and displays | Thresholded controls, gear indication, altitude transform, selected seat-input access and controller power | All sensor frames/units/timing, alias scope, native control combinations, network discovery, digital input origins, data transport and displays |
| Script language and microcontrollers | Current interpreter/loop paths, 256-per-loop cap, 10 W base demand and power gate | Complete grammar, expression round trips, types/conversions, binding, compiler restrictions, recursion/resource guards, debugging and persistence |
| Actors, survival, inventory, progression, combat and AI | Oxygen branch, impact helper, AI stuck predicate and actual server unlock path | Conditions/stamina, food/drink/medical effects, loot, unlock prerequisites/persistence, crafting existence, weapons/projectiles, AI sensing/navigation/combat and all creature variants |
| World, environment and generation | Full definition/file inventory; weather sampling and simulation branch | Seeds, terrain, tiles, roads/buildings/dungeons/bunkers, vegetation binary format, oceans, time, weather interactions, world persistence and spawning |
| Saves, creations, metadata and versions | Current vehicle and metadata parser exports; archived native files re-audited | Full creation/world schema, omitted fields, migration, IDs, object construction, cache invalidation, save/load ordering and corruption recovery |
| Multiplayer, authority and synchronization | Peer seat-input fields, server unlock messaging and replication leads | Ownership and validation, authority transfers, update order, loss/reconnect behavior, persistence, host/client differences and version handling |
| Rendering, assets, materials and animation | Existing Mesh/asset pipeline, current plate geometry and collision distinction | All asset variants/formats, dynamic assembly, texture/material semantics, animations, visibility, lighting, particles and performance |
| Input, audio, UI, localization and journal | Historical digital pedals; current seat getters; shipped audio/localization resources | Complete input mapping/device origin, bindings, spatial audio/event timing, UI states/settings, manuals/journal and translation completeness |
| Residual code and data | Every indexed function retained, with unmatched leads explicit | Classify remaining helpers/platform/library/generated code and unidentified data; never infer feature absence from a zero keyword count |

## Earlier work that must remain in scope

The following is a subject-level reconciliation queue. It does not replace the detailed source archives or claim that every sentence in them was re-proven.

| Earlier subject | Evidence retained / current recheck | Open boundary |
| --- | --- | --- |
| Native creation schemas and paired files | [Native data](../NATIVE-AND-RESEARCH.md); current vehicle/metadata parser exports | Complete load/write/cache behavior, unknown fields and migrations |
| Mesh extraction and material/asset publication | [Resource analysis](../../RESOURCE_ANALYSIS.md), [model import](../../07_MODEL_IMPORT.md) | Browser decoder support differs from native game behavior; all formats not decoded |
| Editor copy, mirror, split and merge | [Build operations](../../05_BUILD_OPERATIONS.md) | Editor operations are not proof of native weld/split physics or universal handedness mapping |
| Mechanical mates, hinges, latches, rails and tow | [Mechanical mates](../../10_MECHANICAL_MATES.md) | All orientations, moving-body behavior and loaded states |
| Hydraulic and pneumatic connections | [Hydraulics](../../11_HYDRAULIC_CONNECTIONS.md); new pressure/control traces | Port ordering, every size, native/display unit conversions and actual cylinder mechanics |
| Inclined grids and native transforms | [Inclined placement](../../12_INCLINED_PLACEMENT.md); current attachment branches | Full equivalence, contact, reflection and collision rules |
| Tracks and roller/sprocket assembly | [Tracks](../../13_TRACKS.md) | Full native dynamics, traction and exact runtime assembly |
| Belts, engine wheels and pulleys | [Belts](../../14_BELTS.md); accepted starter observations | Torque/slip/tension, winding, all pulley/engine-wheel variants and dynamic load |
| Plates and surface sides | [Plates](../../15_PLATES.md); current support/thickness and compound collision exports | All outer strips, slopes, glass states and contact tolerances |
| Native islands and component mounting | [Islands](../../16_NATIVE_ISLANDS.md); current reciprocal adjacency/flood traces | Old null-beam crash claim is historical until rechecked; frame-only groups omit component bridges |
| Pedestal combustion engine | [Experiment archive](../EXPERIMENTS.md); matching-build engine paths | Successful running observations cover that assembly and snapshot, not every engine |
| Compact I4 / CPE1Running | [Compact I4](../COMPACT-I4.md); archived running file re-audited | Historical 135.188 RPS is a saved observation; a current fuel gate is not a hard shaft clamp; endurance remains unknown |
| Giant engine starter and circulation | [Giant vehicle](../GIANT-VEHICLE.md); current speed gates/pump/manifold paths | Preserve layout-specific pump signs; full loaded thermal/torque behavior unfinished |
| Oil filter | Fitted-item/removal path newly traced | Condition depletion, replacement, species accounting and all bypass paths |
| Falling controls and physical mounting | [Current facts](../CURRENT-FACTS.md); current attachment predicates | Electrical/mechanical connections do not replace structural mounting; full inclined audit still incomplete |
| Pneumatic shift failure and correction | Current magnitude threshold, gas routing, pressure hysteresis and gear transitions | Full gas pressure conversion/vent timing, every gearbox variant and loaded shifting |
| Script type/error diagnostic | [Current facts](../CURRENT-FACTS.md); current loop and power traces | Preserve the failed inequality round trip as a specific case, not a ban on all inequality operators |
| Handbrake/no-drive and gear indication | User-confirmed release-to-drive; current display/clutch branches | No new driving test; eight forward ratios in a generated file are not eight-gear runtime acceptance |
| Long-hood hauler and eight-speed packaging | [Later creation records](FULL-AUDIT-20261019.md#later-creations-recovered-from-the-pc) | Refined cab is statically checked; actual seated visibility, lights and loaded driving remain unverified |
| Helicopter wall spacing, shell and dashboard | User-built geometry and later local reports recovered | A specific two-unit lining pattern is not a universal one-space rule |
| Phantom helicopter plates/edges and rollback | Rejected revision and exact restoration record preserved | Root cause remains unresolved; a passing schema/reference audit does not clear the corrupt revision |
| Pilot-shell mirroring and rear restoration | Recorded 13-panel shell mirror and removal of 45 assistant rear panels | Keep the requested rear design; revalidate new changes independently |
| Rear helicopter completion | Recorded 19 new mirrored panels with six shared center panels retained | Static topology checks are not a new successful game test |
| Hatch/opening water sealing | [Sealing](SEALING.md), all original selected functions integrated into current reader | Collision and water sealing are separate; complete initial-state/scheduling paths unfinished |
| Electrical, liquid and script follow-ups | [Systems report](OFFLINE-SYSTEMS-20261019.md) and original evidence | Complete solver/compiler edge cases remain queued |

## Continuation protocol

Select a bounded coherent dependency chain from the register, search the complete local indexes, reuse already exported methods, and export only missing methods to a new output directory. Read callers, defaults, units and failure paths together. Add claims with exact source identities and explicit limits; update this register and class-level findings only after semantic review.

Refresh the source identity before each new research session. If it changes, create a new baseline and compare definitions/functions; never reuse old offsets blindly. Full local decompilations and creation copies stay local. Publish English findings, tools and selected evidence on the dedicated research branch for mobile/cloud use.
