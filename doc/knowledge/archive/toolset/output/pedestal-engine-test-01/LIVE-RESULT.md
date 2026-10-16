# User-tested pedestal engine — 14 October 2026

The user reported that `Petrol_Pedestal_Test_01` works, supplied an in-game screenshot, and overwrote the creation with an export taken while running. A read-only copy of that export, its paired metadata and the screenshot is preserved under `running-result/`. The original generated state remains preserved in this folder. No current creation files were edited by this inspection.

The screenshot shows engine speed 10.1 Hz, power 2.4 kW, throttle 15%, temperature 20.7 C, oil and coolant quantities of 3.4 L, oil quality 100%, and NO GEARBOX. This corroborates game loading and engine power production without a gearbox. It does not measure sustained cooling or loaded shaft power.

The later running export records:

| Quantity | Value |
|---|---:|
| Engine speed | 133.312954 rps = 7,998.777 rpm |
| Engine temperature | 25.656768 C |
| RUN switch | true |
| Throttle slider | 1.0 (100%) |
| Run/fan relay | on |
| Engine lubricant | 3.901881 L oil |
| Engine coolant | 4.899925 L water |
| Petrol tank | 7.941749 L petrol |
| Battery | 14,378,861.759 J = 3.994128 kWh, 99.853% of initial energy |
| Engine damage factor | 0.001145346 (0.1145% when multiplied by 100) |

Geometry and all six link-family arrays are unchanged from the generated assembly: 60 components, 93 nodes, 119 edges, four plates, one body. The game changed the body ID from 261 to 214, reordered definition indexes, reassigned fitted item IDs and omitted several default values. Compare components by ID and resolved definition, not raw catalog indexes. The running export still passes the static audit with no issues. The game also wrote null gas temperatures; these are native saved states, not evidence by themselves of a broken input file.

There is one concrete circulation question: the radiator's saved `content` contains only temperature, with no water quantity. The oil reservoir likewise contains no oil quantity. All 8.7 L of initial water is accounted for in engine coolant (4.899925 L) and pump chambers (3.750075 L plus 0.05 L), within rounding. Most oil is in the engine and filter. This supports redistribution through connected systems, but not sustained closed-loop circulation. A dry radiator would limit effective cooling; port roles and return flow need verification before declaring this a proven continuous-duty power unit. The small nonzero engine damage has no established cause from this one snapshot.

Acceptance status: **user-confirmed in-game load and running engine, with screenshot and running-save evidence**. Long-duration cooling, starter release/stop sequence, alternator charge rate and loaded output operation were not separately measured. Preserve this successful revision when making any follow-up correction.

Detailed source hashes, values, state differences and comparison results: [running result](running-result/report.json).
