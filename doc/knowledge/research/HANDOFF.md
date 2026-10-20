# Handoff and restart

Current continuation: [survival and scene scheduling](SURVIVAL-SCHEDULE-20261020.md). Reader: 1,191 functions/167,289 instructions/947,427 bytes; 151 tests. Preserve peer/actor-ID eligibility, 61-call condition counter, 50% vital warning versus 25% low-stamina check, full-f64 reserve versus replication byte, and jump-edge-plus-recovery behavior. Clothing/weather shelter differs from cabin sealing. Continue full actors/AI/combat/world/save/authority and the remaining full register; broad goal stays active.

Current continuation: [sensor readings and data discovery](SENSORS-DATA-20261020.md). Reader: 1,129 functions/158,494 instructions/901,354 bytes. Acceleration is a projected velocity difference with no delta-time division; gyro stores f64 after division by 2pi; compass retains its prior value near vertical. Pressure signals multiply internal readings by 9800. Keep data capability/powered flags and direct-contact/cable flood branches distinct. Native angles/units, aliases/resolver, full control interactions and all remaining register areas stay open.

Current continuation: [hinges, mounts, latches, rails, tow links and winches](JOINTS-WINCHES-20261020.md). Reader: 1,110 functions/154,167 instructions/877,643 bytes; 143 tests pass. Hinge suppression is a maximum tier per peer body. Ordinary slider release is 1.0, ballscrew slider release 0.5. Ballscrew repeatedly writes brake; winch retains any blocked-rope brake within its loop. Rope stretch uses endpoint distance. Preserve these distinctions and unresolved lifecycle/native limits. Continue controls/sensors/data and every remaining full-register area. Broad goal remains active.

Current continuation: [hydraulic cylinders, tracks and raycast ordering](ACTUATORS-TRACKS-RAYCAST-20261020.md). Reader 1,093 functions/149,791 instructions/852,045 bytes; 135 synthetic tests pass. Preserve pre-correction chamber-capacity writes and the distinctions between ordinary wheels, fixed/suspension rollers and sprockets. Native exporter 1.1 supports explicit assembly-only work; failed C remains failed. Exception entries can be adjacent fragments, and generic loader specialization remains explicit. Continue all remaining moving-joint families and the full register. Broad goal remains active.

Previous continuation: [contact, fluids and native helpers](CONTACT-FLUIDS-NATIVE-20261020.md). Read the gas pair/vector temperature distinction before reusing models. Exact local/publication paths are in workspace RESEARCH-HANDOFF.md.

Newest checkpoint: [torque, electric machines, jets and rotors](POWERTRAIN-20261020.md). The reader contains 611 functions/103,166 byte-checked instructions/597,691 instruction bytes. All 156 distinct component update implementations declared across 224 types are available; availability is not semantic completion. Selected solver/propulsion arithmetic has 12 additional tests, bringing the research suite to 101. Continue the full register, particularly wheel/contact and track dynamics, actuator/body chains, fluid/gas/thermal behavior and the remaining nonvehicle systems.

Earlier foundation: [component construction, reflection and geometry](COMPONENTS-TYPES-20261020.md). Scanner 1.4 indexes 37,140 functions, preserving all 37,082 earlier records and adding template-qualified names with spaces. The reflection parser reads all 8,084 declared table entries through EOF. All 207 shipped named component classes have matching constructor/declaration evidence. Specialized behavior, intrinsic/loader rules and the broader register remain incomplete. Exact local paths and publication state are in workspace RESEARCH-HANDOFF.md.

Earlier full-scope checkpoint: [full-game audit](FULL-AUDIT-20261019.md). The user explicitly expanded scope to all systems and earlier work; follow the [complete register](AUDIT-REGISTER.md). That checkpoint's reader contained 153 functions/43,027 source-checked instructions, and its 60 synthetic tests passed. The later truck/heli reports, rejected inset and rollback remain preserved. Continue offline without requiring user gameplay tests; keep unresolved bindings explicit.

Status: phase 1 (baseline/existing-work assessment/system map) is complete. The first necessary search and local native-analysis capabilities of phase 2 are delivered. Complete container/type recovery in phase 2 remains unfinished; phase 3's per-system explanations are beginning. Do not mark the whole assignment complete at this checkpoint.

## Restart sequence

1. Read parent AGENTS, the knowledge hub, CURRENT-FACTS, and this directory's README/COVERAGE/VERSIONS.
   Also read AUDIT-REGISTER and FULL-AUDIT-20261019 before selecting new work. Earlier focused next steps remain useful subsets, not the full assignment.
2. Locate the separate research directory. Exact machine paths are in workspace `RESEARCH-HANDOFF.md`; the public repository stores only relative paths and hashes. Without local inputs, recollect the matching version using TOOLS; never request or commit private keys.
3. Confirm `gcl/index.sqlite` by source SHA. Query the target signature/references and read local original bytes/limited exports. Do not load the entire decompilation into context.
4. Read this checkpoint's `historical-check.json` first. All 96 historical addresses are invalid; use relocated addresses. The 66 identical code hashes do not establish unchanged data/caller environments.
5. Check for installation updates. A new build or any changed input hash requires a separate version directory and comparison.
6. Continue independent static analysis without controlling the running game. Planned experiment protocols are not results.

## Next steps, in order

1. Extend the new systems findings: trace stable component-vector construction/mutations and generator/redistribution losses; multi-source liquid constraints, enum names/display units and source/sink paths; compiler call-graph and broader resource guards. Sequential consumer acceptance, following-build source debit, native capacity factor/head, direct-transfer conservation and per-loop clipping are already documented. Use the reader before exporting more functions; keep unresolved virtual targets explicit.
   The user also prioritized engines, edges and plates: continue into full collision/player passage, native plate-facing serialization and all edge widths/slopes, structural strength/destruction, complete engine calibration and other engine classes. Current gates/damage/channel units, attachment graph/base-grid facing and surface offsets/thickness are documented already.
2. Complete actual GCL-loader rules for flags, allocation +8, kind 1/5/6, trailing debug/unwind data, and type tables. The existing scanner already supports search. Extend only when a demonstrated limitation blocks a question; do not build a general decompiler for its own sake.
3. Select representative components from every system-map category. Trace parse/default -> create/post_load -> tick -> inspect/save, listing unchecked sizes/variants. Prioritize electricity, script execution/scheduling, and fluid units, then expand AI/world/multiplayer.
4. Reuse Mesh parsers/audits to review all relevant current-build formats. A `.anim` mesh v5 container is not automatically animation logic. Validate vegetation `.bin` layouts against consumers as well as bytes.
5. Return to Opening/Hatch initial flags, collision builders, player-passage paths, and manager ordering as offline questions. Historical runtime protocols are optional reference plans; do not request a gameplay session as a gate for the current research assignment. Keep gameplay/saves undisturbed.

## Progress log

| Local date | Progress | Evidence/limits |
| --- | --- | --- |
| 2026-10-18 | Located installation/Steam build; verified full inventory/copy hashes | Final baseline 1.1.0; relative-path inventory excludes account fields |
| 2026-10-18 | Reviewed archives, accepted native creations, Ghidra tools, six historical code-evidence groups | Historical records retained; historical user tests are not new tests |
| 2026-10-18 | 37,082 GCL records, definition database, 15-topic system map | Complete local indexes; types/full container unrecovered |
| 2026-10-18 | Relocated 96 historical ranges; 66 code hashes retained | No old offsets matched |
| 2026-10-18 | Opening/Hatch geometry match, seal write, water-flow read path | Partial exports of 18 functions; 6,599 instruction-byte checks; no runtime acceptance |
| 2026-10-18 | 15 new-tool and 25 archived tests passed; one optional corpus skipped | Actual one-function runner smoke test; not an additional unique function |
| 2026-10-19 | Machine-fact exporter, local dependency tracer, full-text code reader, selected-evidence checker | 29 additional functions; 6,813 instructions/39,264 bytes checked; 297 slot-derived call dependencies, 270 unresolved |
| 2026-10-19 | Electrical budget calls, relay hysteresis, liquid pump arithmetic, microcontroller power gate | 42 research-tool tests; 29 records, 17 constants, four strings, 21 call examples checked; no game execution |
| 2026-10-19 | Electrical update ordering/deferred debit, liquid accounting/head/conservation, 256-iteration per-loop limit | 36 further exports/7,042 instructions/38,015 bytes; combined reader 65 functions; 51 tests; 44 selected records, 13 constants, four strings, 20 call examples checked |
| 2026-10-19 | Engine gates/damage/units; edge/plate/component attachment; plate facing/support/thickness | 27 further exports/11,186 instructions/68,043 bytes; reader 92 functions; 27 identities, 24 constants, 14 strings, 15 call examples checked; no new game test |
| 2026-10-19 | Full-game accounting, all earlier subject queue, later truck/heli recovery; gearbox/filter/weather/propulsion/survival/save traces | Reader 153 functions/43,027 instructions/253,345 bytes; 60 tool tests; 62 selected identities, 20 constants, 20 strings, 35 call examples checked; whole-game semantic audit remains incomplete |
| 2026-10-20 | Declared reflection table, all shipped component construction, core defaults/geometry; template signature recovery and faster tracing | 37,140 indexed functions; 8,084 descriptors; reader 394 functions/58,665 instructions; constructor/declaration agreement for 211 non-root types; specialized systems remain pending |

Default Git transfers repeatedly stalled in this environment and were terminated. A separate sparse checkout was recovered through GitHub API objects and existing archive blobs, checking every object's SHA-1: base `bcfea8e9b94604020d8957e456493c744a89e2e0`, 49 trees, 133 matching blobs. Unretrieved application blobs remain absent under sparse checkout; this is not a usable frontend-test checkout. Other checkouts' local changes/commits were neither read nor rewritten.

The original checkpoint changed only research code/docs/indexes, with no main merge, deployment, or release. Publication status and actual commit IDs must come from final Git results and local handoff, not this planned paragraph. Leave no background analysis jobs at session end; explicitly record PID, logs, resource cap, and stop method for any retained job.

Language correction: the user rejected the historical Chinese-documentation instruction and explicitly authorized English documentation/instruction corrections on both the research branch and main. That authorization does not extend to deployments, releases, or application behavior changes. Preserve the original checkpoint's evidence and completion boundaries when translating it.
