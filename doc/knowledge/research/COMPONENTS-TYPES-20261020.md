# Component construction, reflection and geometry

2026-10-20, Steam build 25904830. Source GCL SHA-256 remains `626a994be960b7218409d9ca416d2664450231d1fc3295036fc77c81b8449355`. This continues the [full-game audit](AUDIT-REGISTER.md) offline. The game, installation and active saves were not executed or edited. Complete system behavior remains under investigation.

## Type and function recovery

The new `reflection_index.py` reads the **declared 8,084-entry reflection table**, including 7,633 structure descriptors and 451 enum descriptors. Its counted records consume exactly bytes **66,399,263 through EOF 82,528,301**: 16,129,038 bytes. This is a complete parse of that declared table in this source, not recovery of the entire GCL loader, native ABI or all intrinsic implementations. The 402 bytes between the final indexed code allocation and the table remain outside this parser's interpretation.

The table provides declared parent types, reported sizes/alignment, virtual-method declarations, lifecycle signatures, field types/offsets and enum label sequences. It preserves unknown flags and the unresolved meaning of a zero list count. Two pointer-type names occur twice and remain ambiguous. Some fields start at their owner's reported size; the tool retains them and does not claim their complete native storage widths are valid or recovered.

Reading the table exposed a limitation in function scanner 1.3: it rejected qualified template names containing spaces, such as `property_type_base<property_bool, bool>`. Scanner **1.4** accepts balanced template-qualified names while rejecting spaces in ordinary names. The refreshed index contains **37,140** bounded function records. All earlier **37,082** records retain identical source identities and bytes; **58** additional records account for 18,572 additional native code bytes. Those new bodies were indexed, not automatically understood or all decompiled.

Four new export batches add **241** functions, 15,638 instructions and 86,050 instruction bytes. The combined selected reader now contains **394 unique functions, 58,665 instructions and 339,395 source-checked instruction bytes**. It has 3,203 local slot-derived call dependencies and 2,269 unresolved indirect sites. Declared method tables improve investigation but do not turn those counts into an executed call graph.

The matching [reflection summary](versions/build-25904830/components-types-20261020/reflection-summary.json), [selected declarations](versions/build-25904830/components-types-20261020/reflection-evidence.json), [component bindings](versions/build-25904830/components-types-20261020/component-bindings.json) and [selected code evidence](versions/build-25904830/components-types-20261020/evidence.json) are public. Complete metadata/code databases stay local.

## All shipped component classes now have construction evidence

All **207 named classes** in the 598 shipped component definitions have matching reflected class descriptors and exported constructors. The four definitions omitting `class` use the generic base path described below. There are 224 declared server-component types including the root, shared bases and compiled-only types. Presence in compiled metadata does not establish a shipped, creatable component definition.

The constructor tracer follows the entry object pointer, private stack spills, direct constructor operand dependencies and type-tag stores until the first control-flow boundary. All 208 initial constructors, including the root, store their own type tag. All 207 non-root constructors make a same-address component initialization call. Four additional shared-base constructors close the chains for ammo belts, fixed/suspended rollers and sprockets. Their observed initialization parents agree with the reflection declarations for all **211 non-root constructors** reviewed.

This confirms important previously unresolved relationships:

| Component class | Declared/observed initialization base | Consequence established here |
| --- | --- | --- |
| `furniture`, `weight_block` | Generic `vehicle_component` | No locally declared methods are required for these distinct constructed types |
| `gearbox_c` | `gearbox_b` | Its declared tick, save parser and gear-count implementation come from `gearbox_b` |
| Hydraulic rod ends `_2_2` / `_3_3` | Common hydraulic rod end | Shared implementation is located on the base, with definition-specific geometry/size |
| Hydraulic bases `_2_2` / `_3_3` | Common hydraulic base | Same construction relationship; pressure/constraint behavior still needs its own full trace |
| Engine wheels B/C | Common engine wheel | Shared initialization does not mean identical radii or interface dimensions |
| Roller and sprocket variants | Shared fixed/suspended roller or sprocket base | Shape/width variants must still retain their own definition parameters |

The large gearbox's reflected gear-count declaration points to the current getter computing **clamp(2 + extension.z, 2, 8)**. This closes the earlier declaration-binding gap behind the eight-speed design. It is separate from the accepted two-gear driving observation and does not invent a later successful eight-speed test.

Compiled-only types include solar panels, hydraulic motors and train wheels, alongside shared implementation bases. They have no corresponding class in the current shipped component definitions. Do not generate unsupported definitions or promise these as available building parts from this evidence.

## Factory and save loading

`create_component_class` at 54219509 constructs a qualified type name by appending the definition's class string to `server_scene.vehicle_component.` and calls reflected type creation. An empty class goes directly to base allocation. A failed named creation logs an error and also allocates the base component.

`save_data.vehicle_component.parse_save_data` at 51789634 resolves the definition table entry, performs reflected creation using its class, falls back to base allocation when necessary, then parses the component inline and attaches its definition. A creation loading without an immediate failure therefore does not prove the intended specialized class was instantiated. Definition IDs, class names and saved state must remain consistent.

The shared base parser at 57095517 handles ID, colors, grid position, rotation and extension independently. Reflection names the relevant storage `m_grid_pos`, `m_rotation`, `m_extend_size`, `m_definition`, `m_grid` and separate structural adjacency vectors. This reinforces the earlier distinction between mounting frames, bodies, structural links and functional networks.

## Native defaults and enum labels

The current parser supplies these explicit defaults. Builtin vector default constructors whose numerical initialization has not been recovered are deliberately not converted into guessed numbers.

| Field | Default established by parser and reflection |
| --- | --- |
| Definition class/name/description strings | Empty strings |
| Array modes X/Y/Z | Enum 0, `none`; other labels are `stretch` and `tile` |
| `edge_size` | Explicit `(1,1,1)` |
| `interval` | Explicit `(0,0,0)` |
| `ext_max` | Explicit `(10,10,10)` |
| Building/surface/furniture/devolvable flags | False |
| Density | 400 native coefficient; full mass/unit path remains separate |
| Inventory stack capacity/default stack size | 99 / 1 |
| Logic-node ID | Empty string |
| Logic-node direction | 0, `x_neg` |
| Logic-node type | 0, `mechanical_out` |
| Logic-node size selector | 0 |
| Surface dimensions | Explicit `(1,1)` |
| Surface direction/rotation/gender | 0: `x_neg` / `any` / `none` |
| Zone physics flag | True |

The direction label order is **0 x_neg, 1 x_pos, 2 y_neg, 3 y_pos, 4 z_neg, 5 z_pos**. The current byte comparisons in the port-size offset helper corroborate these axis pairs. Do not pair directions by appearance or import another engine's axis convention.

Logic-node labels in order are **mechanical_out, mechanical_in, electric, belt, belt_track_narrow, belt_track, belt_track_wide, data, liquid, gas, hydraulic_base, hydraulic, ammo_40mm**. Thus gas is index 9, liquid 8 and data 7 in this enum. These enum indexes are distinct from per-type node ordinals and absolute saved logic-node indexes.

The generic string-enum parser converts through reflected enum information. On failed conversion it restores the provided default; its write path omits a default value. This reviewed function does not establish the behavior of every upstream error reporter. The reflection table also contains duplicated localization enum labels, which the parser preserves rather than treating as corrupt data.

## Geometry rules for native tools

`component_geometry.py` exposes explicit-input arithmetic from these traces. Its validation guards are model constraints, not recovered game restrictions; Python integers do not reproduce native s32 overflow. It is not a mounting, collision or native-save certificate.

**Extension availability and limits:** `get_is_extendable` compares the interval vector with `(0,0,0)`. Mode names alone are insufficient. `get_extend_size_clamped` uses `min(requested, maximum)` on each axis; that helper contains no lower-zero clamp. This is not permission to generate negative extensions: other creation/editor paths and supported limits remain separate.

**Point-like nodes:** on each axis, a node position moves by the extension only when the original point coordinate is **strictly greater than** `center_stretch`. Equality does not move it. The two-coordinate overload supplies `(x,0,y)` before using the three-coordinate helper.

**Zone bounds:** the minimum comparison uses **min − 0.5**, while the maximum uses **max + 0.5**, each compared strictly with the stretch center. For a single inclusive cell at zero and center 0.1, a positive extension can move its outer maximum while the node point at zero remains stationary. Applying the point rule to zone bounds would give an incorrect result.

**Native volume getter:** it sums `(max.x-min.x+1) × (max.y-min.y+1) × (max.z-min.z+1)` for the extended zones. It does not compute a geometric union or filter the zone physics flag in this getter. Two overlapping zones therefore contribute twice to this particular count. Collision construction separately checks the physics flag. Do not substitute a union of rendered/collision geometry for the getter's count.

**Port size offset:** an odd size selector adds half a grid unit on both axes perpendicular to the direction axis. X directions 0/1 give `(0,.5,.5)`, Y directions 2/3 give `(.5,0,.5)`, and Z directions 4/5 give `(.5,.5,0)`. Even selectors return zero in the reviewed normal cases. This corroborates the earlier 2×2 hydraulic endpoint offsets. Full placement still requires the component/grid transform and the correct interface type.

**Coordinates:** the component-local transform converts integer grid position using the 0.08 m grid constant and converts the integer rotation matrix. The shared component transform composes that with its mounting-grid transform. The body/world transform remains another operation; do not treat a component's saved position as a world position.

**Port indexes:** `get_logic_node_index` counts only matching node types while returning their absolute position in the complete logic-node list. It returns −1 when no matching ordinal exists. The ID lookup also requires the matching node type. This independently supports the earlier T-valve correction: one mechanical input before three gas nodes makes gas ordinals 0/1/2 correspond to saved indexes 1/2/3.

## Past findings clarified by field declarations

Reflection confirms engine offsets 0x2a0/0x388 as `m_content_lubricant` / `m_content_coolant`, 0x590 as `m_rps` and 0x600 as `m_display_torque`. The field name alone does not supply SI units; the previous combustion/tooltip arithmetic remains the relevant unit evidence.

The oil-filter item field at **0x90 is declared `m_condition`**. This resolves the naming uncertainty in the previous report: the reviewed removal branch spends condition at `removed dirty quantity × 0.1`. It does not settle all replacement, depletion or external flow behavior.

The large gearbox's current/target gear, clutch factor and two trigger latches are separately declared fields, matching the prior transition trace. These declarations help future diagnostics distinguish a target command from actual engagement.

The rejected helicopter inset remains rejected. None of the new metadata or geometry arithmetic establishes the root cause of phantom geometry or validates a new aircraft revision.

## Validation and continuation

The selected evidence check covers 242 function identities, 24 scalar constants and selected strings/call sites. The reflection check reparses the complete counted table and verifies 234 selected type identities, six enum lists, 31 fields and eight virtual declarations. Constructor observations cover 212 types, including four shared bases. Exact completed validation counts are in [verification](versions/build-25904830/components-types-20261020/verification.json).

The tracer's repeated full-table SQL lookups were replaced with a single signature cache, preserving ambiguity. Evidence for all 208 constructor exports was identical before/after that optimization. The final reader was rebuilt with the refreshed index and frozen tool versions; superseded intermediate readers remain local diagnostics.

Tests cover template-qualified signatures, malformed/truncated descriptors, exact declared count/EOF, duplicate labels, boundary fields, forged declaration claims, constructor stack/branch controls, absolute port ordinals and geometry boundary/invariance counterexamples. Passing synthetic tests is not game-runtime acceptance.

Next work uses the recovered declarations to follow complete functional chains: all component variants' tick/parser/mating behavior, physical constraints and structural mutation, propulsion and thermal networks, compiler/intrinsic behavior, world/actors/combat and multiplayer/save authority. The [full register](AUDIT-REGISTER.md) remains active; this foundation does not mark those systems complete.
