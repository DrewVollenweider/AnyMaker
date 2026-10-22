# Hull construction thresholds, face references and linked native ranges

2026-10-22; build 25904830. GCL SHA-256 `626a994be960b7218409d9ca416d2664450231d1fc3295036fc77c81b8449355`; isolated PE SHA-256 `5c46cd34a3b00889ff36154976428ba43f6475430e92a2d113a360a78161a7d0`. Continues [hull mass integration](HULL-MASS-20261021.md). No game execution, installation edits or active-save changes.

**Version scope:** the final source check detected installed build **26113663** with different GCL and PE hashes. Findings below remain verified against the archived **25904830** snapshot. The [build-transition comparison](BUILD-TRANSITION-20261022.md) records the changes; transfer to the new installation is unproven and requires revalidation.

## Exporting linked native code ranges

Several earlier PE selections contained only a function's first runtime range. The approximate C followed branches into further code, but the exported instruction checks covered only the selected prefix. Those cases were explicitly kept separate from whole-body byte evidence.

The executable supplies stronger boundary evidence: version-1 chained unwind records identify previous runtime entries, including nested chains. Microsoft's [x64 exception-handling documentation](https://learn.microsoft.com/en-us/cpp/build/exception-handling-x64) defines the aligned chained entry layout and allows both nested and noncontiguous chains. A linked group still does not prove a complete CFG, ABI, all leaf functions or every semantic path.

New [native_unwind.py](../../../scripts/research/native_unwind.py) 1.0.0 resolves those links against exact declared runtime entries. It rejects cycles, missing/ambiguous targets, malformed headers and invalid flag combinations. Nonchained version-2 headers are explicitly opaque; version-2 chain decoding is unsupported.

[native_export.py](../../../scripts/research/native_export.py) is now **1.2.0**, with opt-in `--chained`. It combines only contiguous linked groups, rejects gaps rather than including intervening code, preserves the metadata in its plan, and rechecks it against the original bytes. Existing explicit-range selection remains available.

The matching PE contains **12,669 runtime records**, grouped into **8,834 metadata groups**, with **3,835 secondary chained records** and **two opaque nonchained version-2 headers**. These are metadata counts, not recovered function counts or a mechanics-completion percentage.

Three hull helpers were successfully exported with this option: face calculation `0x2bacd0:0x2bae48`, two-edge face cleanup `0x2bd700:0x2bd885`, and planar assignment `0x372db0:0x372f61`. Their groups contain 3, 3 and 5 declared ranges respectively. The resolver also reproduces the earlier manually reviewed mass-setter, shape-replacement, compound-inertia and hull-volume ranges.

## Native seed selection

The reviewed `0x2bb560` builder selects:

1. The first point with maximum squared distance from the input coordinate origin.
2. The first distinct index with maximum squared distance from that point.
3. The remaining point maximizing the squared cross-product magnitude of the initial triangle.

An initial triangle with squared cross-product magnitude below the compiled f32 **approximately 1e-12** takes the small-triangle error path. This quantity is four times squared triangle area; it is not a linear distance threshold. Exactly three noncollinear supplied points create a pair of oppositely oriented triangle faces.

With more points, the builder normalizes the triangle normal, calculates signed distances from its plane, and chooses the largest absolute distance for the fourth seed. The ordinary planar/3D choice uses a separate scale:

```text
rounding = (max(abs(x)) + max(abs(y)) + max(abs(z)))
           * 3.5762786865234375e-7
planar_squared = 36 * rounding^2

three-dimensional seed if fourth_distance^2 > planar_squared
otherwise use the projected planar-boundary path
```

The maxima are over the input points. This scale uses absolute coordinate magnitudes, not bounding-box extents. Changing shape input coordinates can therefore change this decision. Moving a spawned vehicle in world space does not necessarily change those native shape inputs; no universal world-position effect is claimed.

Point assignment subsequently receives:

```text
assignment_squared = max(requested_tolerance^2, rounding^2)
```

The ordinary wrapper stores f32 bits `0x3a83126f` at settings offset `0x70`, approximately **0.0010000000474974513**. The constructor passes that value in **XMM2** to the builder. Selected assembly distinguishes it from integer arguments that the approximate C mistypes or omits. The requested assignment tolerance and initial coplanarity threshold are separate decisions.

## Construction, limits and status handling

The 3D path initializes a tetrahedral face structure, assigns remaining points to faces, repeatedly expands through a horizon, and reassigns candidates after removal/merging. The planar path projects into two coordinates, builds a boundary, then creates opposite face loops in the original point index space. Selected face merging and cleanup helpers were reviewed; this checkpoint does not supply a bit-exact native hull generator.

The selected build has a **256 retained-vertex boundary**, with a recount before one 3D limit exit and a 256 boundary in the planar loop. This is not a claim that every component or saved creation is limited to 256 input points.

The constructor explicitly distinguishes EAX values **0** and **1**. Value 0 goes through an additional approximation-error check before integration; value 1 enters integration directly. Other values enter an error path. Selected builder errors include fewer than three points, too few faces and failure to find a sufficiently large initial triangle. The limit exit and ordinary exits must therefore not be collapsed into one invented boolean result.

Some approximate C output incorrectly presents these routines as returning void. The selected assembly records EAX assignments, comparisons and the ordinary return path that preserves EAX. This is local register-flow evidence, not a complete recovered calling convention.

## Face references and the mass helper

The complete face calculation now resolves an earlier unknown: the vector stored at face offset `0x10` is the **mean of the face's vertices**. The normal is accumulated from triangle fans and is not normalized at this stage. The stored mean is not an area-weighted polygon centroid.

The volume helper averages these stored face means equally to obtain its reference point q. Consequently, q is generally neither the mean of all unique hull vertices nor the volume centre. The signed-volume calculation then determines the volume centre as previously documented.

[polyhedral_mass.py](../../../scripts/research/polyhedral_mass.py) is now **1.1.0** and uses this mean-of-face-means construction for the supplied boundary. Native generated faces, accumulation order and f32 rounding still matter. Subdividing a face may change the intermediate q while preserving the ordinary exact geometric integral.

New [hull_geometry.py](../../../scripts/research/hull_geometry.py) 1.0.0 exposes `hull_tolerances`, `initial_hull_seed`, `face_geometry` and `hull_reference`. It models the selected seed decisions and reference calculations with explicit finite inputs, compiled f32 constants and Python float arithmetic. It does not generate the final native hull or certify shape validity.

## Validation and remaining work

The full research suite passes **267 tests**: twelve new hull-geometry tests, one face-iterator regression, eleven unwind/group/export tests and four build-comparison tests beyond the previous 239. Tests include distinct planar and assignment thresholds, coordinate-magnitude dependence, stable seed ties, face means versus area centroids, equal face weighting, nested and noncontiguous metadata, padding, cycles, malformed/truncated data, ambiguous targets, opt-in export selection and metadata tamper rejection. The comparison tests are described in the build-transition report.

Evidence: [selected native spans, constants and register examples](versions/build-25904830/hull-building-20261022/native-evidence.json), [source-bound unwind audit](versions/build-25904830/hull-building-20261022/unwind-audit.json), and [fresh verification](versions/build-25904830/hull-building-20261022/verification.json). Twenty selected/reused export spans verify **5,886 instructions / 22,933 bytes**. Superseded prefixes remain identified; complete grouped exports are the stronger evidence.

No new GCL export was needed. Reader access remains **1,543 functions / 233,869 checked instructions / 1,329,154 independently summed bytes**. Access counts do not establish semantic completion.

The full audit remains active and incomplete. Remaining vehicle work includes complete native hull/margin/support equivalence, component-zone eligibility and transforms, creation mass reconstruction with separate bodies, and the open powertrain, fluid/thermal, electrical/control, suspension and aircraft/marine chains. Combat and AI remain parked under the user's vehicle-building priority.
