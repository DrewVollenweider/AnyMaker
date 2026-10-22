# Current combustion engines, supply paths and gearboxes

Build **26113663**, 2026-10-22. Vehicle engineering remains first and the full audit remains incomplete. This pass reads the current combustion-engine and ordinary gearbox updates in full, plus 32 fresh manifold, pump, fluid, cooling, conversion and pneumatic-gearbox helpers. No game execution, installation edit or active-save modification occurred.

Source: GCL SHA-256 `a3fd2df2fd62e38b629f6a0df824269a34d77d57caf66d596362d7e5e53c3b22`. See [selected evidence](versions/build-26113663/engine-supply-20261022/evidence.json) and [verification](versions/build-26113663/engine-supply-20261022/verification.json). Full vendor exports remain local. This extends the [earlier engine findings](OFFLINE-ENGINE-STRUCTURE-20261019.md), preserving their version boundaries.

## Combustion demand and starvation

Let `N` be the engine's stored component volume, `r` its cached engine RPS, `t` combined throttle and `R` the server tick-rate global. `N` comes from the component volume getter, which sums inclusive extended zone counts; it is not a recovered cylinder count or cubic metres. Each intake's request enters a running maximum clamped to 0..1. Averaged intake pressure produces:

```text
boost = 1 + (clamp(mean_intake_pressure, 1, 10) - 1) / 9
exhaust_factor = 1 - clamp((mean_exhaust_pressure - 4) / 16, 0, 1)
speed_factor = clamp(60*r/8000 + 0.2, 0, 1)
fuel_request = N * 400 * speed_factor * boost * t * exhaust_factor
               / (R * 32000000 * 0.3)
fresh_air_request = fuel_request * 10.9 * 800
```

Fuel demand is cut off at **r < 6** and **r > 8000/60**. Equality passes these speed gates; it does not prove ignition succeeds. The reviewed path also depends on registered intake, fuel and exhaust manifolds. Without an exhaust manifold its exhaust factor remains zero. This is not a mechanical speed clamp.

The draw calculation treats the two supplies independently:

- Gas is drawn proportionally from intake contents, capped by available total gas. Only its fresh-air species counts toward the fresh-air sufficiency factor.
- Petrol is drawn independently, capped by available petrol.
- Calculated combustion energy is consumed petrol × **32,000,000 × 0.3** × fresh-air sufficiency. Damage stage 1 halves that result; stage 2 zeros it **after** consumption.

Thus air starvation can waste fuel, and fuel starvation can consume excess intake gas. A positive fuel-flow field does not establish useful output. For example, a request of **0.001 L** petrol corresponds to **8.72 L** fresh air. With all petrol available but only **4.36 L** fresh air, the ordinary arithmetic still draws the petrol and produces half the otherwise calculated energy. This is a source-derived example, not a new gameplay test.

New [engine_demand.py](../../../scripts/research/engine_demand.py) models these selected demand/draw equations. Its domain uses explicit positive component volume, tick rate and ordinary positive stocks, assumes registered intake/exhaust paths, and excludes zero-stock exceptional arithmetic. Nine tests cover cutoff boundaries, volume/rate scaling, pressure limits, independent starvation, contamination, damage and 500 seeded stock/energy-bound cases. It does not simulate shaft dynamics or measured shaft work. Fuel divides by `R`; the pumps below multiply a separate server-delta-time value `dt`. Their reciprocal initializers are not a universal proof of later equality.

The engine still couples cached speed to registered engine-wheel and gearbox shafts using signed, mass-weighted terms before writing feedback. A starter's own shaft speed is therefore not a substitute for engine RPS. The final speed also receives an update-dependent damping term involving fresh-air sufficiency and throttle. Complete torque-solver units remain open; the initializer named `g_torque_system_newtons_per_joule` is **0.04**, which alone does not establish N m for every script channel.

## Manifolds, internal fluids and filtering

Fuel-manifold activity is `clamp(0.5*r,0,1)`. Its own update writes static pressure **-6 × activity**, reaching maximum suction by **2 engine RPS**, before the 6-RPS fuel gate. Throttle is not the variable in this suction expression. Network scheduling determines when a changed activity value is consumed; no universal one-frame latency is claimed.

Oil and coolant manifolds do not construct independent tanks in their own create wrappers. Mating them to an engine creates liquid nodes referencing the engine's shared lubricant or coolant volume. Multiple ports therefore access shared internal storage. “Feed” and “return” should be traced through actual node pressure, pumps and connections rather than inferred as separate internal chambers.

The engine creates lubricant from inspection layer 0 and coolant from layer 1, both with scale **0.24**. The liquid-volume helper computes capacity from its selected extended inspection geometry × supplied scale × **0.5 L per voxel**. Box/capsule branches differ; the complete axis-specific stretching/geometry contract remains open. This is not simply total engine zone volume × a universal tank constant.

High RPS alone does not directly consume bulk oil or coolant in the reviewed engine update:

- Oil aging moves `clean_oil × 0.00001 × clamped RPM fraction` into pollutant, preserving their sum.
- The lubricant wear factor depends on `clamp(2*clean_oil/capacity,0,1)`. Half-capacity in clean oil eliminates this particular deficit term; quantity and quality both matter.
- A damaged engine requests removal of **0.0001 L per update** from each internal liquid volume into a temporary sink, subject to transfer availability.

This does not diagnose a particular saved engine's depletion. Large falling internal levels require tracing redistribution, supply/return balance, capacity and damage rather than assuming normal combustion burns coolant.

An oil filter with a cartridge removes **pollutant**, up to **0.0001 L per update**, limited by pollutant stock and cartridge condition divided by **0.1**. Condition falls by 0.1 times the amount removed. It does not convert the removed pollutant back to clean oil. Its vector equalizer then redistributes the two sides and recomputes totals from species amounts. Without an accessory, this reviewed equalization branch is skipped. Full component connectivity still matters; this is not a promise that any filter placement works.

## Pump pressure, candidate flow and actual transfer

The liquid and gas shaft pumps have distinct formulas. With `s` the signed/reversed shaft RPS and `f` the stored flow factor:

| Reviewed path | Head term H | Candidate C before adverse-pressure reduction |
| --- | --- | --- |
| Liquid pump | `abs(s) * f * 0.1` | `min(source_volume, H * 0.4 * dt)` |
| Gas pump | `abs(s) * 0.2` | `min(source_volume, H * f * 0.04 * dt)` |

Both compute `Q = C * (1-clamp(adverse_pressure/max(H,0.0001),0,1))`. Direction determines source/destination. The liquid path compares content overfill pressure; the gas path compares cached node pressures. Their load calculations use **C**, before the adverse-pressure reduction, with efficiency **0.6**. Zero movement under resistance therefore does not prove zero shaft load.

Liquid transfer additionally caps movement by **destination free capacity**, unlike the gas helper. Pump `m_flow` is written before that final transfer cap, and the liquid pump ignores the helper's returned amount. A full destination can therefore make actual movement smaller than the stored pump flow. This distinction must be preserved in telemetry or a flow predictor.

The centrifugal gas pump uses **0.1 × absolute shaft RPS**, then subtracts destination-minus-source cached pressure. Positive net head drives forward flow; negative net head permits backward transfer. Its reverse-flow branch does not apply the forward shaft-debit calculation. The reviewed code is not a generic real-world squared-speed centrifugal model.

Liquid `get_pressure` is zero while volume is at/below capacity, otherwise volume minus capacity. Gas `get_pressure` divides volume by capacity, with an **ordered zero-capacity guard**. The earlier [gas report](CONTACT-FLUIDS-NATIVE-20261020.md#gas-content-and-equalization) incorrectly called that a nonpositive-capacity guard. Archived and current comparisons were both reread: negative-capacity protection was not established. The wording is corrected; no changed gameplay behavior is inferred.

## Cooling and fan power

Engine heat uses the initializer **1/4184** and a thermal weight **0.04 × N**. It then blends engine, coolant and lubricant temperatures using that weight and current liquid quantities, assigning a common temperature. This is the game's arithmetic, not a complete species-specific thermodynamic model. Temperature strictly above **160 C** contributes damage; the engine ambient-blend argument is **0.000001**.

The radiator passes ambient coefficient **0.0002**, plus **0.0004 × fan_volume/radiator_volume** for each active mated fan. A damaged radiator requests a **0.0001 L/update** leak. Downstream weather blending and every damaged/empty configuration remain separate contracts.

A fan requests **10 × component_volume × dt** electrical quantity. Its active flag requires consumption factor **strictly above 0.5**. The radiator checks that flag, then adds the full volume-based contribution; this path does not continuously weight cooling by the electrical fraction. Exact half supply is inactive in this test.

## Gearbox count and shift boundaries

Both reviewed ordinary and pneumatic gearboxes return `clamp(2 + extend_z, 2, 8)`. Eight forward gears therefore require extension value **6 along the component's local Z**, six 8-cm units. This getter does not alone validate a complete eight-gear creation, its physical attachment or ratio configuration.

The ordinary gearbox triggers above **+0.75** or below **-0.75**, with its direction state reset only strictly between **-0.25 and +0.25**. The pneumatic gearbox independently activates each unlatched channel at pressure **>3**, resetting it at **<2**. Both channels can act in the same update, preserving the reason for the earlier vehicle's positive-only selector correction.

Both update their automatic clutch by steps of **0.05 per update** and change actual gear after disengagement. Do not replace this with an exact wall-clock shift time or confuse target gear with actual gear. Ordinary ratios include the output/input factor; the pneumatic path uses its own integer ratio/output-factor expression. Reverse polarity and neutral clutch handling are separate branches.

## Verification and remaining work

The current reader now holds **69 methods / 16,045 checked instructions / 97,326 instruction bytes**. Thirty-five selected methods, 79 typed scalars, 35 call examples and the old/current pressure-guard comparison are retained publicly. All **294 research-tool tests** pass; installed code and 2,968 cataloged definition files still match the snapshot.

Continue the complete current fluid/gas graph build and scheduling, pump flow-factor initialization, electrical distribution and control chains. Full torque/native physics, remaining gearbox/engine variants, geometry stretching, endurance, structures, flight and marine systems remain open. The user-confirmed earlier engine/truck successes retain their original scope; no new in-game acceptance is claimed.
