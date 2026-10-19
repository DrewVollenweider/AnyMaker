# Versions and provenance

Current baseline: Steam app 4435340, build **25904830**, matching TargetBuildID, StateFlags=4. The complete [inventory](versions/build-25904830/inventory.json) contains 10,813 relative paths, sizes, and SHA-256 hashes totaling 1,194,452,027 bytes. Steam LastOwner and account fields were not retained.

The selective snapshot includes code, all `rom/data/`, shipped translations, audio descriptor libraries, and installation-provided examples: 4,833 files and 171,094,372 bytes. Originals were untouched. Every copy independently matched its source hash, followed by a second full traversal and hashing of the installation. This detects changes during reading/copying; it is not an operating-system atomic snapshot and cannot guarantee files remain unchanged after the check.

Semantic version **v0.1.25** comes from an existing October 14 game-UI observation. The current Steam build and GCL hash match that record. This checkpoint did not read the current game window, and EXE version resources provided no useful string. Steam build plus full-file hashes are therefore the direct identity evidence for this checkpoint.

Current `bin/game.gcl`: 82,528,301 bytes, SHA-256 `626a994be960b7218409d9ca416d2664450231d1fc3295036fc77c81b8449355`. Native x64 instructions coexist with length-prefixed signatures, global/source-path tables, relocation operands, and undecoded metadata. It was not classified as bytecode merely from its `.gcl` extension.

## Historical evidence

[Six evidence-group checks](versions/build-25904830/historical-check.json) cover grids, mechanical mates, hydraulics, tracks, belts, and structural islands: 96 historical ranges. Original locations matched 0/96; full-signature relocation succeeded for 96/96; 66 relocated code hashes match the historical record. This includes duplicate records across evidence groups, not 96 distinct mechanics.

Historical GCLs such as `32c1389e...`, `d9725681...`, and `da170da3...` must not be mixed with the current build. Different bytes may reflect relocation/layout alone, not a mechanic change. Identical bytes do not remove the need to review callers, data layouts, and external constants.

Existing CURRENT-FACTS, EXPERIMENTS, NATIVE-AND-RESEARCH, NATIVE-TRACE-SUMMARY, TOOLS, accepted CPE1Running/large test vehicles, and archived parsers were reviewed. The earlier statement that GCL recovery covered only three samples remains historical. The new record scanner extends it without claiming complete container decoding.

## Format boundaries

The [format census](versions/build-25904830/format-census.json) identifies bytes rather than guessing from suffixes. The `mesh` v5 signature occurs in both `.mesh` and `.anim`; `.anim` is therefore not universally an animation-instruction format. This checkpoint checked only headers of all 4,470 matching files, not complete geometry. Continue reusing `src/assets/mesh.js` and existing asset audits; full current-build variant review remains pending.

2,979 files passed full JSON parsing, including `.data`, `.meta`, and audio `.slib`. The latter are sound-effect descriptor libraries, not presumed script libraries. TXTR v2, ATLA v1, and fonts were only identified. 1,843 `.bin` files remain unparsed; samples point to vegetation data. There is no evidence to classify these collectively as executable bytecode.

Tools: Ghidra 12.1.4, Temurin 25.0.4.1+1, Python 3.12.14. Existing isolated local runtimes were reused; nothing was downloaded again or installed system-wide. Tool-source, input, and export hashes are recorded separately in the inventory, GCL summary, export checks, and runner record. Full local databases/decompilations stay outside Git.

For future builds, create a new directory, compare inventories first, then definition semantics and function-record hashes. Reuse output only when relevant input and tool hashes both match. Relocate historical addresses again.
