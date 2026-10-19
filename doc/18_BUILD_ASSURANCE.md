# Vehicle delivery standard

2026-10-11. Source: user-provided build failures and development authorization.

## Workflow

Requirements -> system chains -> component/interface evidence -> geometry -> structure/network audit -> static validation -> game loading -> operation/failure testing.

1. For each function record source, consumer, intermediate interfaces, direction, control state.
2. Cite component dimensions/ports/behavior. List unknowns; never silently substitute real-world/Stormworks rules.
3. Default to one rigid chassis; joints/moving parts may require multiple bodies. Record mounting grids separately; grid count alone is not failure.
4. Audit mounting separately from systems. Trace all electrical/torque/mechanical-control/data/liquid/gas paths.
5. Add microcontrollers only when needed, with name bindings, I/O, lines, consumers, startup defaults.
6. Check wheel/shaft/belt/suspension/door/winch clearances; no shafts through frames.
7. Motor rotation does not prove torque reaches wheels/winch. Identify load response/transmission breaks.
8. Record OFF/neutral/forward/reverse/power-loss states. Be conservative about unknown strength without inventing numbers.
9. Back up meaningful changes; expand gradually from minimal working examples.

## Delivery record

| Item | Status/evidence |
| --- | --- |
| Geometry | PASS / FAIL / UNKNOWN, views and scope |
| Mounting | Same; cannot infer from system lines |
| Interfaces/networks | Same; trace sources/loads |
| Static checks | Same; tool versions and actual scope |
| Game loading | NOT TESTED if unperformed |
| Operation/failure | NOT TESTED if unperformed |

## Tool boundaries

`python3 scripts/inspect-native-reference.py PATH.data > inventory.json` inventories vehicles/grids/components/structure/six link kinds/scripts/saved state. This is a read-only snapshot inventory, not connectivity/physics/collision/compatibility validation. Preserve unknown fields; field counts do not prove operation.

Proposed local observation remains unverified: compare timestamps/hashes/diffs before running, startup, spawning, operation, saving, removal. Only observed changes correlated to actions can establish saved fields as telemetry. Native APIs/log interfaces/automatic spawn-reset/keyboard control are not established. Example commands are not an implemented bridge.
