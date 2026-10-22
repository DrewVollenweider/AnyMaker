# Anymaker engineering knowledge — start here

Installed build is now [26113663](research/BUILD-TRANSITION-20261022.md). The hull findings below target archived 25904830; new-build mechanics transfer is unproven. Latest vehicle checkpoint: [hull construction and linked native ranges](research/HULL-BUILDING-20261022.md). Traced seed tolerances, planar/3D paths and face references; added metadata-based export grouping to avoid prefix-only evidence. The full research suite passes 267 tests. Complete hull/margin equivalence and creation mass reconstruction remain unfinished.

Latest vehicle checkpoint: [plate placement, perimeter strips and native angles](research/PLATE-PLACEMENT-20261021.md). Client/server placement adds boundary, turn-consistency, window/opening and same-facing shared-edge checks. Native vec3 angle projection/sign/fallback and 1 cm frame/4 cm inset now have selected evidence. Eleven new model tests; full suite 204. Complete validity/authority and native physics remain open.

Latest vehicle checkpoint: [plate surfaces, clipping and collision inputs](research/PLATE-SURFACES-20261021.md). Visible solid faces use opposed triangle fans; server physics plates supply offset point clouds to a native convex-hull builder. Clipping preserves parallel coordinates. New pure geometry helpers have 12 tests; full suite 193. Complete hull/placement/strip contracts remain open.

Latest vehicle checkpoint: [plate creation, native reconstruction and mesh replacement](research/PLATE-LOAD-20261021.md). Ordered boundary loops determine facing and first-edge size; loading remaps plate IDs and rebuilds plates, while client mesh replacement has separate lifecycle flags. The new read-only plate audit has 10 tests; full suite 181. Historical helicopter phantom geometry remains unresolved.

Latest vehicle research: [attachment surfaces and contact boundaries](research/VEHICLE-ATTACHMENTS-20261021.md). Surface extension, component/beam/plate gates and integer versus floating-point intersection behavior now have source evidence and a reusable offline model. All 171 research-tool tests pass; complete native mounting/save acceptance remains open.

Vehicle engineering is the active research priority as of October 21: [structural connectivity, splitting and update lifecycle](research/VEHICLE-STRUCTURE-20261021.md). Continue attachment, plates/edges and save integrity, followed by powertrain, fluids, electrical, controls, suspension, flight and marine systems. Projectiles, explosions and AI are low priority. The full audit remains incomplete.

Newest research: [character combat, weapon entry points, smoke and hordes](research/COMBAT-SMOKE-HORDES-20261020.md). Traced hotbar-order equipment choice, NPC reload/battery behavior, smoke drift/lifetime and its unbounded forward-ray sight check, plus the separate horde producer. Complete concrete weapons/brains/projectiles remain open. Reader: 1,275 functions; latest tool suite: 159 passing tests.

Newest research: [creatures, sensing and ambient spawning](research/CREATURES-SENSING-SPAWN-20261020.md). All 40 creature definitions have selected factory/default records. Sensing, sight, spawn pools and placement/despawn gates are traced; complete brains/combat/navigation remain open. Reader: 1,228 functions; all 159 research tests pass.

Newest research: [survival, clothing, damage and scene scheduling](research/SURVIVAL-SCHEDULE-20261020.md). New findings distinguish authority/eligibility gates, 61-call condition cadence, 50% vital warnings, full-precision internal reserves, stamina edges and separate rain/wind protection. Reader: 1,191 functions; all 151 research tests pass. Full-game review remains incomplete.

Newest research: [sensor readings and data-network discovery](research/SENSORS-DATA-20261020.md). This traces mounted sensor axes, raw per-update acceleration, gyro/compass behavior, pressure conversion, data discovery and pointer-backed script bindings. Reader: 1,129 functions; research suite: 143 tests. Full-game semantic review remains incomplete.

Newest research: [hinges, mounts, latches, rails, tow links and winches](research/JOINTS-WINCHES-20261020.md). Findings include per-body-pair hinge suppression, distinct release thresholds, ballscrew list-order effects, point-constraint ownership and winch length/stretch gates. The reader has 1,110 functions; all 143 research tests pass. Whole-game semantic review remains incomplete.

Newest research: [hydraulic cylinders, tracks and native raycast ordering](research/ACTUATORS-TRACKS-RAYCAST-20261020.md). This traces two-chamber extension bounds, size-dependent capacity/geometry, body-pair constraint cleanup, separate roller contact and native hit sorting. The current reader has 1,093 functions; 135 research-tool tests pass. Whole-game semantic review remains incomplete.

Previous continuation: [wheel contact, gas/thermal behavior and native helpers](research/CONTACT-FLUIDS-NATIVE-20261020.md), including pressure-released truck brakes, tyre calibration, gas-temperature overload differences and exchanger/world sampling.

Whole-game research started October 18: [versioned research hub](research/README.md), [coverage and gaps](research/COVERAGE.md), [Opening/Hatch implementation trace](research/SEALING.md), and [restart instructions](research/HANDOFF.md). This extends the historical engineering archive below; whole-game understanding and runtime verification remain incomplete.

Latest October 20 findings: [torque, electric machines, jets and helicopter rotors](research/POWERTRAIN-20261020.md). The reader now contains 611 selected functions, including every declared component update implementation. Selected traces cover shared shaft brakes, ratio-dependent load, motor demand, alternator efficiency, jet-chain validation, swashplate mixing and rotor/ground-effect arithmetic. Full-system behavior remains under investigation.

Earlier October 20 foundation: [component construction, reflection and geometry](research/COMPONENTS-TYPES-20261020.md) adds the complete declared 8,084-entry type table, inherited component declarations, core native defaults, interface directions/indexes and current geometry helpers. That reader contained 394 functions.

October 19 scope expanded to **all systems and past research**: [full audit register](research/AUDIT-REGISTER.md) and [findings including the October 17-18 truck/helicopter records](research/FULL-AUDIT-20261019.md). That checkpoint's reader contained 153 functions. Indexed scope remains separate from actual understanding. The rejected helicopter inset stays rejected; later static checks are not successful gameplay tests.

Updated 16 October 2026. This is the accumulated project knowledge from **11–16 October**, including the pedestal petrol engine, **compact inline-four / CPE1Running**, giant-engine circulation and working test vehicle. It complements the existing browser-builder documentation.

Read [current verified facts](CURRENT-FACTS.md) first, then [compact I4 and pedestal engines](COMPACT-I4.md), [giant engine and vehicle](GIANT-VEHICLE.md), and [native files and research methods](NATIVE-AND-RESEARCH.md). [Experiments and corrections](EXPERIMENTS.md) distinguishes successful results from superseded attempts. [Tools and archive map](TOOLS.md) gives working paths and commands.

For a future assistant: use this hub as the handoff, inspect the current creation and actual component definitions, and preserve the accepted assemblies. These documents are an evidence-backed knowledge archive, not a claim that every game system or browser export has been validated.

## Accepted reference files

| Reference | Native files | Acceptance |
| --- | --- | --- |
| Pedestal I4 | [fresh .data](archive/toolset/output/pedestal-engine-test-01/Petrol_Pedestal_Test_01.data), [fresh .meta](archive/toolset/output/pedestal-engine-test-01/Petrol_Pedestal_Test_01.meta), [running save](archive/toolset/output/pedestal-engine-test-01/running-result/running.data) | User loaded and ran it on Oct 14. |
| Compact I4 | [fresh .data](archive/toolset/output/compact-petrol-engine-01-complete/Compact_Petrol_Engine_01.data), [fresh .meta](archive/toolset/output/compact-petrol-engine-01-complete/Compact_Petrol_Engine_01.meta) | Same 60-part assembly subsequently accepted as CPE1Running. |
| CPE1Running | [running .data](archive/toolset/output/compact-petrol-engine-01-complete/running-result/CPE1Running.data), [running .meta](archive/toolset/output/compact-petrol-engine-01-complete/running-result/CPE1Running.meta), [preview](archive/toolset/output/compact-petrol-engine-01-complete/running-result/CPE1Running.png) | User-tested running compact I4; 8,111 RPM snapshot. |
| Giant test vehicle | [clean .data](archive/toolset/output/shift-repair/20261016-100456/Giant_Engine_Test_Vehicle_01.data), [clean .meta](archive/toolset/output/shift-repair/20261016-100456/Giant_Engine_Test_Vehicle_01.meta), [controls](archive/toolset/output/shift-repair/20261016-100456/CONTROL-GUIDE.md) | User confirmed shifting, indication and movement. Clean export removes three temporary diagnostic ports; the successful diagnostic operating save is also preserved. |

These are selected reference fixtures, not a bulk export directory. Paired files should retain matching names; the running files contain saved operating state. Prefer the fresh compact creation for a new test and retain CPE1Running for comparison.

## History and evidence

- [Oct 11 exploration](archive/exploration/report.md), [manual/component knowledge](archive/exploration/game-knowledge.md), [live interaction experiments](archive/toolset/LIVE-VALIDATION.md), [decompilation methodology](archive/toolset/DECOMPILATION.md).
- [Oct 14 version refresh](archive/exploration/research-20261014.md), [pedestal live result](archive/toolset/output/pedestal-engine-test-01/LIVE-RESULT.md), [compact live result](archive/toolset/output/compact-petrol-engine-01-complete/LIVE-RESULT.md).
- [Oct 15 circulation trace and successful follow-up](archive/toolset/output/giant-engine-circulation-03/LIVE-RESULT.md), [Oct 16 final acceptance report](archive/toolset/output/shift-repair/20261016-100456/report.json).
- [Original Oct 11 repository research](../19_EXPERIMENTS_2026-10-11.md) and [delivery standard](../18_BUILD_ASSURANCE.md) remain available.
- [Archive manifest](MANIFEST.json) records source and uploaded hashes. Personal machine paths are generalized; executable/binary dumps, account/world snapshots and downloaded runtimes are omitted. Knowledge from those experiments is preserved in notes and selected evidence summaries.

Historical documents retain their original sequence. Later successful test sections and CURRENT-FACTS.md supersede earlier pending statuses and failed assumptions. The archive does not certify long-duration cooling, handling, endurance, every component family, or general browser-editor export compatibility.
