# Anymaker static decompilation

Portable Ghidra 12.1.4 and Temurin JDK 25 were downloaded from their official release repositories and checked against the release SHA-256 values. They live in `toolset/runtime/`; neither was installed system-wide. Only copies and extracted code blocks were submitted to Ghidra. The game was not executed by the analysis tools.

The executable export completed: **9,710 functions decompiled out of 9,822 visited**. Initial and post-script analysis succeeded. The difference includes skipped external/thunk functions and any functions the decompiler could not recover; this count does not establish complete recovery of the entire game.

## What was recovered

- Executable pseudocode (local evidence not uploaded): approximate C-like output from `game.exe`. This is not original source or a compilable replacement. Many function, variable, and type names are generated or inferred.
- GCL symbol catalog (local evidence not uploaded): 1,172 validated source-path records, 931 global names with types, and 63,339 unique selected readable strings. The paths identify developer `.gc` files; they do not contain their source text. Later GCL tables are not fully decoded.
- Three small native x64 initialization routines extracted from `game.gcl`, with original file offsets and hashes in the sample manifest (local evidence not uploaded).

The developer paths include `geocode-language/lib`, Anymaker game/client/server code, component definitions, save handling, buoyancy, and microcontrollers. The name Geocode comes from those paths; the complete language and compiler format remain unknown.

## Verified initialization values

Ghidra recovered the assignment and multiplication operations. The constant bytes in the extracted blocks give:

| Named global | Initialization | Evidence |
|---|---|---|
| `g_server_tick_rate_s32` | 60 | int32 at block offset 16; pointer slot at 24 |
| `server.G_AUTOSAVE_INTERVAL` | 60.0 × 5.0 = 300.0 | float64 operands at offsets 32 and 40; pointer slot at 48 |
| `server.G_AUTOSAVE_MAX_COUNT` | 24 | int32 at block offset 16; pointer slot at 24 |

These are static initialization values, not a measurement of the running save. The 300 value agrees with the previously observed five-minute checkpoint interval. Interpreting the interval as seconds and the tick rate as ticks per second is consistent with the global names and that observation.

A subsequent [running-save observation](LIVE-VALIDATION.md) measured a 300.0003762-second interval between checkpoint timestamps and counted 24 autosave folders. The live server tick rate still was not measured.

Raw decompilation of these samples retains `DAT_...` labels because their global-pointer relocations are unresolved. They are not evidence that the game writes to address zero. Read the constant report (local evidence not uploaded) alongside tick-rate pseudocode (local evidence not uploaded), interval pseudocode (local evidence not uploaded), and count pseudocode (local evidence not uploaded).

## What this helps us investigate

The executable contains a decompiled routine calling `XInputGetState` and converting stick/trigger/button state. This establishes a controller polling path, but does not demonstrate reliable automated input delivery. Its type metadata also contains Jolt (`JPH`) physics types. The original `build_win.pdb` debugging symbols were not found, and the install search found no `.gc` source files.

GCL names include client/server inspection data, microcontroller values, save tasks, and vehicle subsystem functions. These are useful clues for understanding the existing inspection UI and saved fields. They do not establish a public telemetry API, a callable external bridge, or a complete mapping from saved state to live state.

## Next work

1. Trace creation save/load and inspection routines using the recovered names and executable references.
2. Reverse-engineer the GCL function/relocation tables on copies, preserving source IDs and signatures. The three extracted constructors show native-code recovery is feasible; full GCL decompilation is unfinished.
3. Validate relevant findings through reversible sandbox UI tests and paired file snapshots. Keep any initial bridge outside the game: offline parsers, file observation, and existing UI interactions.

The full export has an accompanying function index (local evidence not uploaded) and 28 selected review excerpts (local evidence not uploaded). Keyword matches are investigative leads, not behavioral proof. The saved integrity comparison (local evidence not uploaded) checks the original executable, Steam library, and GCL file against their pre-analysis hashes.

## Reusing the tools

- `read_binaries.py`: PE metadata/imports and hashes.
- `inspect_gcl.py`: validated source/global tables and selected strings.
- `extract_gcl_samples.py`: only the three known constructor layouts, with strict checks.
- `run_headless.ps1`, `SetupSample.java`, `ExportAnymaker.java`: portable static analysis and C-like export.
- `index_decompiled.py`: indexes only a completed export and gathers relevant keyword excerpts.

Exports refuse to overwrite existing output files. The first two raw sample exports had an overly specific header referring to the executable; the linked v2 exports correct the labels without changing the recovered code. Analysis databases are in `C:\Users\PLAYER\AppData\Local\Temp\anymaker-static-analysis-20261011`, because Ghidra rejects project paths containing `.codex`. Durable copies are preserved under `output/decompilation/projects/`; copy them to a path without dot-prefixed directory names before opening them in Ghidra. Runtime settings and caches are under `toolset/runtime/state/`.

Tool sources: [official Ghidra releases](https://github.com/NationalSecurityAgency/ghidra/releases), [official Temurin 25 releases](https://github.com/adoptium/temurin25-binaries/releases). Download URLs and checksums are recorded in `runtime/downloads.json`.
