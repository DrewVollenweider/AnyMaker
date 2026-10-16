# Anymaker local game reference

Compact-engine success: the user tested `Compact_Petrol_Engine_01` and exported it as `CPE1Running` on 14 October 2026. [Running result](../toolset/output/compact-petrol-engine-01-complete/LIVE-RESULT.md) confirms all 60 components in one body, unchanged placements/connections, 8,111 RPM at full throttle and 25.4 C. Use this accepted compact assembly for vehicle integration; sustained fluid circulation still needs separate validation. Its native component bounds are 1.28 × 0.88 × 0.80 m (width × length × height); allow 1.36 × 1.04 × 0.92 m for routed-line clearance.

First generated engine success: the user loaded and ran `Petrol_Pedestal_Test_01` in v0.1.25 on 14 October 2026, supplied a screenshot and exported running state. See [live engine result](../toolset/output/pedestal-engine-test-01/LIVE-RESULT.md). This is an accepted reference for loadability and running combustion; sustained circulation/cooling remains unresolved because the later save records no water in the radiator and no oil in the reservoir. Preserve the working assembly and isolate any future corrections.

Latest research: [v0.1.25 refresh, controls and native assembly findings](research-20261014.md), dated 14 October 2026. It supersedes older version-specific details where stated. The 2026-10-11 reference remains useful as a preserved baseline.

User-confirmed control rule: steering-wheel pedals are digital on/off inputs. Their documented 0–1 channel range does not establish proportional pedal positions. Design pedal-controlled systems around released/pressed states unless a different input source is separately verified.

Read-only inspection on 2026-10-11. Sources are the verified installed game at `C:\Program Files (x86)\Steam\steamapps\common\Anymaker`, especially `rom/data/*.json` and `rom/languages.tsv`. Findings below describe shipped documentation/data, not additional runtime testing. Searchable extracts and source hashes are in `reference/` beside this note.

## Navigation notes supplied by the user

N toggles building/free-move mode with noclip. If turning causes the backpack to obscure the view, press N twice quickly to leave and re-enter the mode and realign the character model. These are user-supplied operational notes; this pass did not retest them. The installed binding label independently identifies a sandbox free-move toggle. Builds should start from an existing structure, as the user explained.

## Building workflow from the installed manual and tutorial strings

- The building grid spacing is 8 cm.
- Sandbox tutorials say the nearby containers hold the parts and tools. Put the Edge Tool on the hotbar and select it.
- Edge placement is a drag between two points on an existing frame or component surface. A simple click is not the documented edge-building operation; this explains why the prior click attempt was inconclusive.
- Plates and windows are made by clicking connected edges around a flat loop and closing it. Openings and hatches also use closed loops; a matching hatch can seal an opening.
- Component placement uses a held action on a frame. Building elements can use a held action on ground or a wall. Rotation controls include variant cycling.
- Electrical, liquid, gas, and data connections are dragged between suitable nodes on the same vehicle. Mechanical connections run from an output node to an input node. Belt nodes must match type and face each other; hydraulic connector and base nodes must match size.
- Properties opens on a component and contains names, limits, and key bindings. The Microcontroller Tool opens a microcontroller's editor. Duplicate copy uses a held action and drag selection; paste places a ghost. Welding requires surfaces or edges aligned within 4 cm.

## Functional rules useful for build audits

Mechanical links transmit unpowered control signals in the -1 to +1 range. Drive torque travels through torque faces, shafts, gearboxes, clutches, and belts. A control wire alone does not constitute a drivetrain.

Seats accept a steering wheel, flight stick, or yoke on their main control face and up to eight throttle/shifter controls on side faces. Controls must share the seat's upright orientation; a backward-facing control is inverted. Steering wheel outputs are steering -1 to +1 and pedals 0 to 1.

The small wheel definition supports up to 32 degrees steering through a mechanical link and brake input 0 to 1; drive enters its torque face. Medium truck wheels instead describe hydraulic steering up to 40 degrees and pneumatic spring brakes, released progressively between 39.2 and 58.8 kPa. These rules must be applied by component ID, not generalized to all wheels.

Electric motors a/b/c draw up to 10/60/120 kW, require an electric port, and document a default powered speed of 30 rps. Target speed is writable through data. Reverse and power settings are available in properties.

Combustion engines document a 6 rps starting requirement, fuel/air, oil and coolant manifolds, and a 160 C limit. Engine size determines compatible gearbox and engine wheel. The small gearbox shifts above +0.75 or below -0.75 with a return to center between shifts; medium/large gearboxes use pneumatic pulses above 29.4 kPa and reset below 19.6 kPa. Clutches disengage above 0.75 and engage below 0.25.

Ports are separate components for many connections. Pipe links must match node size. Face-to-face interfaces connect separate vehicles; electrical, mechanical, torque, and data interface descriptions specify a 4 cm disconnect distance. Cable/hose inventory items provide another connection method.

## Scripts and telemetry possibilities

The microcontroller description specifies 10 W consumption, an electric port, script access to components on its data network, and power for displays/backlights on that network. That is a stronger documented requirement than assuming a controller works without a power connection.

The script UI catalog contains tick and render events, functions, parameters, typed variables, lists, conditions, loops, arithmetic, random values, conversions, and component inputs/outputs. It also contains pause/resume and step-in/over/out controls. These labels indicate intended editor facilities; exact syntax and debugger behavior remain untested.

Data descriptors preserve direction where present: for example motor `rps` and `electric_consumption` are outputs, while `target_rps` and `power_factor` are inputs. Some descriptors omit their type, so no default direction should be assumed without further verification. Sensor descriptions specify pressure in Pa, temperature in C, altitude in metres, tilt/heading in degrees, and gyro rotation in rps. Acceleration and rotation sensors describe their measurement axes, making orientation relevant.

No external script file-writing, networking, or telemetry endpoint was established. The extracted catalog supports internal sensor/controller/display instrumentation and offline validation; an external continuous bridge still needs a supported output mechanism.

## Located reference collections

The installed JSON includes 598 vehicle component definitions, 372 inventory item definitions, 136 props, 272 tile definitions, 220 junction definitions, 9 path-link definitions, 52 spawn-foundation definitions, 40 creatures, and 93 dungeon tiles. Inventory definitions include item classes, descriptions, inventory dimensions, attachment grids, and tier/category information. World definitions include geometry, connections, routes, loot, zones, and props; these are useful for later scene interpretation.

The manual covers movement, inventory, multiplayer, survival/weather, building, vehicle systems, and maintenance. English UI strings include detailed tool and starter-cart tutorials. Sandbox's shipped description says it provides unlimited items with no zombies, loot, or player damage; creative-dome mode describes survival outside the dome. These are documentation claims, not a new test of every game-mode behavior.

Files in `reference/`: `manual-text.json`, `building-and-script-ui.json`, component and inventory catalogs, and `source-index.json` with original paths and SHA-256 hashes. The broader English UI catalog is `ui-english.json`. All originals were read only; generated references live in the project workspace.
