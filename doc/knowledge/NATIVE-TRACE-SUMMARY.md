# Selected native trace findings

These are engineering summaries of inspected native functions, with build-specific record metadata in archive/toolset/output. They are not original game source or a complete formal specification.

1. Pump create/mate path sorts fitted port components by ID. Chamber0 and chamber1 map to distinct saved content offsets; effective speed is shaft speed with the pump reverse flag applied. Positive pumps0→1; negative pumps1→0. Pressure, flow factor, overfill and chamber state participate; no identified50-rps hard cap in the traced liquid-pump tick.
2. Engine inspection reads engine-wheel speed with a sign change. Pulley-to-pump mating introduces another sign change. Follow both before interpreting reverse flags.
3. Engine manifold mating joins oil manifolds to one lubricant volume and coolant manifolds to one coolant volume. Surface number alone does not assign feed versus return.
4. Gas-valve creation calls create_node(type=gas, ordinal=0/1/2). The container resolves an ordinal through the definition's full logic-node list; the resulting saved gas indexes are1/2/3 for this definition.
5. Thresholded input pseudocode: if inactive and (input < -0.75 or input > 0.75), activate; if active and -0.25 < input < 0.25, deactivate. Hence raw opposite signed commands can simultaneously activate otherwise separate valves.
6. Pneumatic gearbox up/down trigger state must reset between changes. Opposing simultaneous commands can negate requested engagement. Positive-only selection fixes the observed case.
7. Gas content initialization derives capacity from inspection geometry and its scale; multiplying a dimensional scale field alone is not a capacity calculation. Pressure depends on contents, geometry/volume and temperature in native conventions.
8. Structural attachment considers supported surfaces/contacts and panel facing. Sharing a vehicle/grid or a network link is not an attachment rule.

Reproduce on the matching version using the source signatures and metadata. Relocate functions and verify hashes after updates. Read the complete current-system trace before copying a numeric constant into a different design.
