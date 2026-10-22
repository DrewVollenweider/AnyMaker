# Whole-game research

Latest current-build checkpoint: [placement checks and differential clarification](PLACEMENT-20261022.md). Ordinary placement requires attachment and no overlap; diagnostics do not waive attachment. Different mounting grids use separate geometric paths. Shipped differential descriptions confirm coupled side outputs with mechanical disconnection and an optional rear pass-through. Reader: 196 methods / 44,180 checked instructions / 257,171 bytes. Of 17 new exports, 10 have full-body reviews, three partial and four pending. Latest executable-tool suite remains 327 passing tests, without a rerun for this documentation-only checkpoint. Full audit incomplete; vehicle systems first.

Latest current-build vehicle checkpoint: [functional mating and drivetrain variants](MATING-DRIVE-20261022.md). Fresh traces separate functional interface/gender/containment rules from structural support, and establish two local battery-face mating candidates without certifying full placement. Motor target/power rules, thresholded clutch switching, fixed-ratio settings and gearbox C inheritance are reviewed. The differential field named locked disconnects two internal links in the reviewed branch; conventional lock behavior remains unverified. Current reader 179 methods / 36,031 checked instructions / 207,688 bytes; 39 new full-body reviews. Ten new tests bring the suite to 327 passing tests, including 2,304 independent interface-pair checks and 300 geometry invariance cases. Full audit incomplete; vehicles first.

Latest current-build vehicle checkpoint: [electrical storage, mechanical routing and controller power](ELECTRIC-CONTROLS-20261022.md). Fresh traces cover sequential allocation, deferred debit, producer sharing, terminal registration, relay hysteresis and script power gates. Distinct-store sharing conserves energy in the bounded model; repeated-reference counterexamples prevent a general conservation claim. Battery share defaults to 0.001; alternator share is 1 and generation efficiency is separately 0.75. Mechanical routing retains raw signs and discards multiply paired terminal routes. Current reader 140 methods / 29,559 checked instructions / 172,331 bytes; 45 new exports and two formerly pending full-body reviews. Fifteen new tests bring the suite to 317 passing tests, including 500 seeded distinct-store cases. Full audit incomplete; vehicles first.

Latest current-build vehicle checkpoint: [liquid networks, scheduling and pump settings](LIQUID-NETWORK-20261022.md). Connection building precedes component ticks; direct port pairing, saved links and internal flooding have distinct paths. A bounded multi-source model can exceed destination capacity while conserving contents; shared-content aliases and group revisit cadence remain open. Pump flow_factor defaults to 100%, with ten-percentage-point UI steps. Current reader 95 methods / 23,570 checked instructions / 141,171 bytes; 24 new full-body reviews and two pending. Eight new model tests bring the suite to 302 passing tests, including 300 seeded conservation cases. Full audit incomplete; vehicle systems first.

Latest current-build vehicle research: [engines, supply paths and gearboxes](ENGINE-SUPPLY-20261022.md). Fuel and intake gas are drawn independently; air starvation can reduce calculated output while fuel is still consumed. Fresh traces cover manifold suction/shared oil and coolant storage, filter disposal, pump candidate versus actual flow, fan activation and both gearbox shift interfaces. New engine_demand.py has nine tests including 500 stock/energy cases; full suite 294 passing tests. Current reader 69 methods / 16,045 checked instructions / 97,326 bytes. Full audit active and incomplete; vehicle systems first.

Latest current-build vehicle research: [contact, suspension and belt recognition](CONTACT-TRACKS-20261022.md). Integral tread avoids bare-wheel reductions; all six suspension roller travels are calibrated. Moving-support contact/tether arithmetic and pressure-released wheel brakes have fresh traces. Belt recognition includes a two-entry dead-end exception and can depend on starting endpoint; true does not certify physical closure. New belt_topology.py and eight tests include 384 independent graph comparisons. Full suite 285 passing tests; current reader 37 methods / 10,548 instructions / 64,882 bytes. Full audit active and incomplete; vehicle systems remain first.

Current vehicle checkpoint: [build 26113663 vehicle systems](VEHICLE-UPDATE-20261022.md). Fresh reflection and selected exports show shared wheel rotation-lock gates and roller inheritance; engine/gearbox update methods pass scoped archived-instruction/direct-read/reference comparisons. The comparison covers 1,543 archived entries; 1,464 local matches do not prove complete semantic transfer. Current reader: 12 methods / 8,099 checked instructions / 51,029 bytes. All 277 research-tool tests pass. Full audit active and incomplete; vehicle systems first, combat/projectiles/explosions/AI parked. Earlier checkpoints below retain their own archived-build limits.

Installed build is now [26113663](BUILD-TRANSITION-20261022.md). The hull findings below target archived 25904830; new-build mechanics transfer is unproven. Latest vehicle research: [hull construction, face references and native range grouping](HULL-BUILDING-20261022.md). New hull_geometry.py 1.0.0, native_unwind.py 1.0.0, native_export.py 1.2.0 and polyhedral_mass.py 1.1.0. All 267 tests pass. Reader remains 1,543 functions / 233,869 instructions / 1,329,154 bytes. Full audit active and incomplete; vehicle engineering first.

Latest vehicle research: [plate placement, perimeter strips and native angles](PLATE-PLACEMENT-20261021.md). Traced both placement predicates, signed-turn limits, window/opening suitability and orientation-specific strips; followed selected native vec3 angles through registration and their mathematical callee. Reader: 1,530 functions/229,223 instructions/1,301,220 bytes. All 204 research-tool tests pass. Full audit remains active and incomplete; vehicles are the priority.

Latest vehicle research: [plate surfaces, clipping and collision inputs](PLATE-SURFACES-20261021.md). Traced solid-face winding, orientation-dependent clipping planes, parallel-coordinate interpolation and distinct server hull inputs. Reader: 1,507 functions/220,625 instructions/1,248,373 independently summed bytes. Twelve new helper tests; all 193 research tests pass. Vehicle-first full audit remains active and incomplete.

Latest vehicle research: [plate creation, native reconstruction and mesh replacement](PLATE-LOAD-20261021.md). Traced boundary-edge gates, facing fallback, saved-size reconstruction, paint ID remapping and client buffer replacement. Added a read-only plate audit; all 181 research tests pass. Five archived samples have zero findings within the new checks, including the rejected helicopter; this is not game acceptance. Reader: 1,492 functions/215,549 instructions/1,217,324 bytes. Vehicle-first priority and the incomplete full audit persist.

Latest vehicle checkpoint: [attachment surfaces and contact boundaries](VEHICLE-ATTACHMENTS-20261021.md). The complete recovered server predicate and selected helpers were read; quarter-unit extension thresholds, frame/facing conditions, lattice sampling and repeated floating-test corner arguments are documented. New explicit-input geometry tools have 12 tests; full suite 171. Reader: 1,463 functions/206,138 instructions/1,163,700 bytes. Vehicle-first priority persists; full semantics remain incomplete.

Active priority, October 21: **systems for making vehicles**. [Structural connectivity, splitting and update lifecycle](VEHICLE-STRUCTURE-20261021.md) follows reciprocal attachment, object-count-based body retention, service-link remapping and deferred physics cleanup. Continue attachment/plates/edges/save integrity before powertrain, fluids, electrical, controls, suspension, flight and marine systems. Combat/projectile/AI work is parked at low priority. Reader: 1,440 functions/201,934 checked instructions/1,141,198 bytes; access coverage is not semantic completion.

Latest continuation: [character combat, smoke and hordes](COMBAT-SMOKE-HORDES-20261020.md). Includes equipment/timing, shared weapon entry points, smoke emitters/lifetime and a native ray/sphere binding, plus horde creation/flocking/cleanup. Reader: 1,275 functions/184,600 checked instructions/1,042,178 bytes. Complete variants, projectile/armour physics, AI states and every other open register area remain in scope.

Latest continuation: [creatures, sensing and ambient spawning](CREATURES-SENSING-SPAWN-20261020.md). Includes selected records for all 40 creature definitions, actor/vehicle sensing differences, sight filters, timing and ambient placement/despawn gates. Reader: 1,228 functions/176,005 checked instructions/996,711 bytes; 159 tests pass. Complete AI/combat/navigation and every other open register area remain in scope.

Latest continuation: [survival and scene scheduling](SURVIVAL-SCHEDULE-20261020.md). Selected actor eligibility, vital thresholds/precision, clothing wetness, body temperature and damage paths are traced. Reader: 1,191 functions/167,289 checked instructions/947,427 bytes; all 151 tests pass. Complete actors/AI/combat, world, saves/authority, vehicles/native/compiler and all other open register areas remain in scope.

Latest continuation: [sensors and data-network discovery](SENSORS-DATA-20261020.md). Read sensor frame/history limits, pressure conversion by 9800, separate data power flags and descriptor-driven microcontroller bindings. The reader has 1,129 functions/158,494 checked instructions/901,354 bytes. Native angle/physics contracts, complete input/resolver/lifecycle and the broader full-game audit remain open.

Latest continuation: [hinges, mounts, latches, rails, tow links and winches](JOINTS-WINCHES-20261020.md). Per-peer tiers, release/capture gates, slider construction, ballscrew motor arithmetic and rope endpoint stretch are traced. The reader has 1,110 functions/154,167 checked instructions/877,643 bytes; all 143 research tests pass. Native solver units and full joint lifecycle remain open, along with the full-game audit.

Latest continuation: [hydraulic cylinders, track contact and native raycast ordering](ACTUATORS-TRACKS-RAYCAST-20261020.md). The reader has 1,093 functions/149,791 checked instructions; 135 synthetic tests pass. New findings cover chamber bounds/update order, cylinder-size geometry, multibody cleanup, distinct roller contact, hit sorting and native generic erase. Loader specialization remains explicit; whole-game semantic review is incomplete.

Previous continuation: [wheel contact, gas circulation, heat and selected native helpers](CONTACT-FLUIDS-NATIVE-20261020.md). That checkpoint added suspension/grip arithmetic, pressure-released truck brakes, gas overload temperature differences, exchanger/world-sampling paths and selected native vector/math registrations.

Latest checkpoint: [torque, electric machines, jets and helicopter rotors](POWERTRAIN-20261020.md). All 156 declared component update implementations are available in the local reader, which now contains 611 selected functions. New selected traces explain ratio-dependent mass, shared brakes, motor demand, alternator losses, jet-chain validation, swashplate mixing and rotor/ground-effect arithmetic. The full-game audit remains active and incomplete.

Earlier October 20 checkpoint: [component construction, reflection and geometry](COMPONENTS-TYPES-20261020.md). The parser reads the complete declared 8,084-entry reflection table and indexes 37,140 bounded function records, preserving all earlier records. All 207 shipped named component classes have reflected declarations and constructor-prefix evidence; specialized behavior remains separately reviewable. That checkpoint's reader contained 394 selected functions.

Previous checkpoint: [full-game scope and new traces](FULL-AUDIT-20261019.md), with an [audit register covering every system and past subject](AUDIT-REGISTER.md). It accounted for the then-indexed records and 207 named component classes, added gearbox/filter/weather/propulsion/survival/save traces, and recovered the later truck/helicopter records. Its combined reader covered 153 selected functions. Continue offline without requiring in-game testing, retaining unresolved bindings and historical failures explicitly.

Earlier checkpoints: [engines, edges and plates](OFFLINE-ENGINE-STRUCTURE-20261019.md), [electrical/liquid/script systems](OFFLINE-SYSTEMS-20261019.md), and the [offline reader](OFFLINE-20261019.md). Historical runtime protocols remain reference plans, not a gate for this assignment.

2026-10-18 (America/New_York). This is the first whole-game baseline checkpoint of an ongoing research system, not a claim to understand the entire game. Start with [coverage](COVERAGE.md), [versions](VERSIONS.md), and [handoff](HANDOFF.md), then search through the [system index](versions/build-25904830/system-map.json). The existing [engineering findings](../CURRENT-FACTS.md) and acceptance records remain applicable within their own version and evidence boundaries.

This checkpoint completed a two-pass SHA-256 inventory of the entire installation, an isolated snapshot, review of existing research, definition indexes, GCL function-record/reference indexes, historical-address relocation checks, and an initial detailed static investigation of the Opening/Hatch sealing path. The game was never launched, attached to, or controlled. Installation files and active saves were untouched. Runtime experiments have not been performed.

## Answering questions

1. Confirm the Steam build, input SHA-256, and analysis-tool SHA-256. Never reuse old addresses without checking.
2. Query original fields in the definition database. Preserve omitted fields as omitted; do not invent defaults.
3. Find functions by full signature in the GCL database, follow symbol references to callers, and inspect original code and disassembly. A symbol reference is not an executed call.
4. Inspect representative native files, distinguishing loaded state, static connections, and historical runtime acceptance.
5. State findings and limits using the [evidence categories](#evidence-categories). Continue investigating ambiguities offline; historical [experiment protocols](EXPERIMENTS.md) remain optional future plans, not required user testing.
6. Record reproducible commands, input hashes, results, counterexamples, and next steps. Keep full decompilations, binaries, ROM copies, and personal saves local.

## Search and tools

Python 3.12+. Indexing and basic parsing use only the standard library. Run commands from the repository root; `$r` points to a separate research directory outside the repository. Output directories must be new; existing outputs are not overwritten.

```powershell
python scripts/research/gcl_index.py build "$r/snapshot/bin/game.gcl" "$r/gcl"
python scripts/research/catalog.py build "$r/snapshot" "$r/catalog"
python scripts/research/gcl_index.py query "$r/gcl/index.sqlite" hatch_manager
python scripts/research/gcl_index.py query "$r/gcl/index.sqlite" hatch_manager.tick --callers
python scripts/research/catalog.py query "$r/catalog/definitions.sqlite" 'microcontroller OR battery'
python scripts/research/system_map.py "$r/gcl/index.sqlite" "$r/catalog/definitions.sqlite" "$r/system-map.json"
python -m unittest discover -s scripts/research -p 'test_*.py' -v
```

`gcl/index.sqlite` stores full local signatures, code ranges/hashes, relocation operands, global/source-file tables, and reference-resolution status. `catalog/definitions.sqlite` stores definition JSON, JSON Pointers, source/normalized-definition hashes, and full-text search. Retrieve original records through `functions.record` and `definitions.json`; the lightweight component index does not republish complete definitions.

[Tools and maintenance](TOOLS.md) covers baseline collection, Ghidra, historical evidence checks, and update comparison. Exact paths on the current machine are in workspace `RESEARCH-HANDOFF.md`, not the public repository.

## Evidence categories

| Category | Meaning |
| --- | --- |
| `shipped` | Explicitly stated in shipped documentation/definitions; not automatically implementation behavior |
| `static` | Established by checking matching-version implementation, references, or original bytes |
| `runtime` | Actual game observation; identify operator, initial state, controls, and observation scope |
| `inference` | Supported deduction; state the reasoning and possible counterexamples |
| `hypothesis` | Explanation awaiting a test; never report it as a result |
| `unknown` | Insufficient evidence; record the next investigation |

Record confidence separately from evidence category. Function counts, keyword hits, successful decompilation, and passing static checks do not count as system runtime acceptance.

Behavioral findings are in [Opening/Hatch](SEALING.md) and the [offline electrical, pump, and microcontroller investigation](OFFLINE-20261019.md). There is currently no whole-game units table, complete type recovery, complete GCL container grammar, general runtime telemetry, or universal decompiler.
