# Current facts and rules to carry forward

Evidence cutoff: 16 October 2026, Anymaker v0.1.25, Steam build 25904830. Earlier v0.1.24 findings are version-labeled in the archive. “User-tested” means the user performed the game test; offline checks are identified separately.

## Geometry and connections

- Native building unit is **8 cm**. `vehicles.vehicles[]` represents bodies; a body's `grids[]` are mounting frames, not necessarily separate bodies. Transform inclined-grid positions before comparing body-space geometry. Native matrices are column-major; browser reflection conventions must not be copied into native-to-native tools.
- Structural attachment, electrical power, torque, mechanical control, data, liquid and gas paths are separate requirements. Visual contact, overlapping origins or a connected control line proves none of the others. Drive torque passes through compatible torque faces, shafts, gears and belts; mechanical links carry control values.
- Panel winding matters. The first giant test vehicle lost exactly nine unmounted controls/air-system parts; the base-grid mounting audit predicted the same nine. Correct panel facing and explicit frame support fixed the assembly. The auditor supports cardinal components, beam spans and rectangular panels; it is not a general physics or collision certificate.
- Component size and interface family matter. The giant engine required its compatible large engine wheel. Small car wheels use mechanical steering/braking; medium truck wheels instead document hydraulic steering and pneumatic spring brakes. Do not generalize by appearance.

## Inputs, scripts and power

- **Steering-wheel pedals are digital pressed/released inputs**, user-confirmed. Their 0–1 channel range does not imply analog travel.
- A native button is momentary; switch/toggle switch latch. Emergency-stop-looking buttons are documented as momentary. Native toggle, set/reset, max/min, invert, abs, offset/scale/add junctions can avoid unnecessary microcontrollers. Confirm defaults and simultaneous-input behavior rather than assuming them.
- Microcontroller consumption is documented as **10 W**. Fit and wire an electric port and the complete data network. A lit display showing 0 does not prove the controller program is running.
- Script syntax is Anymaker `on_tick`, `out` reads, `in` writes, typed variables and conversions; it is not Stormworks Lua. Runtime `global_private` state can serialize alongside script text. Saved body IDs, definition ordering and default omission can change on re-export.
- Integer channels cannot serve directly as `if` booleans. A diagnostic `!= 0` expression reimported with its operator missing, producing “Expecting a boolean value.” Explicit `> 0` / `< 0` conditions corrected this case. Do not infer that every possible inequality expression is unsupported.

## Engines and fluids

- Component documentation gives **6 rps** for combustion starting. Large-wheel belt ratio is **0.267 / 0.04 = 6.675**. A 60 kW starter plus fixed gearing produced a successful giant-engine start. Starter wheel RPM and actual engine RPM are different measurements.
- The compact I4 has **60 components in one body**; accepted as **CPE1Running**. Native component bounds: **1.28 × 0.88 × 0.80 m** (width × length × height); reserve **1.36 × 1.04 × 0.92 m** including routed-line reach. Its saved full-throttle state is **135.188261 rps / 8,111.296 RPM**, **25.423453 °C**. Sustained circulation remains unproven for this smaller engine.
- The giant engine's oil/coolant starvation at high RPM was a **pump-direction/feed-return problem**, not established pump undersizing or a 50-rps pump limit. For its particular unreversed belt, current shaft signs and sorted port layout: oil pump 17 **Reverse OFF**, coolant pump 20 **Reverse ON**, fuel pumps 84/85 **Reverse ON**. These are layout-specific settings, not universal pump rules.
- After correction the user showed **23.6 L oil** at both 20% and 100% throttle, and coolant **24.5 / 24.3 L**. The 100% snapshot showed **72.8 rps, 499.5 kW, 34.9 °C**. This confirms retention at those snapshots, not endurance or loaded vehicle power.
- Both engine oil manifolds reach the same lubricant volume; coolant manifolds similarly share coolant volume. Pump chambers and reservoir quantities alone do not establish external flow direction. Trace shaft sign, reverse, chamber mapping, fitted-port sorting and complete external circuits.
- Preserve the user's colors: **orange fuel, red oil, blue coolant, white air**. Saved indices used here are 20, 25, 47 and 7 respectively. The added oil filter 105 belongs inline on the reservoir-to-oil-pump feed with ports 106/107.

## Pneumatic shifting — final correction

- Gas-valve creation uses **gas-node ordinals**, which are converted into absolute saved logic-node indexes. For this valve definition saved node **1 = common supply, 2 = activated output, 3 = resting output**. Ordinals 0/1/2 are not directly saved endpoint indexes. Earlier reports confusing these are superseded.
- Native thresholded mechanical activation detects **magnitude**: input below −0.75 OR above +0.75 activates; reset occurs inside −0.25…+0.25. Sending raw +1 to one valve and inverted −1 to the other therefore activates **both** and cancels shifting.
- Accepted solution: native Max selectors produce **up = max(shifter, 0)** and **down = max(−shifter, 0)**. The unconnected second Max input is zero in this tested configuration. Components 143/144 implement the positive-only requests. The user's test confirmed gears 1 and 2 and reverse indication; saved trace records gear engagement and no simultaneous valve activation.
- Medium/large gearbox documentation gives shift/reset thresholds **29.4 / 19.6 kPa**. Native code compares its own pressure quantity at >3 / <2; do not equate raw saved gas contents with pressure or litres without the conversion/geometry trace.
- Gas chamber capacity comes from inspection geometry, not just an apparent scale field. Recorded gearbox chamber capacity is approximately 0.536165 native volume units; the small reservoir approximately 9.694431. The test vehicle stores precharge contents totaling 80, which is finite pressure reserve, not an 80-L geometric tank or an infinite compressor.

## Driving and indication

- The accepted vehicle spawns **handbrake ON, neutral**. Key **1** releases/reapplies handbrake; **3** shifts up; **2** shifts down; release shift controls between commands. Right pedal/W applies throttle; left pedal/S brakes and disconnects the rear axle.
- Handbrake applies all four brakes **and disconnects rear drive**. The “shifts but won't move” save had handbrake ON. Releasing it made the vehicle move; the user then confirmed everything works.
- Gear display: 0 neutral, 1/2 forward; a red lamp indicates negative gear/reverse. The numeric display clamps negative values, so a separate reverse lamp is intentional. Power and data wiring are required.
- Current cleaned creation has **103 parts**. The actual successful diagnostic save had **106**, including temporary ports 140/141/142 subsequently removed. Distinguish user operating evidence from the offline cleanup; do not invent a separate endurance test.

See [compact engine](COMPACT-I4.md), [large engine and vehicle](GIANT-VEHICLE.md), [experiment history](EXPERIMENTS.md) and the archived source reports for exact evidence.
