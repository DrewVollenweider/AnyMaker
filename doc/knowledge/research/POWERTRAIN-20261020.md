# Torque, electric machines, jet assembly and helicopter rotors

Build 25904830, researched offline on 2026-10-20. Source SHA-256 remains `626a994be960b7218409d9ca416d2664450231d1fc3295036fc77c81b8449355`. No game process, installation, creation or active save was modified or executed.

The torque solver now explains the shared effect of brakes and the ratio-dependent load seen during starter work. Rotor calculations and jet-chain validation are also accessible without asking the user to repeat gameplay tests. These are selected static findings; the [whole-game register](AUDIT-REGISTER.md) remains unfinished.

## Scope and evidence

The local reader now contains 611 unique functions, 103,166 byte-checked instructions and 597,691 instruction bytes. Two identical re-exports are deduplicated. New batches contain 136 component update methods, 77 torque/jet/rotor dependency methods and five calibration/input helpers, including one previously exported helper.

Every update target declared by all 224 recovered server-component types is now available: **156 distinct implementations**, including inherited implementations and compiled-only classes. The 208 types with shipped definitions include the generic root for four omitted-class definitions. A declaration/export is not a complete review of behavior or proof that a compiled-only type is creatable.

- [Component update map](versions/build-25904830/powertrain-20261020/component-tick-map.json): every type, shipped IDs and exact declared update identity; full behavior explicitly remains pending.
- [Code evidence](versions/build-25904830/powertrain-20261020/evidence.json): 238 selected function identities and 45 scalar constants.
- [Reflection evidence](versions/build-25904830/powertrain-20261020/reflection-evidence.json): 227 types, 88 named fields and 224 update declarations.
- [Verification](versions/build-25904830/powertrain-20261020/verification.json): completed checks and limits.

Full game code and databases stay local. Approximate C is interpreted alongside assembly, operand metadata and declared fields. Unresolved indirect dispatch, native math/physics intrinsic implementations and exceptional states remain separate boundaries. Arithmetic models assume the ordinary meaning of the named math helpers; their tests do not prove those native implementations.

## Shared shaft solver

Relevant methods: `vehicle_torque_node.apply_torque` 59208387; container `pre_build` 59266361, `build` 59246900, `_flood_island` 59236894 and `post_build` 59262886. Reflection names the node fields used below.

`apply_torque(A)` adds **A / node.mass** to pending `delta_rps`. It does not multiply by delta time within this helper. Callers that derive A from energy, impulses or another native quantity must supply their own scaling. The global named `g_torque_system_newtons_per_joule` initializes to **0.04**; its name is not a complete proof of SI torque or angular momentum.

During `build`, a nonzero vehicle-mass factor can replace node mass with `vehicle_mass × factor`, optionally limited by a positive maximum. Speed becomes:

```text
rps = (rps + pending_delta_rps) × 0.9998
pending_delta_rps = 0
```

This retention is per build, rather than an independently established per-second coefficient.

Flooding forms islands through adjacent nodes, internal torque links, registered cross-body torque connections and recognized belt loops. Adjacent and registered cross-body connections invert the propagated ratio; internal links multiply in one direction and divide in the other. Belt propagation uses signed pulley-size ratios. Already visited nodes are skipped. A complete certificate for inconsistent closed ratio loops and every belt geometry is still absent.

For a pre-established island, define for each node:

```text
q = node.gear_ratio × node.island_gear_ratio
c = node.clutch_factor
w = node.mass × c × q²
P = sum((node.rps × c / q) × w)
M = sum(w)
P = P × product(1 - node.brake_factor)
```

If M is positive, each node interpolates its speed toward `(P/M) × q`, using its own c. Assembly confirms **both clutch contributions**: one in w and another in the speed contribution. Do not replace this with a conventional physical clutch formula.

For fully engaged nodes with no brakes, the ordinary model preserves `sum(mass × q × rps)` across this post-build step and establishes equal normalized speed `rps/q`. The preceding retention and component loads are separate. Example: an unloaded 10 RPS node of mass 1 joined to a stationary mass-9 node at equal ratios settles to 1 RPS in that step. A ratio change changes the effective weight through q².

The brake pass multiplies the **shared numerator**. Two factors of 0.5 leave 0.25 of it; one factor of 1 zeros it. The pass includes zero-clutch nodes, even though their weights are zero. This is a reviewed code property, not a recommendation to create an unsupported configuration.

The handbrake component itself ramps a mechanical output toward 0 or 1 by at most **0.1 per update**. Wheel update code reads its brake input by magnitude and clamps it to 0..1 before setting the shaft-node brake factor. These traces are consistent with the historical user-confirmed release-to-drive result. They do not establish every brake wiring layout or a new driving test.

## Electric motors and alternators

Motor methods: `create` 56969898 and `tick` 56982406. Shipped electric motors A/B/C declare **10,000 / 60,000 / 120,000 W**, each with **30 RPS** maximum output. Creation sets the initial target to that limit and creates node mass from `wattage × 0.04 / server_tick_rate`.

Update clamps the target to ±the definition limit and the power factor to 0..1. The two reverse flags combine by inequality: matching flags preserve the target sign; differing flags invert it. The normalized demand starts as:

```text
demand = clamp((signed_target - shaft_rps) / maximum_rps, -1, 1)
```

If the shaft is already beyond the target in the target's direction, demand becomes zero. A zero target also suppresses this demand for either nonzero shaft direction. This branch does not implement regenerative braking.

Requested electrical energy is `definition_wattage × output_power_factor × power_factor × dt × abs(demand)`. The electrical network's accepted supply fraction scales both reported consumption and applied shaft quantity. The reviewed positive-supply branch sets node gear and clutch factors to 1. Remaining control bindings and exceptional power-loss transitions are not inferred solely from these two functions.

The shipped alternator declares **1,500 W** and **100 RPS** for maximum output. Its update uses the absolute speed fraction, so either rotation direction can generate. With ordinary non-overfull storage:

```text
candidate = min(capacity - quantity, wattage × speed_fraction × dt)
electrical_gain = candidate × 0.75
shaft_input = -candidate × 0.04 × sign(rps)
```

Thus this reviewed conversion gives 75% electrical gain while charging the full candidate to the shaft. Full storage produces zero candidate. Creation uses the same wattage/shaft-scale mass relationship and initializes its internal electrical content. Wider redistribution losses and stable consumer ordering after topology mutations remain separate work.

## Jet assembly and starting conditions

There is no single generic shipped `jet_engine` class. The recovered chain uses combustion, compressor, exhaust, fuel manifold, side gearbox, nose gearbox and optional particle separator classes.

`jet_engine_combustion.rebuild_jet_engine` 55811182 follows the declared upstream/downstream links from mating surfaces. It rejects another combustion component on either traversal, an upstream exhaust and a downstream compressor. It records an upstream compressor, downstream exhaust, upstream separator, side gearboxes and an upstream nose gearbox where encountered. A compressor and exhaust are required for its validity flag. This is the reviewed traversal; it is not a general cycle-safe assembly validator.

The combustion update also requires nonzero total assembly mass and a nonzero shaft-element count. Side and nose gearboxes contribute to that count. An apparently connected chain with no recognized shaft element will therefore skip the main calculation. Rebuild accumulates mass using component volume × **0.8**. That is a native solver coefficient, rather than a recovered density in SI units.

The combustion update at 55827040 combines fuel-manifold throttle by maximum and clamps it to 0..1. Fuel request is gated below **2 RPS** and above **20,000/60 RPS**. At exactly 2 RPS the request gate permits fuel, but the later shaft-energy addition requires speed strictly greater than 2. These are distinct predicates, and neither is a hard shaft-speed clamp.

The reviewed fuel/energy calculation contains coefficients **37,000,000** and **0.3**, available-air limiting, proportional removal across fuel manifolds and damage multipliers. Stage 1 halves computed energy; stage 2 zeros it after earlier supply accounting. Lubricant degradation, deficit wear, ambient blending and a **1,400 temperature threshold** participate in damage. Full jet intake, species, temperature units, load calibration and all repair paths remain under review; do not substitute piston-engine limits.

The combustion component sends normalized speed to exhaust thrust state. The exhaust update at 55899323 then constructs a vector using scalar arguments **(0,800,800)** before applying component/body rotation and scaling by its thrust factor. The arguments were rechecked in assembly because this differs from an assumed single-axis jet. Application uses the native `add_force` helper. Its full intrinsic contract, intended calibration and whether this is deliberate remain unresolved; it must not be silently rewritten as a conventional axial force. The same method reduces the stored factor by 0.01 afterward, clamped at zero.

## Helicopter swashplate and rotor

The swashplate has three reflected mechanical inputs: `m_logic_pitch`, `m_logic_roll_l`, `m_logic_roll_r`. At 54741304:

```text
roll = clamp(roll_r - roll_l, -1, 1)
collective = clamp((roll_l + roll_r)/2, -1, 1)
pitch = clamp(input_pitch - collective, -1, 1)
```

Pitch and roll interpolate toward their targets with factor **0.1** per update; collective is assigned directly. The component supplies shaft speed and delegates the force calculation to the shared rotor element. This is not three independent conventional joystick axes: equal left/right inputs determine collective, while the pitch input is compared with that collective.

The shipped main rotor definition declares blade length 2..8, and the tail rotor 0.5..2. Their common accessory offset is 0.16. These definition values do not replace saved-state parsing or installed blade inventory. The save parser has a configured-count default of 2 and saved-length default of 0; post-load/rebuild/property handling must be followed before assuming the final loaded blade length.

`vehicle_element.rotor.tick` 58447234 counts blade slots with a valid accessory definition. Configured slot count and installed count are distinct. It derives four clamped point inputs:

```text
a = collective + roll       b = collective - roll
c = collective + pitch      d = collective - pitch
```

Each is clamped to -1..1. With r = shaft RPS, L = blade length, n = installed count:

```text
B = r × 2π × dt × L × 32 × n × 0.25
point_impulses = B × (a,b,c,d)
```

The axial direction is the component's transformed local +Y. The four impulses act at opposite transformed X/Z offsets based on blade length. Zero collective with symmetric cyclic inputs gives zero summed axial impulse before saturation effects, while still producing opposing point impulses. The displayed force field takes the magnitude of the summed impulse vector in this method; interpreting it as newtons requires the wider display/unit path.

The shaft load passed to `apply_torque` is:

```text
-abs(B) × (abs(a)+abs(b)+abs(c)+abs(d)) × sign(r)
-r × 2π × dt × L × 32
```

The second term persists with zero installed blades in this reviewed calculation. Transverse body angular velocity is also damped with retention `exp(-abs(r) × L × n × 0.5 × dt)`; rotation along the rotor axis is excluded from that damping operation. These explicit game formulas are not a real-world rotor aerodynamic model.

The separate blade collision object is added when absolute speed is **below 0.75 RPS**, retained at up to **1 RPS**, and removed above 1 RPS in this path. Physics creation/rebuild, other collision paths and damage handling remain separate; this does not prove that fast blades can never collide or injure anything.

## Ground effect

`rotor.apply_ground_effect` 58399246 requires the rotor axis's world-Y component to be at least **0.75** and upward summed impulse at least **0.001**. It searches downward over **32** native world-distance units, with sphere radius at least 0.5 and otherwise based on blade length.

The search excludes the vehicle and its rotor body, checks collision masks, rejects the inspected motion class and excludes dynamic supports below mass **250**. A qualifying support has normal-Y at least **0.4**. An ocean-height path is also present with additional world/dungeon conditions; water support is not unconditional.

After selecting a qualifying distance h, the extra impulse fraction is `(1-h/32)²`. It scales the existing summed rotor impulse and applies it at the hub. A qualifying dynamic support receives the opposite extra impulse at its hit point. This is an extra contribution, not a total-force replacement. Native physics cast/filter implementations and every ocean case remain to audit.

## Reusable model and continuation

[`powertrain_models.py`](../../../scripts/research/powertrain_models.py) models the reviewed ordinary arithmetic with explicit state and guards. Its 12 tests include 500 seeded fully engaged island cases, weighted-momentum/ratio invariants, reverse rotation, multiplicative brakes, the double clutch contribution, motor overspeed, alternator losses, rotor symmetry and ground-effect endpoints. Guards are model-domain choices, not discovered native restrictions.

The research suite now has **101 passing synthetic tests**. Source checks, selected identity/constant checks, reflected declarations, documentation and exact publication hashes are recorded independently. None is a new gameplay test or complete component certificate.

Continue with wheel/contact and track dynamics, all actuator/body ownership chains, full fluid/gas/thermal exchange, controls/sensors/data, script/native intrinsics, world/actors/combat, save/multiplayer authority and asset/UI/audio systems. Every declared update implementation being available removes an access gap; it does not close that remaining semantic work.
