# Installed build transition: 25904830 to 26113663

2026-10-22. The final source check for [hull-building research](HULL-BUILDING-20261022.md) detected a changed installation. Steam identifies the installed build as **26113663**. A fresh read-only snapshot and two independent complete hash passes were taken. No game execution, installation edit or active-save change was performed.

## Scope and identities

The earlier mechanics findings remain verified against archived **25904830**. They are not automatically revalidated for the new installation.

| Source | Archived 25904830 SHA-256 | Installed 26113663 SHA-256 |
| --- | --- | --- |
| GCL | `626a994be960b7218409d9ca416d2664450231d1fc3295036fc77c81b8449355` | `a3fd2df2fd62e38b629f6a0df824269a34d77d57caf66d596362d7e5e53c3b22` |
| PE | `5c46cd34a3b00889ff36154976428ba43f6475430e92a2d113a360a78161a7d0` | `097e1167477587c51a3b93ab7e7843382d99d30010678c9bd89a2fee648fec23` |

The installation comparison finds **8 added files, 1 removed, 1,526 changed and 9,286 unchanged**. Changes include code, component declarations, building data and assets. Asset additions alone do not establish new playable components.

## Complete catalog comparison

Both catalogs contain **1,737 definition records**. Comparison now keys each by **source file plus JSON Pointer**, preserving anonymous records and repeated IDs. The former source-plus-ID key collapsed these records into 1,020 keys; its preliminary comparison was superseded before publication.

The corrected comparison finds **9 changed records and 1,728 unchanged**, with no additions/removals. Each changed record differs only in `tech_tier`, from **2 to 3**:

- Liquid and gas pressure sensors.
- Liquid and gas temperature sensors.
- Acceleration, altitude, tilt, compass and gyro-rotation sensors.

This establishes the declared tier change. Its complete progression/unlock behavior is not inferred from the declaration alone.

## Code comparison and next work

GCL indexed records increase from **37,140 to 37,175**. Grouping by signature and comparing sorted code-hash/size lists gives **72 added groups, 37 removed, 2,271 changed and 34,832 unchanged**.

These are byte-level change groups, not a count of changed mechanics. Even identical code bytes can depend on changed constants, bindings, callers or data. Native RVAs and old source offsets must not be reused against the new binaries without mapping and validation.

[The transition summary](versions/build-26113663/transition-20261022/summary.json) preserves selected identities, counts and the nine field changes. Full inventories, game resources, code exports and indexes remain local. The comparison fix has four regression tests; the full research suite passes **267 tests**. An initial test-fixture cleanup failed because its SQLite writer connection remained open on Windows; the fixture now closes it, and the failed private log is preserved.

The audit remains active and incomplete. Next work must establish a new-build evidence baseline and revalidate the vehicle chains, while retaining the archived research and continuing unanswered mechanics questions. Engines, drivetrain, structures, fluids, electrics, controls, suspension and flight/marine systems remain the priority.
