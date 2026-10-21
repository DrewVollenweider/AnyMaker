# Vehicle structures, body splitting and deferred updates

Date: 2026-10-21. Build 25904830; GCL SHA-256 `626a994be960b7218409d9ca416d2664450231d1fc3295036fc77c81b8449355`. Decimal offsets refer to this exact file. These are offline implementation traces; the game and active creations were not changed or run.

## Research priority

The user prioritizes systems for making vehicles. Continue structural attachment, plates/edges, save integrity and usable cabin geometry first; then engines/drivetrains, fuel/oil/coolant/gas circuits, electrical power, controls, suspension/steering, flight and marine systems. Revisit older findings, variants, failure states and native units within those chains. Projectiles, explosions and AI are low priority; preserve their existing notes without letting that queue displace vehicle work. The full audit remains incomplete.

The practical target is reliable creations: supported parts, coherent skins and hidden services, working transmissions, and complete supply/control chains. Earlier user-confirmed results and failures remain evidence at their original scope. In particular, retain panel-facing corrections, layout-specific pump directions, positive-only pneumatic shift requests, digital pedals and the distinction between mounting grids and physical bodies.

## Structural connectivity and the retained body

The existing [engine/structure report](OFFLINE-ENGINE-STRUCTURE-20261019.md) established separate structural and functional networks. This continuation follows the traversal through actual splitting and update scheduling.

`_reset_island_indices` (52589302) assigns **-1** to unremoved edges/plates and to grid components. `_flood_islands` (52533957) seeds edges first, then plates, then components still carrying that index. Every new group starts with size zero. Each visited edge, plate or component increments that group's size by **one**; nodes are not separately counted.

| Visited object | Traversal follows |
| --- | --- |
| Edge, 52539235 | Other edges registered at either endpoint node, linked plates, linked components |
| Plate, 52543833 | Referenced boundary edges and linked components |
| Component, 52547798 | Linked edges, plates and components |

The shared worklist loop (52526963) continues until all three lists are empty. The assigned index guards repeat visits. It does not traverse the vehicle's electric, liquid, gas, data, mechanical-control or belt link collections as structural connections.

`_split_islands` (52623865) runs its split body when there is more than one group. It retains the group with the **largest counted object total** in the original vehicle and creates vehicles for the others. The comparison is strictly greater: equal counts retain the first encountered group. This selection is not based on mass, volume, seat presence or mounting-grid count in the reviewed method.

This matters when diagnosing detachment: the group that remains under the original vehicle identity need not be the physically heaviest group. A frame-only connected-components audit also remains insufficient, because components and plates can bridge frame groups.

## How attachments are registered

`vehicle_component.create_island_links` (54223153) passes the definition, extension, rotation, position and mounting frame to the attachment tester. On success it looks up returned edge/plate/component IDs and records reciprocal pointer links; it excludes the component's own ID from component-to-component links.

`vehicle_edge.create_island_links` (58207708) registers itself at its endpoint nodes. It also collects nearby components using an expanded bounds query and refreshes their attachment links. The expansion is edge size plus **one grid unit** per axis. `vehicle_plate.create_island_links` (59065172) registers itself on its actual boundary edges and performs a component-refresh query around its node bounds, expanded by **one grid unit**.

Those spatial queries collect candidates. The attachment tester still decides which links exist. They do not prove that every nearby or intersecting part attaches. Full contact branches, inclined mounts and every variant remain separate work; the earlier report records selected current-build plate-facing rules.

## Removing geometry is a coordinated transaction

The reviewed remove paths change more than the visible geometry:

- `remove_edge` (53247730) marks the edge removed, schedules cleanup, destroys structural links, removes its octree entry and removes plates referencing that edge. It decreases endpoint reference counts, removes unused nodes or conditionally attempts node collapse, clears endpoint pointers, and requests physics/island rebuilding.
- `remove_plate` (53273079) marks it removed, schedules cleanup, destroys links and removes its octree entry. It collects adjacent plate IDs, removes matching paint, clears adjacency and rebuilds neighboring adjacency while excluding the removed plate. It then requests physics/island rebuilding.
- The three nontrivial `destroy_island_links` helpers remove reciprocal references before clearing their own link arrays. Edge-to-node, plate-to-edge and component-to-edge/plate/component links have different ownership paths.

Plate adjacency metadata is also distinct from the structural flood graph. `rebuild_all_plate_adjacencies` (65648697) first sets each surviving plate edge's adjacent plate ID and edge index to **0**, then rebuilds adjacency. This zero sentinel must not be confused with the **-1** island-unvisited sentinel. The adjacency builder (65510638) considers other surviving plates and their shared-edge IDs, excludes a specified plate and opposite-facing candidates, and compares the angle helper's results before assigning adjacency. Detailed winding checks and angle semantics need assembly/helper closure before a complete adjacency emulator is justified.

Practical implication: moving or deleting just a rendered polygon is not a complete native edit. IDs, references, nodes, edges, facing, paint and derived geometry have to remain coherent. This trace does **not** establish the cause of the earlier helicopter's phantom plates or reverse its rejected result. Client rendering/replication, save application and geometry invalidation still need investigation.

## What splitting does to components and service links

The split method remaps nodes, rebuilds departing edges/plates in their destination vehicles, and removes the originals. Component movement goes through `_move_component_to_vehicle` (52567209), which unregisters old dynamic state, removes structural/octree links, transfers the component into a matching destination mounting frame, records its old/new IDs, moves network nodes, updates its parent and rebuilds attachment links. Component-specific split callbacks and ID-remap methods are invoked; their full implementations are not all covered here.

For electrical, mechanical-control, liquid, gas, data and belt links, the split method handles endpoints through the ID map:

| Endpoint outcome | Reviewed handling |
| --- | --- |
| Both endpoints remain in the original body | Keep the original link |
| Both move into the same new body | Recreate with remapped endpoints in that body, then erase the old link |
| Endpoints separate into different bodies | Erase the old link |

`vehicle_island.id_map.remap_ids` (58706337) writes **-1** to both supplied IDs and returns false on a missing mapping. The caller's original-body case and missing-map semantics matter when reproducing this table. Do not assume that every failed lookup represents a deleted component. Malformed IDs and component-specific links still require separate review.

The method also has distinct rope handling and finishes with motion-state rebuilding, split notifications and destination `post_load`. That is not evidence that ordinary service links can hold two bodies together or that every cross-body connection family follows this same table.

## When changes reach physics

`vehicle.tick` (53321058) skips its reviewed body while `_m_is_pending` is set. Otherwise it begins with `clean_removed`. A requested island rebuild runs before the requested physics rebuild and requests physics afterward. Physics rebuilding updates component/node bounds and motion state, calls the physics builder, refreshes dynamic-component constraints, then requests buoyancy rebuilding. Separate flags handle internal constraints and tier updates. Dynamic-component ticks follow those operations.

`clean_removed` (52818004) is gated by the general cleanup flag and the per-kind node/edge/plate flags. It erases marked entries, clears those flags and checks mounting grids. `vehicle_grid.empty` (58677471) delegates to its component container; that alone is not a whole-body emptiness test. A grid-side inherited flag can defer grid removal; its full contract remains open.

`post_load` (53212996) clears the pending flag, updates node/edge/plate/component ID counters and calls each grid's post-load method. It is a lifecycle step, not a complete substitute for loading, validation, attachment reconstruction or mesh rebuilding.

## Evidence and remaining work

[Selected function/call/constant evidence](versions/build-25904830/vehicle-structure-20261021/evidence.json), [field declarations](versions/build-25904830/vehicle-structure-20261021/reflection-evidence.json) and [verification](versions/build-25904830/vehicle-structure-20261021/verification.json) are retained with this report. Full decompilations and databases stay local. Byte-checked exports establish source identity and recovered instruction coverage; approximate C types and indirect/native calls still require judgment.

Next vehicle targets: complete attachment/contact predicates and split callbacks; plate creation/winding/size and rendering/collision invalidation; save-load reconstruction; body mass/inertia and structural strength; then complete powertrain, fluid/thermal, electrical, driving controls, suspension and rotor/jet/marine chains. No new gameplay acceptance or full-system completion is claimed.
