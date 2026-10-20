# Tools, reproduction, and maintenance

Source: `scripts/research/`. Python 3.12+ standard library; Ghidra exports additionally use an existing isolated Ghidra/JDK. Outputs refuse overwrites and game files remain read-only. Never create output directories inside the active installation.

| Tool | Responsibility and limits |
| --- | --- |
| `baseline.py` 1.1.0 | Resource checks; one worker/BelowNormal; full inventory, selective copies, two-pass source hashes, actual-format identification; not an atomic snapshot |
| `gcl_index.py` 1.3.0 | Bounded length prefixes, operands, code/allocation fields, zero-slot checks; local SQLite function/reference search; not a full GCL parser |
| `catalog.py` 1.0.0 | All parseable data-directory JSON; original definitions, JSON Pointers, hashes, FTS; no guessed defaults |
| `system_map.py` | 15 topic leads and common question queues; keyword counts are not understanding |
| `export_plan.py` | Verify database/input hashes, unique signature, and code hash before planning selected exports |
| `ExportResearch.java` | Local Ghidra disassembly, pointer-slot annotations, approximate pseudocode, machine facts/raw p-code; no original-file patches or guessed structure types |
| `run_export.py` | Reuse archived launcher arguments; explicit runtime/project paths; 2 GiB heap, one worker, BelowNormal; disable whole-file autoanalysis; verify actual products |
| `check_exports.py` | Compare every exported instruction with original bytes/range; does not prove pseudocode semantics |
| `check_static_evidence.py` | Reparse 18 recorded functions and individually verify format/value/raw bytes of 13 constants |
| `check_historical.py` | Historical range hashes and current full-signature relocation; changed hashes do not prove changed mechanics |
| `compare_builds.py` | Compare installation inventories, definition fields, and function-record hashes; distinguish omitted/null/boolean/numeric |
| `test_research.py` | Original synthetic fixtures, all truncation points, bad slots/metadata, changing sources, format/suffix conflicts, omissions/type differences |
| `trace_code.py` | Source/record/assembly byte audit, conservative local operand dependencies, actual embedded reads and separate address previews; not a complete call graph |
| `code_reader.py` | SQLite full-text reader over selected C/assembly/evidence; source-bound build with incomplete/overwrite rejection |
| `check_offline_evidence.py` | Independent matching-source checks of selected published records, constants, strings, and call bytes; not a proof of prose semantics |
| `test_code_trace.py` | Synthetic dataflow boundaries, tampering/failure controls, literal distinctions, reader and evidence-checker tests |
| `static_models.py`, `test_static_models.py` | Selected explanatory arithmetic and conservation/order/boundary counterexamples; not a game simulator or runtime acceptance |

## New baseline

```powershell
python scripts/research/baseline.py "$env:ANYMAKER_INSTALL" "$r" --steam-manifest "<SteamLibrary>/steamapps/appmanifest_4435340.acf"
python scripts/research/gcl_index.py build "$r/snapshot/bin/game.gcl" "$r/gcl"
python scripts/research/catalog.py build "$r/snapshot" "$r/catalog"
```

Before initial checks, retain at least snapshot disk requirements plus 20 GiB and 4 GiB available RAM. Approximately 15–16 GiB RAM was available during current baseline collection. Serialize large operations. Check resources again before Ghidra and pause analysis when necessary; authorization does not permit consuming gameplay resources indiscriminately.

## Selected function exports

`$runtime` must contain `ghidra/ghidra_<version>/` and `jdk/<jdk>/bin/java.exe`. Reuse a verified runtime; do not automatically run download scripts. `$project` must be a nonexistent plain temporary path, with no path component beginning with a dot or containing braces; do not place it under `.codex`. `$out` must be new.

```powershell
python scripts/research/run_export.py "$r/snapshot/bin/game.gcl" "$r/gcl/index.sqlite" "$out" "$runtime" "$project" 'hatch_manager._test_node_match'
```

The runner binds the index to source SHA and records Java version, Ghidra properties/script hashes, and resources. Original slots remain unrelocated; readable labels do not mean function-pointer types are recovered. GCL code_size includes constants/padding; do not linearly disassemble every byte and count it as valid instructions.

This checkpoint exported 18 functions and checked 6,599 instructions. The new runner also passed an actual smoke test on one previously exported node-match function, without increasing the unique-function count. Full output and Ghidra projects remain local.

## Offline reader and evidence checks

The [2026-10-19 continuation](OFFLINE-20261019.md) exported 29 additional distinct functions in two new batches. It checked 6,813 instructions/39,264 bytes and created a searchable reader with 297 slot-derived call dependencies and 270 unresolved calls. A dependency is not a proven virtual callee. Use a matching source/index and new export/output paths; `$e1` and `$e2` identify the two completed `run_export.py` output directories.

```powershell
python scripts/research/trace_code.py "$r/snapshot/bin/game.gcl" "$r/gcl/index.sqlite" "$e1" "$r/trace.json"
python scripts/research/code_reader.py build "$r/snapshot/bin/game.gcl" "$r/gcl/index.sqlite" "$r/reader" "$e1" "$e2"
python scripts/research/code_reader.py search "$r/reader/code.sqlite" 'consume_factor OR liquid_pump'
python scripts/research/code_reader.py show "$r/reader/code.sqlite" 56368934 --section constants
python scripts/research/code_reader.py show "$r/reader/code.sqlite" 56368934 --section calls
python scripts/research/code_reader.py show "$r/reader/code.sqlite" 56368934 --section c
python scripts/research/check_offline_evidence.py "$r/snapshot/bin/game.gcl" doc/knowledge/research/versions/build-25904830/offline-20261019/evidence.json --output "$r/evidence-check.json"
python -m unittest discover -s scripts/research -p 'test_*.py' -v
```

The reader and checks use Python standard-library modules, including SQLite FTS5 in the verified runtime. Ghidra/JDK are required only to produce new exports. No game launch, attachment, or in-game test is required. Full exports/databases contain proprietary code and stay outside Git. This continuation passed 42 tests and checked 29 selected function identities, 17 constants, four strings, and 21 call-instruction examples. These counts supplement the historical validation paragraph below.

The [systems follow-up](OFFLINE-SYSTEMS-20261019.md) adds two further batches: 36 functions, 7,042 instructions/38,015 bytes. Build a new reader from all four distinct export directories to obtain 65 functions/13,855 instructions. `python scripts/research/static_models.py` prints illustrative electrical and liquid calculations without game execution. All 51 research-tool tests passed; the new selected evidence checks 44 identities, 13 constants, four strings and 20 call examples. Use `versions/build-25904830/offline-systems-20261019/evidence.json` as the checker input for this follow-up. Models have an explicitly narrower scope than the native network solver.

## Updates and historical records

```powershell
python scripts/research/check_historical.py "$r/snapshot/bin/game.gcl" "$r/gcl/index.sqlite" "<directory-of-selected-evidence-json>" "$r/historical-check.json"
python scripts/research/compare_builds.py "<old>/inventory.json" "<new>/inventory.json" "<new>/diff.json" --old-definitions "<old>/catalog/definitions.sqlite" --new-definitions "<new>/catalog/definitions.sqlite" --old-functions "<old>/gcl/index.sqlite" --new-functions "<new>/gcl/index.sqlite"
```

`check_historical.py` accepts the current six evidence groups' camelCase `functions[]` fields. Other schemas need explicit adapters; do not claim automatic compatibility with all archives. Definition differences align by source+ID and initially report nested changes at top-level fields; this is not a complete field-level migration engine.

Continue reusing old `anymaker.py`, `structural_mounts.py`, native generators, Workshop index, and Ghidra helpers through the [existing tool guide](../TOOLS.md). This checkpoint did not regenerate game assets or change browser application/export behavior.

Validation: 15 new-tool tests passed; 26 archived tests ran, 25 passed, one skipped for missing optional corpus. No frontend npm/browser checks or new game runtime experiments were performed.
