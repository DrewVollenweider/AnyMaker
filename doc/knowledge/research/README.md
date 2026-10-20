# Whole-game research

Latest continuation: [electrical ordering, liquid accounting, and script loop limits](OFFLINE-SYSTEMS-20261019.md), following the [offline code reader checkpoint](OFFLINE-20261019.md). The reader now covers 65 selected functions; the new report traces deferred electrical debit, order-sensitive consumer acceptance, native liquid units/head/conservation, and a 256-iteration per-loop cap. The user requested research without required in-game testing; continue offline and label remaining unknowns explicitly. Historical runtime protocols remain reference plans, not a gate for this assignment.

2026-10-18 (America/New_York). This is the first whole-game baseline checkpoint of an ongoing research system, not a claim to understand the entire game. Start with [coverage](COVERAGE.md), [versions](VERSIONS.md), and [handoff](HANDOFF.md), then search through the [system index](versions/build-25904830/system-map.json). The existing [engineering findings](../CURRENT-FACTS.md) and acceptance records remain applicable within their own version and evidence boundaries.

This checkpoint completed a two-pass SHA-256 inventory of the entire installation, an isolated snapshot, review of existing research, definition indexes, GCL function-record/reference indexes, historical-address relocation checks, and an initial detailed static investigation of the Opening/Hatch sealing path. The game was never launched, attached to, or controlled. Installation files and active saves were untouched. Runtime experiments have not been performed.

## Answering questions

1. Confirm the Steam build, input SHA-256, and analysis-tool SHA-256. Never reuse old addresses without checking.
2. Query original fields in the definition database. Preserve omitted fields as omitted; do not invent defaults.
3. Find functions by full signature in the GCL database, follow symbol references to callers, and inspect original code and disassembly. A symbol reference is not an executed call.
4. Inspect representative native files, distinguishing loaded state, static connections, and historical runtime acceptance.
5. State findings and limits using the [evidence categories](#evidence-categories). Continue investigating ambiguities offline; historical [experiment protocols](EXPERIMENTS.md) remain optional future plans, not required user testing.
6. Record reproducible commands, input hashes, results, counterexamples, and next steps. Keep full decompilations, binaries, ROM copies, and personal saves local.

## Search and tools

Python 3.12+. Indexing and basic parsing use only the standard library. Run commands from the repository root; `$r` points to a separate research directory outside the repository. Output directories must be new; existing outputs are not overwritten.

```powershell
python scripts/research/gcl_index.py build "$r/snapshot/bin/game.gcl" "$r/gcl"
python scripts/research/catalog.py build "$r/snapshot" "$r/catalog"
python scripts/research/gcl_index.py query "$r/gcl/index.sqlite" hatch_manager
python scripts/research/gcl_index.py query "$r/gcl/index.sqlite" hatch_manager.tick --callers
python scripts/research/catalog.py query "$r/catalog/definitions.sqlite" 'microcontroller OR battery'
python scripts/research/system_map.py "$r/gcl/index.sqlite" "$r/catalog/definitions.sqlite" "$r/system-map.json"
python -m unittest discover -s scripts/research -p 'test_*.py' -v
```

`gcl/index.sqlite` stores full local signatures, code ranges/hashes, relocation operands, global/source-file tables, and reference-resolution status. `catalog/definitions.sqlite` stores definition JSON, JSON Pointers, source/normalized-definition hashes, and full-text search. Retrieve original records through `functions.record` and `definitions.json`; the lightweight component index does not republish complete definitions.

[Tools and maintenance](TOOLS.md) covers baseline collection, Ghidra, historical evidence checks, and update comparison. Exact paths on the current machine are in workspace `RESEARCH-HANDOFF.md`, not the public repository.

## Evidence categories

| Category | Meaning |
| --- | --- |
| `shipped` | Explicitly stated in shipped documentation/definitions; not automatically implementation behavior |
| `static` | Established by checking matching-version implementation, references, or original bytes |
| `runtime` | Actual game observation; identify operator, initial state, controls, and observation scope |
| `inference` | Supported deduction; state the reasoning and possible counterexamples |
| `hypothesis` | Explanation awaiting a test; never report it as a result |
| `unknown` | Insufficient evidence; record the next investigation |

Record confidence separately from evidence category. Function counts, keyword hits, successful decompilation, and passing static checks do not count as system runtime acceptance.

Behavioral findings are in [Opening/Hatch](SEALING.md) and the [offline electrical, pump, and microcontroller investigation](OFFLINE-20261019.md). There is currently no whole-game units table, complete type recovery, complete GCL container grammar, general runtime telemetry, or universal decompiler.
