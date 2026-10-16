# Downloaded Workshop examples

Copied 33 installed Anymaker Workshop creations from Steam's `steamapps/workshop/content/4435340` into `output/workshop-examples/`. Each numeric ID folder preserves `vehicle.data`, `vehicle.meta`, and `workshop_preview.png` byte-for-byte. `integrity.json` records source paths and hashes: all 99 copies match and all originals remained unchanged.

Browse `output/workshop-examples/index.html` for previews and component summaries. `index.json` contains audits, component counts, Workshop links and embedded scripts. Author titles are not stored locally and remain unverified, so IDs identify examples. Script text is data only; none was executed.

All 33 pass the current offline error checks, with warnings requiring review. In-game functionality was not tested. Sixteen builds contain 36 embedded script fields.

## Selected study examples

| ID | Verified contents | Study purpose inferred from data |
|---|---|---|
| 3806342313 | 29 components; motor, differential, torque interfaces, stepper, controller | Compact reverse-toggle controller |
| 3806831263 | 34 components; motor, controller, stepper; pressure/switch script | Conditional motor reversal and actuator control |
| 3804792002 | 137 components; rotor, engine, gearbox; two scripts | Fuel fraction, engine temperature and altitude displays |
| 3803978986 | Eight bodies; 400 components; tracks, motors, data/electric interfaces; four scripts | Hydraulic steering, motor speed, speedometer, battery gauge and odometer |
| 3803945559 | Fifteen bodies; 440 components; liquid interface; eleven scripts | Complex assembly and controller arrangements |
| 3804435424 | 49 components; jet engine, manifold, nosecone gearbox, torque interfaces | Compact jet-system inventory |
| 3804938753 | Four bodies; medium engine/gearbox, tracks, electric interfaces; three scripts | Larger drivetrain and controls |

## Lessons for the toolset

Real scripts confirm saved `on_tick`, `define var`, `out NAME.channel`, and `in NAME.channel` syntax. Examples include `if`, `elseif`, booleans, conversions, absolute value and persistent variables. Embedded source gives us realistic fixtures for further analysis.

Scripts route sensor readings directly to displays, supporting investigation of an internal instrument panel. This does not establish external telemetry. Several files have separate bodies and cross-body interfaces, so future attachment and drivetrain analysis must respect vehicle boundaries.

One odometer script divides by 60 per tick. That is an author assumption, not proof of the game's tick frequency. Thresholds, constants, component names and units must be verified before reuse. Community examples write `is_reverse`, whose descriptor omitted a type in the installed definitions; intended usage is visible, but runtime semantics remain untested.

## Reusable importer

```powershell
python toolset/workshop_index.py "C:\Program Files (x86)\Steam\steamapps\workshop\content\4435340" --out another-workshop-snapshot
```

The importer copies only the three known assets in numeric item folders, indexes the copies, audits them and generates a local gallery. Outputs stay in `toolset/output/`; existing files are refused. It does not subscribe, install content or modify Steam files.

To repair a missing HTML gallery after a partial run without recopying originals:

```powershell
python toolset/workshop_index.py toolset/output/workshop-examples/index.json --out workshop-examples --render-index
```

Preview asset folders must remain alongside the gallery. Workshop links preserve source attribution; no online titles or performance claims have been added.
