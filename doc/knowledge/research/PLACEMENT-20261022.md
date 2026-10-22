# Component placement checks and differential clarification

Build 26113663, offline checkpoint on 2026-10-22. GCL SHA-256: `a3fd2df2fd62e38b629f6a0df824269a34d77d57caf66d596362d7e5e53c3b22`. This preserves the unpublished work following [functional mating and drivetrain variants](MATING-DRIVE-20261022.md). The game was not executed, and active creations were not changed.

## Review and evidence status

Three export batches add **17 methods**. Ten approximate-C bodies have been reviewed fully, three partially and four await semantic review. In particular, the attachment helper's plate branch and the complete server/editor placement callers remain unfinished. Available exports must not be mistaken for completed understanding.

The combined current-build reader now contains **196 methods, 44,180 byte-checked instructions and 257,171 checked instruction bytes**. Its 1,794 unresolved indirect calls remain explicit. Counts describe the reader, not a completion percentage.

- [Evidence](versions/build-26113663/placement-20261022/evidence.json) retains method identities, code/export hashes, individual review states, typed constants, the definition layout and differential source identities.
- [Verification](versions/build-26113663/placement-20261022/verification.json) records the complete reader audit and limits.
- The latest executable research-tool suite remains **327 passing tests** from the preceding checkpoint. No executable tools changed here, so those tests were not rerun. Documentation and publication checks are separate.

## Ordinary placement requires both support and clearance

The fully reviewed `vehicle_util.can_add_component<server_scene>` first tests attachment. Failed attachment returns false immediately when no blocker collector is supplied. With a collector, it continues to the overlap check so blockers can still be reported, while retaining the failed result. Overlap also makes the result false. Diagnostic collection therefore does not waive structural support.

The multibody utility is narrower: this helper returns the inverse of an overlap test and passes the other component definition's assigned ID as an exclusion. It does not itself call the attachment helper. The complete caller chain still needs review before describing the whole multibody placement policy.

The reflected definition field `m_assigned_id` is at byte offset **656 / 0x290**. This exclusion compares component-definition IDs, rather than individual component instance IDs. The ordinary no-diagnostic overlap wrapper passes integer zero. Which assigned IDs occur in each relevant lifecycle remains a separate question.

## Overlap has several geometric branches

The fully reviewed server overlap template gathers octree candidates using rotated cached definition bounds plus extension, expanded by one building voxel. It then checks each candidate collision zone. This broadphase box is distinct from the narrowphase zone tests.

| Existing object | Reviewed narrowphase path |
| --- | --- |
| Unremoved structural node | Inclusive integer point-in-zone test for a base-grid candidate; an AABB/OBB test for another mounting grid |
| Unremoved edge with valid endpoints | Dedicated oriented-box-versus-edge helper; the complete callee contract is pending |
| Component on the same mounting grid | Separate local zone-bounds helper, exported but not yet semantically reviewed |
| Component on a different mounting grid | Existing-zone and candidate-zone oriented boxes tested for overlap |

In the physical box construction, candidate bounds are inset by **0.01 voxel**, or **0.0008 m** on the native 8 cm lattice. The opposing existing-component box uses full half-voxel boundaries in the reviewed different-grid branch. This asymmetry matters near contact; a generic touching-box test is not automatically equivalent.

The reviewed routine has node, edge and component loops, with no plate-polygon loop in its full body. That does not establish that plates can never block placement elsewhere. A supplied blocker collector allows collection to continue; without it, a detected blocker can return immediately. Collector deduplication and every native intersection helper remain outside this checkpoint.

## Structural surfaces and functional ports remain separate

The reviewed portion of the current attachment helper accepts component-face support when mounting-grid origins/directions match exactly, face normals oppose, and transformed surface bounds overlap after a one-voxel normal shift. This branch does not apply functional interface-type/gender checks. Those stricter checks remain in the separately reviewed mating predicates.

The helper also has structural-edge and plate paths. Its plate path is only partly read, so this checkpoint does not generalize the component-face rule into a complete attachment validator. The prior two-plug battery geometry example remains a local analytical mating witness, without full placement or operating acceptance.

## Differential intent is now supported by shipped descriptions

Both shipped differential definitions describe a splitter whose lateral outputs rotate together. Their mechanical input disconnects those outputs; variant B additionally passes the input to its rear output at **1:1**. This agrees with the earlier traced disconnection of internal links 0 and 1 while the optional rear link remains connected.

The reflected internal field is named `m_is_locked`, but that name should not be interpreted as a conventional differential-lock command. The earlier report left intended behavior open; the shipped descriptions now resolve that selected question. Complete loaded behavior and external driveline paths remain separate runtime questions.

The freshly reviewed constructor initializes this control state to false and both ratio factors to 1. The reviewed tooltip reads shaft speeds and the factor ratio; the shipped definitions have empty data-descriptor arrays. These observations do not create a new controller-readable lock signal.

The description for variant A gives positive activation above 0.75 and reconnection below 0.25. The previously reviewed boolean threshold helper additionally responds to sufficiently negative inputs and uses strict release boundaries. Keep the actual signed threshold trace when designing control logic rather than extending the abbreviated description into an exact all-input specification.

## Resume here

Finish the attachment plate branch and reread both truncated server-event bodies. Review the editor placement caller, normal vehicle wrappers and local zone-overlap helper already exported. Then trace remaining placement/default/occupancy and graph-grouping dependencies before certifying any complete battery-port arrangement. Continue steering/brakes, geometry and structural reconstruction, then flight and marine systems. Vehicle-making systems remain the priority; combat, projectiles, explosions and AI are parked. The full audit remains incomplete.
