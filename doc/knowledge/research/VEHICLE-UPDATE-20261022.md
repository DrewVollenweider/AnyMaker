# Vehicle systems in build 26113663

2026-10-22. Vehicle engineering remains the active priority: engines, transmissions, fluids and heat, electricity, controls, wheels and suspension, structures, flight and marine propulsion. Combat, projectiles, explosions and AI are parked at low priority. The full audit remains incomplete.

This checkpoint follows the [installed-build transition](BUILD-TRANSITION-20261022.md). All current evidence below targets **26113663**, GCL SHA-256 `a3fd2df2fd62e38b629f6a0df824269a34d77d57caf66d596362d7e5e53c3b22` and PE SHA-256 `097e1167477587c51a3b93ab7e7843382d99d30010678c9bd89a2fee648fec23`. Full code exports and game resources remain local. Selected identities, layouts, instructions and scalar readings are in [evidence.json](versions/build-26113663/vehicle-update-20261022/evidence.json); checks are in [verification.json](versions/build-26113663/vehicle-update-20261022/verification.json).

## What transfers from the earlier review

The new [compare_reviewed.py](../../../scripts/research/compare_reviewed.py) verifies the archived source/index/reader before matching exact signatures in the new source. For equal-sized methods it compares the previously reviewed instruction spans, their recorded direct embedded reads and reference metadata at corresponding relative positions. It separately reports whole-code equality and changed bytes outside those spans. Different-sized methods are not mapped this way.

Across **1,543 archived reader entries**, the result is:

| Local comparison result | Entries |
| --- | ---: |
| Reviewed instructions, direct reads and reference metadata match | 1,464 |
| Reviewed instruction bytes changed | 45 |
| Code size changed; new local mapping not performed | 25 |
| Exact signature missing | 8 |
| Reference metadata changed | 1 |

These counts measure selected evidence, not completed mechanics. Address-taken data, native targets, callers, inherited implementations and dependency behavior can change independently.

The main **engine.tick** and **gearbox.tick** both pass the local checks. Each nevertheless has three changed bytes outside the reviewed instructions/direct reads. Those bytes remain unclassified; they are not declared harmless padding. Their complete dependency chains still require current-build review. Fresh exports of both methods are available, but this checkpoint does not claim a full new reading of their C bodies.

## Track rollers now use the shared wheel element

Current reflection and fresh code establish a structural refactor:

| Type | Archived size | Current size | Relevant change |
| --- | ---: | ---: | --- |
| Shared wheel element | 736 | 744 | Adds `m_is_rotation_locked` at byte 512 |
| Fixed roller component | 984 | 1,720 | Embeds shared wheel at byte 632 and its definition at 1,376 |
| Suspension roller component | 1,032 | 1,720 | Now derives from the fixed roller class |
| Ordinary wheel component | 1,504 | 1,512 | Following fields shift with the embedded wheel layout |
| Landing gear component | 1,272 | 1,280 | Following fields likewise shift |

The suspension roller's former separate update implementation is absent from its own current declarations; its base is now `roller_wheel_fixed`. This is inheritance/refactoring evidence, not removal of the playable roller.

The fresh fixed-roller update calls `is_node_part_of_belt_loop` for torque node zero, then writes the inverse result to component byte **0x478**. Reflection resolves that location exactly: embedded wheel **632** plus lock field **512** equals **1,144 / 0x478**. It invokes the shared wheel update and reports torque-node RPS only while unlocked; otherwise it reports zero.

Two selected sections of the shared wheel update independently require a non-null torque node and a false rotation lock:

- Reading torque-node RPS for the rotation term; the reviewed sign multiplier is **-1.0**, not an inferred angular-unit conversion.
- Applying contact-derived torque feedback to that node.

Contact-force/impulse handling continues outside the second gate. A locked roller is not therefore proven to have no contact force or friction. The full shared contact/slip/load calculation remains open. For track design, the verified dependency is that belt-loop recognition affects these rotation and torque-feedback paths; no in-game tracked vehicle test was performed.

## Body recreation and native mass wrappers

The current body-creation wrapper was read in full. Existing objects outside the scene receive shape/motion/group updates, are added, then receive the transform. Existing added objects receive shape/motion/group updates, nearby-object activation and a transform update. The archived wrapper already contains these branches; this checkpoint does not label them new fixes.

After rebuilding constraints, numeric motion **0** (the reflected `dynamic` label) selects angular damping and the maximum-angular/linear-velocity setter calls. One literal address serves two typed uses: its first four bytes represent integer **0**, while its eight-byte floating value is **0.5**, the damping argument. Treating the integer comparison as a zero-valued damping constant would be wrong. The velocity globals' values and downstream native behavior are not established here.

Fresh native registration instructions connect `physics.object.get_mass` to RVA **0x14aa70** and `set_mass` to **0x14b4c0**, including both registration-store branches. The getter promotes a returned **f32** to the script's **f64** result. The setter converts its f64 argument to f32 before storing/passing it. When the returned reference scalar is positive, it scales twelve floats by requested/reference before forwarding the result. Full virtual-target/callee contracts remain open; no native solver equivalence or safe arbitrary mass range is claimed.

## Verification and next work

The fresh reflection index reads **8,090 descriptors / 7,639 structures / 451 enums** through the declared table end. Two duplicate pointer names remain explicitly ambiguous. Internal added type names alone are not new playable-component evidence.

The separate current-build reader contains **12 freshly exported methods, 8,099 checked instructions and 51,029 instruction bytes**. Availability is distinct from full review. The registry and two mass-wrapper exports also pass their selected source-byte/bounds checks. Installed GCL/PE hashes and all **2,968 cataloged definition files** match the snapshot at final verification.

Ten comparison regression tests bring the research suite to **277 passing tests**. They cover rebasing, instruction/read/reference changes, unclassified bytes, size mismatch and rejection of invalid archived evidence. They validate the research tool, not gameplay.

Next: finish current-build wheel/roller/contact interpretation, then follow complete powertrain, liquid/gas/thermal, electrical and driving-control chains. Continue plates, edges, attachment integrity and creation mass reconstruction where needed for reliable builds. Flight and marine systems remain in the vehicle queue. No game execution, installation edit or active-save modification occurred.
