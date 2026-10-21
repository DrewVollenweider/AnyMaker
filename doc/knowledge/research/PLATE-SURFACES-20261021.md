# Plate surfaces, clipping and collision inputs

2026-10-21; build 25904830; GCL SHA-256 `626a994be960b7218409d9ca416d2664450231d1fc3295036fc77c81b8449355`. Continues the vehicle-first [plate construction/load research](PLATE-LOAD-20261021.md). No game execution or installation/active-save edits.

## Visible faces and physical boundaries differ

For a solid plate, `add_geometry_inner_solid` (63302744) creates a triangle fan anchored at the first node. Each front triangle uses node order **0, i+1, i**; the opposite face uses **0, i, i+1**. Both use the supplied support offset. The second face also receives the opposite-normal thickness displacement calculated by `add_static_geometry` (63375987). This helper does not triangulate arbitrary concave loops or validate their admissibility.

The [earlier support-offset trace](OFFLINE-ENGINE-STRUCTURE-20261019.md) established an ordinary cardinal support distance of **0.04 m**, a large selector distance of **0.12 m**, and plate thickness **0.01 m**. Thus the ordinary cardinal solid faces lie at **0.03 and 0.04 m** along the normal from the node plane. These are face positions; perimeter strips, beams, and native collision margins are separate.

The server `build_physics_shape` (52757266) uses a different operation for each eligible physics plate. For every boundary node it supplies two positions to **`physics.shape.create_convex_hull`**:

```
node_position_metres + unit_normal * 0.08 * 0.35
node_position_metres + unit_normal * 0.08 * 0.45
```

Those inputs sit at **0.028 and 0.036 m** from the node plane, an **0.008 m** separation. The reviewed point-generation path uses the plate normal and grid size; it does not use the visible support-offset selector or visible triangle fan. It first checks removal/type/glass eligibility. This is evidence for the hull inputs, not a recovered native hull algorithm or final contact margin.

Practical consequence: a visible recess or gap in a proposed node loop does not establish collision clearance. The source requests a convex hull for the whole eligible plate. Whether a particular concave loop can be built through the normal tools still needs separate placement-rule research. Separate plates around an intended opening are a better-founded design direction than assuming one complex loop preserves a physical cutout; complete opening/window/hatch behavior remains separately scoped.

The broader shape builder also adds edge capsules and component-zone boxes, with fallback shapes for otherwise empty bodies. It does not use the visible mesh as a universal collision mesh. This checkpoint does not close all component-zone, mass/inertia, native shape or player-contact contracts.

## Clipping is an ordered half-plane operation

`clipping_plane` construction (24921261) stores position, edge vector, normal and `dot(position, normal)`. The single-plane helpers (63215559, 63218159) calculate:

```
distance = dot(point, normal) - origin_distance
inside = distance <= 0
```

They walk every edge of the closed input loop, retain an inside starting point and insert a linearly interpolated point when the edge crosses the plane. There is no positive tolerance in the reviewed comparison: the calibrated threshold is exactly **0.0**. Exact boundary transitions can produce repeated points; the helper does not deduplicate them.

The parallel-coordinate overload interpolates its second vec2 stream with the **same crossing fraction**. This matters for paint/texture coordinates: clipping geometry alone and retaining the original coordinate list would break the correspondence. The multi-plane wrappers (63384346, 63387505) apply planes in order using temporary output buffers. No planes preserve the input, and later planes still run after an empty result. The coordinate wrapper reports an error if the two input counts differ; the error handler's termination behavior is not established here.

## Plane construction depends on orientation

The plate grid is built by 63451963/63452860/63454188. Its first axis is the normalized cross product of the plate normal and a reference axis; the reference changes from Y-positive to Z-positive when `abs(normal.y) > 0.9`. The second axis is the normalized cross product of the first axis and normal. Grid origin combines `normal * plane_origin_distance` with the separately calculated support offset. Zero/invalid normals remain outside the helper model's supported domain.

`get_plate_clipping_planes_inner` (63424596) requires at least three nodes and appends one plane for every projected boundary segment. The outward 2D normal is **(-edge_unit.y, edge_unit.x)**. It appends to the supplied list; callers must manage prior contents.

`get_plate_clipping_planes_outer` (63431577) has three branches, selected by the number of nonzero components in the integer facing vector:

| Facing components | Reviewed outer clipping construction |
| --- | --- |
| One | Projected bounds expanded by half a grid unit; diagonal boundary segments also contribute planes shifted by signed half-grid components. |
| Two | Expansion projected through the missing world axis; diagonal segments receive a component-wise scaled shift, followed by two limiting bounds planes. |
| Three | One plane per projected boundary segment without those half-grid expansion branches. |

This is a clipping-plane list, not proof that every branch creates an identical visible perimeter. The separate `add_geometry_outer` dispatcher (63344115) calls its one-axis or two-axis strip helper only; it contains no three-axis dispatch. Those strip helper implementations remain a next target. Do not turn this into an unsupported rule that all three-axis plates fail to render.

## Reusable calculations and checks

New [plate_surfaces.py](../../../scripts/research/plate_surfaces.py) 1.0.0 provides pure calculations for ordered 2D clipping with optional parallel coordinates, the solid-face triangle fans, and the server collision **input point cloud**. Callers supply explicit local metre coordinates, a unit normal and, for faces, the support offset. It does not read or edit creations, implement the native hull solver, classify glass/type eligibility, create outer strips or certify a build. Its input guards are model restrictions, not newly claimed game restrictions.

Twelve new tests check known half-plane boundaries, coordinate interpolation, repeated boundary points, empty outputs, input preservation, opposite winding, both normal directions and an oblique 8 mm slab separation. The full research-tool suite passes **193 tests**. The first run exposed a decimal-versus-binary floating comparison in the negative-normal test; its expected extent comparison now rounds at eight decimal places. Geometry arithmetic was unchanged, and the failed log is retained locally.

The local reader now contains **1,507 functions / 220,625 byte-checked instructions / 1,248,373 independently summed instruction bytes**, including both new batches. Selected [code evidence](versions/build-25904830/plate-surfaces-20261021/evidence.json), [reflection evidence](versions/build-25904830/plate-surfaces-20261021/reflection-evidence.json) and [verification](versions/build-25904830/plate-surfaces-20261021/verification.json) remain narrowly scoped. Counts measure access and checks, not semantic completion. Historical helicopter phantom geometry remains unresolved.

Continue with perimeter-strip helpers, placement validity and collision/native contracts, then body mass/inertia and the remaining powertrain, fluid, electrical, control, suspension, flight and marine chains. Vehicle systems remain the priority; combat/projectile/AI research stays parked.
