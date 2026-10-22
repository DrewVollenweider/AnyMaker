# Current wheel contact, suspension and belt recognition

Build **26113663**, 2026-10-22. This continues the [vehicle update](VEHICLE-UPDATE-20261022.md) using the matching isolated GCL, SHA-256 `a3fd2df2fd62e38b629f6a0df824269a34d77d57caf66d596362d7e5e53c3b22`. Vehicle engineering remains first; the full audit remains incomplete. No game execution, installation edit or active-save change occurred.

Evidence: [function identities, typed constants, selected calls/instructions, layouts and roller definitions](versions/build-26113663/contact-tracks-20261022/evidence.json), plus [verification and test limits](versions/build-26113663/contact-tracks-20261022/verification.json). Full game exports remain local.

## Tyres, integral treads and roller travel

The shared wheel update was read in full. Its tread-present condition is **a nonempty accessory ID OR definition flag `m_is_tread_integral`**. The new flag is at definition byte 320; the definition grows from archived size 320 to 328. The base wheel-definition constructor sets it false, while fixed-roller creation sets it true. Suspension rollers inherit the fixed implementation.

Without either kind of tread, the shared calculation multiplies grip friction by **0.35**, memory friction by **0.2**, friction-circle mu by **0.6** and memory tether range by **0.3**. Integral rollers therefore avoid these bare-wheel reductions without needing a tyre accessory. This condition is not a universal check that an accessory ID is a valid compatible tyre.

The tyre-radius lookup searches by exact ID and returns zero if unmatched. Effective radius is the maximum of that result and the component definition's radius. A fitted wheel's `m_is_damaged` flag multiplies its shaft-derived rolling term by **0.2**; the undamaged factor is 1. This affects the term used for contact motion and replicated wheel rotation, not a proven global 80% engine-power loss. Rotation locking still gates the shaft-derived term and torque feedback as described in the previous checkpoint.

The grid initializer is **0.08 m**. Current travel values are:

| Creation ID | Server class suffix | Travel |
| --- | --- | ---: |
| `roller_wheel_suspension_a` | small_narrow | 0.08 m |
| `roller_wheel_suspension_b` | large_narrow | 0.08 m |
| `roller_wheel_suspension_c` | small | 0.16 m |
| `roller_wheel_suspension_d` | large | 0.24 m |
| `roller_wheel_suspension_e` | small_wide | 0.16 m |
| `roller_wheel_suspension_f` | large_wide | 0.24 m |

Fixed rollers return one grid unit, **0.08 m**, as shared-contact travel. The suspension base-class placeholder returns zero; the six shipped suspension classes above override it. A placeholder is not actual variant calibration.

Fixed creation sets zero steering limits, damping **0.1**, tether **0.16**, bump-stop scale **1**, roll damping zero and integral tread true. The generic wheel-definition constructor separately declares stiffness **0.15**, damping **0.3**, travel **0.1**, tether **0.02**, grip **1**, memory friction **10**, mu **2**, load sensitivity **0.25**, bump-stop scale **4** and roll damping zero. These generic defaults are not a claim that every wheel variant retains them.

## Contact and moving-support memory

The suspension ray length is travel plus effective radius. Filtering removes the vehicle itself and groups rope, effect, character, ragdoll and buoyancy volume. The code then selects the first retained hit. Current native hit ordering was not revalidated here.

The [earlier suspension equations](CONTACT-FLUIDS-NATIVE-20261020.md#wheels-and-suspension) are visible again in the fresh current body: squared stiffness/damping settings, compression clamping, cubic bump stop, compression-difference damping, nonnegative normal contribution and body mass clamped to **1..1000**. Grip uses nonnegative base load separately from the roll correction, updates its remembered load by **0.003**, and applies the sensitivity floor **0.2**. This is selected current arithmetic, not complete native-physics equivalence.

Two tangential contributions precede the friction circle:

1. **Contact displacement:** for the same added support object, the previous support-local contact position is compared with the new local hit and rotated into the current world frame. The code subtracts that movement from signed circumferential wheel travel, then removes the normal component. Circumferential travel includes **2 × pi × radius × server delta time**. For positive compression it limits displacement length to **0.4**, multiplies by **20 × adjusted grip × effective grip load × clamped body mass**, and applies a fade factor `clamp(0.1/original_length,0,1)` for nonzero length.
2. **Tether memory:** changing/losing an added support resets its remembered anchor. Otherwise the anchor moves with the support transform and advances along the normalized cross of contact normal and wheel-side direction. It is constrained to the adjusted tether radius. With positive compression, the contribution uses anchor error plus **10 times the side-axis projection of the error change**, multiplied by adjusted memory friction, effective grip load, clamped body mass and the fade factor above. The prior error is retained for the next update.

The direct-motion basis and normalized tether-motion basis are distinct. These steps are not a generic one-variable slip model. After combining them, the code projects away the normal and caps magnitude at:

```text
adjusted_mu × adjusted_grip × effective_grip_load × clamped_body_mass
```

Skid conditions include requested tangent magnitude above **1.5 times** that cap, or tether excess strictly above **0.04 m**. No hit increases suspension extension by **0.005 m per update**, up to travel, and resets the contact object/normal and the shown memory state.

When shaft feedback is enabled, the update projects the combined contribution onto the normalized contact tangent and multiplies by radius before calling `apply_torque`. The body-side contribution is subsequently multiplied by **0.9**, then by server tick rate before `impulse_activator.add_force`. The supplied position is the suspension-ray origin. Support reaction additionally uses a support/body mass ratio clamped to 0..1; equal/opposite magnitude must not be assumed for every mass combination. Native force units, complete activator/callee behavior and all lifecycle/exceptional cases remain open.

The initial integer server tick rate is **60**, the floating rate converts it, and delta time initializes as its reciprocal. This is initializer evidence, not a measured runtime frame rate or proof that globals cannot later change.

## Belt recognition is not proof of physical closure

The roller's recognition helper first resolves an initial belt link using the owning component, transformed surface position and extended logic-node positions. It appends the link's two endpoint IDs to a fresh vector, then walks from the opposite endpoint. At each step it excludes the current link and counts matching other links:

- Exactly one: follow it, or accept if it returns to the starting link.
- More than one: reject that traversal as ambiguous.
- None: accept only when the accumulated vector still has **two entries**; otherwise reject.

Consequently a single link can be accepted. More subtly, an immediate dead end can be accepted even if other links connect behind the starting endpoint. For links `(0,1), (0,2)`, starting at endpoint 0 of the first link accepts; starting at endpoint 1 follows the second link and rejects at the later dead end. The initial matching-link order and start endpoint therefore matter. This refines the previous shorthand “belt loop”: a true helper result does not prove an enclosed track or valid belt tension/geometry.

New [belt_topology.py](../../../scripts/research/belt_topology.py) models this walk **after explicit start-link/side resolution**. It accepts supplied endpoint tokens, assumes a fresh empty output vector and excludes self-links from its model domain. It does not parse creations or certify placement. Eight tests include **384 comparisons** against an independent degree-based oracle over all nonempty simple graphs on four vertices, both start orientations, plus parallel links and a dedicated first-dead-end counterexample.

The initial oracle wrongly required a one-link connected component for the two-entry exception. That test failure exposed the endpoint-dependent acceptance above; the source-shaped walk already returned true. The oracle and notes were corrected, the counterexample retained, and the final full suite passes **285 tests**.

## Pressure-operated truck brakes and next work

The current hydraulic-wheel update preserves:

```text
brake = 1 - clamp((gas_pressure - 4)/(6 - 4), 0, 1)
steering = clamp(2 × hydraulic_extension - 1, -1, 1)
```

Pressure at/below 4 applies full brake; at/above 6 releases it. These are internal pressure numbers, not a new bar/psi conversion. Shared wheel contact runs before this method writes the new brake/steering values. Its brake-temperature factor retains **0.999** of the old value, adds `abs(RPS × brake × 0.002)` and clamps to 0..1. This is a factor, not degrees Celsius.

Fixed roller geometry uses dynamic mesh index 0 for belt data and a zero-position wheel transform; suspension rollers use dynamic mesh index 1 for both belt center and wheel-transform position. Both transform wrappers select the reflected `z_neg` surface rotation. The retained definitions preserve omitted position fields as omitted rather than manufacturing offsets.

This checkpoint adds **25 fresh helper methods** and a full reading of the shared wheel update. The separate current reader now holds **37 methods / 10,548 checked instructions / 64,882 instruction bytes**; availability still exceeds full semantic review. Installed code and all 2,968 cataloged definition files match the snapshot. Continue current engine/gearbox supply, fluid/gas/thermal and electrical/control chains, retaining the remaining solver, belt-force, structural, flight and marine questions.
