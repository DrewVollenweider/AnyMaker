# Anymaker resource research

This is the initial historical asset-research record. Later Ghidra/code findings are in [reverse engineering](06_REVERSE_ENGINEERING.md) and the knowledge hub; do not read its original unperformed-analysis status as current.

## Reproducible evidence

Source: local Anymaker/rom. Tools `scripts/extract-catalog.mjs`, `scripts/audit-assets.mjs`; [asset audit](evidence/asset-audit.json). Installation/external Stormworks workbench were read-only.

- ROM: 10713 files, 3333 Mesh, 115 txtr, 204 data, 204 meta.
- Components: 598 definitions/22 categories, 794 unique static/dynamic resources, all references exist.
- Parser supports 3230 Meshes, 793 component references; individual failures recorded.
- EXE/definition SHA-256 in report; game-UI version not checked at this initial stage.
- starter_vehicle.data: JSON, one vehicle/112 nodes/181 beams/27 plates/two grids/39 components.
- starter_vehicle.meta: JSON transforms/bounds, loading semantics unverified.

Paths/hashes/parse results establish format checks, not matching rendering/physics.

## Supported Mesh v5

Header: mesh magic, uint32 version, part count. Each part: length/name, layout header, metadata, six float64 bounds, vertex-buffer length/data, index-buffer length/data. Supported ending: two zero uint32s.

| First eight uint32 layout values | Stride | Reads |
| --- | --- | --- |
| 3,1,5,2,0,0,0,0 | 16 | Position + four packed bytes |
| 3,1,5,2,3,4,0,0 | 28 | Position + four packed bytes + normal |
| 3,1,5,2,2,3,3,4 | 36 | Position + four packed bytes + UV + normal |

Check lengths/indexes/nonfinite floats/trailing data/truncation. Preserve unknown metadata; packed bytes are not automatically confirmed sRGB. Multiple parts differ from dynamic components; see [operations](05_BUILD_OPERATIONS.md).

## External workbench methods

Read external README/AGENTS/docs/02_PIPELINE.md/config/analysis_config.json in `D:/00Data00/Stormworks/analysis`. Static scans cover PE/strings/resource references/structure indexes. Headless Ghidra exports functions/string xrefs/call graphs/selected pseudocode. Config points to `G:/ghidra_12.0.3_PUBLIC`; default no-analysis imports/runs scripts only, not completed decompilation.

Original Anymaker plan:

1. Separate ignored `artifacts/` Ghidra project targeting Anymaker game.exe; never modify external Stormworks project.
2. Search mesh/txtr/vehicle/grid/save/load for reader/serializer candidates.
3. Targeted analysis with EXE hash/tool versions/addresses/call paths/pseudocode provenance.
4. Cross-check minimal ROM samples, synthetic fixtures, controlled saves/loads.
5. Commit concise findings/selected hashes to doc/evidence, not full outputs/game data.

At this initial stage no Anymaker Ghidra decompilation had run and no native XML reader evidence existed. Parser research came from static samples, not recovered game source.
