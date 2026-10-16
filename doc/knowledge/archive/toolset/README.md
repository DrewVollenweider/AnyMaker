# Anymaker offline toolset

Practical building rules and what the tools can verify: [VEHICLE-DESIGN.md](VEHICLE-DESIGN.md).

Current installation refresh: [14 October research](../exploration/research-20261014.md). `research_install.py INSTALLATION --creations CREATION_FOLDER --out NEW_NAME` creates a read-only, source-hashed version comparison, raw interface catalog, GCL names/types catalog and saved-creation/script index beneath `output/`. The original `reference/` remains the 11 October baseline; the new v0.1.25 snapshot is `output/research-20261014/`. Ordinary `anymaker.py` commands still use the baseline catalog (its only component JSON difference is the cannon description); use the fresh JSON directly when studying that changed component.

Static executable/GCL analysis and portable decompiler setup: see [DECOMPILATION.md](DECOMPILATION.md).

Post-decompilation running-save observation: see [LIVE-VALIDATION.md](LIVE-VALIDATION.md). `observe_files.py` records disk changes and checkpoint copies without game input or source writes.

Downloaded Workshop examples and reusable importer: see [WORKSHOP.md](WORKSHOP.md). The local gallery is `output/workshop-examples/index.html`.

Use `python toolset/anymaker.py` from the Anymaker project workspace. Python 3.10+; no third-party packages, game hooks, or network access required.

**All inputs are read-only. Every generated file is confined to `toolset/output/`, and existing outputs are never overwritten.** The tool does not install creations into the game, write its save folders, or alter originals. The reference folder contains copies of the installed component and inventory definitions with source hashes in `reference/manifest.json`.

## Commands

| Command | Purpose |
|---|---|
| `inspect FILE` | Bill of materials, saved component fields and data channels, counts and findings |
| `systems FILE` | Component requirements, input/output directions and direct saved links; functional status stays unverified |
| `systems FILE --markdown` | Readable vehicle-system checklist suitable for build review |
| `audit FILE` | IDs/references, rotations, structural edges, plate coplanarity, frame groups, connection endpoints/types |
| `scan DIRECTORY` | Audit `.data` files directly in a creation folder |
| `catalog QUERY` | Search component IDs, descriptions and data channels; `--full` includes geometry/surfaces, `--items` searches inventory items |
| `interfaces ID` | Read surface, logic-node and channel details |
| `interfaces ID --with-definition OTHER` | List type/gender surface candidates, with explicit limits |
| `diff BEFORE AFTER` | Compare JSON fields, including added/removed values |
| `view FILE` | Standalone HTML with top/front/side frame schematics and component origins |
| `clone FILE --out NAME.data` | Separate template draft, preserving IDs and unknown fields |
| `draft BASE PLAN --out NAME.data` | Make explicit draft edits; save audit and change log alongside it |
| `snapshot FILE --out NAME.json` | Capture stable JSON, with time/source/hash sidecar; supports working-state JSON too |

Read commands print JSON by default; add `--out NAME.json` to save a new result. Output names are relative to `toolset/output/`. Absolute paths are accepted only if they resolve inside that folder. `view --out NAME.html` produces a browser-readable file. Exit codes: 0 success/no audit errors, 2 audit errors, 1 input/output failure. Audit warnings require review even with exit code 0.

## Examples

```powershell
python toolset/anymaker.py inspect exploration/baseline/steercart.data
python toolset/anymaker.py systems exploration/baseline/steercart.data --markdown --out my-cart-systems.md
python toolset/anymaker.py catalog electric_motor --full
python toolset/anymaker.py interfaces steering_wheel --with-definition high_back_car_seat
python toolset/anymaker.py audit "C:\Users\PLAYER\AppData\Roaming\Anymaker\creations\buildcart.data"
python toolset/anymaker.py view exploration/baseline/steercart.data --out my-cart.html
python toolset/anymaker.py draft exploration/baseline/steercart.data toolset/example-plan.json --out my-draft.data
python toolset/anymaker.py diff exploration/baseline/steercart.data toolset/output/my-draft.data
```

The supplied example plan changes only the copied steercart's handbrake fields. It is specific to that template and its array layout; inspect the component IDs before adapting it to another build. The generated sample draft is **not game-tested** and was never installed into the creation folder.

The `systems` review uses curated requirements for 14 known component definitions and includes shipped descriptions and data channels for the remaining components. An omitted channel direction stays unknown. Direct saved links do not establish port attachment, a shared network, torque continuity, or runtime power. Structural errors withhold the systems review; functional requirements do not block draft generation. Review rules are in `vehicle_rules.json`, grounded in the copied installed definitions.

## Draft plans

Plans are JSON objects with these optional operations, applied in order:

1. `replace`: `{"path":"/existing/field","value":VALUE}` entries. Uses JSON Pointer paths; nonexistent fields fail. Rotation, position, properties, or entire arrays can be replaced.
2. `append`: `{"path":"/existing/array","values":[...]}` entries. Useful for explicit frame nodes, edges, plates and links. Node and plate IDs remain the caller's responsibility.
3. `add_components`: `{"vehicle_id":209,"definition":"electric_motor_a","grid":0,"component":{"pos":[0,0,0]}}` entries. Resolves/adds the definition reference and allocates an unused component ID when omitted. Supply orientation and any required properties/accessories explicitly.

Drafts begin with an existing creation to preserve fields whose defaults or meaning are not yet verified. Unknown fields survive. Component addition is serialization assistance: it does **not** automatically find an attachment, connect power/torque, or establish that the game will accept the design. No `.meta` or preview is invented; export behavior must be checked in a separately named sandbox test.

## Interpretation limits

- Error checks cover malformed structure and certain geometric invariants. Warning checks depend on incomplete format knowledge.
- Disconnected frame-only groups can be connected through components; they are not a definitive structural-failure diagnosis.
- Plate perimeter checks use exact edge endpoint pairs; subdivided boundaries can trigger warnings on valid builds.
- Logic-node indexes follow the observed zero-based endpoint convention. Missing node types/sizes/defaults remain unknown. Dynamic definitions may invalidate a static endpoint warning.
- Surface candidates are raw type/gender matches. They do not prove positional alignment, overlap coverage, size, orientation, or mating behavior. Direction-code and matrix conventions have not been runtime-certified.
- Schematics show local component origins and frame geometry, not component meshes or collisions. Separate vehicles are drawn separately; their transforms are not applied.
- JSON diff treats array indexes positionally. A reordered array can look like many changes; inspect IDs before concluding a component changed.
- Checkpoints are delayed saved snapshots, not continuous telemetry. Snapshot reads retry if file size/timestamp changes, but multi-file transactional consistency is not guaranteed.
- No watertightness, collision, complete drivetrain continuity, script compilation, in-game loadability, or functional physics certification is claimed.

## Agent workflow

Read `../exploration/game-knowledge.md` first, then inspect a source and look up its definitions. Save an audit and schematic, review each issue, and create a new draft plus a change log. Keep original files immutable. Use Computer Use only for explicitly authorized game tests; N/free-move and the user's quick N/N backpack workaround are recorded in the knowledge note. Do not use shell input automation, binary patches, mods, or process memory.

Run meaningful verification with:

```powershell
python -m unittest discover -s toolset/tests -v
```

Tests use the preserved game-authored steercart fixture and deliberately corrupted copies, exercise source preservation and output confinement, and check structural/draft/diff behavior.
