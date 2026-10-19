# Documentation index

Requirements, architecture, and formats come first; implementation order is in [TODO](../TODO.md). Scope: desktop Web + Three.js + GitHub Pages; touch/mobile deferred.

| Document | Contents |
| --- | --- |
| [01 System architecture](01_SYSTEM_ARCHITECTURE.md) | Responsibilities, target model, dependencies, frontend boundaries |
| [02 Anymaker architecture](02_ANYMAKER_ARCHITECTURE.md) | ROM, definitions, native structures/grids, research limits |
| [03 XML and native formats](03_XML_AND_NATIVE_FORMAT.md) | JSON/XML/native mappings |
| [04 Component/Mesh splitting](04_COMPONENT_MESH_SPLIT.md) | Per-component details/bindings, shared assets, lazy loading |
| [05 Building operations](05_BUILD_OPERATIONS.md) | Split/copy/move/merge/mirror, boundaries, acceptance |
| [06 Local decompilation](06_REVERSE_ENGINEERING.md) | Read-only inputs, Ghidra workflow, evidence |
| [07 3D model parsing](07_MODEL_IMPORT.md) | GLB/OBJ/STL, shell simplification/symmetry, lattice/footprint, limits |
| [08 Editing/render quality](08_EDITOR_PERFORMANCE.md) | Incremental updates, downsampling, settings/persistence, limits |
| [09 Interface colors](09_INTERFACE_COLORS.md) | Real local colors, paint isolation, cable-end occlusion, regressions |
| [10 Mechanical mates](10_MECHANICAL_MATES.md) | Hinges/pins/rails/latches/towing, multibody references |
| [11 Hydraulics](11_HYDRAULIC_CONNECTIONS.md) | Steering circuits, three cylinder sizes, reciprocal references, code evidence |
| [12 Inclined placement](12_INCLINED_PLACEMENT.md) | Dashboard mounting frame, local lattice/90° rotations, export |
| [13 Tracks](13_TRACKS.md) | Networks, 18 wheels, three Meshes, closed paths, static/native round trips |
| [14 Belts](14_BELTS.md) | Four wheel classes, reverse idlers, continuous surfaces, real texture/six-wheel sample |
| [15 Plates](15_PLATES.md) | Support offsets, unordered selection, closed-boundary validation, missing thickness/frames |
| [16 Native islands](16_NATIVE_ISLANDS.md) | Split crash, traversal, general guards, regressions/limits |
| [17 Drive archives](17_GOOGLE_DRIVE_ARCHIVES.md) | Local overwrite, OAuth setup, upload/update/list/lazy download, permissions |
| [Resource research](RESOURCE_ANALYSIS.md) | Scans, Mesh support, external-workbench methods |
| [Asset audit](evidence/asset-audit.json) | Counts, EXE/definition/Mesh SHA-256 hashes, parse successes/failures |
| [Native-grid evidence](evidence/native-grid-transform.json) | Functions/constants, mounting offsets, four door-handle coordinates |

Distinguish verified facts, implementation, design goals, and unverified items. Checkboxes are not whole-product acceptance; game loading/1:1 visuals remain incomplete.

## Maintenance

- Use English for documentation, research, development notes, comments, and commits, as explicitly requested by the user. The former Chinese-documentation instruction was incorrect. Run `python scripts/check-documentation.py`; see the [correction record](LANGUAGE-CORRECTION.md).
- English documentation belongs in `doc/`; root retains entry points/TODO.
- Cite source/scripts/tests; never paste binary blocks into docs/code.
- Commit selected auditable summaries; ignore local resources/experiments/Ghidra projects.
- Schema edits require format/migration/test updates.
- Split special assembly by component, not an ever-growing global factory.

## 2026-10-11 creation/testing records

- [18 Vehicle delivery standard](18_BUILD_ASSURANCE.md)
- [19 Experiments/evidence limits](19_EXPERIMENTS_2026-10-11.md)
- [Native sample inventory](evidence/2026-10-11/native-reference-inventory.json)

## Accumulated engineering knowledge, October 11–16

[Engineering knowledge hub](knowledge/README.md): bench engines, compact inline-four CPE1Running, giant engine/test vehicles, findings/failures/corrections/tools/selected native examples. Read current findings before history. Independent-tool game acceptance does not establish general browser-editor export compatibility.
