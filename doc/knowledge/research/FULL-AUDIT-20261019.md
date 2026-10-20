# Full-game audit: scope, historical review and new traces

2026-10-19, build 25904830. The assignment now includes every system and earlier research. The [audit register](AUDIT-REGISTER.md) is the continuing queue. **The full-game semantic audit is incomplete.** This checkpoint establishes complete accounting over the supplied indexes and adds bounded implementation traces; it does not claim complete decompilation or understanding.

The installed GCL and isolated snapshot share SHA-256 `626a994be960b7218409d9ca416d2664450231d1fc3295036fc77c81b8449355`. No game process, installation or active save was changed or executed. All investigations used local copies. Existing Ghidra/JDK tools were reused; no new runtime was downloaded.

## Scope accounting

The new `scripts/research/audit_scope.py` enumerates all indexed functions and all definition records, grouping component methods by their exact owner names. It excludes return/parameter types from topic matching and ignores dots inside template arguments when finding owners. Matching names remain implementation candidates, including when inherited dispatch has not been recovered.

| Accounted object | Result | Limit |
| --- | --- | --- |
| Definition records | 1,737 in 379 source/class groups | Not 1,737 understood behaviors |
| Vehicle components | 598 definitions; 207 explicit classes; four definitions omit class | Omission is retained rather than assigned a guessed default |
| Exact component-owner name candidates | 203 classes | Name matching does not recover factories, inheritance or dispatch |
| Code records | All 37,082 retained in 4,364 owner groups; no unparsed signature in this input | Function-boundary/container completeness remains limited by the existing scanner |
| Unclassified method-name leads | 15,049 explicitly retained | Includes helpers/generated/library code and potentially untouched game behavior |
| Combined selected reader | 153 unique functions; 43,027 instructions / 253,345 instruction bytes checked | Export is not semantic completion |
| Call dependencies | 1,946 local slot dependencies; 1,748 unresolved indirect sites | Neither set is a resolved runtime call graph |

Missing exact-name component owners include the furniture class, weight block, two hydraulic connector variants and the omitted-class group. These require generic/inherited binding research; they are not evidence of broken or nonexistent components. See [scope summary](versions/build-25904830/full-audit-20261019/scope-summary.json) and [all component class groups](versions/build-25904830/full-audit-20261019/component-audit.json). Full method records and per-class leads remain local.

Three new export batches contain 62 distinct function identities, including one battery method already in the reader and 17 earlier sealing functions. They add 61 identities to the previous 92-function reader; 44 had not been in the earlier selected export corpus. The original 18 sealing exports are now represented in the combined reader, including the plate geometry method already integrated earlier. Re-exports are not counted as newly discovered mechanics.

## Current implementation findings

These are `static` findings from selected current-build branches. The [evidence](versions/build-25904830/full-audit-20261019/evidence.json) records exact functions, constants, strings and selected instruction dependencies. Approximate C still has unreliable hidden return types; assembly/source checks do not automatically prove every interpretation below.

### Pneumatic gearboxes, valves, clutch and display

`server_scene.vehicle_component.gearbox_b.tick` at 55020130 activates an unlatched shift channel at pressure **strictly above 3**, and resets its latch **strictly below 2**, in native pressure units. Each channel has its own latch. Holding an activated channel high does not repeatedly increment its target. Both commands can act in the same update; positive-only selectors remain necessary for the earlier magnitude-sensitive valve arrangement.

The internal clutch factor falls by 0.05 per update while current and target gear differ, switches current gear after reaching the disengaged branch, then rises by 0.05 when current and target agree. This is a per-update transition, not an independently established time in seconds. The gear-count getter at 55006260 computes **clamp(2 + extension.z, 2, 8)**. This establishes that getter's arithmetic; all inherited bindings and loaded gearbox behavior are not thereby proven.

The T-valve's flood-node method at 54906191 always selects its common node at component +0x228. It pairs that with +0x2a8 while inactive or +0x268 while active. Its tick calls the current magnitude-threshold helper and requests a gas-network rebuild after switching. The create path also uses gas-node ordinals; saved absolute logic-node indexes still require the ordinal-to-index conversion explained in [current facts](../CURRENT-FACTS.md).

The standalone clutch at 54175871 uses thresholded mechanical input to disconnect its torque link when active and reconnect it when inactive. This particular component's control is discrete; it is not an analog friction-pedal implementation. The gearbox's separate internal clutch transition must not be conflated with it.

The seven-segment display at 57501235 publishes `max(requested_value, 0)`, and its illumination requires received data-node power and its illumination input. A reverse lamp remains appropriate for the accepted vehicle. A lit zero still does not establish that a controller script runs.

### Gas pressure and hydraulic control

Gas content pressure at 58574484 is **quantity / capacity**, with a zero-capacity log/zero return branch. The gas-content pressure getter itself has no temperature multiplier. This does not establish the complete gas network's thermal behavior or convert saved quantity into litres or Pascals.

This differs from the already traced liquid getter's overfill surrogate `max(quantity - capacity, 0)`. Feeding either raw result into calculations using assumed SI pressure would be unjustified without the remaining conversion and geometry paths.

`hydraulic_actuator.tick` at 55329901 is a pressure-to-mechanical-control path: its state activates above **0.5**, resets below **0.3**, and writes **1 or 0** in native units. It also updates liquid content and blends its temperature toward ambient. The component name is not grounds for treating this method as a complete cylinder force/stroke simulation.

### Oil filter and radiator

The oil-filter tick at 57083087 enters its filtering branch only when a fitted item is present. In ordinary nonnegative states it accesses dirty species index **3**, removes up to **0.0001 per update**, further limited by available dirty content and the fitted-item reserve field at +0x90 divided by **0.1**, then reduces that field by **removed amount × 0.1**. The two internal liquid contents are equalized inside that fitted-item branch. Installing the component housing alone does not prove active filtration. Complete naming/defaults of the accessory reserve remain to confirm.

This method removes dirty content; it does not visibly add the same quantity to clean species in the reviewed branch. Preserve that distinction rather than modeling it as an automatically volume-preserving dirty-to-clean conversion. Complete quantity-cache updates, accessory depletion/replacement and all external flow paths remain to trace.

The radiator tick at 57151646 starts an ambient blend factor at **0.0002**, then adds **0.0004 × fan volume / radiator volume** for each linked fan reporting active. It passes that factor to ambient blending. These are per-update factors in this branch, not a kW rating or a full airflow/cooling curve. Damaged-radiator handling also contains a liquid-removal path, whose complete leakage behavior remains unfinished.

### Weather and ambient temperature

Ambient blending at 63741958 samples the current game mode/time-of-day cycle and weather at the supplied transform's position, obtains temperature degrees, and interpolates the previous temperature toward that value using the caller's coefficient. It is not a universal fixed ambient temperature.

The temperature endpoint initializers set **-5 and 28 degrees**. The degree getter interpolates those globals using the weather temperature field; this is not proof that every later temperature is clamped to that interval. Rain and snow factors multiply the same precipitation quantity by complementary internal snow fractions. A separate simulation branch uses sandbox weather offsets; the other branch advances two maps using timestep-scaled drift. Complete seed/time/altitude/weather equations remain open.

### Propulsion, sensors, actors and progression

The boat-propeller branch at 53828211 applies its calculated impulse only after checking the physics object is present and the queried position is submerged. It then derives a torque load from the impulse magnitude/sign. Exact coefficients, sampling geometry and transitions remain unfinished; an above-water propeller cannot simply be assigned the same thrust formula from this branch.

Control-surface tick at 54205652 limits deflection using definition fields and combines branches weighted by water submergence before applying force. Collective tick at 54692330 reads torque RPS and clamps its control before delegating to the native rotor element. Jet combustion/compressor methods were exported and their network/oil paths inspected, but complete thrust/start/assembly equations are **not** yet established.

Altitude-sensor tick at 53533340 composes vehicle and component transforms and stores the resulting world Y coordinate. No terrain raycast appears in this tick; do not describe that value as height above ground. Seat-input getters and steering-wheel application were also re-exported. Floating-point axis fields alone do not override the user's established digital pedal observation; the full client/device mapping remains queued.

Character oxygen tick at 41964849 checks invulnerability, uses a view-transform point and an ocean submersion query, then changes oxygen by timestep divided by recovery/depletion globals. Exact durations and every cabin/submersion interaction remain open. The actor impact helper at 40779193 uses a scaled relative-velocity magnitude squared, a threshold squared and divisor **100**; the horizontal-scale initializer is **4**. These are selected actor impact paths, not a universal vehicle/weapon damage formula.

The AI locomotion stuck predicate at 40908105 checks a stored flag or an unreachable target with no path. Actual AI state transitions, timers and recovery still require callers and mutation paths.

Progression is no longer only a suggestive keyword lead: `process_item_unlock` at 40122547 constructs an unlock from an item, checks unlock status, conditionally sends an unlock-component message and recursively visits child item grids. Its companion lookup at 40117400 includes definition/game-mode exceptions and searches stored unlocks. Full prerequisites, callers, persistence, economy and whether crafting exists remain unfinished. This is a verified unlock path, not proof of a crafting system.

### Save structure and collision

Vehicle save parsing at 51778349 treats nodes, edges, plates, plate paint, mounting grids and each link family as separate fields. It also parses motion type, server/spawn fields, loot/creature locations and buoyancy fill. A geometry edit must preserve the relevant graph/reference/state relationships; moving a visible polygon alone is not a complete native mutation transaction. The `.meta` parser is a separate exported method.

Vehicle compound collision construction at 52757266 has plate physics classification and capsule, convex-hull and box construction paths. This establishes another concrete separation from render geometry and buoyancy sealing. Complete partitioning, material/glass/mode filters and actor-capsule passage remain unreviewed; do not infer that every visually open region is traversable.

## Later creations recovered from the PC

The previous main knowledge archive focused on October 11-16. This audit also read the later local truck/helicopter reports and scripts, recording selected facts and original report hashes in [later creation history](versions/build-25904830/full-audit-20261019/later-creation-history.json). Those reports describe previous work; the generators/installers were **not** run now.

- **Hauler revision 03:** 117 components; 49 rewound panels; seat raised 0.48 m and moved forward 0.32 m; 31 routed service runs; 27 forward sightline samples at planned eye heights. The report's own limit says these are planning heights, not a recovered native camera transform. No successful seated-view, light or eight-gear driving test was recorded for this revision.
- **Rejected helicopter inset:** the user reported phantom plates/edges and requested rollback. The restoration record preserves the exact earlier `.data`, `.meta` and preview hashes. Its note distinguishes restoring files from replacing an already spawned object. The exact corruption/cache cause remains unknown.
- **Native helicopter lining:** the later work copied the user's wall/dash pattern with two grid units, 0.16 m, of recorded axis spacing. The user subsequently reported the test good, then requested a pilot-shell mirror and a rear-design correction. That observation does not validate every later revision or prescribe a universal spacing rule for all sloped walls.
- **Pilot shell/rear correction:** the report records 13 mirrored shell panels, removal of 45 assistant-added rear panels, exact prior rear footprint/frame coverage and tank refills of 240/240/180/180 L petrol plus 144 L oil. These are historical saved tank values, not current tank contents or consumption tests.
- **Rear completion:** a 25-panel user patch supplied the pattern; 19 mirrored panels were added while six shared center panels were retained. Existing geometry/state was preserved according to the historical static checks. No new game test was performed.

Five archived native files were re-audited read-only using the existing native schema/reference auditor and current snapshot definitions. Four reported no findings, including the **rejected** helicopter inset. The 103-part cleaned giant vehicle reported a warning for six disconnected **frame-only** groups; the auditor explicitly does not evaluate component bridges. The cleaned export followed the user's successful 106-part diagnostic test; this re-audit is not a new operating test of the cleaned version. Neither result reverses the user observations. This is direct evidence that a basic file audit is insufficient to certify visual topology or physical mounting.

## Validation and remaining work

All 60 synthetic research-tool tests passed. The new scope tests cover owner/template separation, type-only false topic hits, omitted/unparsed retention, stale/incomplete readers, unknown functions and duplicate offsets. Reader 1.1 now audits repeated exports, deduplicates only identical source identities/C/assembly/evidence and rejects conflicting duplicates; both cases are tested. An initial combined build correctly rejected a duplicate under the previous strict policy and remains an incomplete local diagnostic, superseded by the successful new reader.

Independent evidence checking passed for **62 function identities, 20 constants, 20 strings and 35 selected call-instruction examples**. All 43,027 reader instructions matched original source bytes. These checks establish source/byte identity and tool invariants, not every prose claim, recovered ABI, dynamic binding or runtime acceptance. Installation/source identity and documentation validation are recorded in the [verification report](versions/build-25904830/full-audit-20261019/verification.json).

The [register](AUDIT-REGISTER.md) retains the entire assignment, including all historical topics and unclassified code. Next traces should resolve actual generic/inherited component binding and follow complete dependency chains, prioritizing unfinished native physics/structural mutation, jet/rotor propulsion, network/thermal units, script/compiler behavior, world/survival/combat and save/multiplayer authority. Rendering, audio, UI and journal remain included. No untouched system is marked understood merely because its definitions were indexed.
