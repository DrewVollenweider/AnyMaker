# Local Anymaker tools

The reusable offline creation/analysis tools are documented in [toolset/README.md](toolset/README.md). Entry point: `python toolset/anymaker.py`. Original game files are read-only; generated reports, schematics and drafts go exclusively into `toolset/output/` with no overwrite.

Game knowledge and user-supplied navigation notes: [exploration/game-knowledge.md](exploration/game-knowledge.md).

Latest installation research (v0.1.25, 14 October 2026): [exploration/research-20261014.md](exploration/research-20261014.md). Read it before using older decompilation offsets or treating mounting grids as separate bodies. Current definition snapshots and the source-integrity report are under `toolset/output/research-20261014/`.

Engine revisions: the user tested [Petrol Pedestal Test 01](toolset/output/pedestal-engine-test-01/LIVE-RESULT.md). [Compact Petrol Engine 01](toolset/output/compact-petrol-engine-01-complete/README.md) packages its 60 components in a 1.36 m wide × 1.04 m long × 0.92 m high static envelope. It is installed as a separate creation and requires a fresh in-game test. `toolset/compact_engine.py` provides zone-based clearance checks, a connected cradle and routed lines; the completed output's `final-checks.json` records 36 port/fan mounts, five torque mounts, 19 frame contacts and 24 routes. Older intermediate compact folders are development snapshots; use the `-complete` folder as the delivered revision.

The compact revision subsequently passed the user's loading/running test: [CPE1Running result](toolset/output/compact-petrol-engine-01-complete/LIVE-RESULT.md). Its native export and preview are preserved in `running-result/`. This supersedes the earlier pending load/run status; prolonged circulation and drivetrain loading remain unverified.
