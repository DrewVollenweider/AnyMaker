# Interface identification colors and local materials

## Verified asset facts

Evidence comes from repository-published gzip Meshes, definitions/bindings, and loading regressions. This investigation did not reread or regenerate ROM assets.

- Part names are not material-region boundaries. For example, `wheel_hub_a_base.mesh` has one `mechanical_surface_f` part containing both body and interface.
- `mechanical_bracket.mesh` and `gear_box_a.mesh` contain interface colors but parts are named `mechanical_bracket` and `small_engine_mating_surface`. Broader name matching cannot solve missing colors.
- RGBA [153,0,0,255] appears on motor housings and various interface frames; it cannot universally mean liquid-interface red. Motors also have a large [153,37,0,255] body region.
- Standalone-interface bindings include `cable_end_a.mesh` / `cable_end_b.mesh` with `addComponentTool: false`. Unconditional assembly covers their front identification colors; actual browser screenshots reproduced the occlusion.
- Gas gold also occurs on instrument scales/buildings. RGB equality alone does not identify an interface.

Actual published-Mesh identification-color triangle counts below are loaded/asserted by `tests/unit.test.js`, not substitute handmade geometry.

| Mesh (`meshes/components/`) | Identification color | Triangles |
| --- | --- | ---: |
| interface_electric_a.mesh | #ff3131 | 132 |
| interface_data_b.mesh | #1860ff | 18 |
| interface_gas_a.mesh | #997100, #cc9900 | 48 |
| interface_mechanical_f_a.mesh | #1e9999, #ffcc31 | 38 |
| wheel_hub_a_base.mesh | #1e9999, #ffcc31 | 48 |
| mechanical_bracket.mesh | #1e9999, #ffcc31 | 32 |
| gear_box_a.mesh | #136666, #1e9999, #ffcc31 | 32 |
| engine_block_a_0_0_0.mesh | Dark teal torque-mating ring #136666 | 16 |
| manifold_pipe_c_straight.mesh | #ff3131 | 6 |
| air_manifold_a.mesh | #1e9999, #ffcc31 | 16 |

## Implementation

`src/assets/mesh-interface-colors.js` groups triangles by the confirmed RGBs at loading. All three vertices must belong to identification colors for a protected interface material; mixed triangles with ordinary body vertices retain the body material.

- Bodies retain paintable neutral diagnostic material; interfaces multiply white material base by local vertex color.
- Vertex colors convert sRGB to Three.js linear input. Original RGBA remains in `gameColorBytes`; parse caches are untouched.
- Gas colors apply only to confirmed `interface_gas_a/b.mesh`, not similar instrument/body colors.
- Local and published Meshes share implementation. Painting/submesh views skip interfaces by **material**, not entire mixed Meshes.
- Published assembly excludes only the two explicitly `addComponentTool: false` cable ends in standalone `interface_*` classes. Wheel-hub suspension and other dynamic Meshes still assemble; this default is not globally filtered.
- Grouping occurs only on instantiation, with at most two draw groups per affected part: no frame-by-frame scan, helper spheres, or per-face materials. Mirror clones preserve groups/colors; disposal uses `disposeObject`.

## Regression and limits

- Real published-file unit tests cover both loading paths, unchanged original colors/indexes, body/interface isolation, gas/instrument distinction, mirroring, and material disposal.
- Assembly tests confirm standalone interfaces are not obscured by unconditional cable ends and wheel-hub dynamic assembly remains present.
- `native interface colours` in `tests/browser/editor.spec.js` imports real components, reads red/blue/teal/yellow WebGL framebuffer pixels, captures front/back screenshots, and checks painting, undo/redo, local mirroring, submesh view, and display after leaving connection tools.
- Published vertex channels for liquid and some standalone torque interfaces lack these identification-color regions. They retain diagnostic materials; dark-red housing channels are not forced into interface colors. This does not establish absence of other game materials/shader rules.
- No claim of complete game materials, all native dynamic connection states, or 1:1 game rendering. Unsupported packed-color/material-slot interpretation remains open.

Actual checks at this historical checkpoint: 136 unit tests and 48 editor browser cases passed. Asset checks passed (797 referenced Meshes, 865 manifest entries, one retained opaque native variant). Browser tests first built the Pages subpath into temporary `dist`, without changing committed `docs` publication output. Front/back screenshots were visually inspected. No game loading or 1:1 comparison was performed.
