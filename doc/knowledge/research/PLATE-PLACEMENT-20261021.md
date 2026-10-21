# Plate placement, perimeter strips and native angles

2026-10-21; Steam build 25904830. GCL SHA-256 `626a994be960b7218409d9ca416d2664450231d1fc3295036fc77c81b8449355`; isolated PE SHA-256 `5c46cd34a3b00889ff36154976428ba43f6475430e92a2d113a360a78161a7d0`. This continues the vehicle-first [surface/collision checkpoint](PLATE-SURFACES-20261021.md). No game execution or installation/active-save edits.

## Placement adds gates beyond raw creation

The client and server ID-list wrappers (15732514, 52802086) delegate to their placement utilities with no excluded plate. The ID utilities (64051517, 65542671) resolve every node, optionally reverse the coordinate order, and reject a missing ID before calling the coordinate utilities.

Both coordinate utilities (64058882, 65550238) follow the same reviewed gate sequence, with different replication/container access:

1. Require at least **three** coordinates.
2. Resolve each coordinate to an existing node and find every consecutive boundary edge, including the closing edge. Missing nodes or edges reject placement.
3. Calculate facing and normalized normal; take size from the **first boundary edge**.
4. Call `test_is_convex` and reject its false result.
5. For Window type **1**, call window suitability; for Opening type **2**, call opening suitability. The opening helper delegates to the window helper in this build.
6. Check existing nonremoved plates classified by the type-only physics predicate, excluding the supplied plate pointer. When facing vectors have the same direction, a shared boundary edge traversed with the **same ordered node IDs** blocks placement. With a diagnostic collector the method records the blocker; without one it returns false immediately.

Opposite-facing skins are therefore not automatically blocked by that final same-direction condition. This supports the distinction between intentional opposed skins and same-facing shared-edge conflicts. The method does not perform a general mesh-intersection scan. It stops searching a particular existing plate once it finds a shared edge, including when that edge has opposite traversal. Do not expand this into a complete malformed-topology or overlap guarantee.

These are placement predicates. The [fresh-save loader and lower-level creator](PLATE-LOAD-20261021.md) have their own reviewed paths; they do not thereby inherit every placement gate. Tool interaction, server message authority and every mutation caller remain separate audit work.

## The convexity helper checks turn consistency

`vehicle_util.test_is_convex` (63697773) constructs a projection basis from the supplied normal. Its reference is Y-positive when `abs(normal.y) <= 0.99`, otherwise X-positive. It compares signed angles between each pair of successive boundary segments, rejects mixed nonzero signs and permits zero turns. The loop includes all cyclic triples.

The helper returns true for **fewer than three points**; the placement caller supplies the separate three-point minimum. It does not independently check coplanarity, winding count or self-intersection. A synthetic crossed five-point star has consistent turns and passes the modeled helper; a noncoplanar loop can also pass. These are helper counterexamples, not claims that complete in-game placement accepts those inputs. Native rounding, caller gates and all normal-tool reachability still apply.

Use simple, coplanar, convex panels for proposed vehicle bodywork. Keep extra engineering diagnostics separate from the exact source predicate; replacing the predicate silently with a stronger geometry algorithm would misrepresent the game.

## Native angle contract now traced

The matching PE registration body constructs the selected signature strings and stores the target pointer through both registration branches:

| Signature | Target RVA | Reviewed finite-input behavior |
| --- | --- | --- |
| `vec3.get_angle(first, second)` | `0x2cef0` | `acos(clamp(dot(first,second), -1, 1))`; **no input normalization** in this wrapper. |
| `vec3.get_angle(first, second, axis_x, axis_y)` | `0x2cf40` | Project both vectors onto the supplied axes, normalize each resulting vec2, then calculate the signed planar angle. |

The four-argument routine uses **(0,1)** when a projected vector has zero length. It does not normalize or orthogonalize the supplied axes. Its internal callee at `0x17e430` clamps the normalized 2D dot product, calls the reviewed `acos` implementation at `0x41cf94`, and chooses the sign using:

```
positive when second.x * first.y - first.x * second.y > 0
negative otherwise
```

With axes X-positive/Y-positive, X to Y is **-pi/2**, Y to X is **+pi/2**, and an exact half-turn takes **-pi**. Coincident directions take negative zero in the reviewed finite branch. The `acos` body contains its error-name literal and pi/2, pi endpoint constants, corroborating radians; this is not a bit-exact recovery of its exceptional-input/rounding contract.

This resolves the selected four-argument angle uncertainty noted in earlier attachment/adjacency research. It does **not** close the separate `vec2.get_angle` registration, all compass conventions, or complete plate-adjacency candidate ordering. Native loader specialization and the whole ABI remain outside these selected binding claims.

## Perimeter geometry has orientation-specific construction

The ordinary solid faces remain distinct from the [server convex-hull inputs](PLATE-SURFACES-20261021.md). `server_scene.vehicle_node.get_pos` (58914066) confirms that its position getter converts integer node coordinates to vec3 and multiplies by the native **0.08 m** grid size.

For **one-axis facing**, outer-strip builder 63347330 projects the nodes onto the plate axes, expands their bounds by **half a grid unit (0.04 m)**, and builds four clipping planes. For each cyclic boundary edge it gets the previous/start/end/next points, computes two outer-line intersections, constructs a four-point strip, clips it to those bounds and triangulates its surviving polygon. It also emits the opposite face using the supplied thickness displacement and back color. This is not a universal perpendicular offset of 4 cm: the line-position helpers choose signed sums/differences of the plate axes.

Inner and outer one-axis line-position helpers (63392243, 63401881) use the signs of the edge's projections on both axes. Inner and outer offsets oppose one another; both use half-grid factors. Their intersection helpers (63395253, 63398738) take a ray/plane intersection when `abs(dot(adjacent_unit_edges)) <= 0.99999`, otherwise use a perpendicular projection fallback. The ray/plane helper (63390690) returns its starting point when the absolute **numerator** is at most **0.0001**; otherwise it divides by the direction/normal dot product. It does not introduce a nonnegative-ray-distance clamp or a separate denominator guard in this reviewed body.

For **two-axis facing**, builder 63360918 finds the missing world axis. It skips boundary segments parallel to that axis; for each other segment it extends a quad by **0.04 m** along the signed missing axis, chosen from the cross-product orientation. It emits two triangles per face, including the opposite displaced face. The outer dispatcher still has no three-axis strip branch; that does not mean three-axis plates lack their separately built faces.

The shared 3D clipper (63548966/63552366) retains `dot(point,normal)-origin_distance <= 0`, reverses the distance sign when its boolean selector is set, and applies planes in order. The strip caller supplies the false selector. Boundary duplication and final GPU/native collision behavior remain separately scoped.

## Windows and openings need room for their frame

The recovered global constructors set **window frame width = 0.01 m** and **window inset = grid size * 0.5 = 0.04 m**. Opening suitability (63405539) delegates to window suitability (63407965).

The suitability helper first compresses consecutive segments with the same integer direction and converts retained corners to supported metre positions. For a cardinal plate it constructs inner-line intersections, suppresses consecutive/first-point near duplicates using **squared distance <= 1e-7**, then requires at least three retained points. It calculates a further frame-width inset at each corner. For noncardinal facing, its corner inset distance uses **0.04 + 0.01 = 0.05 m** instead.

Both branches use corner bisectors and a half-angle denominator `sqrt((1 + dot(side_normals))/2)`. Successive inset points must not reverse the corresponding original edge according to the dot-product check. The reviewed comparison runs from the second corner onward; it is not an additional complete polygon-validity certificate. No single minimum width is asserted for all slopes, corner angles, edge widths and degenerate loops.

For vehicle windows, reserve actual room for the frame and use supported simple panels around openings. Bare node dimensions alone do not establish usable opening dimensions.

## Tools, evidence and remaining scope

New [vector_angles.py](../../../scripts/research/vector_angles.py) 1.0.0 supplies ordinary finite-input models for the two selected native vec3 angle overloads and the turn-consistency helper. Eleven tests cover raw versus normalized inputs, native sign/half-turn, zero projection, supplied-axis scaling, concavity, reversal, collinear runs, noncoplanarity and a crossed-star counterexample. All **204 research-tool tests pass**. The model uses Python libm, excludes overflow/nonfinite inputs and is not bit-exact native execution or a full placement validator.

The local reader now has **1,530 functions / 229,223 byte-checked instructions / 1,301,220 independently summed instruction bytes**. New native exports cover four selected exception-directory spans, **276 instructions / 1,345 bytes**. Counts are access/checking measures, not whole-game completion.

Selected [GCL evidence](versions/build-25904830/plate-placement-20261021/evidence.json), [native evidence](versions/build-25904830/plate-placement-20261021/native-evidence.json) and [verification](versions/build-25904830/plate-placement-20261021/verification.json) preserve hashes and limited calibrations. Full proprietary exports remain local. Historical helicopter phantom geometry remains unresolved.

Continue remaining caller/authority and adjacency contracts, then native shape mass/inertia, structural strength, and complete vehicle powertrain, fluid, electrical, controls, suspension, flight and marine chains. Vehicle research remains the priority; the full audit stays incomplete.
