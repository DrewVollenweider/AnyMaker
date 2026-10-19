# Native structural islands and export guards

## Verified failure path

The 2026-09-28 `981.1.data` sample has two physical vehicles. Main vehicle: 96 nodes, 184 beams, 87 plates. Nodes 99/100 are referenced by plates without any connected beam. IDs identify evidence only; repair code does not special-case IDs/filenames.

Crash report `crash-2026-09-28-153708-32024.json`, UTC `2026-09-28T15:37:09Z`, points to `server_scene.vehicle._split_islands + 1871`. Matching local GCL identifies file offset `0x31c350d`, instruction `mov rax, [rax]`, `rax = 0`. Earlier code calls `front()` on node beam list at `+0x60`, then reads the first beam's island index at `+0x118`, without an empty-list branch. Beamless nodes satisfy this null-dereference condition.

[Audit](evidence/native-islands.json) records fingerprints, ten functions, relocation names, key instructions. Read-only check without launching game/modifying saves:

```powershell
node scripts/check-native-island-evidence.mjs <Anymaker/bin/game.gcl>
```

## Game traversal and implementation

Statically checked `_flood_island`, four `_flood_islands` overloads, `_rebuild_islands`, `_reset_island_indices`, `_split_islands`, `find_edge`, plate-adjacency rebuild records:

| Object | Game traversal | Editor treatment |
| --- | --- | --- |
| Beam | Other beams at both endpoint nodes; registered plates/components | Connect by identical node IDs, not coordinate proximity |
| Plate | Actual boundary-beam references and registered components | Find beams by unordered adjacent-node ID pairs; missing boundaries do not connect arbitrary beams sharing corner nodes |
| Component | Registered beams/plates/components | Existing static contact approximation from mounts/dedicated interfaces |
| Node | First connected beam determines island on split | Require at least one beam per plate corner and consistent corner/plate membership |

Signal networks/physical joints do not directly form rigid-island edges. Multiple islands can be valid; do not weld everything merely to reduce counts. Beams need not touch components at every endpoint; independent structural shells can be valid.

`src/editor/structural-topology.js` handles IDs, coordinates, references, degenerate/duplicate beams, plate geometry, actual boundaries. `src/editor/subgrid-connectivity.js` checks cross-island plate-node references after traversal. Missing some boundary beams yields warnings; beamless corners/cross-island references are safety errors preventing partition application. Node markers/localized diagnostics locate problems.

## General export rules

Before physical-body partitioning, `toNativePairFromEditor` normalizes a temporary structure copy, then runs the same island preflight as the UI:

1. Existing collinear-orphan cleanup removes only redundant intermediate boundary nodes with no beam references.
2. For remaining unsupported plate corners, add adjacent boundary beams, deduplicated by unordered node pairs. Preserve existing beam colors; new beams use front plate color, falling back to back.
3. Do not blindly add all triangulation edges for nodes already supported by beams; cross-island references still need explicit correction.
4. Reject duplicate IDs, degenerate beams, invalid plates, cross-island references, dangling links. After splitting, revalidate all vehicle structure references and a connected beam for every exported node.
5. Normalize only the export copy, never implicitly rewrite current project, history, or originals.

`tests/native-export.test.js` uses independent synthetic fixtures for beamless corners, shared-edge deduplication, renumbering/reordering, reverse winding, all missing beams, cross-island rejection, multibody output, round-trip idempotence. `tests/browser/editor.spec.js` covers localized errors, node location, download/reimport, unchanged project on failure. `tests/unit.test.js` explicitly includes these tests.

## Validation limits

In-memory import/export/reimport of the original failure sample produces 189 main-vehicle beams with unchanged nodes/plates; second vehicle remains nine nodes, 12 beams, four plates. No dangling references/beamless nodes remain, physical-mate vehicle/component references are valid, original `.data/.meta` SHA-256 is unchanged. Results: zero errors, three missing-boundary warnings, two valid structural islands. Zero errors is not zero diagnostics.

Actual 2026-09-28 checks: 231 unit tests and build passed in `npm run check`; `npm run test:browser:editor` passed 94 editor workflows. After an overlapping-ID location fix, three related browser cases passed again. Evidence matched ten GCL records/four instructions. Build still warns about chunks over 500 kB; bundling policy was unchanged.

Evidence applies only to the recorded GCL fingerprint. Complete component-contact tolerances, runtime damage/dirty flags, and splitting schedule are not reproduced. Static contact approximation may differ from game behavior. No exported-file game loading, dynamic physics, or game-compatibility acceptance was performed.
