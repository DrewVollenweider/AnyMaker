# Native data, components and research methods

## Format and serialization

Native creation `.data` and companion `.meta` files are JSON; `.png` is the preview. Resolve component `def` indexes through `definitions.components`. Components sit in mounting grids within `vehicles.vehicles`; nodes, edges, plates and six saved link families are vehicle-level arrays. Liquid/gas/electric/data/control networks do not substitute for torque faces or structural mates. Hydraulic connector/base relationships are saved on components, including reciprocal target vehicle/component/node indexes; no invented `hydraulic_links` array is required for observed cylinder pairs.

Keep unknown fields and typed controller state. Normalize omitted defaults only for comparison; do not gratuitously fill every omitted native field. Game exports can reassign body/fitted-item IDs, reorder definitions and omit [0,0,0] node positions. Generic array-position diffs can mislead. Compare semantic IDs, resolved definitions, normalized transforms and complete links. Native gas temperatures may be null; that alone is not corruption.

Matrices are column-major. Non-base mounting grid transforms require frame projection and offset; older repository evidence describes localY=normalize(dir), X=normalize(dir×up), Z=X×Y with a non-base translation term origin+0.5sign(dir)+0.5normalize(dir). Those exact code offsets were from an older GCL. All seven tested old ranges failed byte-hash matching in the current build. Re-locate by function ownership/signature before reusing offsets; do not assume either unchanged implementation or changed mechanics solely from hash mismatch.

Interfaces can pair inside the same vehicle in observed saves; do not enforce cross-body-only links without definition/runtime evidence. A source connector's own node index differs from its target `connected_node_index`. Data descriptors can omit types/directions; preserve unknown rather than inventing defaults.

## Versioned research

Oct11 exploration used v0.1.24 build25826614. Oct14 refresh identified **v0.1.25 build25904830**, 598 component definitions and372 inventory definitions. The vehicle catalog changed one description: cannon_120mm breech thresholds now29.4/19.6 kPa instead of the earlier4.9/vent text. That is a documentation comparison, not by itself a runtime proof. The inventory catalog was unchanged. Fifty inspected sources retained identical before/after hashes.

GCL header parsing found1172 source-path records and931 global-name/type records. Forty-four path prefixes changed; name counts did not prove code identity. Native executable export recovered9710 decompiled functions from9822 visits; this was **not full GCL reconstruction**. The archive contains parser/indexer/headless-export tools and selected function-record metadata, not the game executable, GCL binary, full pseudocode dump, runtime downloads or analysis databases.

Use [research refresh](archive/exploration/research-20261014.md), [source-integrity report](archive/toolset/output/research-20261014/report.json), [old-offset check](archive/toolset/output/research-20261014/grid-evidence-version-check.json), [decompilation method](archive/toolset/DECOMPILATION.md) and the repository's existing native-format documents. Selected diagnostic JSON records preserve function signatures/addresses and hashes; addresses are build-specific. Follow the owning function, not merely the last nearby call.

## Observation and control lessons

Working saves are checkpoints, not continuous telemetry. On Oct11 two checkpoint timestamps were300.0003762 seconds apart and24 autosave folders existed, agreeing with recovered initialization values300 and24. Scene version advanced18000, consistent with60 increments/second but not independently proven tick semantics. No supported external telemetry socket, script file-write API or networking bridge was established. Use user-saved operating snapshots and in-game instrumentation for current measurements.

Computer interaction achieved a reversible door open/close cycle and two automated1-grid-unit edges after a user-created10-unit edge. This proves limited interactions, not reliable arbitrary geometry construction, duration-controlled driving or a complete automated game test runner. Require target label/context prompt before actions; distinguish visible animation from settled state. N toggles free-move; the user supplied quick N/N as a backpack-alignment workaround. These were navigation findings, not new game APIs.

Read-only tools retry unstable file reads, preserve hashes and refuse overwrite/escaped output paths. Checkpoint files can update naturally while being observed; don't describe that as tool modification. A live observation blocked by a permission overlay was explicitly recorded as unperformed interaction, not hidden success.

## Evidence hierarchy and practical workflow

1. Inspect the current creation and component definitions for the installed version.
2. Trace complete structural and functional chains separately, including all ports, state, controls and torque consumers.
3. Calculate transforms/ratios and run static checks within their stated scope.
4. Save a separately named candidate with paired metadata and a clear change record.
5. Obtain actual game load and operating evidence, preserving the accepted previous revision.
6. Update these notes with confirmed results, failed hypotheses and remaining questions.

Keep browser-builder export acceptance separate from these procedural native fixtures. The compact engine and giant test vehicle were user-tested; that does not establish arbitrary editor exports as game compatible. See [delivery standard](../18_BUILD_ASSURANCE.md).
