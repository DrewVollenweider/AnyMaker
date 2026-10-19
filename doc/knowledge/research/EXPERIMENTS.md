# Coordinated runtime experiment protocols

**All are planned / unperformed.** Do not run them during this checkpoint: the user may be playing. Use backed-up or disposable worlds and separately named creations only after the user explicitly arranges a separate research session. First check the complete hashes in [versions](VERSIONS.md); relocate static evidence before testing a different version.

## SEA-01: independent roles of Opening, Hatch, and latch

Competing explanations: A, Opening itself always blocks water; B, Opening passes water and a matching Hatch seals it; C, latch engagement is independently necessary; D, geometry/physical alignment alone explains their apparent relationship. Static evidence currently supports B and geometric matching; it is not a runtime result.

Preparation: build a supported simple closed box in a disposable world, keeping mass, materials, face orientation, and boundary beams fixed. Keep ventilation/observation conditions above it consistent; place the test hole at the same position below the waterline. First establish a watertight baseline using a complete solid plate, then replace the test face with the native Opening Tool. The Hatch must be the correct independently moving rigid body, mounted with supported hinges/latches. Do not edit native coordinates to introduce unsupported geometry.

Planned names: `Research_SEA01_Solid`, `Research_SEA01_OpeningOnly`, `Research_SEA01_HatchAlignedUnlocked`, `Research_SEA01_HatchAlignedLatched`, `Research_SEA01_HatchOpen`. These are planned names, not files already generated/imported.

| Condition | Single changed variable | Support/contradiction |
| --- | --- | --- |
| Solid control | No opening | If it leaks, repair the box; invalidate the entire run |
| Opening only | Test face is Opening, without Hatch | Flooding contradicts unconditional water blocking; no flooding requires checking pressure difference/water level, duration, and valid cavity |
| Aligned, unlatched Hatch | Add matching Hatch, stationary and closed | Water exclusion supports geometric sealing; rule out merely failing to see short-term flow |
| Latched at same alignment | Change only latch state | If sealing changes with alignment maintained, retrace an independent latch condition |
| Open Hatch | Change only relative alignment | Flooding after mismatch supports dynamic unsealing; record delay instead of claiming instantaneous response |

Wait for geometry/motion to settle for each condition. Record explicit observations at 0, 10, 30, and 60 seconds and repeat at least twice. Use available game UI/supported instruments for water level or cavity volume. If only visual observation is available, state its resolution; do not invent a telemetry API. Compare paired trials with equal initial water volume, waterline, and environment. One saved snapshot is not continuous flow measurement.

Separately test player passage on safe dry ground, comparing Opening and open/closed Hatch. Do not use buoyancy results as collision evidence. Do not automate untested actions such as entering vehicles or changing camera mode.

Preservation: retain user-exported `.data/.meta` and version inventories for each condition; analyze only these separate research files. Existing archived tools offer read-only `snapshot`, `inspect`, and `diff`; check `--help` first and use fresh output names. Keep world backups and personal saves outside Git. Record UTC/local time, operator, initial state, unique variable, observations, failures/counterexamples, file hashes, and restoration status. A failed control cannot be marked PASS.

SEA-02 separately addresses threshold boundaries: use supported hinge motion, known grid points, or native assemblies to vary relative alignment. First establish whether states near 0.02 native coordinate units can be measured reliably. Do not alter game capabilities or geometry to obtain an exact threshold.

## Other priority protocols

| ID | Hypothesis/competing explanation | Controls/observations | Status |
| --- | --- | --- | --- |
| ENG-01 | Compact-engine cooling reaches sustained equilibrium / only works in short snapshots | Separate derivative of accepted CPE1Running; equal initial oil/water/fuel and RPM; sustained temperatures, reservoir quantities, and load; design instrumentation first | Unperformed; insufficient preparation |
| ELEC-01 | Controller immediately stops on power loss / delays or retains outputs | Independently cut only power; same program, load, data network, initial state; observe supply/output/recovery; statically trace scheduling first | Unperformed; insufficient preparation |
| SCRIPT-01 | Specific operator missing on import / expression or type problem | Keep working `>0/<0` controls; change one expression at a time; pair exported text with compile diagnostics; do not generalize the historical `!=` case | Unperformed; insufficient preparation |
| MP-01 | Server authority / local prediction creates visible differences | User must arrange two clients and a disposable world; first finish authority/replication paths; protect current gameplay | Unperformed; insufficient preparation |

Before any runtime work, prepare exact creations/initial states, instrument capabilities, and restoration steps for review, then request coordination. This document does not authorize background experiments.
