# Coverage and gaps

Measurements in this checkpoint apply to build 25904830. Keyword counts come from the [machine-readable system index](versions/build-25904830/system-map.json), with overlapping topics and template expansion; they cannot be converted into a percentage of understanding.

| Dimension | Completed | Does not establish |
| --- | --- | --- |
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
| System map | 15 topics with definition/code leads and question queues | Explanations of 15 systems |
| Detailed investigation | Opening/Hatch matching -> sealing flag -> water-flow branch | Player passage, all geometry/dynamic states, or runtime acceptance |
| New runtime experiments | **0** | Testing of any new game behavior |

## System coverage

| System | Current reliable entry point | Remaining work |
| --- | --- | --- |
| Building/coordinates/welding/structural islands | Existing grid/island research; historical signatures relocated this checkpoint | Current call paths, all contact tolerances, destruction/island-split scheduling |
| Components/interfaces/accessories/defaults | All 598 definitions, field presence, and interface-type index | Native parser defaults, compatibility of every variant, instance state |
| Physics/collision/damage/repair | PE/GCL physics leads and existing constraint research | Collision shapes, constraint parameters/failure, damage/repair state machines |
| Engines/torque/gears/clutches/wheels/belts/tracks | Accepted engines/vehicles and historical native traces | Current per-class review, load/durability, all sizes and wheel arrangements |
| Electrical | Shipped ports/loads, previously operated assemblies; new consume_binary/consume_factor and relay hysteresis traces | Complete network solver, storage/overload, consumer ordering |
| Liquid/gas/temperature/cooling | Existing circuit evidence; new pump shaft/reverse/pressure-limit arithmetic and save-field bindings | Unit conversion/conservation, every valve/pump variant, sustained thermal equilibrium |
| Doors/openings/hatches/latches/rails/actuators | New sealing path; historical mechanical/hydraulic connections | Collision/player passage, independent latch experiment, dynamic boundaries |
| Controls/sensors/data/displays/microcontrollers | Positive/negative selectors and working examples; new 10 W demand and >1% power gate/analogue reset path | All power-loss effects, alias scope, sensor units/timing, all logic blocks |
| Scripts | Native samples/typed state; GCL parser/binding leads | Full grammar, compilation/execution/scheduling/persistence/budget |
| Inventory/progression/survival/weather/combat/AI | Inventory/creature/zombie definitions and code leads | Do not infer functionality from content names; first establish whether crafting/progression exist |
| World/buildings/bunkers/environment | All data JSON; tile/dungeon source leads | Generation/seeds/environment state; vegetation binaries |
| Saves/creations/metadata/versions | Accepted native examples; raw-field preservation tools | Current parse/save defaults, migration, world-versus-creation differences |
| Multiplayer | Server/client/replication global leads | Authority, ownership, synchronization order, disconnect/reconnect persistence |
| Rendering/materials/dynamic assembly/animation | Existing Mesh/binding/resource tools and format identification | All current formats, dynamic assembly, comparison with runtime visuals |
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
