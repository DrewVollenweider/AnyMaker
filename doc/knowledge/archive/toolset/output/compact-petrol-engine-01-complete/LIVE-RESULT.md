# CPE1Running — successful compact-engine test, 14 October 2026

The user reported success and saved the running build as `cpe1running.data/.meta/.png`. Read-only inspection confirms one physical vehicle containing all 60 intended components. Component placements/orientations, the normalized frame geometry and every saved link are unchanged. Static audit has no issues. The game-generated preview was visually inspected and preserved with the running export under `running-result/`.

| Saved measurement | Value |
|---|---:|
| Engine speed | 135.188261 rps / **8,111.296 RPM** |
| Throttle slider | 100% |
| Engine temperature | **25.423453 C** |
| Engine lubricant | **3.966045 L oil** |
| Engine coolant | **4.979944 L water** |
| Petrol tank | **7.945572 L** |
| Battery | **99.897479%** of initial 4 kWh |
| Engine damage factor | 0.000918059 |

The native metadata gives component bounds of **1.28 m wide × 0.88 m long × 0.80 m high**. These bounds omit some routed-line reach; retain the conservative **1.36 × 1.04 × 0.92 m** fit envelope when planning a vehicle bay.

The same fluid-distribution question appears in both successful builds: radiator and oil-reservoir contents record temperature without water/oil quantities. In this export, all 8.7 L of initial water is accounted for in the engine and coolant pump chambers. The compact engine starts and runs, but sustained cooling/return flow has not been established by this single operating snapshot. Small nonzero damage is recorded; its cause is not established.

Useful serialization discovery: frame node 70 is at the origin and re-exports with `pos` omitted. Normalize omitted node positions to `[0,0,0]`, alongside resolved definition IDs, before judging geometry changes. The physical body ID was reassigned to 215; fitted item IDs and optional default fields were also rewritten.

This is now a **user-tested compact engine reference for game loading and running combustion**. Preserve it for future vehicle integration. No loaded drivetrain, run duration, measured charging rate or long-term thermal result is claimed. Detailed values, hashes and comparisons are in [the report](running-result/report.json). Inspection did not alter any creation.
