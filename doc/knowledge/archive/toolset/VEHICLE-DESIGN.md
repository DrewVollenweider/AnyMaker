# Practical vehicle-building knowledge



This reference describes shipped component/manual rules, supported by copied definitions and saved examples. The generated petrol pedestal engine has now been loaded and run by the user, with a screenshot and running export: [live result](output/pedestal-engine-test-01/LIVE-RESULT.md). Vehicle driving and sustained engine cooling still require their own tests.



## Decisions this knowledge changes



| Task | Verified rule | Design consequence |

|---|---|---|

| Deliver drive power | The `wheel` definition receives drive at a torque face. Mechanical links carry control signals. | Plan the torque path separately from steering, braking, and throttle control. A control link alone cannot drive a wheel. |

| Power a small electric motor | `electric_motor_a` draws up to 10 kW, requires an electric port, and runs at 30 rps when powered. | Provide its electrical connection and plan speed reduction/control before assuming it behaves like a pedal-controlled engine. |

| Supply battery energy | `battery_a` needs a matching battery item inserted by hand and an electric port; documented capacity is 4 kWh. | The placed battery component alone is not enough to establish an energized supply. |

| Install driving controls | `steering_wheel` mounts on the seat's main control face; `high_back_car_seat` requires matching upright orientation. Backward-facing controls are inverted. | Check attachment face and orientation, not just proximity. Steering is −1 to +1; pedals are 0 to 1. |

| Control small wheels | `wheel` accepts steering through a mechanical link, up to 32 degrees, and braking from 0 to 1. | Connect these controls independently of its drive torque path. |

| Use medium truck wheels | `wheel_c` uses hydraulic steering and pneumatic spring brakes; brakes begin releasing above 39.2 kPa and fully release at 58.8 kPa. | Do not reuse a small-car brake/steering recipe for this wheel. |

| Run a microcontroller | It draws 10 W, requires an electric port, and reads/writes components on its data network. | Plan power and data wiring; an unpowered, disconnected controller is not a working control system. |

| Add instrumentation | Motor `rps` and `electric_consumption` are outputs; `target_rps` and `power_factor` are inputs. Battery `energy_store` is an output. | Distinguish measured values from writable commands. Use these channels for control and troubleshooting displays. |

| Build a frame | Grid spacing is 8 cm; plates follow closed coplanar edge loops. | Use consistent geometry and check frame nodes, connections, rotations, and plate planarity before import. |

| Mount parts on panels | The native attachment routine checks the panel normal and opposing component surface. A downward-facing floor does not mount components above it. | Wind upward floors toward +Y, and certify each component has a structural path to the chassis. Cables and pipes do not substitute for mounts. |



## Vehicle panel failure and repair, 2026-10-16



The first Giant Engine Test Vehicle spawn lost nine components: starter key 83, idle slider 75, inverter 124, shift-air tank/port 127–128, valves 130–131, and vents 132–133. The user's saved survivor creation retained 86 of the original 95 components. The motor 62, starter gearbox 104 and pulley 64 remained present. All four newly generated horizontal panels had downward normals.



Static analysis of `vehicle_util.test_component_attaches_to_vehicle<server_scene>` confirms oriented panel mounting, component surface adjacency, and frame endpoint/span contact. The new [attachment auditor](structural_mounts.py) predicts exactly the nine components absent from the user's save. It is deliberately limited to base-grid/cardinal geometry, beam endpoints/axis-aligned spans and rectangular panels; it is not a full native physics emulator.



The repair report (local evidence not uploaded) records restored parts and links, reversed panel winding, and explicit frame mounts. The repaired creation has one static structural island containing all 95 components. Two independent controls also pass: correcting panel direction alone restores connectivity; the added direct beams maintain connectivity even with the original panel direction. This repaired version has been installed, but its revised spawn has not yet been tested in game. The generator now creates upward panels, direct mounts and runs the structural audit before exporting.



## Pneumatic shifting correction and actual-gear display, 2026-10-16



The user's subsequent save contained all 95 components and reported a shifting failure. **Correction to the first decompilation interpretation:** `gas_valve_t.create` passes gas ordinals 0/1/2, but `vehicle_gas_node.container.create_node` converts them through `definition.get_logic_node_index(type=gas, ordinal)`. Saved pipe endpoints are the resulting mixed-list indexes **1 common, 2 activated branch, 3 resting branch**. `gas_valve_t.get_gas_flood_nodes` selects common/third ordinal at rest and common/second ordinal when activated. Trace the conversion, not just the caller's constants. Evidence: node constructor (local evidence not uploaded), valve constructor (local evidence not uploaded), and valve flood (local evidence not uploaded).



The original circuit connected supply to resting branch 3 and vent to activated branch 2. Both shift chambers were pressurized at rest. The incorrect first repair used gas ordinals directly as saved endpoints; its common-node 0 was invalid and the user's next save showed the tank draining to atmosphere while chamber contents stayed unchanged. That repair and its report at `20261016-093328` are failed evidence, not a validated design.



The corrected revision (local evidence not uploaded) uses supply 2, gearbox/common 1 and vent 3. Its graph check follows both the ordinal conversion and native flood selection. The generic audit now rejects saved gas-valve node 0. Both the original generator and indicator-install helper have been corrected.



`gas_content.create` calculates capsule volume from inspection geometry, then multiplies by its scale argument. The gearbox constructor's 0.1 argument is a scale, not a 0.1 chamber capacity. Actual unstretched large-gearbox chamber capacity is about 0.536165 native litres; the tank is about 9.694431. The original failed save's 1.237104 chamber contents imply native pressure about 2.307, below the trigger >3; reset requires <2. The corrected creation initializes chambers at their ambient-equivalent capacity and charges the tank to 80 volume units for reserve after filling pipes and a chamber. These use native pressure/volume conventions; do not assume real-world pressure units without tracing their presentation conversion.



A powered microcontroller reads `DriveGearbox.current_gear` through a fitted data port and drives a front single-digit display plus reverse lamp. Script syntax and conversion are copied from the existing `4wdchassisengine` gear-display example. The controller connects to battery port 82, upstream of the starter relay. Display: 0 neutral, 1/2 forward; red lamp indicates reverse while the digit clamps negative values to 0. User bindings remain **3 upshift, 2 downshift, 1 handbrake**.



### Actual remaining control fault: signed inputs activate both valves



The 09:41 mapping/charge correction still did not engage a gear. A running diagnostic controller proved both shifter directions and both valve activations reached the gearbox; a positive target was observed but no positive engaged gear. A five-second upshift still returned neutral. The native threshold helper (local evidence not uploaded) explains this: a false valve activates below **-0.75** OR above **+0.75**, and a true valve releases only inside **(-0.25,+0.25)**. Negative is active too. Therefore a raw shifter and its negation activate both valves together. This contradicts extrapolating the description's 0-to-1 wording to signed signals.



The 09:59 revision (local evidence not uploaded) adds two supported max junctions: `up=max(shifter,0)` and `down=max(-shifter,0)`. Each uses an unconnected second input's default zero and has a direct floor-frame mount. After this revision the user verified **gear 1, gear 2, and the reverse light in game**. The [saved acceptance trace](output/shift-repair/shifting-success-no-drive.data) records `SawGear=true` and `SawBothValves=false`, with reverse engaged and clutch 1.0. This is live shifting/display acceptance, not just offline validation.



The temporary diagnostic's first `!= 0` conditions were not accepted: the imported script dropped those operators and the editor reported "Expecting a boolean value." Explicit `> 0` comparisons compiled and ran, and the saved private variable `Ticks=1003` established execution. Do not infer script execution merely from a lit default digit, and do not assume unsupported comparison syntax survives import. Private runtime values do serialize when the program runs.



The same accepted save reported no movement but had **handbrake ON**, engine 36.31 rps, reverse selected, and clutch engaged. This vehicle's handbrake applies all four brakes and disconnects the differential; key **1** releases it. **The user then confirmed that the vehicle moves after releasing the handbrake.** This establishes live drive-path operation in addition to the reported gear 1/2 and reverse-light tests; sustained driving, handling, and endurance remain untested. The [cleaned creation](output/shift-repair/20261016-100456/report.json) retains the two positive-only selectors and actual-gear display, removes three temporary diagnostic data ports and trace variables, and starts parked in neutral with charged shift air. All 103 remaining components form one static structural island. The cleanup script only accepts a saved trace with successful engagement and no simultaneous valve activation.



## A useful next prototype



Use a copied simple cart as the frame/control reference. Add a compatible electric drive with an energized battery supply, the required ports and electrical links, and a continuous torque path to the driven wheels. Keep steering and brakes on their appropriate control paths. Start with a restrained motor power/speed setting and verify brake state before a driving test.



Add a powered microcontroller and data network only when needed for throttle mapping or instrumentation. Start with motor RPS and battery energy readings. Motor speed, power limits, torque-face alignment, gearing, wheel attachment, and runtime stability must still be checked in the game; this is an architecture checklist, not a tested assembly recipe.



## What the tools can already do



- Inspect and compare the component fields, geometry, and links in saved creations.

- Resolve component IDs against 598 shipped definitions and expose their connection surfaces/data descriptors.

- Audit IDs, references, rotations, frame edges, plate planarity, and selected link endpoint rules.

- Preserve unknown saved fields while making explicit changes to a separate draft.

- Study 33 downloaded Workshop examples, including controller scripts, and produce a schematic.



These checks cannot currently prove torque-face mating, complete runtime power/flow paths, balance, handling, buoyancy, or physical stability. Separate frame groups can be intentional articulated bodies; warnings are not proof of a broken vehicle.



## Evidence and lookup



The component rules above are in `reference/vehicle_component_definitions.json`. Broader manual notes: [game knowledge](../exploration/game-knowledge.md). Creation tools: [README](README.md). Workshop examples: [WORKSHOP](WORKSHOP.md). Static code findings: [DECOMPILATION](DECOMPILATION.md).



Useful queries include `catalog electric_motor --full`, `interfaces steering_wheel --with-definition high_back_car_seat`, and `inspect`/`audit` on a copied creation. No original creation or installed game file needs to be changed for these analyses.

