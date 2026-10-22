# Tools, reproduction, and maintenance

Current vehicle checkpoint: [build 26113663 vehicle systems](VEHICLE-UPDATE-20261022.md). Fresh reflection and selected exports show shared wheel rotation-lock gates and roller inheritance; engine/gearbox update methods pass scoped archived-instruction/direct-read/reference comparisons. The comparison covers 1,543 archived entries; 1,464 local matches do not prove complete semantic transfer. Current reader: 12 methods / 8,099 checked instructions / 51,029 bytes. All 277 research-tool tests pass. Full audit active and incomplete; vehicle systems first, combat/projectiles/explosions/AI parked. Earlier checkpoints below retain their own archived-build limits. New [compare_reviewed.py](../../../scripts/research/compare_reviewed.py) compares selected reviewed spans without transferring unclassified data or dependency semantics.

Installed build is now [26113663](BUILD-TRANSITION-20261022.md). The hull findings below target archived 25904830; new-build mechanics transfer is unproven. New [hull_geometry.py](../../../scripts/research/hull_geometry.py) 1.0.0 models selected seed/tolerance and face-reference arithmetic. [native_unwind.py](../../../scripts/research/native_unwind.py) 1.0.0 resolves declared version-1 unwind links; [native_export.py](../../../scripts/research/native_export.py) 1.2.0 adds opt-in --chained selection and metadata rechecking. [polyhedral_mass.py](../../../scripts/research/polyhedral_mass.py) 1.1.0 uses the native mean-of-face-means reference. Build comparison now uses source plus JSON Pointer to preserve all definition records, with four additional tests. See [research and limits](HULL-BUILDING-20261022.md). Full suite 267; grouping is not a complete CFG/ABI and seed decisions are not full shape validity.

New pure calculation tool: [vector_angles.py](../../../scripts/research/vector_angles.py) 1.0.0, explained in [plate placement/strips/native-angle research](PLATE-PLACEMENT-20261021.md). `dot_angle3` uses the raw clamped 3D dot; `projected_angle3` normalizes supplied-axis projections with fallback (0,1) and native sign; `consistent_plate_turns` models the cyclic sign check only. No creation writes or complete geometry certification. Eleven new tests bring the suite to 204; Python libm is not bit-exact native emulation.

New pure geometry tool: [plate_surfaces.py](../../../scripts/research/plate_surfaces.py) 1.0.0; see [surface/clipping/collision research](PLATE-SURFACES-20261021.md). `clip_polygon(points, planes, coords=None)` returns ordered 2D clipping and optional interpolated coordinates; `solid_faces` builds the reviewed solid fans from explicit metre coordinates/support offset/unit normal; `collision_point_cloud` returns server hull inputs only. No creation reads/writes or native hull emulation. Twelve tests bring the suite to 193.

New read-only creation tool: [plate_reconstruction.py](../../../scripts/research/plate_reconstruction.py), explained in [plate creation/load/render lifecycle](PLATE-LOAD-20261021.md). Run `python scripts/research/plate_reconstruction.py creation.data --output plate-audit.json` from the repository root; output must be a new file. It checks selected plate reference, direction, planarity and first-edge-size rules, preserves fresh-load duplicate-edge behavior and distinguishes opposed skins from same-facing loops. It is not complete native-load or rendering acceptance. Ten new tests bring the full research suite to 181.

New vehicle helper module: [attachment_geometry.py](../../../scripts/research/attachment_geometry.py), documented in [attachment surfaces and contact boundaries](VEHICLE-ATTACHMENTS-20261021.md). Import its explicit-input surface_bounds, voxel_overlap, grids_equivalent, sampled_line_rectangle, sampled_triangle_rectangle and compiled_triangle_rectangle functions. The last function preserves the reviewed repeated-corner behavior; none is a complete mounting/save validator. Run `python -m unittest discover -s scripts/research -p 'test_*.py' -v` from the repository root. All 171 tests pass at this checkpoint.

Source: `scripts/research/`. Python 3.12+ standard library; Ghidra exports additionally use an existing isolated Ghidra/JDK. Outputs refuse overwrites and game files remain read-only. Never create output directories inside the active installation.

| Tool | Responsibility and limits |
| --- | --- |
| `baseline.py` 1.1.0 | Resource checks; one worker/BelowNormal; full inventory, selective copies, two-pass source hashes, actual-format identification; not an atomic snapshot |
| `gcl_index.py` 1.4.0 | Bounded length prefixes, operands, code/allocation fields, zero-slot checks and template-qualified signatures; not a full GCL parser |
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
| `powertrain_models.py`, `test_powertrain_models.py` | Selected torque-island, motor, alternator, swashplate, rotor and distance-only ground-effect arithmetic; explicit model-domain guards; not a native physics solver |
| `contact_models.py`, `test_contact_models.py` | Selected wheel load/grip, tangent cap and pressure-brake arithmetic; excludes casts, topology, support motion and native physics |
| `gas_thermal_models.py`, `test_gas_thermal_models.py` | Ordinary gas transfer, explicit pair/vector temperature difference and quantity-weighted heat blend; not a whole-network simulator |
| `actuator_models.py`, `test_actuator_models.py` | Selected two-chamber quantity bounds, pre-correction capacity writes and size-dependent geometry; not a native constraint/force solver |
| `joint_models.py`, `test_joint_models.py` | Selected per-peer constraint tiers, hinge interval repair, ballscrew brake/target/mass and winch length gates; ordinary-domain guards; excludes native constraint/rope physics and complete lifecycle |
| `survival_models.py`, `test_survival_models.py` | Selected condition cadence, vital flags, stamina edges, clothing wetness and body-temperature arithmetic; explicit ordinary domains; excludes full actor/authority, native physics, item lifecycle and network encoding |
| `ai_models.py`, `test_ai_models.py` | Selected actor/vehicle sensing ranges, target eligibility, nonnegative-ID modifiers and weighted selection for supplied draws; excludes brains, casts and native RNG/rounding |
| `native_image.py`, `test_native_image.py` | Bounded read-only x64 PE mapping, exception-directory ranges, signature strings and relative-byte-pattern leads; patterns do not establish bindings |
| `native_export.py` 1.1.0, `ExportNative.java`, `test_native_export.py` | Static selected native spans through existing Ghidra; explicit assembly-only mode; exact source/range/artifact/instruction checks; manual spans and exception entries do not guarantee full function boundaries or ABI |

## Selected native executable research

The [contact/fluid/native checkpoint](CONTACT-FLUIDS-NATIVE-20261020.md) uses a separate matching isolated executable. Keep its full index/exports local. Source SHA, native RVAs and GCL offsets are separate address domains. PE indexing never executes its source; selected exports execute only the existing Java/Ghidra analysis runtime.

```powershell
python scripts/research/native_image.py "$r/snapshot/game.exe" "$r/native-index"
python scripts/research/native_export.py "$r/snapshot/game.exe" "$r/native-export" "$runtime" "$project" 0x2a580 0x2c280:0x2c290
```

Use fresh output/project directories. The exporter uses a 2 GiB heap, one headless worker, BelowNormal priority and disabled automatic analysis. A selection without a colon requires exactly one containing exception-directory entry; an explicit begin:end span is recorded as manual. Exact bytes and complete output artifacts are checked before success. Ten production spans passed; no game process was executed. Selected registration bodies must be traced separately from string/pattern discovery.

The [actuator/track/raycast continuation](ACTUATORS-TRACKS-RAYCAST-20261020.md) adds 11 further checked native spans across five successful batches. Use `--assembly-only` when pseudocode is deliberately excluded; a mode marker and false decompilation status are required, and failed pseudocode cannot silently pass as assembly. Two earlier physics pseudocode attempts timed out and remain failed. Read adjacent exception fragments together; approximate C can cross a selected fragment and return-type inference can be wrong.

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

The [engine/structure follow-up](OFFLINE-ENGINE-STRUCTURE-20261019.md) adds another two batches: 27 functions, 11,186 instructions/68,043 bytes. A reader built from all six distinct batches contains 92 functions/25,041 instructions. Its selected-evidence input is `versions/build-25904830/offline-engine-structure-20261019/evidence.json`: 27 identities, 24 constants, 14 strings, 15 call examples checked. No research implementation changed, so the prior 51-test suite was not repeated; the new validation is byte/evidence/documentation checking. Earlier engine generators and cardinal structural-mount audits remain useful within their documented limits.

## Updates and historical records

The [2026-10-20 component/type checkpoint](COMPONENTS-TYPES-20261020.md) adds a counted reflection-table parser/query tool, constructor-prefix tracer, explicit-input geometry models and a selected declaration checker. Full reflection databases stay local. Scanner 1.4 accepts template-qualified function names containing spaces; rebuild the GCL index after changing parser source because export planning verifies its tool hash. Source bytes/build did not change. Tracer 1.1 caches signature candidates once while preserving duplicates as unresolved; before/after constructor evidence matches.

```powershell
python scripts/research/reflection_index.py build "$r/snapshot/bin/game.gcl" "$r/gcl/index.sqlite" "$r/reflection"
python scripts/research/reflection_index.py show "$r/reflection/types.sqlite" server_scene.vehicle_component.gearbox_c --section methods
python scripts/research/reflection_index.py show "$r/reflection/types.sqlite" vehicle_component_definition.e_logic_node_type --section enum
python scripts/research/constructor_trace.py "$r/snapshot/bin/game.gcl" "$r/gcl/index.sqlite" "$e1" "$r/constructors"
python scripts/research/component_geometry.py
python scripts/research/check_reflection_evidence.py "$r/snapshot/bin/game.gcl" doc/knowledge/research/versions/build-25904830/components-types-20261020/reflection-evidence.json --output "$r/reflection-check.json"
```

Reflection requires a bounded, counted table ending exactly at EOF; arbitrary descriptor-looking strings are insufficient. Unknown flags/list meaning, duplicate names/labels and boundary fields remain explicit. Constructor analysis stops at branches/gaps, distinguishes field constructors from same-address base initialization, clears call-clobbered state and does not recover the complete ABI or vtable execution. Geometry models require explicit inputs rather than inventing unrecovered vector defaults or native validation limits.

The [full-game audit](FULL-AUDIT-20261019.md) adds `audit_scope.py` for exhaustive accounting over the supplied GCL/definition indexes. It retains unclassified names and omitted classes, checks a reader's completion/source identity, and emits local function/class/definition-group queues. Public summaries deliberately omit the full method inventory. No class is automatically marked understood.

```powershell
python scripts/research/audit_scope.py "$r/gcl/index.sqlite" "$r/catalog/definitions.sqlite" "$r/scope" --reader "$r/reader/code.sqlite"
```

Reader 1.1 accepts identical repeated exports after auditing every batch, counts each function's instructions once, and reports deduplicated exports. Identity, approximate C, assembly and evidence must all match; conflicting duplicates are rejected and the reader stays incomplete. Use a fresh output after a failed build. That nine-batch checkpoint reader had 153 functions/43,027 instructions/253,345 bytes. Its 60 synthetic research-tool tests passed, including duplicate conflict and scope-accounting failure controls. Its evidence checker input is `versions/build-25904830/full-audit-20261019/evidence.json`.

```powershell
python scripts/research/check_historical.py "$r/snapshot/bin/game.gcl" "$r/gcl/index.sqlite" "<directory-of-selected-evidence-json>" "$r/historical-check.json"
python scripts/research/compare_builds.py "<old>/inventory.json" "<new>/inventory.json" "<new>/diff.json" --old-definitions "<old>/catalog/definitions.sqlite" --new-definitions "<new>/catalog/definitions.sqlite" --old-functions "<old>/gcl/index.sqlite" --new-functions "<new>/gcl/index.sqlite"
```

`check_historical.py` accepts the current six evidence groups' camelCase `functions[]` fields. Other schemas need explicit adapters; do not claim automatic compatibility with all archives. Definition differences align by source+ID and initially report nested changes at top-level fields; this is not a complete field-level migration engine.

Continue reusing old `anymaker.py`, `structural_mounts.py`, native generators, Workshop index, and Ghidra helpers through the [existing tool guide](../TOOLS.md). This checkpoint did not regenerate game assets or change browser application/export behavior.

Validation: 15 new-tool tests passed; 26 archived tests ran, 25 passed, one skipped for missing optional corpus. No frontend npm/browser checks or new game runtime experiments were performed.
