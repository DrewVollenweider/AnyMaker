# Tools, archive and reuse

The archive preserves the project's reusable utilities and historical creation scripts. All previous explanations are included; CURRENT-FACTS.md resolves superseded conclusions. Existing game resources are already published under the repository's public/data and public/assets; this upload does not duplicate a full ROM or executable.

## General read-only tools

- [anymaker.py](archive/toolset/anymaker.py): inspect, audit, systems review, catalog/interface lookup, semantic draft operations, JSON diff, schematics, clone and stable snapshots. Python3.10+ standard library.
- [structural_mounts.py](archive/toolset/structural_mounts.py): conservative base-grid mounting islands and contact audit. Supports cardinal component rotations, beam endpoints/axis-aligned spans and rectangular panels.
- [research_install.py](archive/toolset/research_install.py), [read_binaries.py](archive/toolset/read_binaries.py), [inspect_gcl.py](archive/toolset/inspect_gcl.py), [extract_gcl_samples.py](archive/toolset/extract_gcl_samples.py): local read-only research utilities. Some depend on historical local baselines/full catalogs not included here; consult their source and the archived methodology before use.
- [observe_files.py](archive/toolset/observe_files.py): bounded file observer, not continuous game telemetry.
- [workshop_index.py](archive/toolset/workshop_index.py): copies and indexes an available Workshop corpus; the downloaded community corpus is not redistributed. Its optional corpus test is expected to skip if absent.
- Ghidra Java/headless/setup helpers and [analysis notes](archive/toolset/DECOMPILATION.md) are archived as source, without downloaded executables/databases.

From the repository root:

```sh
python doc/knowledge/archive/toolset/anymaker.py inspect doc/knowledge/archive/toolset/output/compact-petrol-engine-01-complete/running-result/CPE1Running.data
python doc/knowledge/archive/toolset/anymaker.py systems doc/knowledge/archive/toolset/output/shift-repair/20261016-100456/Giant_Engine_Test_Vehicle_01.data --markdown
python -m unittest discover -s doc/knowledge/archive/toolset/tests -v
```

Catalog loading uses ANYMAKER_CATALOG when supplied, then a local reference catalog, then the repository's existing public/data/definitions files. The shipped selected-definition fixture is sufficient for archived creations and offline unit tests; it is not a complete catalog. To test the archive standalone, set **ANYMAKER_CATALOG** to `doc/knowledge/archive/toolset/fixtures/component-definitions.json`. The fixture is from the Oct14 version; published repository catalog provenance may differ.

Native creation builders use Pillow for preview generation and some Windows fonts. They are revision-specific scripts, not a general build API. Local paths in copied Python sources are configurable through **ANYMAKER_CREATIONS** and **ANYMAKER_INSTALL** using archive_paths.py. Historical PowerShell examples use a generic PLAYER profile and require adaptation. No original source files were changed by archiving.

The `catalog --items` command still requires a local inventory reference catalog. Installation-refresh comparisons also require their original baseline catalogs. These large extracted caches are deliberately not included; the notes preserve their findings and hashes. Do not claim every historical script can run without its documented inputs, local installation, fonts or tools.

## Creation history

- [build_pedestal_engine.py](archive/toolset/build_pedestal_engine.py) and [compact_engine.py](archive/toolset/compact_engine.py): accepted small-engine layout generation, zone occupancy, cradle, line routing and control arrangement. Accepted native outputs and capture/verification scripts are preserved with their result folders.
- [fill_giant_engine.py](archive/toolset/fill_giant_engine.py) and [upgrade_giant_starter.py](archive/toolset/upgrade_giant_starter.py): refill and starter revisions.
- [build_giant_test_vehicle.py](archive/toolset/build_giant_test_vehicle.py): initial vehicle generation, before the discovered mounting/shift faults; **historical failed revision**.
- [repair_giant_vehicle_mounts.py](archive/toolset/repair_giant_vehicle_mounts.py): mounting correction.
- [repair_shift_and_add_indicator.py](archive/toolset/repair_shift_and_add_indicator.py), [correct_shift_mapping.py](archive/toolset/correct_shift_mapping.py): historical diagnostics/partial fixes; final positive-only selectors in accepted native output supersede these intermediate assumptions.
- [finish_vehicle_diagnostics.py](archive/toolset/finish_vehicle_diagnostics.py): successful-trace checks, removal of temporary ports, clean display script and neutral/parked defaults.

Use [manifest](MANIFEST.json) for exact staged files and hashes. Modified portable/sanitized copies have different upload hashes from original source hashes. Do not interpret an archive hash difference as game-state mutation.

## Preserved methods and limits

[Tool manual](archive/toolset/README.md), [design checklist](archive/toolset/VEHICLE-DESIGN.md), [validation limits](archive/toolset/VALIDATION.md), [Workshop research](archive/toolset/WORKSHOP.md), [all earlier tool index](archive/TOOLSET.md).

The original local path examples and output links are historical. Unpublished evidence links are rendered as plain labels marked “local evidence not uploaded” rather than pretending the raw source exists on GitHub. Their substantive conclusions are summarized in the current notes. Runtime code and the browser editor are unchanged by this documentation/tool archive.
