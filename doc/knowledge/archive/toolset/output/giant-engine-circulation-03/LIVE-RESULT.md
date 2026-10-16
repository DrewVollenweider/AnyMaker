# Giant engine: combustion confirmed, circulation unresolved

15 October 2026. User supplied two in-game screenshots and explicitly confirmed
that the engine runs. The latest giantenginetest.data was inspected read-only.
The geared 60 kW starter revision has therefore passed a user-run ignition test.

Screenshot observations:

| Measurement | High speed | Lower speed |
|---|---:|---:|
| Engine speed | 72.8 RPS | 16.8 RPS |
| Throttle | 100% | 20% |
| Engine oil | 50 mL | 11.2 L |
| Engine coolant | 50 mL | 12.9 L |
| Temperature | 39.4 C | 33.0 C |
| Displayed power | 499.5 kW | 80.5 kW |

The high-speed save records 72.817462915 RPS. It contains approximately
0.05 L in each engine fluid chamber, 20.4403 L in oil-pump content_1,
22.4252 L in coolant-pump content_0, 167.6588 L in the oil reservoir, and
166.7774 L in the radiator. This establishes fluid redistribution and substantial
remaining reserves. It does not establish the flow direction of each external
pipe or prove that a larger/faster pump is the correct remedy.

The nominal belt speed at the small pulleys is approximately 6.7 * 72.8 =
488 RPS. The liquid pump's native tick calculation scales pressure/flow with
shaft speed and flow_factor; it does NOT impose the previously suspected
50 RPS limit. Do not infer such a limit from unrelated default definition fields.

Static native-code checks in this directory establish:

- Pump content_0 maps to offset 0x1e0; content_1 to 0x2c8.
- Pump fitted ports are sorted by component ID before mapping to these chambers.
- Positive effective pump rotation moves content_0 to content_1; negative
  effective rotation moves content_1 to content_0. Reverse negates shaft speed.
- Pump static pressure, internal chamber pressure and overfill participate in
  flow. A large saved chamber volume alone does not identify external flow.
- Both oil manifolds connect to the same engine lubricant volume; both coolant
  manifolds connect to the same coolant volume. There is no separate designated
  intake/output role selected by engine surface index in engine.add_mating_component.

The later color-coded save was inspected and copied as color-coded-snapshot.data.
Its engine is running at 16.774252881 RPS with 20% throttle. All colored liquid
and air links match their endpoint component colors.

The signed drive trace is now resolved: engine.tick reads engine-wheel torque
speed with a negative sign; the unreversed belt keeps the same sign at the
small pulleys; mating each pulley to a pump negates speed again. Thus the pump
shafts run positively for this positive engine speed. The actual large-wheel
radius is 0.267 m and the small pulleys are 0.04 m: ratio 6.675, rounded to 6.7
in the component description. Large-wheel direction handling was checked against
the small-wheel and pulley functions.

| Circuit | Chamber 0 external path | Chamber 1 external path | Current direction | Correction |
|---|---|---|---|---|
| Red oil, pump 17 | port35 -> reducer33 -> tank port61 | port36 -> reducer34 -> bracket37 -> engine manifold11 | Reverse ON: engine -> tank | Reverse OFF |
| Blue coolant, pump 20 | port31 -> reducer30 -> engine manifold4 | port32 -> reducer29 -> radiator port15 | Reverse OFF: engine -> radiator | Reverse ON |
| Orange fuel, pumps84/85 | ports86/88 -> fuel manifolds100/101 | ports87/89 -> tank ports48/49 | Reverse ON: tank -> engine | Retain |

The other oil path is directly between engine manifold12 and tank port60; the
other coolant path directly joins engine manifold5 to radiator port16. Thus
both existing oil/coolant pumps are on extraction paths, leaving passive paths
for refill. Increasing suction with engine speed matches the observed RPM-
dependent loss of engine fluid. Changing the two flags would instead positively
feed the engine, with the other paths serving as returns. This correction has
not yet been applied or tested. Full trace: color-coded-direction-report.json.

No creation files were modified during this inspection. Thermal endurance and
stable circulation after correcting direction remain unvalidated.

## User test after the direction correction

The user subsequently supplied screenshots 20261015103439_1.jpg (20%) and
20261015103500_1.jpg (100%), reporting successful operation at both throttle
settings. These screenshots show the high-speed draining has been resolved
following the instructed oil Reverse OFF / coolant Reverse ON correction.

| Measurement | 20% throttle | 100% throttle |
|---|---:|---:|
| Engine speed | 16.8 RPS | 72.8 RPS |
| Oil retained in engine | 23.6 L | 23.6 L |
| Coolant retained in engine | 24.5 L | 24.3 L |
| Temperature | 27.1 C | 34.9 C |
| Displayed power | 80.5 kW | 499.5 kW |
| Oil quality | 100% | 99% |

This is user-tested evidence for fluid retention at both operating points, in
addition to the earlier successful ignition test. It supersedes the pending
direction-correction test status above. It does not establish long-duration
thermal equilibrium or loaded drivetrain performance. No new save was inspected
for this screenshot follow-up, and no creation was edited.

Reusable lesson: for the large engine's current unreversed belt, shaft and port
layout, oil pump17 Reverse OFF and coolant pump20 Reverse ON positively feed
the engine. Fuel pumps84/85 retain Reverse ON because their first/second external
port assignments differ. Do not apply one common Reverse setting to every pump.
