# Anymaker exploration — 11 October 2026

Explored the running v0.1.24 sandbox using the Computer Use plugin and read-only file inspection, under the supplied Local Development Access rules. Steam's manifest and the running window both identify `C:\Program Files (x86)\Steam\steamapps\common\Anymaker` as the installation; manifest build ID is 25826614.

## Verified findings

- Creation `.data` files are readable JSON. Typical companion files are `.meta` metadata and `.png` previews. JSON contains component definition references, vehicles, transforms, structural nodes/edges/plates, component placement/rotation, and separate electrical, mechanical, liquid, gas, belt, and data links. Link endpoints identify components and sometimes positions; routes can contain waypoints.
- Small saved carts provide useful examples. `steercart` has a seat, four wheels, a steering wheel, handbrake, and mechanical inverter junctions. Saved fields include handbrake state and wheel state; their presence alone does not establish live updates.
- The installation exposes 598 component definitions; 174 have data descriptors. Definitions include connection surfaces, positions, directions, types, sizes, and other geometry/interface information. Examples include motor RPS and power factor, battery energy store, wheel brake factor/RPS, steering and pedals, switches, and display values. Relevant definitions were copied into `component-map.json`.
- The game manual describes data connections and microcontrollers. An existing local script uses `on_tick`, reads a switch, and drives outputs. This verifies an internal scripting mechanism, not an external telemetry API.
- `working/scene.json` and tile files contain persisted world/player data, including position, inventory, and hotbar. During observation, working files and autosaves were rewritten at 14:09:22 and 14:14:22 EDT, five minutes apart. Later scene timestamps continued at five-minute intervals. These observations support periodic checkpoint behavior; disk state should not be treated as continuous telemetry.
- Inventory open/close, toolbar left/right, mouse-wheel selection, Duplicate Tool mode switching, and the local creation browser responded. Selecting `steercart` in the browser returned to the sandbox. A large scroll delta still changed the toolbar by one slot. Camera drags changed the view. The accessibility tree exposed the game window, without individually addressable game controls.
- A short forward key press produced no visible movement. Aiming Properties, Paste, and Edge tools at the nearby building produced no properties panel, placement preview, or visible construction from the current distance. The supplied rule to start from an existing structure was followed for the anchor attempt, but successful placement was not established.
- Final saved player position, vehicle counter (190), and entity counter (2030) matched the pre-test copy. All 102 recursively inventoried files beneath `creations` retained their baseline hashes. The game log remained 253 bytes with its original timestamp; no action-by-action telemetry appeared during the watched interval.

## Unknowns and limits

No successful spawn, component addition, steering/physics run, controller automation, or manual save/export round trip was completed. Consequently, interaction-driven vehicle file changes and exact live-to-saved field mapping remain unverified. The control API documents key presses but no duration-controlled key hold or controller input; sustained movement is unresolved. Debug/metrics key attempts did not yield a confirmed overlay. No supported external API, socket protocol, or script file/network output was verified.

## Recommended next steps

1. Build a read-only JSON inspector/validator from copies: resolve component definitions, inspect mating surfaces, audit structural connectivity and link endpoints, and display channels. This can immediately improve build review without relying on screen interpretation.
2. Repeat a small test within reach of an existing structure: add one component, save a separately named copy, change one switch or steering value, then compare exports and checkpoints. Keep explicit action timestamps to distinguish autosaves from deliberate saves.
3. Investigate documented script output/export capabilities before choosing a bridge. If none exists, use checkpoint diffs for slow observations and in-game displays/screenshots for live readings. A continuous external telemetry bridge remains a proposal.

Evidence and copies are in this `exploration` folder: baseline hashes, working-state backup, change events, component definitions, final scene/player tile copies, integrity results, and scene comparison. Ignore watcher `FirstSeen` records when analyzing changes: its initial scan marks existing entries as newly observed. The bounded watcher finished; it is no longer running.

No original creation files or installed binaries were edited. No mods, process-memory access, or destructive UI actions were used. The game naturally updated checkpoint files and settings during the session.
