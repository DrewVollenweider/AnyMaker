# Sensor readings and data-network discovery

Build **25904830**, 2026-10-20. This follows the [joint/winch checkpoint](JOINTS-WINCHES-20261020.md), using matching isolated resources. No game execution, installation or active-save edits. The [full-game audit](AUDIT-REGISTER.md) remains incomplete.

The reader contains **1,129 selected functions / 158,494 checked instructions / 901,354 instruction bytes**. New exports resolve sensor getters, pressure conversion, data-island discovery and microcontroller connection rebuilding. [Selected source evidence](versions/build-25904830/sensors-data-20261020/evidence.json), [reflection evidence](versions/build-25904830/sensors-data-20261020/reflection-evidence.json) and [verification](versions/build-25904830/sensors-data-20261020/verification.json) retain exact build boundaries. Counts are not a measure of complete understanding.

## Sensor frames, conversions and retained state

Let R be the rotation of `vehicle_transform × component_transform`. These ticks use the mounted component's orientation, not an assumed vehicle-forward axis.

| Sensor | Reviewed calculation | Script field |
| --- | --- | --- |
| Acceleration | `dot(R × (0,1,0), current_body_linear_velocity - previous_velocity)`; then save current velocity as previous | `acceleration` |
| Gyro rotation | `dot(R × (0,1,0), body_angular_velocity) / (2pi)` | `rps` |
| Tilt | `math.deg(math.asin(clamp((R × (0,0,1)).y, -1, 1)))` | `tilt` |
| Compass | Project `R × (0,0,1)` into XZ; if projection length >0.001, normalize and pass its angle against `(0,1)` to `math.deg` | `north_angle` |
| Altitude | Y translation of the combined vehicle/component transform | Altitude getter was reviewed previously |

Source ticks: acceleration **53462170**, gyro **55106881**, tilt **57725284**, compass **54184833**, altitude **53533340**. New getter methods **53456086 / 55101339 / 57719970 / 54179298** return pointers to the stored f64 fields when the requested field name matches; otherwise null. They do not add a time or unit conversion.

The acceleration calculation contains **no division by delta time** and no gravity subtraction. Its parser **53459190** preserves `prev_velocity`, defaulting to the zero vector when omitted. Thus this exposed value is the reviewed per-update projected velocity change. Do not silently interpret it as a time-normalized accelerometer or a real sensor's proper acceleration. Initial/load history and update interval affect interpretation.

The gyro's assembly uses floating-point division followed by `MOVSD` into the f64 field. Approximate C printed an apparent integer cast; the instructions do not perform that conversion. Its formula is consistent with RPS when the native angular-velocity getter supplies radians per second, but the full native physics getter contract remains a separate calibration question.

Compass tick has no alternative write when horizontal projection length is at or below **0.001**. It keeps its previous value in that branch. The exact sign/range and degenerate behavior of the native `vec2.get_angle` intrinsic are not established by its name; do not assign east/west signs from a different game. Tilt explicitly clamps its inverse-sine argument. The native angle/degree helper implementations remain follow-up work.

## Pressure and temperature signals

Gas pressure tick **54810751** and liquid pressure tick **56347710** require a node with an island-group pointer. They read that group's pressure and call **61821653**, `units.pressure_to_pascals`, which multiplies the reading by **9800.0**. Missing node/group writes zero. This resolves the script-facing conversion; an internal pressure value of 3 yields a script value of 29400 through this helper. It does not prove every UI uses the same display unit.

Gas temperature getter **54874419** returns a pointer to its gas-content temperature field for `temperature`. Its reflected class inherits the base component tick rather than declaring a separate temperature-sensor update. Liquid temperature's tick **56422218** instead calls its liquid-volume tick. Sampling/flow behavior depends on those content/network paths, not a fictional common temperature-sensor tick. Empty contents, initialization and all environmental paths remain separately reviewable.

## Data islands, power flags and direct contacts

The reflected data node separates:

- `m_component` from `m_component_flood`;
- `m_can_distribute_power` at offset 24 from `m_is_powered` at 25;
- the data-island pointer from component/node IDs and vehicle-node index.

The group-creation helper **58190674** sorts its node list by component ID and then node index, sets each flood-component pointer and its capability flag. Method **58199899**, despite its `set_distribute_power` name, writes each node's **is-powered byte at 25**. Data post-build **58169216** sets the island group's powered state true if any node in its energy-distributor lists is powered, otherwise false. Those distributor lists are populated only for nodes with the capability flag during flood.

`get_is_receive_power` **58188364** returns that group flag, or false without the required island/group pointers. It does not sum watts or infer power merely from the existence of a data cable. Full scheduling relative to electric consumption and cross-body group construction remains open.

Data pre-build **58177823** first resets descriptors of analogue-input type. When rebuilding, it clears old island assignments, derives node positions/directions from component definitions and transforms, and constructs a direct-contact pair array. The reviewed pair checks use grid-origin comparison, an adjacent integer position and opposite normals. Exact extended-grid equivalence and malformed/duplicate contact candidates require further review.

Flood **58150592** marks a node before recursion, preventing ordinary revisits. When that node has a direct-contact pair, it follows that pair. Otherwise it scans explicit data links in both directions using component/node IDs. It also follows the component-provided flood-node list. Do not replace this branch order with an unconditional union of every visible cable and physical contact. Reachability of exceptional duplicate contacts and cross-body paths is not proven here.

## Microcontroller discovery and naming

Group rebuild **58142590** collects microcontrollers from nonnull flood-component pointers, deduplicates them by pointer, calls each controller's connection rebuild, then clears the group's rebuild flag.

Controller rebuild **56775897** clears its eight typed input/output binding vectors. It walks the islands reachable from its data-node groups, deduplicates islands by pointer, and collects flood components without repeating a vehicle-ID/component-ID pair. It then reads each other component's data descriptors, resolves the matching typed getter and creates a pointer-backed execution value only when that getter returns nonnull.

The descriptor enum has distinct bool, s32, f64 and analogue input/output kinds. Analogue data is a **peer ID plus f64 signal**, not merely another name for f64. Reset **58131605** stores peer **-1** and signal **0**; setter **58131963** stores the supplied pair directly. Source direction names and controller binding-vector names must retain their declared perspective.

The binding name comes from `component.get_name`, passed through the native script-token sanitizer. Name helper **55083474** uses a nonempty user alias; otherwise it uses the definition's name field. The sanitizer's exact normalization rules and resolution of duplicate sanitized aliases remain open. Discovery in this method does not check every island's power flag; execution power gating was traced separately in the [earlier script/electrical findings](OFFLINE-SYSTEMS-20261019.md).

The rebuild also resolves the script root, updates compilation state and conditionally resets globals/start position. Complete resolver/type diagnostics, write permissions, reload state and debugger ordering remain broader compiler/lifecycle work. The existence of pointer-backed bindings does not certify every descriptor against every getter.

## Verification and continuation

The existing **143** research tests remain passing at the joint checkpoint; no executable research tool changed in this documentation/evidence continuation. New exports passed exact source/range/instruction checks, and the combined reader re-audited all batches before advertising completeness. Selected constants, literal field names, reflection fields/enums and assembly instructions are checked independently. Installed GCL/PE and all 2,968 indexed data files were rechecked against the isolated source.

Continue native angle/physics contracts, all control interaction variants and device input paths, data-group cross-body rebuilds, aliases/resolver rules and scheduling. Every other full-register domain remains in scope. No game-runtime result is claimed.
