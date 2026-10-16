# Validation — 2026-10-11

## Systems-review update

- 26 unit tests passed: the existing 20 creation/Workshop checks plus six systems-review checks. New cases cover direct-link reporting, separately wired electric ports without assumed consumer power, unknown channel direction, malformed creation rejection, preservation of input fields, and unknown/frame-only components.
- Systems reviews generated successfully for all 64 examples (31 local creations and 33 copied Workshop builds). SHA-256 comparisons confirmed every input `.data` file remained unchanged. Summary: `output/systems-review-corpus.json`.
- Markdown and JSON examples were generated for the starter steering cart, Workshop 3806342313, and Workshop 3804792002. Reviews keep functional status unverified and do not certify power, torque continuity, mating, or runtime behavior.
- Curated requirements cover 14 known definitions; remaining definitions retain their shipped descriptions/data channels and are clearly labeled as having no curated checklist. Wheel checklists distinguish driven wheels from passive wheels; motor checks refer to the intended load, allowing uses beyond wheeled vehicles.

## Earlier validation

- 17 unit tests passed, using a real saved creation plus corrupted copies. Covered dangling references, duplicate IDs, definition indexes, improper rotation, nonplanar plates, malformed input, frame-only schema, field preservation, draft additions, append operations, JSON diffs, HTML escaping, nonfinite JSON, output confinement and overwrite refusal.
- Read-only scan of 31 existing `.data` files: no errors under the implemented checks, seven frame-group warnings. These warnings require attachment-aware review and do not establish that those creations are broken. Latest report: `output/creations-audit-v2.json`.
- Sample draft: `output/steercart-handbrake-release.data`. Diff confirms exactly two changes: handbrake `is_on` true to false and `value` 1 to 0. Audit and change log accompany the draft. No import or runtime validation was attempted.
- Generated inspection, motor catalog, seat/control interface candidates, schematic HTML and world snapshot successfully through the CLI.
- All 102 baseline files under the original creation directory retained their hashes. Both original installed definition files match the hashes recorded when copied.

Schematic: `output/steercart-schematic.html`. It is an origin/frame visualization, not a rendered game model. No external dependencies or game modifications were installed.
