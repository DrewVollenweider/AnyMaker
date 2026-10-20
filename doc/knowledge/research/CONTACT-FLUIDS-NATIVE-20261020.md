# Wheel contact, gas circulation, heat and selected native helpers

Build **25904830**, 2026-10-20. These are static findings from the matching isolated GCL and executable. No game, installation or active save was changed or executed. The full-game audit remains active and incomplete; [the register](AUDIT-REGISTER.md) retains every system and earlier research subject.

The practical additions are suspension and tyre arithmetic, pressure-operated wheel brakes, a significant gas-temperature overload difference, exchanger coefficients, world fluid sampling, and verified native vector/math helper bodies. The source-bound reader now contains **1,074 selected functions, 149,292 byte-checked instructions and 849,610 instruction bytes**. It retains 7,361 slot-derived dependencies and 5,989 unresolved indirect sites. Exporting actuator methods makes them accessible; it does not establish their behavior.

Evidence: [GCL identities/scalars/calls](versions/build-25904830/contact-fluids-native-20261020/evidence.json), [declared fields/enums](versions/build-25904830/contact-fluids-native-20261020/reflection-evidence.json), [tyre lookup](versions/build-25904830/contact-fluids-native-20261020/tyre-calibration.json), [selected native registrations](versions/build-25904830/contact-fluids-native-20261020/native-evidence.json), and [verification](versions/build-25904830/contact-fluids-native-20261020/verification.json). Exact byte checks support source identity; they do not automatically prove the prose interpretation.

## Wheels and suspension

`server_scene.vehicle_element.wheel.tick` **58495995** is the shared wheel-contact implementation. Track rollers use separate implementations. The contact radius is the maximum of the component definition's radius and its fitted accessory's lookup radius. An unmatched accessory ID returns radius zero, leaving the component minimum effective. The [26-entry table](versions/build-25904830/contact-fluids-native-20261020/tyre-calibration.json) preserves actual IDs, including `wheel4x4`, rather than deriving dimensions from names or meshes. For example, `wheel_truck` has lookup radius 0.73 and thickness 0.7, while the two truck inner/outer pairs use radii 0.56 and 0.62. Thickness is a separately retrieved value.

The suspension ray has length travel plus radius. Its hit filtering excludes the vehicle itself and physics groups named rope, effect, character, ragdoll and buoyancy_volume. It then uses the first retained result. The underlying native cast's ordering is still unknown; this is not proof of a globally nearest-hit guarantee.

For positive travel, let d be hit distance, R effective radius, x previous compression, s/ds the stiffness/damping settings, and k/dk the corresponding definition coefficients:

```text
c = clamp(1 - max(0, d-R)/travel, 0, 1)
K = k × 4 × s²
D = dk × 8 × ds²
base_load = K × (c + c³ × bump_stop_scale) + D × (c-x)
```

The normal contribution adds a roll-damping term derived from angular point velocity, clamps the resulting scalar below at zero, and multiplies by body mass clamped to 1..1000. The damping difference in this expression has no explicit division by dt. A previous sufficiently long normal is interpolated toward the hit normal by 0.3 and normalized; otherwise the new normal is copied. No hit extends suspension by 0.005 per update, up to travel, and clears the contact/memory state.

Grip uses nonnegative base load separately. Its remembered average interpolates by 0.003 when the previous average is positive; otherwise it takes the new load. With load L, updated average A, and definition sensitivity S:

```text
variation = clamp(L/max(0.0001,A) - 1, -1, 3)
effective_grip_load = L × max(0.2, 1-S×variation)
```

The candidate friction vector is projected away from the contact normal, then limited by a friction circle using effective load, adjusted friction/mu and clamped body mass. With no tyre ID, grip_friction is multiplied by 0.35, memory_friction by 0.2, mu by 0.6 and memory_tether_range by 0.3. Missing tyres therefore affect more than radius.

Contact memory is expressed relative to the support object, advances with signed circumferential wheel motion and uses a limited tether plus a derivative contribution. Full vector reduction and moving-support behavior remain open. Skid flags include requested tangent magnitude above 1.5 times the cap or tether excess above 0.04. Shaft reaction uses the contact tangent projection times radius before a 0.9 multiplier applied to the body-side contribution. Dynamic support reaction is further scaled by `clamp(support_mass/vehicle_mass,0,1)`; equal/opposite magnitude cannot be assumed for all masses. Native force units and the complete physics solver remain unresolved.

## Truck wheel brakes and track dimensions

`wheel_hydraulic.tick` **58094140** obtains a gas pressure and writes:

```text
brake = 1 - clamp((pressure-4)/(6-4), 0, 1)
```

Thus pressure at or below 4 applies full brake; at or above 6 releases it. These are native pressure values, not an established bar/psi conversion. Steering maps hydraulic extension through `2×extension-1`, clamped to -1..1. The component invokes shared wheel contact before updating its new brake and steering values in this method; full network/solver scheduling is a separate question. This explains why a pressure supply can be necessary even when the drivetrain is otherwise connected, without retroactively changing the earlier user-confirmed handbrake diagnosis.

Actual large and small roller/sprocket variants use shared radius globals of **0.34** and **0.18** respectively. Track width globals derive from the 0.08 building unit: narrow `2×0.08-0.04 = 0.12`, normal `4×0.08-0.04 = 0.28`, wide `8×0.08-0.04 = 0.60`. Base-class placeholders are not actual variant calibration. Complete roller contact, belt tension and track assembly dynamics remain pending.

## Gas content and equalization

The declared gas species are air and exhaust. Liquid labels are water, petrol, oil and pollutant. The earlier engine path's conversion from species 2 to 3 is therefore oil to the declared pollutant species; its role in that path is contaminated oil, not a reason to rename the enum globally.

Gas pressure is quantity/capacity, with a nonpositive-capacity guard returning zero. `move_content` **58576281** caps a requested positive movement by source quantity, but has no destination-capacity cap in this helper. Species move proportionally; destination temperature mixes by incoming quantity and source temperature remains. `modify_content` **58575275** adds its signed amount without a lower clamp in this helper; positive additions invoke temperature mixing. Caller validation and ordinary-state assumptions must remain separate.

Two gas equalization overloads differ:

| Method | Species/quantity redistribution | Temperature writes |
| --- | --- | --- |
| Pair, **58571899** | Capacity-proportional | Preserves each input temperature; no writeback to either +0x30 field |
| Vector, **58569300** | Capacity-proportional | Assigns a shared quantity-weighted temperature |
| Liquid pair, **58730228** | Capacity-proportional | Assigns both temperatures |

The gas pair computes a temporary temperature but does not store it back. Assembly corroborates the missing field writes; this is not simply a pseudocode naming difference. Earlier liquid equalization findings remain applicable to their overload. A single generic equalization model would erase a real implementation distinction.

Gas pre-build caches node pressure/quantity and clears flow. Local graph reconstruction considers facing/origin-grid adjacency and explicit links; flood forms component islands and cross-body gas connections merge groups. Post-build **58616162** sums group quantity/capacity, computes target pressure, collects excess gas and distributes deficits. No explicit rate coefficient was found in this reviewed passive redistribution pass. Content-pointer aliases, all empty cases, ordering across components and the complete network remain open, so this does not establish unlimited instantaneous throughput for every device.

Gas capacity creation uses the selected inspection shape rather than the generic inclusive zone-volume helper: stretched box extent product, or capsule cylinder-plus-sphere volume, scaled by 0.5 L per grid voxel. Unsupported shape/missing inspection-ID paths log an error. Full shape selection and stretch behavior still need completion before treating this as a universal capacity generator.

## Heat exchange and world sampling

Shared helper **63541757** computes a quantity-weighted temperature mean and interpolates both inputs toward it by the supplied factor, when total quantity is positive. Gas/gas **58553453**, gas/liquid **58554079** and liquid/liquid **58718124** wrappers pass the same quantity/temperature fields. These wrappers introduce no species-specific heat capacities. For ordinary factor f between 0 and 1, quantity-weighted temperature is conserved and the temperature difference becomes `(1-f)` times its previous value. This is not a claim about SI thermal energy.

The native helper does not clamp f. The three exchanger ticks use:

```text
f = 0.003 × round(local_AAB_Z_span/0.08)
ambient_temperature_interpolation = 0.0002
```

Their cross-side temperature blend does not mix species. The length comes from the local AAB's Z span, not whichever dimension appears longest in a screenshot. Content-volume updates and ambient exchange are additional steps; full equilibrium under every flow state remains unreviewed.

World gas sampling **47260216** constructs capacity/quantity 500 with 499 air and 1 exhaust, and a weather/time-derived temperature. This helper has no submersion branch. It does not prove all intake devices can function underwater: their own availability and placement paths still matter. Gas vents and the air filter call world sampling and the pair equalizer, whose temperature-write distinction applies locally.

World liquid sampling **47262318** sets capacity 1000. Its submerged branch sets total/water quantity to 1000 and gets temperature from weather/time. The non-submerged branch does not explicitly clear all caller content in this method; caller initialization remains relevant. Avoid interpreting split integer pieces of a double constant as an independent zero-volume literal. Liquid vents use the liquid pair equalizer.

Gas pump and centrifugal pump branches have been read sufficiently to establish that they are distinct: the former uses signed shaft speed with a reverse flag, while the centrifugal branch uses absolute speed, a pressure-head difference and a separate reverse-flow path. The first path debits load from its candidate amount before an adverse-pressure reduction. Full coefficients, all reverse/empty cases, network scheduling and display pressure units remain queued; no complete pump model is claimed here.

## Native vector and math helpers

The isolated matching `game.exe` SHA-256 is **5c46cd34a3b00889ff36154976428ba43f6475430e92a2d113a360a78161a7d0**. New read-only tools [`native_image.py`](../../../scripts/research/native_image.py) and [`native_export.py`](../../../scripts/research/native_export.py) parse bounded PE32+ x64 sections/exception records and export selected native spans through existing Ghidra. They never execute the source executable. Manual leaf spans retain an explicit warning that they are not recovered complete function boundaries.

The native index contains 12,669 exception-directory entries, 1,207 signature strings and 1,175 relative-byte-pattern leads. Leaf functions can lack exception entries. Pattern leads can be false positives and do not prove a binding. Registration routines copy some signature text using SIMD loads, so scanning only LEA references would miss real registrations.

Selected registration bodies were followed from literal construction through both target-pointer store branches and the selected helper bodies. Five examples are retained in native evidence; this is corroborated selected registration, not complete boot/loader/ABI recovery:

| Native RVA | Reviewed helper behavior |
| --- | --- |
| `0x2c280` | Default vec3 stores three 64-bit zero coordinates |
| `0x2c290` | Explicit vec3 writes scalar arguments in x/y/z storage order |
| `0x282a0` | Default vec3_s32 stores three 32-bit zero coordinates |
| `0x38b30` | f64 clamp is min(max(value,lo),hi) for ordinary finite inputs |
| `0x38bb0` | f64 lerp is first + (second-first)×factor |

Additional selected bodies implement inverse interpolation `(value-lo)/(hi-lo)` and its 0..1-clamped version. Their full registration/loader chain and zero-width/NaN edge cases remain outside the selected binding claims. This constructor evidence resolves the earlier vector-default uncertainty for these native helpers. It also corroborates the earlier jet exhaust tuple **(0,800,800)** as actual coordinate order; it does not establish the force intrinsic's units or excuse replacing the tuple with a conventional axial force.

The production native exporter checked ten selected spans, **4,303 instructions / 18,570 instruction bytes**, against the original PE mapping. Full native C/assembly/databases remain local. The original PE-loader function-overlap probe failed; a corrected exporter reused existing function entries and the production run succeeded. Failed probe output is not counted as a successful export.

## Validation and remaining work

[`contact_models.py`](../../../scripts/research/contact_models.py) and [`gas_thermal_models.py`](../../../scripts/research/gas_thermal_models.py) encode selected ordinary arithmetic with explicit model guards. Nine contact tests include 500 seeded friction-circle cases; six gas/thermal tests include 1,000 seeded conservation/temperature cases and an overload counterexample. Seven PE-parser tests cover malformed/truncated mappings and ambiguous exception entries; four native-export tests cover bounded selection and source/artifact tampering. The complete research suite has **127 passing synthetic tests**. These tests do not execute the game.

One constraint scalar was also recovered: `g_constraint_break_force` initializes to **100000**. `hinge_pin.tick` compares native position/rotation lambda lengths strictly above this threshold before disconnecting. Without the native solver contract, this is not an established 100000-newton breaking strength. Other actuator exports are available but still require semantic review.

Continue with full track contact and moving-body/actuator ownership, then complete controls/sensors/data, script/compiler/native physics, world/actors/combat, save/multiplayer authority and assets/UI/audio. Existing edge/plate, engine and historical creation findings remain in scope. Neither the reader count nor a passing schema audit establishes that a creation, every class or the whole game is understood.
