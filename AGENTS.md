# AGENTS.md

## Scope and workflow

This guide applies to the entire repository. Additional `AGENTS.md` files in subdirectories supplement these rules within their scope.

- **Use English for all documentation, research records, development notes, code comments, commit messages, and communication with the user. The user cannot read Chinese and has explicitly rejected the former Chinese-documentation instruction. Do not restore that instruction or infer a Chinese preference from historical files. Use another language only when the user explicitly requests it. Existing optional UI localization is separate from this English-language policy.**
- Before starting, read `README.md`, `TODO.md`, and `doc/README.md`, then the design and implementation relevant to the task.
- Distinguish verified facts, current implementation, design goals, and unverified items. Proposed directories, capability descriptions, and checked TODO items do not prove implementation or acceptance. State discrepancies explicitly.
- Change only files needed for the task and preserve existing user changes. Do not casually refactor large modules, upgrade dependencies, regenerate the entire asset set, or fix unrelated issues.
- Keep the UI English by default and preserve existing language-switching and persisted preferences. Follow the existing localization system for UI strings; this does not authorize Chinese documentation. Keep code identifiers in their established English form. Report changes, checks actually performed, and unverified items; never call an unperformed check successful.
- **All Git commit titles and bodies must be in English.**

## Project purpose

Anymaker Builder is a desktop-first vehicle-building research prototype using **Vite 7, Three.js, native JavaScript ES modules, DOM, and CSS**. It currently has no React/Vue, TypeScript, backend, database, or account system.

- The target is static hosting such as GitHub Pages. Production must be self-contained and must not depend on the game process, installation directory, or an asset conversion service.
- Local Mesh selection is for development and asset auditing, not a prerequisite for online users.
- This phase targets desktop mouse and keyboard. Do not proactively add touch, phone, or tablet support.
- The current renderer uses neutral diagnostic materials. Complete game materials, dynamic constraints, structural editing, and native save compatibility remain unfinished. Geometry parsing, asset inclusion, or a successful build do not prove visual parity or game-load acceptance.

## Actual directories and responsibilities

The following are implemented paths. Do not mistake proposed paths such as `src/assets/published/` or `src/components/` for existing modules.

| Path | Responsibility |
| --- | --- |
| `index.html`, `src/main.js` | Entry point, DOM composition, event coordination, Three.js scene, tools, and editing workflows |
| `src/style.css` | Global theme, desktop layout, toolbar, catalog, and Inspector styles |
| `src/catalog/component-catalog.js` | Component index, lazy detail/binding loading, validation, and caching |
| `src/assets/mesh.js` | Mesh v5 binary parser shared by the browser and Node scripts |
| `src/assets/library.js` | Development-only local resources, geometry instantiation, diagnostics, and disposal |
| `src/assets/published-library.js` | Published manifest, gzip Mesh loading, caching, basic assembly, and `PublishedAssetLoader` alias |
| `src/assets/geometry-ops.js` | Geometry reflection, normals, and triangle winding |
| `src/editor/document.js` | Project schema, validation, migration, snapshot history, and intermediate XML |
| `src/editor/model.js` | Rendering-independent `Project`, `Vehicle`, `Grid`, `Component`, `Node`, `Edge`, `Plate`, `Link`, and adapters |
| `src/editor/operations.js`, `src/editor/topology.js` | Component/grid operations and pure-data node, beam, and plate operations |
| `src/native/anymaker-data.js` | Native JSON parsing, domain mapping, and experimental write-back preserving raw fields |
| `public/data/` | `index.json`, `component-index.json`, and per-component `definitions/` and `bindings/` |
| `public/assets/` | Published `manifests/mesh-manifest.json` and separate `meshes/*.json.gz` |
| `scripts/` | Offline extraction, conversion, auditing, and published-asset integrity checks |
| `tests/unit.test.js`, `tests/fixtures.js` | Node unit tests and synthetic Mesh fixtures |
| `tests/browser/editor.spec.js` | Playwright editor workflow tests |
| `test-vehicle/` | Native vehicle samples; treat as format-research inputs and do not casually overwrite |
| `doc/`, `doc/evidence/` | Design, format research, and selected auditable summaries |
| `.github/workflows/pages.yml` | Recorded static build and Pages workflow location; confirm current existence before use |

## Environment, commands, and validation

Run commands from the repository root. Use npm and the committed `package-lock.json`; do not introduce another package manager's lockfile.

Build settings are in `vite.config.js`; preserve `.gitignore` rules when working with local artifacts.

The locked Vite requires Node `^20.19.0 || >=22.12.0`. The recorded Pages environment uses Node 20, so a local 20.x version must be at least 20.19. Browsers need WebGL and `DecompressionStream`; automated browser tests use Chromium.

| Command | Purpose |
| --- | --- |
| `npm ci` | Install locked dependencies |
| `npm run dev` | Start the Vite development server |
| `npm test` | Run `tests/unit.test.js` with `node:test` |
| `npm run check` | Routine default: unit tests and production build |
| `npm run test:browser:editor` | Editor interaction workflows only |
| `npm run test:browser:preferences` | Settings and recovery workflows only |
| `npm run check:assets` | Component references, Mesh manifest, file presence, and compressed-output SHA-256 |
| `npx playwright install chromium` | Initial browser download; not needed for every check |
| `npm run test:browser` | Complete Playwright workflows |
| `npm run check:full` | Pre-release unit, asset, browser, and build checks |
| `npm run build` | Generate the configured build output; this guide historically recorded `dist/` |
| `npm run preview` | Preview an existing build |
| `npm run test:serve` | Internal browser-test server: build for `/anymaker-builder/` and serve on port 4173 |

- Playwright starts its own server at `http://127.0.0.1:4173/anymaker-builder/`, with one worker, a 1500x960 viewport, and SwiftShader. Do not start another server on that port; the configuration does not reuse an existing server.
- Normally run `npm run check`. For UI, loading, or file-workflow changes, add only the relevant editor or preferences browser file. Add asset checks for catalog, binding, Mesh, manifest, or conversion changes. Run `check:full` for cross-module refactoring or before release, rather than indiscriminately for every small change.
- For documentation-only changes, verify paths, commands, and facts. Installing dependencies or reconverting assets is unnecessary.
- Run `python scripts/check-documentation.py` for documentation/instruction changes (or supply `--git PATH` when Git is not on PATH). It checks all tracked Markdown for Han characters and local file/heading links, without reading game files or fetching remote links. This is a language/link guard, not proof that prose or game findings are correct.
- `npm test` explicitly selects one test entry point. If adding another test file, update the entry point; do not assume automatic discovery.
- No lint, formatter, or type-check script is configured. Do not claim nonexistent checks ran. The historical CI record covered asset checks and builds, not unit tests or Playwright; inspect current workflow files before making a current CI claim.
- Preserve failure evidence and distinguish pre-existing failures from regressions. Do not delete assertions, skip cases, or fabricate resources to hide failures.
- Fix errors through general rules, input validation, and regression tests covering related inputs. Do not substitute a one-off vehicle repair for a code fix. Base structural-island checks on auditable game traversal/connections and identify unverified contact or runtime behavior.

## Coding and architecture conventions

- Keep `.js`/`.mjs`, ES modules, explicit `.js` relative imports, two-space indentation, single quotes, and semicolons consistent with the surrounding files. Do not reformat unrelated code.
- `src/main.js` coordinates the application. Independently testable parsing, domain, and format logic belongs in the appropriate module. Split component-specific assembly by component rather than growing a global factory.
- Keep dependency direction UI -> commands/domain model -> validation/history. Resource libraries supply rendering assets; format adapters read/write domain data. Parsers must not depend on DOM, and domain objects must not hold Three.js objects.
- Store only serializable snapshots in project/history data. Exclude selection state, tools, `File`, Three.js objects, caches, and local absolute paths.
- Operations return independent data. Copies allocate new IDs and remap references. Validate before committing; failure must preserve the original project, and user operations must be fully undoable.
- Reuse disposal paths such as `disposeObject` when replacing scene objects. Clone before reflection to avoid contaminating shared resources. Define lifetimes for geometry, materials, textures, and caches.
- Preserve accessible names, form labels, focus behavior, and desktop workflows when changing UI. Update affected tests if DOM IDs, `data-*` attributes, or text change.

## Domain, geometry, and format boundaries

### Projects and structures

- The project format is `anymaker-web-project` v1. `migrateDocument` handles known v0 migration and must reject unknown versions. Schema changes require corresponding validation, migration, serialization, tests, and `doc/03_XML_AND_NATIVE_FORMAT.md` updates.
- Current editor validation limits projects to 2,000 components, position/rotation magnitudes to 10,000, and scale to `(0, 100]`. These are editor limits, not verified game limits.
- Persist rotations as XYZ Euler radians; Inspector may display degrees. Do not mix units. Complete mapping of game coordinates, grids, and parent transforms still needs evidence.
- Mesh parts/render submeshes, dynamic meshes, and vehicle `Grid` are different concepts. Native nodes, beams, and plates live at vehicle level; editor projection does not make them inherently belong to one grid.
- Current split/merge operations primarily change component `gridId`; they are not complete topology transactions, welding, or coordinate conversion. Consult `doc/05_BUILD_OPERATIONS.md` before extending them.
- Mirror with explicit `mirror` metadata, positive scale, and correctly reflected vertices, normals, and winding. Negative scale or ordinary rotation alone is insufficient. Port, joint, and handedness mappings remain unfinished.

### Native data and XML

- `.data`/`.meta` samples are JSON. Project JSON, domain models, and native schemas are separate layers.
- Native adapters preserve unknown fields, omitted values, and raw data. Do not guess editor scale or Euler values. Write-back remains experimental; arbitrary edits are not guaranteed lossless.
- Intermediate XML must retain `game-compatible="false"` and its non-game-save explanation. Escape attributes and text. There is no intermediate XML importer, and six-decimal output is not lossless.
- Without actual game loading, field mapping, and comparison evidence, do not label exports game-compatible or diagnostic materials visually faithful to the game.

## Published resources and offline generation

The runtime pipeline is component index -> lazy details/bindings -> manifest -> corresponding gzip Mesh -> Three.js instance. Keep the index lightweight and Mesh resources separate; do not inline the entire asset collection into JavaScript or load it all on the first screen.

- Build resource URLs from `import.meta.env.BASE_URL`. Production base defaults to `./` and can be overridden by `VITE_BASE`. Do not hardcode the site root; support Pages subpaths.
- `public/data/` and `public/assets/` are publishing inputs, not disposable caches. Change extraction/conversion logic before regenerating affected outputs; do not manually alter compressed files, fabricate hashes, or update only a manifest.
- `mesh.js` supports v5 16/28/36-byte vertex layouts. Preserve part boundaries, metadata, bounds, packed color, normals, UVs, and indexes. Reject unknown layouts, truncation, nonfinite values, and out-of-range indexes explicitly.
- Published assets include an opaque native variant. Keeping raw bytes does not make it renderable. Use the manifest and `doc/evidence/asset-audit.json` for support counts; do not remove failures to improve statistics.
- Manifest source paths, source/output hashes, formats, compression parameters, and parsing status must be traceable. `check:assets` verifies output hashes; browser comparison of hash fields does not itself recalculate downloaded-file integrity.
- Support both servers that decode gzip and those returning compressed bytes. Report loading failures; never substitute an invented model while claiming success.

Run these only when the task needs them, local-resource reading is authorized, and the ROM is available. Routine frontend work does not require the installation.

| Command | Inputs and outputs |
| --- | --- |
| `node scripts/extract-catalog.mjs <Anymaker/rom>` | Definitions/translations to two component indexes and per-component detail/binding files |
| `node scripts/build-published-assets.mjs <Anymaker/rom>` | Bindings to converted static/dynamic Mesh assets and manifest |
| `node scripts/audit-assets.mjs <Anymaker/rom>` | Scan ROM and starter vehicle, hash the parent `game.exe`, and write `doc/evidence/asset-audit.json`; never execute the game |

After generation, run `npm run check:assets`, inspect expected differences, and add parser/browser checks appropriate to the change. Scripts depend on the current directory; run from the repository root. Never put developer-specific drive letters or paths into production resources.

## Safety and repository maintenance

- Treat JSON, native files, Meshes, resource paths, and user input as untrusted. Validate types, versions, counts, finite values, unique IDs, and reference integrity before changing state or allocating large buffers.
- Do not use `eval`, dynamic execution, or unsafe deserialization for imports. Prevent prototype pollution and oversized inputs/decompression. Prefer `textContent` for names and errors, and escape HTML/XML correctly.
- Restrict resource paths to intended static directories; reject traversal and arbitrary remote URLs. New proxies/download features must validate protocols, targets, and redirects. Internal-network access requires authorization; without it, block common private ranges and the recorded `9.*`, `10.*`, `11.*`, `21.*`, and `30.*` ranges.
- Credentials come only from environment variables, never source, samples, logs, or Git. Browser `VITE_*` values are public configuration and cannot contain secrets.
- Keep documentation in `doc/`, with entry points, TODO, and this guide at root. Cite source files, scripts, or tests for research conclusions; do not paste large binary blocks into documentation or code.
- Keep local game copies, experiments, and exports in ignored locations such as `local-assets/`, `local-data/`, `game-dumps/`, `asset-cache/`, and `exports/`. Never commit a complete ROM or game executable.
- Preserve approved published assets, lockfiles, fixtures, and evidence summaries. Do not globally ignore `.mesh`, `.data`, or `.xml` extensions that may be legitimate fixtures.
- Do not commit `node_modules/`, build output, reports, caches, or credentials. Do not delete `.codebuddy/` project data. Commit, push, or deploy only when authorized; the current research assignment authorizes dedicated-branch research publication, and the user's language correction also authorizes English documentation/instruction fixes on main. Deployment and releases remain unauthorized.

## Anymaker creation acceptance (2026-10-11)

For user-requested native creations, first read `doc/18_BUILD_ASSURANCE.md` and `doc/19_EXPERIMENTS_2026-10-11.md`.

- Design the complete functional chain before placing geometry. Use only components/interfaces supported by game definitions, native examples, user tests, or explicit documentation.
- Distinguish verified, inferred, and unknown behavior. Default to one rigid chassis while retaining necessary joints, rotating parts, and mounting frames. Grid count is not physical-body count.
- Audit structural mounting separately from electrical, torque, mechanical-control, data, liquid, and gas connections. Contact, intersection, or visual alignment does not prove connection.
- Prefer direct controls and verified mechanical arrangements. Microcontrollers need a necessary purpose, complete I/O, endpoints, and defaults.
- Check motion clearance, power transmission to loads, and off/neutral/forward/reverse/power-loss states. Do not fabricate exact safe limits for unknown loads.
- Record geometry, connections, static checks, game loading, and operation separately for each delivery. Unperformed checks cannot be marked PASS.
- The user authorizes reading specified Anymaker files and creating project diagnostic tools. Original-file modification, deletion, irreplaceable-file overwrites, patching, injection, memory changes, and mods still require explicit approval. Authorization does not create unavailable tools.
- Back up major creation/development changes. Public Git should contain necessary evidence only, omitting personal paths and account data.

## Accumulated engineering knowledge (2026-10-16)

Read [doc/knowledge/README.md](doc/knowledge/README.md) and [doc/knowledge/CURRENT-FACTS.md](doc/knowledge/CURRENT-FACTS.md) before engine, vehicle, or microcontroller work. This archive covers October 11-16, including accepted CPE1Running, large-engine fluid-direction correction, and positive-only pneumatic selectors. Later verified findings supersede explicitly historical assumptions. Preserve browser-editor acceptance boundaries.
