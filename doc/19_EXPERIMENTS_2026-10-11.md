# 2026-10-11 experiments and evidence boundaries

## Direct review in this session

Inputs: user-uploaded `allofthem.data / allofthem.meta`, archived unchanged under `evidence/2026-10-11/`. Read-only `scripts/inspect-native-reference.py` produced `native-reference-inventory.json`, including SHA-256/scripts/state.

| Vehicle ID | Components | Grids | Electric/mechanical/liquid/gas/belt/data links |
| --- | ---: | ---: | --- |
| 217 | 49 | 1 | 2 / 6 / 7 / 0 / 5 / 0 |
| 218 | 86 | 1 | 5 / 12 / 8 / 8 / 6 / 2 |
| 219 | 105 | 2 | 6 / 14 / 1 / 0 / 6 / 17 |
| 220 | 73 | 1 | 6 / 10 / 8 / 5 / 6 / 0 |
| 221 | 121 | 2 | 3 / 15 / 18 / 34 / 12 / 0 |
| 222 | 64 | 1 | 7 / 2 / 6 / 2 / 5 / 0 |

Total: six vehicles/eight grids/five plates. Multiple grids may share one vehicle; counts are not body counts. Saved temperature/fluid quantities/lubricant contamination/battery energy do not prove continuously updated files or live axle RPM.

Direct script evidence: 218 controls EngineFan.input from EngineTemp.temperature > 20; 219 reads ignition/pedals/handbrake/wheel speed/gears/temperature and writes throttle/clutch/brake/displays; 221 has empty on_tick. Anymaker uses on_tick, out reads, in writes, not interchangeable Stormworks Lua. Thresholds belong to examples, not universal recommendations.

## Earlier analysis recovered from records, not fully rechecked here

Earlier chat identified 217/218/219/220/221/222 as Jet/V12/4WD/inline-3/V12 2/inline and reported mechanical-junction automation, separate fuel/oil/cooling, cross-grid links. `120mmgunexample.data` reportedly has readable script/four data links; four user screenshots show microcontroller drag-and-drop items.

These names/findings came from chat records. This session did not obtain/recheck every individual example/four logic screenshots. Do not fabricate missing catalog entries. Port behavior, complete name binding, cross-grid electrical rules, runtime capability need specific connections/tests.

## Missing lunch-session results

The user authorized PC read-only observation/screenshots/creation/log reading and had a sandbox save. That historical cloud workspace lacked Windows filesystem/local game controls. No reviewable lunch runtime/telemetry/test reports were found. Earlier RPM/torque/automation examples were proposals, not collected results.

## Capability assessment (engineering judgment, not success rates)

| Goal | Assessment |
| --- | --- |
| Frames/shells/simple static structures | Relatively strong; check thickness/performance/game loading |
| Reference-based single-system modification | Moderate; small changes/tests |
| New complete car/engine/winch | Candidate files possible; first-run reliability insufficient |
| Microcontrollers | Research/edit evidenced scripts; full binding/runtime still needs tests |
| Automatic physics tests/continuous telemetry | Unimplemented/unverified |

Next valuable step: minimal electric vehicle, separately recording loading/mounting/power/torque/steering/braking/forward/reverse, expanding only after runtime evidence.

## Sensor experiment (user-selected next step)

For each sensor record definition/model, ports/fields, units/range/rate, local/world coordinates/orientation, stationary baseline, known-input response, disconnected/unpowered values, name bindings. Minimal rig, one variable at a time, creations/screenshots/timestamped readings retained. Unperformed; do not presume measurable quantities/external telemetry capabilities.
