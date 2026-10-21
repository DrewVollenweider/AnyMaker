# Vehicle attachment surfaces and contact boundaries

2026-10-21; Steam build 25904830; GCL SHA-256 `626a994be960b7218409d9ca416d2664450231d1fc3295036fc77c81b8449355`. Research remains offline. The game and active creations were not executed or modified. This continues the [structural lifecycle trace](VEHICLE-STRUCTURE-20261021.md) and the vehicle-first research priority.

## What the attachment tester actually checks

The complete recovered body of `vehicle_util.test_component_attaches_to_vehicle<server_scene>` (65662243) was read, together with its supporting surface and intersection helpers. It collects spatial candidates, then follows three different paths:

| Candidate support | Reviewed requirement |
| --- | --- |
| Another component | Equal mounting-frame origin **and** direction; a pair of opposed rotated definition surfaces; overlap after shifting the new surface's voxel bounds by one unit along its normal |
| An edge/beam | The proposed component is on the exact base frame; the edge survives and has both endpoint references; endpoint or supported side-contact tests pass |
| A plate | The plate survives, passes the **type-only** physics-plate classifier, has at least three nodes and a valid first-node reference; then the applicable cardinal or equivalent-frame plate branch passes |

The exact base-frame test (63669379) requires origin `(0,0,0)` and direction `(0,1,0)`. Component-to-component comparison uses the actual origin/direction pair, not merely a grid container ID. The looser grid-equivalence helper used for plate mounting is a different operation.

The reviewed component-to-component structural path checks surface direction and bounds. It does not compare the surface's functional type string, gender or rotation-mode fields. Those declarations exist, but compatible torque, electrical and other mating interfaces remain separate requirements. Structural attachment alone is not evidence of power or signal transfer.

With no hit collector supplied, the tester can return on its first accepted support. With a collector, it records accepted component/edge/plate IDs and continues. The reciprocal structural links in the preceding report consume those results.

## Surface bounds and extension

`get_surface_min_max` (62420550) builds inclusive integer bounds from a surface's position, size and direction. X-facing surface size is arranged along Z/Y; Y-facing along X/Z; Z-facing along X/Y. The upper coordinate for a size-N span starts at position plus N minus one.

Extension is not a uniform translation of every face. For each tangential axis, let the original inclusive coordinates be `lo, hi`, the extension be `e` and the stretch center be `c`:

- Move the lower coordinate by `e` only when `lo - 0.5 > c - 0.25`.
- Move the upper coordinate by `e` only when `hi + 0.5 > c + 0.25`.

These strict comparisons include a **quarter-grid-unit deadband** around the stretch center. On the surface-normal axis, the positive-facing physical plane uses `hi + 0.5 > c`; the negative-facing plane uses `lo - 0.5 > c`. When that test passes, both normal-axis coordinates move by the extension.

`get_component_surface_bounds_voxel_local_to_grid` (62944565) then rotates both resulting corners, adds component position and orders their coordinate minima/maxima. This is component/grid-space arithmetic, not a world-space transform or arbitrary-angle collision solver. The [component geometry report](COMPONENTS-TYPES-20261020.md) covers separate point/zone extension rules; do not substitute those for this surface helper.

`test_voxel_bounds_overlapping` (63709927) uses inclusive bounds. Shared boundary coordinates count as overlap. In component-to-component attachment, the additional one-unit normal shift and opposed-face gate still apply.

## Beams and plates have different contact paths

The edge branch first checks each endpoint: it must be outside the original surface voxel bounds and inside their one-normal-unit shift. It also has side-contact branches for edges whose endpoint difference has one or two nonzero axes. Those branches include an exact plane-distance condition involving edge size plus one; the two-axis case projects into a 2D integer line test. A three-axis diagonal is not accepted through those side branches, although its endpoints still go through the earlier endpoint tests. This is narrower than a universal nearest-beam or bounding-box attachment rule.

For a component on the base frame, plate mounting requires a cardinal plate direction. The component surface normal must oppose it, and a bound's signed distance from the plate position must equal **plate size plus one** in native grid coordinates. The component's projected integer rectangle is tested against a triangle fan of the plate nodes.

For a component on a non-base frame, the code checks grid equivalence against the plate's first node and direction. It then accepts only a rotated **Y-negative** component surface whose lower local Y bound is **0** before performing the projected floating-point tests. Thus a generally overlapping inclined part is not sufficient.

`test_grids_equivalent` (63198804) has a cardinal shortcut: if each direction has exactly one nonzero axis, it returns true without checking the supplied origins. Otherwise it requires same-direction parallel vectors and zero dot product between the direction and origin displacement. This helper result must not be repurposed as a general world-plane equivalence certificate.

The frame transform (63672764) also incorporates the plate support-offset helper and half a grid unit along the frame normal. It is not simply integer origin multiplied by 0.08 m. The earlier [plate geometry findings](OFFLINE-ENGINE-STRUCTURE-20261019.md#plates-facing-support-offset-and-thickness) explain why node spacing, visible skin spacing and plate thickness are separate quantities.

## Two intersection details that affect validators

The integer rectangle/triangle helper (63692561) enumerates **integer points inside the rectangle** and checks the triangle's three closed half-planes in either winding. It is not a continuous polygon-overlap test. For rectangle `(0,0)..(1,1)` and triangle `(-1,0), (2,1), (3,1)`, there is continuous overlap but none of the four rectangle lattice points is inside. The helper therefore returns false. The point `(1/2,7/16)` is an independent interior witness, with positive barycentric weights `9/16,1/4,3/16`.

The integer rectangle/line helper (63682197) similarly traverses raster points using integer error updates and tests closed rectangle bounds. A replacement continuous line clipper is not automatically equivalent.

The floating-point rectangle/triangle helper (63685564) has an additional anomaly. Its first edge checks all four rectangle corners. Its second and third edges each check the second corner twice and omit the lower-left corner. This is present in the **assembly argument addresses**, not just approximate C: the corresponding dot-product calls load `R8` from stack offsets `0x300,0x300,0x310,0x320`; the first edge uses `0x2f0,0x300,0x310,0x320`. Constructor argument checks map those slots to the four corners.

An explanatory counterexample is rectangle `(0,0)..(4,4)` and triangle `(-8,-8), (1,2), (2,1)`. The origin is inside the triangle: barycentric weights `3/19,8/19,8/19` are positive and produce `(0,0)`. Yet the reviewed floating helper rejects the case because the omitted corner is the only corner inside the relevant edge half-plane. This establishes a helper-level discrepancy. It does **not** establish that a particular valid in-game placement reaches that counterexample, or explain the earlier helicopter corruption.

## Reusable tool and verification

[`attachment_geometry.py`](../../../scripts/research/attachment_geometry.py) exposes explicit-input surface bounds, voxel overlap, grid equivalence and the three reviewed 2D tests. It preserves the floating helper's repeated-corner behavior rather than silently replacing it with ideal geometry. Work caps and input guards are tool constraints; Python integers do not reproduce s32 overflow. The module does not parse a save, gather octree candidates, simulate physics or certify a complete mount.

Twelve new tests cover strict extension thresholds, positive/negative faces, all six surface directions, inclusive contact, raster endpoints, grid equivalence and independent barycentric counterexamples. The full research suite passes **171 tests**. Those are offline tool tests, not new game tests.

[Selected source evidence](versions/build-25904830/vehicle-attachments-20261021/evidence.json), [field/enum declarations](versions/build-25904830/vehicle-attachments-20261021/reflection-evidence.json) and [verification](versions/build-25904830/vehicle-attachments-20261021/verification.json) retain source identities, calibrated literals, selected calls and assembly arguments. Full code and databases stay local.

Next work remains vehicle-focused: finish candidate gathering, surface parser/defaults and valid placement constraints; trace plate creation/winding, render/collision invalidation and save reconstruction; then apply that knowledge to stronger native-file audits. Structural strength, body mass/inertia, complete powertrain/fluid/electrical/control/suspension and aircraft/marine chains remain open in the full register.
