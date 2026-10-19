# Tools, reproduction, and maintenance

Source: `scripts/research/`. Python 3.12+ standard library; Ghidra exports additionally use an existing isolated Ghidra/JDK. Outputs refuse overwrites and game files remain read-only. Never create output directories inside the active installation.

| Tool | Responsibility and limits |
| --- | --- |
| `baseline.py` 1.1.0 | Resource checks; one worker/BelowNormal; full inventory, selective copies, two-pass source hashes, actual-format identification; not an atomic snapshot |
| `gcl_index.py` 1.3.0 | Bounded length prefixes, operands, code/allocation fields, zero-slot checks; local SQLite function/reference search; not a full GCL parser |
| `catalog.py` 1.0.0 | All parseable data-directory JSON; original definitions, JSON Pointers, hashes, FTS; no guessed defaults |
| `system_map.py` | 15 topic leads and common question queues; keyword counts are not understanding |
| `export_plan.py` | Verify database/input hashes, unique signature, and code hash before planning selected exports |
| `ExportResearch.java` | Local Ghidra disassembly, pointer-slot annotations, approximate pseudocode; no original-file patches or guessed structure types |
| `run_export.py` | Reuse archived launcher arguments; explicit runtime/project paths; 2 GiB heap, one worker, BelowNormal; disable whole-file autoanalysis; verify actual products |
| `check_exports.py` | Compare every exported instruction with original bytes/range; does not prove pseudocode semantics |
| `check_static_evidence.py` | Reparse 18 recorded functions and individually verify format/value/raw bytes of 13 constants |
| `check_historical.py` | Historical range hashes and current full-signature relocation; changed hashes do not prove changed mechanics |
| `compare_builds.py` | Compare installation inventories, definition fields, and function-record hashes; distinguish omitted/null/boolean/numeric |
| `test_research.py` | Original synthetic fixtures, all truncation points, bad slots/metadata, changing sources, format/suffix conflicts, omissions/type differences |

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

## Updates and historical records

```powershell
python scripts/research/check_historical.py "$r/snapshot/bin/game.gcl" "$r/gcl/index.sqlite" "<directory-of-selected-evidence-json>" "$r/historical-check.json"
python scripts/research/compare_builds.py "<old>/inventory.json" "<new>/inventory.json" "<new>/diff.json" --old-definitions "<old>/catalog/definitions.sqlite" --new-definitions "<new>/catalog/definitions.sqlite" --old-functions "<old>/gcl/index.sqlite" --new-functions "<new>/gcl/index.sqlite"
```

`check_historical.py` accepts the current six evidence groups' camelCase `functions[]` fields. Other schemas need explicit adapters; do not claim automatic compatibility with all archives. Definition differences align by source+ID and initially report nested changes at top-level fields; this is not a complete field-level migration engine.

Continue reusing old `anymaker.py`, `structural_mounts.py`, native generators, Workshop index, and Ghidra helpers through the [existing tool guide](../TOOLS.md). This checkpoint did not regenerate game assets or change browser application/export behavior.

Validation: 15 new-tool tests passed; 26 archived tests ran, 25 passed, one skipped for missing optional corpus. No frontend npm/browser checks or new game runtime experiments were performed.
