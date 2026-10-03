# Anymaker technical reference

**Status:** Working reference, revision 1 — 2026-10-03. **Scope:** Anymaker only.  
**Purpose:** One place to check game mechanics before proposing a design, writing a controller, generating a native save, or asking for an in-game test. This is a mechanics/reference document, not a claim that the browser builder is an exact simulator.

## 1. Evidence and rules for using this reference

| Mark | Evidence | What it establishes |
| --- | --- | --- |
| **[GAME]** | In-game tooltip or direct gameplay observation supplied by the builder | Intended behavior stated by the game, or behavior actually observed |
| **[SAVE]** | Inspectable native Anymaker .data/.meta sample | Saved component properties, bodies and connection topology; not proof that every mechanism runs |
| **[ROM]** | Game component definitions or assets extracted into this repository | Component identities, faces, logic port indices, declared fields, dimensions and assets |
| **[GCL]** | Read-only inspection of the fingerprinted game-code version | Static code behavior for that version; not universal across updates |
| **[EDITOR]** | Implementation or tests in this repository's experimental browser builder | What the browser builder does; not necessarily what the game does |
| **[INFERENCE]** | A derived mechanical or mathematical conclusion | Design reasoning that still needs suitable verification |
| **[OPEN]** | Not established by the available evidence | Do not assume or silently fill in |

Rules:
1. Inspect the relevant repository definition, document and native examples **before** asking the builder to perform another in-game test.
2. Prefer direct in-game descriptions for intended controls, but distinguish tooltip wording from measured runtime behavior.
3. Never promote a browser-builder feature, passing test, mesh appearance or plausible model into a verified game mechanic.
4. Preserve **raw logic node indices** and distinguish signal links, torque faces, physical connector mates and rigid-body relationships.
5. Keep this reference restricted to Anymaker. Record contradictions, game-version differences and uncertainty explicitly.
6. Never overwrite supplied example saves; preserve original .data, .meta and preview image together. Do not publish example saves without permission.

Primary source index: [component catalog](../public/data/index.json), [definitions](../public/data/definitions/), [native format](03_XML_AND_NATIVE_FORMAT.md), [game/resource architecture](02_ANYMAKER_ARCHITECTURE.md), [mechanical mates](10_MECHANICAL_MATES.md), [hydraulics](11_HYDRAULIC_CONNECTIONS.md), [belts](14_BELTS.md), [plates](15_PLATES.md), [native structural islands](16_NATIVE_ISLANDS.md). Fingerprinted code summaries are in [evidence](evidence/).

## 2. Grid, geometry, rigid bodies and plates

### Grid and structure

- **[GAME + EDITOR]** Nominal lattice spacing is **8 cm per grid cell** (0.08 world units). A beam/edge can connect two grid nodes at arbitrary supported grid-point separation, including diagonals. The diagonal's physical length follows the endpoint displacement; it is not simply one axis's grid count.
- **[GAME observation]** Beam-connected structure belongs to a shared rigid physical body until it is separated by a movable joint or another body boundary. Different installed component coordinate frames do **not** automatically imply different rigid bodies.
- **[SAVE + GCL]** A native .data may contain multiple objects in vehicles.vehicles[], representing separate physical bodies. Each physical body may contain multiple grids[] used as component mounting frames. The browser builder's gridId is an editor grouping concept, not a native physical-body identifier. See [native format](03_XML_AND_NATIVE_FORMAT.md) and [mechanical mates](10_MECHANICAL_MATES.md).
- **[ROM]** surfaces[] describes attachment faces. The mesh's visible bounding box must not be substituted for the component's legal construction zone. Relevant definition fields include zones, interval, mode_x/y/z, surfaces[].pos/dir/type/gender, logic_nodes and data_descriptors.

### Plates and windows

- **[GAME observation]** The game selects a connected chain of frame edges, offers eligible following edges, and closes a boundary. The side from which the last edge is selected affects **which physical face of the boundary beams** receives the plate. It is more than a cosmetic normal flip.
- **[GAME observation]** The same boundary can hold **two separate plates**, one on each side. These can be painted independently. A rear-facing plate may show its metallic-looking back and exposed beam from the opposite side.
- **[SAVE]** plates[] references nodes and can contain col_front and col_back; plate_paint stores additional native painting data. A window may use plate type window.
- **[GCL]** For the inspected version, the game builds a connected node chain and applies planarity/convexity candidate rules before committing a plate. Geometry uses surface offset, thickness and outer frame operations. See [plates](15_PLATES.md).
- **[EDITOR limitation]** The current builder's edge-selection process differs from the game's connected-chain interaction and its duplicate-boundary logic does not yet fully reproduce the game-valid two-plates/opposite-sides case. Rendered plate thickness, outer trim, glass frames and painting are not fully equivalent. Do not infer game restrictions from these editor limitations.

### Separate physical bodies and joints

- **[GAME observation + SAVE]** Hinges and similar moving mates join **different bodies**; the joined beam is not rigidly welded to its parent. A hydraulic cylinder can connect a stationary base to a rod endpoint mounted on a separate hinged body.
- **[GCL + SAVE]** Hinges, latches, mounting pins, rails/sliders and tow connections use explicit native references, generally connected_vehicle and connected_component. Hydraulics additionally use connected_node_index. Merely overlapping the component meshes or drawing a mechanical control link is not equivalent to making the physical mate. See [mechanical mates](10_MECHANICAL_MATES.md).
- **[EDITOR]** The builder implements mate detection and exports multiple bodies for known supported configurations. Complex contacts, runtime articulation and real-game loading of generated saves are not fully validated.

## 3. Control signals and mechanical links

A **mechanical link** is a control-signal network. It is not a rotating torque shaft, a rigid hinge, or the physical connector face on a torque interface. **[ROM + SAVE]**

| Part / behavior | Verified rule | Source |
| --- | --- | --- |
| Mechanical Junction | One incoming mechanical signal splits into two identical outputs. | [GAME tooltip + ROM definition](../public/data/definitions/mechanical_junction.json) |
| Mechanical Invert | Output = input × −1. Thus 0 stays 0; 1 becomes −1. **Not** Boolean NOT. | [GAME tooltip + ROM definition](../public/data/definitions/mechanical_junction_invert.json) |
| Mechanical Offset | Output = input + configured offset, limited to the range −1 to 1. | [GAME tooltip + ROM definition](../public/data/definitions/mechanical_junction_offset.json) |
| Mechanical Scale | Has a configured scale; the small-engine example stores scale = 0.5. | [SAVE + ROM definition](../public/data/definitions/mechanical_junction_scale.json) |
| Mechanical Add | Definition has two mechanical inputs and one output. Exact clipping and operating semantics still need a matching tooltip/code check. | [ROM definition](../public/data/definitions/mechanical_junction_add.json) |
| Switch / toggle switch | Definition class button_switch, with a mechanical output and Boolean data output is_pressed. Do not assume every switch style latches. | [ROM definitions](../public/data/definitions/switch.json) |
| Clutch | Control **below 0.25 engages**; control **above 0.75 disengages**. | [GAME tooltip + ROM definition](../public/data/definitions/clutch.json) |
| Winch | Shaft rotation reels rope in or out. Settable rope length: 0.5–20 m. Its mechanical control link disengages the drum. | [GAME tooltip + ROM definition](../public/data/definitions/winch.json) |

**[OPEN]** The clutch's exact state transition inside 0.25–0.75, and the winch's exact disengagement threshold, have not been independently established. Do not assume either is continuously proportional.

### Complementary clutches from one 0/1 switch

**[GAME + INFERENCE]** Send the switch directly to clutch A and through Invert, then Offset set to **+1**, to clutch B:

    A = x
    B = clamp(1 - x, -1, 1)

| Switch x | Clutch A input | Clutch B input | Expected state |
| ---: | ---: | ---: | --- |
| 0 | 0 | 1 | A engaged; B disengaged |
| 1 | 1 | 0 | A disengaged; B engaged |

Inverting alone produces 0 and −1 for switch values 0 and 1, so it **cannot** control complementary clutches. This circuit is supported by the tooltips and thresholds; the complete physical drivetrain must still be appropriate.

### Data and microcontrollers

- **[ROM]** data_descriptors enumerates typed data inputs/outputs. The switch exposes is_pressed; electric motors expose target_rps and input_power inputs and rps/electric_consumption outputs. Some components expose additional status outputs.
- **[SAVE]** Native microcontrollers retain script and global_inputs/global_outputs/global_private. The saved examples show define var fractional, define var bool, on_tick, if, Boolean NOT, in/out component fields and persistent var assignments.
- **[EDITOR limitation]** The browser builder edits/preserves scripts but does not execute their logic or simulate the game's signal network.

## 4. Rotary torque, gearboxes, belts and winches

### Distinguish the mechanical connection types

- **Torque face:** a rotational drivetrain interface; declared under surfaces[].type = torque (or an engine-specific torque type). **[ROM]**
- **Drive shaft:** used for direct rotational transmission between compatible torque connections. **[SAVE]**
- **Torque interface:** has a torque face and a *separate* mating connector face. The straight form places them on opposite sides; the angled form turns the route through 90°. Two interface connector faces mate face-to-face and disconnect beyond **4 cm**. **[GAME tooltip + ROM]**
- **Important:** The trailer and torque-reversal saves contain reciprocal torque-interface pairs inside the **same** physical body. Their use is not restricted to connecting different bodies. **[SAVE]**
- **Mechanical control link:** carries a numeric control value; it does not carry rotating torque. **[ROM + SAVE]**

### Electric motors and transmissions

| Component | Behavior | Evidence |
| --- | --- | --- |
| electric_motor_a | Draws up to **10 kW**; runs nominally at **30 rps** while powered. Reverse and power are properties; target rps can be set by data link. | [GAME tooltip + ROM](../public/data/definitions/electric_motor_a.json) |
| electric_motor_b | Up to **60 kW**, nominally **30 rps**. | [GAME tooltip + ROM](../public/data/definitions/electric_motor_b.json) |
| electric_motor_c | Up to **120 kW**, nominally **30 rps**. | [GAME tooltip + ROM](../public/data/definitions/electric_motor_c.json) |
| gearbox (small engine) | Fits small engine; stretch for **2–8 gears**. Mechanical input **above +0.75 shifts up**, **below −0.75 shifts down**, then return to center before the next shift. Ratios and reverse in properties. | [GAME tooltip + ROM](../public/data/definitions/gearbox.json) |
| gearbox_b / gearbox_c | Fit medium / large engines; **two pneumatic shift ports**, first up, second down. Pulse **above 29.4 kPa** once; drop **below 19.6 kPa** before next shift. Stretch for **2–8 gears**. | [GAME tooltips + ROM](../public/data/definitions/gearbox_b.json) |
| gearbox_fixed_ratio | Fixed ratio between two torque faces. Input and output ratios each **1–8**, set as properties. Reverse is a property that flips output direction. | [GAME tooltip + ROM](../public/data/definitions/gearbox_fixed_ratio.json) |
| differential_gearbox_a | Torque faces named **in, left, right** plus a mechanical control input. Used in the trailer and torque-reverse saves to split the motor's input between two branches. | [ROM + SAVE](../public/data/definitions/differential_gearbox_a.json) |
| differential_gearbox_b | Torque faces named **in, left, right, out** and mechanical input. The extra out face distinguishes it from variant A. | [ROM](../public/data/definitions/differential_gearbox_b.json) |

**[GAME tooltip, variant caution]** A differential tooltip says its left/right outputs turn together at a property-defined ratio, its mechanical control above 0.75 disconnects both outputs, and a **rear output** passes input through 1:1. Only variant B's inspected definition exposes the extra face called out. Do not assign the rear-pass-through behavior to variant A without checking the specific in-game variant.

**[OPEN]** Whether a negative target_rps dynamically reverses the electric motor, and whether any differential/fixed gearbox can safely combine two independently driven shafts, remain unverified. The motor definition's is_reverse field is not, by itself, proof of a live reverse input.

### Belts and wheel radii

| Wheel | Radius | Speed of this wheel compared with ordinary pulley when coupled as described |
| --- | ---: | --- |
| pulley_wheel | 0.04 m | Reference radius |
| engine_wheel (small) | 0.10 m | Ordinary pulley runs **2.5×** engine wheel's speed |
| engine_wheel_b (medium) | 0.155 m | Ordinary pulley runs **3.875×** (~3.9×) |
| engine_wheel_c (large) | 0.267 m | Ordinary pulley runs **6.675×** (~6.7×) |

**[GAME tooltips + GCL]** Belt speed scales by radius ratio. Wheel reverse properties flip the belt direction. Ordinary pulley has radius 0.04 m. Game-code evidence establishes ordinary-belt path/mesh details; see [belts](14_BELTS.md). A two-wheel belt can be saved as one closed link; multiwheel loops require a coherent unbranched circuit. **[GCL + SAVE]**

**[EDITOR limitation]** The browser builder generates static belt geometry and preserves belt links, but does not simulate rotational speed, torque, tension or runtime belt motion.

### Proven design: reversible winch trailer

**[GAME observation + SAVE]** The builder reports that their trailer's winch reverses successfully. Its saved drive topology is:

    Electric motor A
       → differential gearbox A
       → two selectable branches, each with a clutch and pulley
       → shared three-wheel belt loop
       → output pulley / torque interfaces / drive shaft
       → winch torque input

The save has one electric motor A, one differential gearbox A, two clutches, two stepper motors, three pulley wheels, one winch, three belt links and three data links on the primary body. The torque-reverse standalone example demonstrates a smaller version of the same concept. Actual direction behavior is builder-reported; do not infer every belt contact's runtime direction from the .data alone.

**[SAVE]** The trailer and standalone torque-reverse example contain this controller script (names and syntax preserved):

    define var fractional DIR
    var DIR = 1.0
    define var bool RELEASED
    on_tick
    {
        if (out DIRSWITCH.is_pressed && var RELEASED)
        {
            var DIR = var DIR * -1.0
        }
        in Right.input = (var DIR + 1.0) / 2.0
        in Left.input = (1.0 - var DIR) / 2.0
        var RELEASED = ! (out DIRSWITCH.is_pressed)
    }

Each new press changes DIR's sign; the RELEASED variable prevents repeated toggling while the switch is held. Right/Left receive complementary 0/1 commands. This is a known *saved* solution for switching the actuators; no browser-side simulation has been claimed.

## 5. Fluid, gas, hydraulics and electrical systems

### General network rules

- **[SAVE + ROM]** Native saves contain distinct electric_links, mechanical_links, liquid_links, gas_links, belt_links and data_links. Each network must connect compatible **raw logic ports**, not merely components that look adjacent.
- **[ROM]** Valves, pumps, tanks, ports and junctions have different typed logic_nodes. Trace the complete route and control path before assuming flow.
- **[OPEN]** Detailed liquid/gas pressure loss, pump curves, gas mixing and all temperature-related simulation effects have not been comprehensively verified by these examples.

### Hydraulic cylinder and hinged arm

- **[ROM + GCL]** External cylinders come in matching base/rod sizes **1×1, 2×2 and 3×3**. Base raw logic nodes 0 and 1 are liquid; node 2 is hydraulic_base. The corresponding rod has raw node 0 of type hydraulic. The matching size matters. See [hydraulic connections](11_HYDRAULIC_CONNECTIONS.md).
- **[GCL + SAVE]** External cylinders use bidirectional connected_vehicle / connected_component / connected_node_index references, with length_max and extension_factor on the base, plus preserved hydraulic_cylinder fluid state. They do **not** use an invented hydraulic_links array.
- **[GAME observation]** The builder's example mounts a short beam on a hinge, with the cylinder rod connector mounted approximately halfway along the beam. Extending/retracting the cylinder rotates the beam around the hinge.
- **[SAVE — incomplete example]** The shared hydraulics.data has **one saved body, ID 205**. Its hinge pin references **body 206 / component 1**; the cylinder base (component 8) references **body 206 / component 2 / node 0**. Body 206, the moving beam, is **absent from this file**. The base stores length_max = 10 and extension_factor = 1. Do not synthesize or claim to have inspected the omitted geometry.
- **[SAVE]** The stationary hydraulic example contains 30 components, including two electric_motor_c units, hydraulic_pump, gearbox_fixed_ratio, two liquid_valve_t, two liquid_valve_straight, oil tank, relay, Mechanical Add/Invert/Offset and controls. It has 3 electric, 8 mechanical and 9 liquid links. A stored gearbox input property is 8; do not reinterpret its effect without the matching property semantics.
- **[EDITOR limitation]** Browser support stores the actuator's cross-body link and renders a diagnostic cylinder but does not simulate the arm's motion, fluid pressure or force.

### Small-engine example

**[SAVE]** The shared smallengine.data has one physical body, 64 components, 17 nodes, 17 edges, no plates, 7 electric links, 2 mechanical links, 6 liquid links, 2 gas links and 5 belt links. It contains the small engine, engine wheel, gearbox, alternator, multiple pulley wheels, electric motors, fuel and oil manifolds, oil filter, coolant manifolds, pumps, radiator/fan, air filter/manifold and tank/port components. Mechanical Scale is saved at **0.5** on its control path. This demonstrates the saved assembly and topology, **not** a measured output-power or fuel-consumption result.

### Electrical and control

- **[GAME observation + ROM]** Batteries supply the electrical network; electric relays have a mechanical activation input. Motor electrical supply and motor control data are distinct interfaces.
- **[SAVE]** The trailer's reversible winch combines electrical supply, motor torque, belt links, stepper motors and data-driven direction selection. The hydraulic example controls an electric relay and liquid valves through mechanical links.
- **[OPEN]** Exact battery output limits, electrical-network power sharing, relay thresholds and detailed alternator charging behavior need component-specific evidence before being treated as design constants.

## 6. Native saves and browser-builder compatibility

**[ROM + SAVE]** Native Anymaker .data/.meta are JSON, not XML. Representative native .data shape:

    definitions.components[]        // definition identifiers used by the save
    vehicles.vehicles[]
        id, transform
        nodes[], edges[], plates[], plate_paint[]
        grids[].components[]
        electric_links[], mechanical_links[], liquid_links[]
        gas_links[], belt_links[], data_links[]
        buoyancy_fill, loot_locations, creature_locations

A component instance can contain def (index into definitions.components), id, pos, rot, ext, colors and type-specific properties; joints and interfaces can contain connection references. .meta records body transforms/bounds summary. **[SAVE + format documentation](03_XML_AND_NATIVE_FORMAT.md)**

- **[SAVE]** Each link's endpoints reference component IDs and raw port indices. Do not renumber a port after filtering some logic-node types from the UI.
- **[SAVE]** The trailer's .data contains four physical bodies (IDs 264, 272, 274, 275); three are small joint-connected secondary bodies. Its reciprocal torque-interface references can also connect two components within body 264.
- **[GCL]** The game's structural-island traversal expects valid beam support for nodes in relevant cases. An example missing boundary beams caused a null dereference during island splitting in the inspected game version; the browser export has structural validation/normalization for known cases. See [native islands](16_NATIVE_ISLANDS.md).
- **[EDITOR]** The project format is anymaker-web-project v1. Editor JSON and the intermediate XML are **not** native .data. Native export exists experimentally, but arbitrary exported vehicles have **not** been accepted as loadable, behaviorally correct builds in-game. Import/edit/export can lose unsupported painting/geometry/detail; consult [native format](03_XML_AND_NATIVE_FORMAT.md).
- **[EDITOR]** The existing plate editor cannot yet round-trip all game-valid front/back duplicate loops; game-specific trim/thickness and complex native plate_paint also remain incomplete.

### Example inventory (provided in conversation, not published by this document)

| Original basename | Native data | Useful verified purpose | Limitation |
| --- | --- | --- | --- |
| trailerwithwinch | .data + .meta + .png | User-confirmed reversing winch; belt/clutch/controller/physical joints | No independent runtime simulation here |
| torquereverse | .data + .meta + .png | Compact belt/clutch reversing module and matching controller | Saved topology is not a generic torque-combiner proof |
| hydraulics | .data + .meta + .png | Stationary hydraulic machinery and cross-body references | Moving physical body 206 omitted from uploaded save |
| smallengine | .data + .meta + .png | Multi-network small modular engine assembly | Performance not measured |

These source uploads are not included in the public repository. The user-supplied archive, when available in its originating conversation, should be retained unchanged.

## 7. Design and verification checklist

For each new build:

1. **Brief:** target dimensions, body count, mechanical function and desired user controls.
2. **Manifest:** exact component definition IDs, extensions, settings, ports and power/fuel requirements; find definitions in the repository first.
3. **Geometry:** grid nodes, beams, legal plate loops, exterior/interior face choice, occupied component zones and clearance.
4. **Body graph:** identify every rigid body, hinge, latch, slider, rail, tow mate and hydraulic base/rod; ensure explicit reciprocal relationships where required.
5. **Network graph:** separately trace electric, mechanical-control, data, torque/belt, liquid and gas paths. No implicit conversion between network types.
6. **Controller:** specify input values and thresholds, including off/idle/failure states; use saved examples for Anymaker script syntax.
7. **File audit:** maintain valid native definition indices, body/component/port references, structural support, transforms, .data and matching .meta.
8. **Validation:** distinguish syntactic export/import tests from actual game-load tests and dynamic behavior. Log observed failures and game version.

## 8. Questions not yet answered

| Question | Why it matters | First place to investigate |
| --- | --- | --- |
| Can a negative motor target_rps reverse shaft rotation dynamically? | Could replace mechanical reversing assemblies in some designs. | Motor runtime code and matching in-game test, only if code is inconclusive |
| What exactly happens to a clutch between 0.25 and 0.75? | Determines safe switching and neutral behavior. | Clutch game code or measured in-game response |
| What value disengages the winch drum? | Needed for reliable winch interlocks. | Winch tooltip/code and a focused test if needed |
| Which differential variants support rear pass-through, and how are their ratios and disconnects implemented? | Avoids assigning a B-only face to A. | Variant-specific ROM definitions and game code |
| What are the full dynamic torque/back-drive rules of a multiwheel belt loop? | Needed to generalize the trailer's reversing layout. | Belt/torque simulation code and isolated builds |
| How do all pump/valve pressure curves and thermal effects work? | Required for predictive hydraulic and fluid machinery. | Component-specific ROM/GCL evidence before any trial |
| Where are the original English component tooltip strings stored? | Enables a complete component handbook without repeated screenshots. | Inspect additional language/resource files from the local game installation |
| Can the full revised native export load and operate reliably in-game? | Required before promising ready-to-use generated builds. | Test controlled minimal native saves, then complex assemblies |
| Can the browser reproduce separate plates on the two physical beam faces? | Required for accurate vehicle skins and interior panels. | Compare game save examples and update topology/plate serializer |

**Update policy:** Add only Anymaker findings. Record the game version, exact source file or tooltip, evidence level and any contradictory result. Keep unresolved items unresolved. Consult this document and linked definitions before asking the builder to repeat a test.
