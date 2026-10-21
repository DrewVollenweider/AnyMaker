# Plate creation, native reconstruction and mesh replacement

2026-10-21; build 25904830; GCL SHA-256 `626a994be960b7218409d9ca416d2664450231d1fc3295036fc77c81b8449355`. This continues the vehicle-first [attachment research](VEHICLE-ATTACHMENTS-20261021.md). The game, installation and active saves were not modified or executed.

## How a plate is created

The primary `server_scene.vehicle.add_plate` path (52734497) requires at least **three nodes**. Its ID-list wrapper (52721127) first resolves every node ID and returns null if any is missing. In the primary path, each consecutive node pair—including the closing pair—must have an actual boundary edge. Edge lookup (65577661) accepts either endpoint order, skips removed edges and returns the first match. A missing boundary edge causes the newly allocated plate to be erased and the method to return null.

The supplied reverse flag reverses node order **before** the plate records its nodes and calculates facing. It is not a late rendering-only flip. Construction assigns:

- Direction from the ordered node coordinates.
- Position from the first ordered node.
- The normalized direction and its plane-origin distance.
- Type and front/back colors from the arguments.
- Boundary edge references from consecutive node pairs.
- **Plate size from the first boundary edge's size.**

It then builds adjacency, inserts the plate into the spatial tree, creates structural links and requests physics rebuilding. This is a coordinated construction path, as the [removal/splitting report](VEHICLE-STRUCTURE-20261021.md) showed for deletion.

With mixed boundary widths, changing the node order can change which edge supplies plate size. A generator should account for that instead of assuming reversal changes only the normal. The reviewed method does not itself provide complete simple-polygon, coplanarity or self-intersection validation. Earlier tool/UI checks remain separate work; accepting a reference loop here does not certify its geometry.

## Facing calculation has a specific fallback

`calculate_plate_dir` (63379396) uses the first segment `p1-p0` as a fixed reference. It crosses that with each subsequent segment in order and returns the first nonzero result. The integer result is **not reduced to a unit vector or by a greatest common divisor**. Normalization is a later operation.

If fewer than three points are supplied, or every tested cross product is zero, the helper returns **X-positive `(1,0,0)`**. A repeated first coordinate therefore makes the reference segment zero and selects this fallback even if later points describe an area. The higher-level creator still rejects fewer than three nodes; the helper's fallback is not permission to create a valid two-node plate.

This also means “first three points are collinear” is insufficient to predict fallback: later segments can establish direction as long as the fixed first segment is nonzero. Complete admissible loop shapes remain unproven.

## Saved data is reconstructed, not restored as a mesh

The plate parser (51820491) reads `id`, `nodes`, `col_front`, `col_back`, `type`, `size`, `glass_state` and `glass_impacts`. ID, size and the two enum defaults use raw zero; omitted colors use the nearest palette entries to the game's front/back color globals. Do not substitute palette index zero for those color defaults. Node and edge parsers separately supply zero defaults for node IDs/coordinates, edge endpoint IDs and edge size.

The save writer (51730643) records surviving nodes, edges and plates. Plate records include their ordered node IDs, type, colors, size and glass data; they do not serialize the generated plate mesh.

The loader (51761852) performs the following reviewed sequence:

1. Recreate nodes with their saved IDs and positions, then update the node ID counter.
2. Create edges only when both endpoint IDs resolve. The loader disables endpoint collapse. The edge creator (52698203) rejects later duplicate endpoint pairs and retains the first edge, including its size/color.
3. Recreate plates through `add_plate`, with reverse **false**, using the saved ordered node list, type and colors.
4. Map each successfully recreated plate's saved ID to its newly assigned ID, then use that mapping for paint references. Paint whose plate was not recreated is not pushed through this branch.
5. Restore glass state and bounded impact data for successful plates.
6. Add mounting grids and components, invoke component creation/post-add hooks, update component IDs and restore each functional link family only when its `can_add_*` predicate accepts the endpoints.

The saved plate **size field is parsed and written**, but the reviewed load method does not apply it after construction. The construction path derives size from the first boundary edge instead. Facing, position, boundary references, adjacency and structural links are similarly rebuilt through creation. Editing a saved `size` field alone therefore does not control the resulting support offset in this path.

This is not a complete loader emulator: outer world/body creation, parser error contracts, every component callback and native resource behavior remain separately reviewable.

## What reaches the client

The client plate-container create callback (20263885) derives normal and plane distance from replicated direction/position, resolves node and edge references, builds adjacency and inserts the spatial-tree element. It requests physics and plate/edge geometry rebuilding. The destroy callback (20268553) clears adjacency, rebuilds surviving neighbors while excluding the removed plate, removes its spatial-tree entry and requests the same rebuild categories.

Plate replication (20328391) explicitly requests plate/edge geometry updates for changed type, colors, glass state or impact data. Changes in the physics-plate classification also request physics rebuilding. The complete container/property callback contract is not established by this one method.

Component geometry, paint geometry and plate/edge geometry have **separate rebuild flags and builders**. `_rebuild_geometry_plates_edges` (15667609) iterates the current edge and plate containers into a fresh builder. `vehicle_plates_edges_builder.build` (63503803) replaces pending buffers for opaque plates, glass plates, edges and plate cracks.

The pending-buffer helper (63149088) is significant for deletion: when a pending buffer exists, it destroys the old rendered resource first, creates a replacement only if vertex count is greater than zero, then releases the pending buffer. An empty buffer therefore still removes the old mesh. This is not a code path that deliberately retains old geometry whenever the new vertex count is zero.

Client tick (16024717) calls `_rebuild` only while its `m_pending_split_vehicles` list is empty; it applies already-pending geometry afterward regardless of that rebuild gate. `_rebuild` (15648309) handles physics/buoyancy/bounds before the separate component, paint and plate/edge flags. These are traced scheduling conditions, not proof of a stalled renderer or the cause of an earlier visual failure.

## Read-only plate audit and historical samples

[`plate_reconstruction.py`](../../../scripts/research/plate_reconstruction.py) checks the native creation's plate node loops, required boundary pairs, direction fallback, coplanarity and first-edge size. It preserves first-edge behavior when later duplicate edges appear and leaves duplicate node-ID binding unresolved. It reports shared node loops separately from same-facing, same-size loop warnings: opposed skins on one frame must not be mistaken for duplicate visible surfaces.

```powershell
python scripts/research/plate_reconstruction.py creation.data --output plate-audit.json
python -m unittest discover -s scripts/research -p 'test_*.py' -v
```

The creation is read-only and a supplied output must be a new file. These are selected reconstruction checks, not a complete polygon, attachment, collision or game-load certificate. Python arithmetic does not reproduce native s32 overflow.

Ten new tests cover reference failures, winding, collinear prefixes, fallback, first-edge size changes, duplicate handling, intentional opposed skins and input preservation. The complete research-tool suite passes **181 tests**.

Five archived samples were audited without changing their input hashes: the helicopter before inset, rejected generated inset, the archived user-reported corrupt copy, a later rear-shell version and the accepted compact I4 running save. All had **zero findings within these checks**. The generated inset and archived corrupt copy have the same SHA-256. Shared node-loop groups in the helicopter samples have opposing facing rather than same-facing duplicate loops. These results do **not** rehabilitate the rejected inset or establish what caused the phantom surfaces. The earlier failure remains unresolved; another all-clear static check is not gameplay acceptance.

[Source evidence](versions/build-25904830/plate-load-20261021/evidence.json), [field declarations](versions/build-25904830/plate-load-20261021/reflection-evidence.json), [scoped archive results](versions/build-25904830/plate-load-20261021/archive-audit.json) and [verification](versions/build-25904830/plate-load-20261021/verification.json) are published. Full code, databases and private creation copies remain local.

Next vehicle work: plate clipping/outer strips and collision generation, valid tool placement rules, complete client invalidation and load/replication contracts, then body mass/structural strength and the remaining powertrain, fluids, electrical, controls, suspension and aircraft/marine chains. The full audit remains active and incomplete.
