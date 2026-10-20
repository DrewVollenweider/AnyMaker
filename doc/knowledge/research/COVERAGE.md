# Coverage and gaps

Newest continuation: [sensor/data chains](SENSORS-DATA-20261020.md). Selected sensor getters, mounted-axis calculations, pressure conversion, data-island flood and controller discovery are reviewed. Reader: 1,129 functions/158,494 instructions/901,354 bytes. The existing 143-test suite remains passing; no executable research tool changed in this continuation. Complete native units, controls, compiler, lifecycle and other full-register domains remain unfinished.

Newest continuation: [joints and winches](JOINTS-WINCHES-20261020.md). Selected hinge/mount/latch/rail/tow/winch chains now have source/field evidence and eight arithmetic tests. Reader: 1,110 functions/154,167 checked instructions/877,643 bytes. Suite: 143 tests. This adds reviewed behavior at the stated scope; it does not close all moving joints, loaded states, tool compatibility or other audit domains.

Newest continuation: [hydraulic cylinders, tracks and native raycast ordering](ACTUATORS-TRACKS-RAYCAST-20261020.md). The reader has 1,093 functions/149,791 checked instructions/852,045 bytes and 135 synthetic tests pass. Cylinder chamber/geometry/body cleanup, distinct roller contact and selected raycast sorting/erase paths are reviewed. Full native loader specialization, all actuator families and whole-game semantics remain open. The [previous contact/gas/native checkpoint](CONTACT-FLUIDS-NATIVE-20261020.md) remains applicable at its stated scope.

Measurements in this checkpoint apply to build 25904830. Keyword counts come from the [machine-readable system index](versions/build-25904830/system-map.json), with overlapping topics and template expansion; they cannot be converted into a percentage of understanding.

Current continuation: [torque/electric machines/jets/rotors](POWERTRAIN-20261020.md), following [component types/construction/geometry](COMPONENTS-TYPES-20261020.md). All declared component update methods are available, with selected coherent behavior chains reviewed. The current local index has 37,140 functions; reflection supplies declared class/enum/method/field information. Historical rows below remain measurements of their own checkpoints.

Latest scope supersedes the earlier topic-only queue: [full-game audit register](AUDIT-REGISTER.md), [new findings and historical review](FULL-AUDIT-20261019.md), [complete indexed scope accounting](versions/build-25904830/full-audit-20261019/scope-summary.json), and [every component class group](versions/build-25904830/full-audit-20261019/component-audit.json). The table below retains chronological measurements; they must not be summed blindly because later readers include earlier exports.

| Dimension | Completed | Does not establish |
| --- | --- | --- |
| Cylinder/track/raycast continuation | Chamber volume bounds, six cylinder calibration getters, body-pair cleanup, roller differences and native hit ordering/erase | Every moving joint, complete belt rendering/topology, native physics solver or generic loader specialization |
| Contact/gas/native continuation | Suspension/load/grip, gas brake thresholds, tyre calibration, overload temperature distinction, exchangers/world sampling and selected native constructors/math | Full track contact, moving-support/native physics, actuator ownership, all gas aliases/empty states or complete ABI |
| Component update access | All 156 distinct declared update implementations across 224 types; all 598 shipped definition IDs retained | Complete review of their behavior or availability of compiled-only classes |
| Torque/propulsion follow-up | 611-function reader/103,166 instructions/597,691 bytes; 101 synthetic tests; selected solver, motor, alternator, jet and rotor traces | Full contact/track/aerodynamic/thermal models, native intrinsic behavior or game-runtime acceptance |
| Installation files | 10,813/10,813, two-pass SHA-256 | Understanding of every file's internal structure |
| Snapshot | 4,833 verified code/data/document copies | A complete ROM copy or atomic disk snapshot |
| Formats | Full JSON syntax validation; PE/GCL/mesh/TXTR/ATLA/Ogg/font identification | Complete parsing; 1,843 binary data files remain unknown |
| Definitions | 2,968 data JSON files indexed; 1,737 definitions; 598 components | Recovery of omitted defaults, all interface compatibility, or implementation behavior |
| GCL header tables | 1,172 source paths; 931 global types/names | Original source code or a complete type table |
| Function records | 37,082 nonoverlapping, structurally checked records | All function boundaries or 37,082 understood functions |
| References | 179,409 operand slots; 84,872 linked to function records, 9,629 to header globals, 84,908 unresolved | An executed call graph or resolution of every indirect call |
| Instruction exports | 18 unique functions; 6,599 instructions and 40,843 bytes individually checked | Complete semantic understanding of 18 functions or decompilation of the entire GCL |
| Additional offline exports, 2026-10-19 | 29 distinct functions; 6,813 instructions/39,264 bytes; searchable C, assembly and machine facts | Full types, all dynamic bindings, or complete behavior of each exported function |
| Offline call-use traces | 297 local operand-slot dependencies at call sites; 270 unresolved indirect calls | A resolved runtime call graph; a kind 6 displacement is not necessarily a direct function pointer |
| Offline selected evidence | 29 record identities, 17 constants, four strings, 21 call examples checked; 42 research-tool tests | Automated proof of prose semantics or game-runtime acceptance |
| Offline systems follow-up | 36 further functions/7,042 instructions/38,015 bytes; combined reader 65 functions/13,855 instructions; 51 tests | Complete component ordering, all conservation edge cases, or a whole-program script budget |
| Engine/structure follow-up | 27 further functions/11,186 instructions/68,043 bytes; combined reader 92 functions/25,041 instructions | Complete engine calibration, all contact/collision cases, or structural strength thresholds |
| Full-game scope follow-up | All 1,737 definitions/379 source-class groups; 598 components/207 named classes; all 37,082 records/4,364 owner groups retained | Class binding, default recovery or understanding of every indexed item; 15,049 method-name leads remain unclassified |
| Expanded combined reader | 153 unique functions/43,027 instructions/253,345 bytes; 60 synthetic tool tests | Whole-game decompilation, ABI recovery, all virtual targets or all prose interpretations |
| Historical creation recheck | Six later truck/heli reports recovered; five archived files re-audited | The rejected heli inset still passes the basic audit; the cleaned giant export retains a frame-only grouping warning |
| Function parser refresh | 37,140 bounded records; all previous 37,082 unchanged; 58 additional template-qualified functions | Complete GCL/container/loader coverage or understanding of the new bodies |
| Declared reflection table | All 8,084 counted entries parsed through EOF: 7,633 structures, 451 enums | Complete runtime ABI, flag meanings, intrinsic implementations or ambiguity resolution for two repeated pointer names |
| Component construction | All 207 named shipped classes have declarations/constructors; 211 non-root initialization parents agree with declarations | Complete specialized behavior of every class, every variant or every declared method |
| Current selected reader | 394 unique functions/58,665 instructions/339,395 original instruction bytes | Whole-game semantic completion; 2,269 indirect sites remain unresolved |
| System map | 15 topics with definition/code leads and question queues | Explanations of 15 systems |
| Detailed investigation | Opening/Hatch matching -> sealing flag -> water-flow branch | Player passage, all geometry/dynamic states, or runtime acceptance |
| New runtime experiments | **0** | Testing of any new game behavior |

## System coverage

| System | Current reliable entry point | Remaining work |
| --- | --- | --- |
| Building/coordinates/welding/structural islands | Current edge/plate/component adjacency, reciprocal attachment registration, and base-grid plate-facing checks; earlier mounting auditor | All inclined/contact cases, stable topology mutation, strength/destruction and split scheduling |
| Components/interfaces/accessories/defaults | All 598 definitions; reflected class/enum/field information, constructor paths, generic fallback and core parser/geometry defaults | Remaining defaults/intrinsics, complete variant compatibility and specialized instance behavior |
| Physics/collision/damage/repair | PE/GCL physics leads and existing constraint research | Collision shapes, constraint parameters/failure, damage/repair state machines |
| Engines/torque/gears/clutches/wheels/belts/tracks | Current combustion engine speed gates, manifold throttle combining, staged damage, oil/thermal paths, raw channel versus tooltip conversions | Full calibration/load model, other engine classes, complete durability and all drive variants |
| Electrical | Consumer calls are sequential within component updates; pending demand debited in following pre-build proportionally across sources; relay hysteresis | Stable component-vector construction across loads/splits, generator/redistribution losses, complete solver |
| Liquid/gas/temperature/cooling | Native 0.5 L/voxel capacity factor; overfill pressure surrogate and level/static-bias head; conservative direct mixture transfers and equalization | Multi-source edge cases, all units/species labels, sources/sinks, all variants and thermal equilibrium |
| Doors/openings/hatches/latches/rails/actuators | New sealing path; historical mechanical/hydraulic connections | Collision/player passage, independent latch experiment, dynamic boundaries |
| Controls/sensors/data/displays/microcontrollers | Positive/negative selectors and working examples; new 10 W demand and >1% power gate/analogue reset path | All power-loss effects, alias scope, sensor units/timing, all logic blocks |
| Scripts | Normal event/body traversal; repeat/foreach cap 256 iterations per invocation in run/execute/debug paths | Complete grammar, call-graph restrictions, global resource/time budget, persistence and full scheduling |
| Inventory/progression/survival/weather/combat/AI | Inventory/creature/zombie definitions and code leads | Do not infer functionality from content names; first establish whether crafting/progression exist |
| World/buildings/bunkers/environment | All data JSON; tile/dungeon source leads | Generation/seeds/environment state; vegetation binaries |
| Saves/creations/metadata/versions | Accepted native examples; raw-field preservation tools | Current parse/save defaults, migration, world-versus-creation differences |
| Multiplayer | Server/client/replication global leads | Authority, ownership, synchronization order, disconnect/reconnect persistence |
| Rendering/materials/dynamic assembly/animation | Existing Mesh tools; current plate support offsets, 1 cm thickness and type dispatch | Full outer/sloped/window geometry, collision, dynamic assembly, runtime visual comparison |
| Input/audio/UI/translations/journal | Historical digital-input evidence; audio descriptors and translation identification | Complete input mapping, audio timing, UI/journal logic |

Each topic still needs inputs/outputs, units/coordinates, defaults/thresholds, state transitions, update order, dependencies, serialization omissions, failure modes, implementation evidence, and experiments. Keyword hits do not promote unfinished work to completed status.

## Contradictions and tool limitations

- All old addresses are invalid, but 66/96 relocated ranges have identical code hashes. Changed offsets do not imply changed mechanics.
- Hidden return pointers, temporaries, and structure-member types in exported C are unreliable. Do not treat it as a recovered C ABI or compilable source.
- GCL's declared allocation sometimes exceeds code plus operand slots by 8 bytes. The scanner preserves the difference and excludes following debug bytes from code; its meaning remains unknown.
- Full loader semantics for kind 1 numeric operands, kind 5 type-like references, and kind 6 references are unrecovered. New instruction traces show kind 6 used as virtual-dispatch displacements; the earlier scheduling-like description was an unverified lead. Preserve unresolved references.
- The scanner is not a complete container parser. Unsupported-candidate counts include signatures inside references and are not missing-function counts.
- The first baseline exposed a path-sort comparison defect. Collection was repeated in full after correction; UTF-8 prefix-boundary classification was subsequently corrected too. Failed outputs remain local and are not labeled successful.
- Ghidra initially rejected a sandbox temporary path containing braces. It succeeded with a separate plain temporary path. The runner requires an explicit project directory and verifies actual products rather than relying only on exit status.
