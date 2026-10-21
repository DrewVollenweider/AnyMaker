# Vehicle primitive mass, compound inertia and tank lifecycle

2026-10-21; build 25904830. GCL SHA-256 `626a994be960b7218409d9ca416d2664450231d1fc3295036fc77c81b8449355`; isolated PE SHA-256 `5c46cd34a3b00889ff36154976428ba43f6475430e92a2d113a360a78161a7d0`. Continues [body mass and ballast](BODY-MASS-20261021.md). No game execution or installation/active-save changes.

## What this adds for vehicle building

The native primitive mass methods and selected compound assembly path now support an offline helper for explicit shapes, positions and rotations. This helps compare packaging choices and rotational inertia before building. It is **not yet a complete creation-file mass estimator**: component collision zones, eligibility, hull integration, separate bodies and all creation transforms must still be reconstructed.

The reviewed compound path adds each accepted child's mass independently. It rotates each child's inertia and adds its contribution from its displacement relative to the compound centre. It does not calculate a geometric union in this mass method. Consequently, coincident or overlapping child shapes can still contribute independently; visible exterior volume alone is insufficient for mass estimates. This conclusion concerns accepted compound entries, not every upstream placement/deduplication rule.

## Primitive formulas

The binding chain is the previously traced native wrapper, settings table factory at slot `+0x18`, constructor assignment of the actual shape table, then shape mass-properties slot `+0x38`. Settings tables and actual shape tables are distinct.

| Shape | Actual table RVA | Mass method RVA |
| --- | --- | --- |
| Box | `0x54f0c0` | `0x22f890` |
| Sphere | `0x4ed658` | `0x2131e0` |
| Capsule | `0x54e250` | `0x210260` |
| Convex hull | `0x54f338` | `0x2344e0` |
| Selected compound | `0x551040` | `0x283630` |
| Transformed child | `0x551800` | `0x2ac280` |

For full box side lengths x/y/z and density coefficient rho:

```text
m = x*y*z*rho
Ixx = m*(y*y + z*z)/12
Iyy = m*(x*x + z*z)/12
Izz = m*(x*x + y*y)/12
```

The native box constructor stores half extents; its mass method doubles them back to full lengths. These inertia values are about the primitive's centre in its local axes. Convex collision radius/margins are not added as extra volume by this selected formula.

For sphere radius r:

```text
m = (4*pi/3)*r^3*rho
Ixx = Iyy = Izz = (2/5)*m*r^2
```

For a capsule along local Y, L is the **cylinder length**, excluding both end caps. The wrapper halves its length argument before storing native half length. Let mh be one hemisphere's mass and mc the cylindrical section's mass:

```text
mh = (2*pi/3)*r^3*rho
mc = pi*r^2*L*rho
m = 2*mh + mc

caps_axial = (4/5)*mh*r^2
cylinder_axial = (1/2)*mc*r^2
Iyy = caps_axial + cylinder_axial
Ixx = Izz =
    ((3/4)*L*r + (1/2)*L^2)*mh
    + caps_axial + mc*L^2/12 + mc*r^2/4
```

These are interpretations of the selected native arithmetic. The executable uses f32 constants and operations. The helper retains the compiled pi-related constants but uses Python float arithmetic; it does not emulate all native rounding, input narrowing, overflow or solver storage.

### Zero-length capsule factory boundary

With positive radius and native half length exactly zero, the settings factory creates a **sphere and writes density 1000**. The positive-length capsule branch copies the supplied settings density. Raw selected instructions verify the constant write and the alternate density copy.

This makes a literal zero-length request with density 400 differ from the positive-length capsule's limiting mass as length approaches zero. Normal game reachability of this boundary has **not** been established, so this is not reported as a gameplay bug. The helper models explicit zero length separately; it does not emulate f32 underflow of very small positive input into that branch.

## Compound centre and inertia

The registered compound APIs are now traced through literal construction and both registration pointer-store branches:

| API path | Registered RVA | Selected implementation |
| --- | --- | --- |
| Scene compound object creation | `0x14b250` | `0x110f00` |
| Object compound shape replacement | `0x14c870` | `0x10ee60` |
| Compound add-shape | `0x14de40` | `0x10e040` |

Add-shape appends a child and its twelve f64 transform values. Creation/replacement converts position and rotation to native f32 child settings. The compound settings factory handles zero entries as an error, optimizes a single identity child, wraps a single transformed child, and constructs the reviewed multi-child compound for larger counts.

Selected child setup `0x2885b0` obtains the child's centre, rotates it and adds the child translation. The reviewed compound constructor prefix accumulates mass-weighted centres, divides by positive total mass, then recentres its stored child coordinates. Its centre accessor returns that cached centre. The constructor's remaining spatial-tree construction is not claimed complete.

The complete selected compound mass method obtains each child's mass properties, rotates its inertia, applies the displacement term and sums:

```text
M = sum(mi)
C = sum(mi*ci)/M
di = ci - C

I = sum(Ri*Ii*transpose(Ri) + mi*(dot(di,di)*identity - outer(di,di)))
```

The transformed-child mass method rotates its child's tensor. The reviewed complete compound method spans three adjacent PE exception-directory ranges; selecting only its first range yielded a prefix, not a full verified body. The final evidence includes the complete reviewed manual span and explicitly identifies the superseded prefix. The same distinction applies to the shape replacement helper.

The hull mass method scales a cached coefficient and matrix by density. The full constructor/integration algorithm producing those cached quantities remains open; no arbitrary convex-hull volume calculator is supplied here.

## Tank lifecycle

The new GCL wrappers complement the prior ballast trace:

- `liquid_tank.create` (56392986) calls the base create method, resolves its grid origin/direction, and delegates to its content volume's create method. Complete initial content defaults are not established by this wrapper.
- `destroy` (56394328) conditionally removes and destroys the constraint, then conditionally removes and destroys the fluid body, and finally invokes base destroy.
- `post_load` (56400432) and `remap_ids` (56401051) both dispatch to `_rebuild_fluid_physics`, rather than merely patching an existing ballast object's IDs.

This closes selected lifecycle callbacks, not every save/split caller, native constraint contract or fluid simulation path. [The preceding checkpoint](BODY-MASS-20261021.md) remains the source for periodic ballast updates and fluid coefficients.

## Helper, evidence and validation

New [mass_properties.py](../../../scripts/research/mass_properties.py) version 1.0.0 exposes `box`, `sphere`, `capsule_y` and `combine`. The latter accepts explicit child COM coordinates and proper orthonormal row-major rotations, returning total mass, centre and a symmetric 3x3 inertia tensor. It does not interpret native matrix serialization or infer geometry from a saved creation.

Eighteen new tests cover independently derived hemisphere integrals, box/sphere values, density/length scaling, the zero-length factory exception, weighted centres, parallel-axis terms, oblique rotation, off-diagonal signs, overlap, input preservation and model guards. The full research suite passes **222 tests**. An initial exact decimal assertion failed on 0.5120000000000001 versus 0.512; only its tolerance was corrected, and the failed private log is preserved.

Selected evidence: [GCL identities and calls](versions/build-25904830/mass-properties-20261021/evidence.json), [native bindings, table slots, typed constants and span checks](versions/build-25904830/mass-properties-20261021/native-evidence.json), and [fresh verification](versions/build-25904830/mass-properties-20261021/verification.json). Twenty-eight checked export spans include a reused assembly-only registration export and superseded prefixes; this is not 28 unique, completely understood functions.

Reader coverage is **1,543 functions / 233,869 instructions / 1,329,154 independently summed instruction bytes**. These are access/verification counts, not a semantic completion percentage.

The full research goal remains incomplete. Next vehicle priorities are remaining hull/shape and creation mass integration, then open powertrain, fluid/thermal, electrical/control, suspension and aircraft/marine chains. Combat, projectiles, explosions and AI remain parked under the user's vehicle-first priority.
