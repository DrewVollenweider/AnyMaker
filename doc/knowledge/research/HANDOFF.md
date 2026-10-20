# Handoff and restart

Latest checkpoint: [2026-10-19 offline code reader](OFFLINE-20261019.md). The user's current request is research without required in-game testing. Tools and static checks now cover 29 additional selected functions; no gameplay test is required to continue. Exact local outputs are in workspace `RESEARCH-HANDOFF.md`. Preserve unknown dynamic bindings rather than inventing targets.

Status: phase 1 (baseline/existing-work assessment/system map) is complete. The first necessary search and local native-analysis capabilities of phase 2 are delivered. Complete container/type recovery in phase 2 remains unfinished; phase 3's per-system explanations are beginning. Do not mark the whole assignment complete at this checkpoint.

## Restart sequence

1. Read parent AGENTS, the knowledge hub, CURRENT-FACTS, and this directory's README/COVERAGE/VERSIONS.
2. Locate the separate research directory. Exact machine paths are in workspace `RESEARCH-HANDOFF.md`; the public repository stores only relative paths and hashes. Without local inputs, recollect the matching version using TOOLS; never request or commit private keys.
3. Confirm `gcl/index.sqlite` by source SHA. Query the target signature/references and read local original bytes/limited exports. Do not load the entire decompilation into context.
4. Read this checkpoint's `historical-check.json` first. All 96 historical addresses are invalid; use relocated addresses. The 66 identical code hashes do not establish unchanged data/caller environments.
5. Check for installation updates. A new build or any changed input hash requires a separate version directory and comparison.
6. Continue independent static analysis without controlling the running game. Planned experiment protocols are not results.

## Next steps, in order

1. Continue the offline electrical/pump/script traces: establish electrical budget initialization/consumer ordering, liquid pressure-unit conversion and conservation, and script loops/budgets. Use the new reader before exporting more functions; keep unresolved virtual targets explicit.
2. Complete actual GCL-loader rules for flags, allocation +8, kind 1/5/6, trailing debug/unwind data, and type tables. The existing scanner already supports search. Extend only when a demonstrated limitation blocks a question; do not build a general decompiler for its own sake.
3. Select representative components from every system-map category. Trace parse/default -> create/post_load -> tick -> inspect/save, listing unchecked sizes/variants. Prioritize electricity, script execution/scheduling, and fluid units, then expand AI/world/multiplayer.
4. Reuse Mesh parsers/audits to review all relevant current-build formats. A `.anim` mesh v5 container is not automatically animation logic. Validate vegetation `.bin` layouts against consumers as well as bytes.
5. Return to Opening/Hatch initial flags, collision builders, player-passage paths, and manager ordering as offline questions. Historical runtime protocols are optional reference plans; do not request a gameplay session as a gate for the current research assignment. Keep gameplay/saves undisturbed.

## Progress log

| Local date | Progress | Evidence/limits |
| --- | --- | --- |
| 2026-10-18 | Located installation/Steam build; verified full inventory/copy hashes | Final baseline 1.1.0; relative-path inventory excludes account fields |
| 2026-10-18 | Reviewed archives, accepted native creations, Ghidra tools, six historical code-evidence groups | Historical records retained; historical user tests are not new tests |
| 2026-10-18 | 37,082 GCL records, definition database, 15-topic system map | Complete local indexes; types/full container unrecovered |
| 2026-10-18 | Relocated 96 historical ranges; 66 code hashes retained | No old offsets matched |
| 2026-10-18 | Opening/Hatch geometry match, seal write, water-flow read path | Partial exports of 18 functions; 6,599 instruction-byte checks; no runtime acceptance |
| 2026-10-18 | 15 new-tool and 25 archived tests passed; one optional corpus skipped | Actual one-function runner smoke test; not an additional unique function |
| 2026-10-19 | Machine-fact exporter, local dependency tracer, full-text code reader, selected-evidence checker | 29 additional functions; 6,813 instructions/39,264 bytes checked; 297 slot-derived call dependencies, 270 unresolved |
| 2026-10-19 | Electrical budget calls, relay hysteresis, liquid pump arithmetic, microcontroller power gate | 42 research-tool tests; 29 records, 17 constants, four strings, 21 call examples checked; no game execution |

Default Git transfers repeatedly stalled in this environment and were terminated. A separate sparse checkout was recovered through GitHub API objects and existing archive blobs, checking every object's SHA-1: base `bcfea8e9b94604020d8957e456493c744a89e2e0`, 49 trees, 133 matching blobs. Unretrieved application blobs remain absent under sparse checkout; this is not a usable frontend-test checkout. Other checkouts' local changes/commits were neither read nor rewritten.

The original checkpoint changed only research code/docs/indexes, with no main merge, deployment, or release. Publication status and actual commit IDs must come from final Git results and local handoff, not this planned paragraph. Leave no background analysis jobs at session end; explicitly record PID, logs, resource cap, and stop method for any retained job.

Language correction: the user rejected the historical Chinese-documentation instruction and explicitly authorized English documentation/instruction corrections on both the research branch and main. That authorization does not extend to deployments, releases, or application behavior changes. Preserve the original checkpoint's evidence and completion boundaries when translating it.
