# Hydraulic cylinders, track contact and native raycast ordering

Build **25904830**, 2026-10-20. The [full-game audit](AUDIT-REGISTER.md) remains active and incomplete. This continuation follows the [contact/fluid/native checkpoint](CONTACT-FLUIDS-NATIVE-20261020.md), using matching isolated inputs without executing the game or editing installation/active saves.

The current GCL reader contains **1,093 selected functions / 149,791 checked instructions / 852,045 instruction bytes**. New exports close cylinder-size and initialization gaps; previously exported methods were reused for the larger behavior chains. Selected evidence and [verification](versions/build-25904830/actuators-tracks-raycast-20261020/verification.json) retain exact source identities and explicit limits.

## Cylinder quantities and update order

`server_scene.vehicle_element.hydraulic_cylinder.tick` **58325834** has two liquid contents, a nominal capacity C and an extension factor e. Before correcting e, it writes the chamber capacities using the incoming measured extension:

```text
capacity_A = C × e
capacity_B = C × (1-e)
```

For positive C and ordinary nonnegative quantities A/B, its extension correction is:

```text
if A+B <= C:
    corrected_e = clamp(e, A/C, 1-B/C)
else:
    corrected_e = A/(A+B)
corrected_e = clamp(corrected_e, 0, 1)
```

It then updates each liquid-volume pressure plane. Those volume updates calculate motion/level/overfill effects; they do not transfer liquid between the two chambers in this method. The capacity writes precede extension correction, so substituting capacities derived from corrected_e changes the reviewed update sequence.

Consequences within these ordinary assumptions:

- With both chambers empty, the quantity bounds allow the measured extension anywhere in 0..1.
- With A+B exactly C, the permitted extension collapses to A/C.
- With A+B below C, the permitted interval has width `1-(A+B)/C`.
- With A+B above C, the branch uses A/(A+B), rather than rejecting or deleting the excess here.

These are arithmetic consequences, not proof of real hydraulic compressibility, finite actuator strength, the native constraint solver or every zero/negative/invalid-state path. The native element has no equivalent of the model's positive-capacity guard in the reviewed calculation. Its capacity and extension setters store their arguments directly.

## Geometry and size variants

The connector's **55396282** update derives maximum length L from saved `length_max × 0.08`. With size-dependent margin m:

```text
stroke = L/2 - m
measured_e = (anchor_distance - stroke - 2m)/stroke
C = L × litres_per_meter
target_distance = 2m + stroke + stroke × corrected_e
```

The resulting ordinary distance range is **L/2+m .. L**. Capacity uses L, not the shorter geometric stroke. Do not infer a real piston cross-sectional area by replacing this formula.

| Cylinder base class | Litres per metre getter | Margin getter |
| --- | --- | --- |
| Base | 8 | 2 building units = 0.16 |
| 2×2 | 16 | 2.5 building units = 0.20 |
| 3×3 | 24 | 3 building units = 0.24 |

These six native getters agree with the shipped 8/16/24 L per metre descriptions. The saved parser defaults `length_max` to **8**, `extension_factor` to **0**, and connected IDs/node index to **-1**. It parses nested `hydraulic_cylinder` contents as `content_a`/`content_b`. Parser defaults are not a certificate for every editor length or loaded physical state.

For the default length field, L=0.64. The base size's stroke is 0.16, nominal capacity 5.12 and target range 0.48..0.64. The corresponding 2×2/3×3 target ranges are 0.52..0.64 and 0.56..0.64. These examples preserve the game's formulas instead of substituting a telescoping-ram model.

## Physical connection and cleanup

`connect_multibody` **55357000** checks that the base has no existing connected pointer and casts the target to the hydraulic connector family. On success it writes reciprocal component pointers and vehicle/component/node IDs, disables collision between the two physics bodies, derives anchor positions from actual extended logic nodes/transforms, creates a distance constraint and adds it to the physics scene. Both bodies are activated. Same-size placement/tool compatibility is a separate chain; the target family cast alone does not establish every mating rule.

The connector update measures the two anchors in their respective body transforms, applies the chamber calculation, then writes **equal minimum and maximum distance targets** to the native distance constraint. If the target changes by more than **0.001**, it activates both bodies. Its flow indicator uses the maximum of the two liquid-node flow fields divided by **0.002**, clamped to 0..1; it is not measured extension or an established pressure gauge.

`disconnect_multibody` **55372053** removes/destroys the constraint according to its actual added/created states, reenables the body-pair collision in that cleanup path, flags internal constraint rebuilding, activates bodies, clears reciprocal IDs and nulls both connection pointers. `post_load` **55380478** looks up the saved vehicle/component and requires the peer physics object to be in the scene and no already-created constraint before reconnecting. `rebuild_constraints` **55382964** preserves saved IDs across disconnect and attempts reconstruction.

The vehicle's `_rebuild_constraints_internal` **52577045** iterates component-reported connected components and disables collision between their body pairs. This is distinct from the structural edge/plate attachment graph. A hydraulic or torque connection must not be treated as proof that a component is welded to the intended body.

The component named `hydraulic_actuator` is also distinct from this two-body cylinder: its reviewed tick **55329901** samples liquid pressure, applies hysteresis and writes a mechanical control output. The earlier pressure-control findings remain applicable to that component; its name does not make it the cylinder constraint implementation.

## Roller and sprocket contact

Fixed roller **57333489** and suspension roller **57400851** contain their own contact calculations. They do not call the ordinary wheel-contact element. Both ask `is_node_part_of_belt_loop` **59219372** before taking driven shaft RPS; a false result selects zero RPS for the reviewed rolling calculation. Contact processing still runs.

The graph helper's name is stronger than its complete predicate: its ordinary walk requires one continuation at each traversed endpoint, but it also accepts the no-continuation case when the accumulated node list has exactly **two entries**. Branches and longer dead-end paths fail that branch. Therefore do not reduce this helper to a blanket requirement for a visually closed multi-wheel track. Its initial match also uses component/surface/node positions; the graph walk alone is not the complete native belt-placement rule.

Fixed roller travel in its compression calculation is one building unit, **0.08**. Actual suspension variants override their base's zero placeholder:

| Suspension roller | Large | Small |
| --- | --- | --- |
| Narrow | 0.08 | 0.08 |
| Normal | 0.24 | 0.16 |
| Wide | 0.24 | 0.16 |

Both reviewed contact methods use compression `clamp(1-max(0,hit_distance-radius)/travel,0,1)` and scalar load `0.1×compression + 0.2×change_in_compression`. Body mass is clamped to 1..1000. The derivative contribution can make this scalar negative; these methods do not use the ordinary wheel element's nonnegative normal-load expression.

Their slip path compares desired circumferential movement with support-relative contact movement, removes the normal component, limits displacement magnitude to **0.4**, and computes a grip multiplier equivalent to `clamp(0.1/slip_length,0,1)` for positive slip length. Selected constants include a 0.7 slip coefficient, an additional factor 20 and a 0.2 memory coefficient. Zero/degenerate vector handling remains an intrinsic boundary.

The memory branch uses a tether limited to **0.2**. Its selected direct/error-difference coefficients are **1 and 10** for fixed rollers, versus **10 and 100** for suspension rollers. Support-object changes reset/rebase remembered coordinates. These constants do not make either implementation a universal no-slip track model.

The fixed-roller method explicitly passes a tangent projection times radius back to `apply_torque`; the suspension-roller method has no corresponding call in its reviewed body. Both scale the body-side impulse by **0.9** and further scale the opposite support impulse by the clamped support/vehicle mass ratio. No claim is made that every other shaft/contact path is absent.

The sprocket's reviewed tick **57601755** reads/replicates shaft RPS and constructs transforms. It contains no equivalent ground-contact impulse loop. Traction in this reviewed chain belongs to the rollers; rendering, belt-loop geometry, construction validation, inconsistent cycles and full track durability remain unfinished.

## Native raycast ordering

The matching executable is unchanged from the previous report. The vector raycast signature is registered to native RVA **0x14ad30**, which forwards to **0x115ec0**. Its collector table at RVA **0x50bcc8** points to callback **0x117920** at slot +0x28. Selected signature-copy/target-store bytes, the table pointer and the callback/implementation bodies were checked separately.

The callback appends each hit, computes its distance, then moves it backward while the previous distance is greater. The comparison and backward swaps implement ascending distance order for ordinary finite hits; equal distances do not swap in this loop. The outer implementation copies this collector sequence to the caller's vector by appending. It does **not clear a preexisting output vector**.

The GCL constructor **31866574** initializes the wheel's local hit vector with count zero. The native generic iterator erase registration targets **0x3aef0**, which calls the index erase path at **0x3acb0**. That path shifts following records down and returns the same logical iterator position. The native generic family therefore preserves the ordered remaining sequence. Its template descriptor matches the GCL vector-erase family; the exact loader specialization remains unreviewed. Together these chains strongly support nearest-retained-hit selection for fresh wheel/roller lists in ordinary valid finite states; this last specialization link remains a stated inference.

This does not prove ordering for reused nonempty outputs, every cast overload, arbitrary invalid direction/length input or all native collision filtering. The single-hit overload at **0x14ad00 / 0x115bc0** was also inspected, but its complete backend semantics are separate.

Exception-directory entries are not necessarily complete function boundaries. Index erase spans **0x3acb0..0x3acc1** and **0x3acc1..0x3ad7d** are adjacent fragments: the first falls through into the second. Their combined instruction flow must be read together. Approximate C can extend beyond a selected fragment and can incorrectly label a boolean-returning function void when it misses a callee's register-preservation contract. The reviewed raycast return instructions were checked in assembly rather than accepting that C type.

## Tools, verification and continuation

[`actuator_models.py`](../../../scripts/research/actuator_models.py) keeps pre-correction capacity writes separate from the corrected extension target. Six tests cover empty/full/overfilled chambers, the allowed interval, 1,000 seeded feasibility cases, geometry inversion and model-domain rejection. The complete research suite has **135 passing synthetic tests**.

Native exporter **1.1.0** adds explicit `--assembly-only` mode. It records that pseudocode was not requested, requires a matching marker and false decompilation status, and still checks source/range/facts/assembly bytes. A failed C export cannot silently become a successful assembly export. Two new tests cover this distinction and invalid modes.

The full physics registration C export and an attempted smaller pseudocode fragment timed out and remain failed runs. Explicit assembly export of the bounded registration blocks succeeded; the shorter raycast/collector/vector helper C exports also succeeded. Full native output stays local. The [selected native evidence](versions/build-25904830/actuators-tracks-raycast-20261020/native-evidence.json) distinguishes registration, implementation, callback and fragment claims.

Continue the remaining hinge/latch/rail/tow/winch ownership and failure paths, complete belt construction/rendering and exceptional track behavior, then all controls/sensors/data, compiler/native physics, world/actors/combat, save/multiplayer authority and asset/UI/audio systems in the register. Selected coherent chains are progress, not whole-game completion or a new gameplay test.
