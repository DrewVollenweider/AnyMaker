# Liquid-network scheduling, topology and multi-source transfers

Build 26113663; researched offline on 2026-10-22. GCL SHA-256: `a3fd2df2fd62e38b629f6a0df824269a34d77d57caf66d596362d7e5e53c3b22`. The installed executable, GCL and 2,968 cataloged definition files were checked against the isolated baseline. The game was not executed or attached to, and installation files and active saves were not edited.

The latest traces connect the previous [engine and supply findings](ENGINE-SUPPLY-20261022.md) to network scheduling and liquid redistribution. A direct liquid-content transfer limits actual movement by destination room. The network group pass uses a different application path: it calculates several incoming candidates against the same destination room and then applies them without an aggregate destination-room normalization in the reviewed loop. A bounded analytical reconstruction can therefore exceed destination capacity while conserving the quantities transferred. This is a source-derived counterexample, not an observed running creation or a complete network simulation.

## Evidence and review boundaries

Two new batches provide 26 methods. Twenty-four complete approximate C bodies have been read; gas-node `pre_build` and mechanical-node `pre_build` are available but their full bodies remain pending review. Approximate C is interpreted with original instruction bytes, operand metadata and reflected field layouts; it is not recovered original source or a complete ABI.

The combined current-build reader has 95 methods, 23,570 checked instructions and 141,171 instruction bytes. Those counts include earlier batches and do not mean all 95 methods are fully understood. The archived build-25904830 reader remains separate.

- [Selected evidence](versions/build-26113663/liquid-network-20261022/evidence.json): 24 reviewed method identities, two explicitly pending identities, 20 typed scalars, two property-key strings, 47 selected call sites, 34 selected instructions, seven layouts and three analytical examples.
- [Verification](versions/build-26113663/liquid-network-20261022/verification.json): source checks, reader totals, test results and limits.
- [liquid_network_pass.py](../../../scripts/research/liquid_network_pass.py): a model of one eligible group visit with resolved ports, explicit cached heads and distinct contents.
- [Eight tests](../../../scripts/research/test_liquid_network_pass.py), including 300 seeded conservation cases. The complete research-tool suite passes 302 tests. These tests validate bounded tools and models, not gameplay acceptance.

Full decompilations, assembly exports, binaries and databases remain local. The evidence contains selected excerpts and identities only.

## Connection building precedes component updates

Current `vehicle.container.tick` calls `connections_manager.build` before iterating vehicle updates. The reviewed connection-building order is:

1. Clear the manager's available-component lists and register connections from dynamic components.
2. Run torque flood rebuilding across vehicles.
3. Run every vehicle's `pre_build`.
4. Run every vehicle's `build`.
5. Run cross-body manager builds: mechanical, electric, liquid, gas and data.
6. Run every vehicle's `post_build`.
7. Return to the container, which runs vehicle updates and later empty-vehicle cleanup.

Vehicle `pre_build` dispatches mechanical, electric, liquid, gas, torque and data passes. The reviewed vehicle `build` calls the torque-node build with the physics mass or its fallback. Vehicle `post_build` dispatches electric, liquid, gas, torque and data passes.

In the ordinary non-pending branch, vehicle update cleans removals, handles requested graph/physics/buoyancy/constraint work, then ticks dynamic components sequentially. This establishes relevant ordering; it does not establish creation-ID, geometric or wire-length priority, nor an immutable order after loads and splits.

Liquid head is cached during network preparation, before the later component updates that change pump or manifold state. A component can see state written by an earlier component, but that does not mean cached network head has already been recomputed. Do not turn this into a universal one-frame-delay rule: the relevant producer, consumer and graph passes must be traced separately.

## Liquid head and graph preparation

Liquid-node `pre_build` resets node height and flow, stamps the vehicle index and, for non-null contents, computes a head-like value. The reviewed path transforms content bounds to world space with half-grid expansion, interpolates world-space height using fill factor, adds node static pressure and adds positive overfill.

This network head differs from the direct liquid-content `get_pressure` helper, which returns positive overfill or zero. Neither path alone recovers pressure in pascals, bar or psi. Pump chamber pressure, component bias and network head must retain their separate meanings.

When rebuilding dirty topology, the code splits existing island groups, clears local islands, resolves each valid node's mounting grid, extended grid position and transformed facing normal, then looks for a direct pair. The reviewed pair requires:

```text
same mounting grid
position_A + normal_A == position_B
normal_B == -normal_A
```

The scan does not break immediately after a match; multiple coincident candidates can overwrite pair indices. This is a review boundary, not a general claim that overlapping placements are accepted by the game.

The island flood assigns an unvisited node and records it. If that node has a direct pair, it follows that pair instead of scanning explicit saved liquid links at that node. Otherwise it follows saved link endpoints using component ID and node index. A non-null internal-flood component then supplies additional nodes through its virtual `get_liquid_flood_nodes` method.

Consequently, spatial pairing, saved service links and component-internal flooding are distinct mechanisms. The reviewed graph does not automatically weld every overlapping port. All component-specific internal-flood variants and malformed endpoint behavior are not closed.

## Cross-body grouping and visit cadence

The reviewed liquid and gas connection-manager builds run when their dirty flag requests rebuilding. When two different island groups connect, they merge group references and cached totals and repoint island group references. These manager merge bodies do not directly transfer fluid in the reviewed paths.

Liquid preparation resets local group volume and capacity caches. Liquid `post_build` loops local island references and enters its transfer work when the referenced group's cached total volume is zero, flattening nodes from all islands in that group. The reviewed liquid body does not accumulate the group totals in the way gas `post_build` does.

This matters across shared groups: do not assume exactly one eligible liquid-group visit per update. References from multiple islands or vehicles may revisit a merged group. Complete execution counts, side effects, aliases and exceptional lifecycle states remain open. The model below represents one visit only.

## One liquid-group visit

The collected nodes are sorted by ascending cached head. The reviewed adjacent-swap condition is strictly less, so equal heads retain their input order. Collection order itself is not established as a stable user-controlled priority.

For each destination in ascending order, the code first calculates candidates from all later, higher-or-equal-head entries with non-null contents:

```text
candidate_j = min((head_j - head_destination) * 2 * 0.01,
                  current_source_volume_j)

if destination is not expandable:
    candidate_j = min(candidate_j,
                      destination_capacity - current_destination_volume)
```

All candidates for that destination are calculated before any is applied. Each therefore sees the same current destination room. Their sum gates whether the application loop proceeds; the reviewed application loop does not normalize that sum to the available room.

For a nonempty source and nonzero stored candidate, the application path calculates the candidate divided by current source volume, moves that fraction of every species, adjusts both cached totals, records opposite signed port flows and blends destination temperature by moved volume over its new total. It does not call the capacity-limiting direct liquid-content transfer helper here.

The distinction is visible in a small analytical example:

| Port | Cached head | Initial volume | Capacity |
| --- | --- | --- | --- |
| Destination | 0 | 0 | 0.1 |
| Source A | 10 | 1 | 1 |
| Source B | 20 | 1 | 1 |

Each incoming candidate is limited to 0.1 by the same destination room. Applying both gives the destination 0.2, exceeding its 0.1 capacity. Later transfers between the other ports do not remove that result from this lowest-head destination. Total volume and each species remain conserved in the bounded model.

This demonstrates why a capacity guarantee for the direct two-content helper cannot be promoted to a whole-network guarantee. It does not prove that a particular accepted creation reaches the example's cached heads and topology, nor certify every native exceptional state.

Other consequences within the modeled domain:

- Lower-head destinations can consume stock before later destinations are processed.
- Equal-head ordering can affect which destination receives limited stock first.
- Equal head produces no candidate even when fill fractions differ; this pass is not simple capacity-weighted equalization.
- An expandable destination skips the individual destination-room cap.
- The coefficient 0.02 belongs to the per-visit candidate calculation. No delta-time or pipe-length operand appears there. It is not a universal litres-per-second rating.

## Gas redistribution uses a different cache path

The fully read gas `post_build` first sums content volume and capacity when its group volume cache is zero. Positive aggregate capacity permits a target pressure calculated from aggregate volume divided by aggregate capacity.

The reviewed path creates temporary gas contents, collects excess from nodes whose cached pressure exceeds the target, and supplies deficits where cached pressure is lower. Excess requests use source volume times the relative pressure difference; deficit requests use target pressure times content capacity minus content volume. Signed node-flow fields record the requests around the transfers.

Unlike the reviewed liquid body, this gas body accumulates group totals before processing, so subsequent cache-gated visits can skip a nonempty group. The liquid 0.02 coefficient does not appear in this gas redistribution calculation. Complete gas preparation, the temperature helper, shared-content aliases, empty cases and wider dispatch remain open; these selected findings do not close the gas network.

## Pump flow setting is now calibrated

The gas and liquid pump creation wrappers do not initialize `flow_factor` in the reviewed bodies. Their save parsers resolve that missing calibration: both use the key `flow_factor` with default **1**. Their property builders expose a percent value with minimum **0**, maximum **1**, and step **0.1**, corresponding to 0-100% in ten-percentage-point steps.

This field is a flow setting, not internal chamber volume. The declared UI range does not prove arbitrary edited saves are clamped to that range. The reviewed property-update methods handle alias changes by requesting connected-controller rebuilding; they do not establish another flow-factor rewrite.

Pump creation also derives shaft-node parameters from definition wattage, the torque conversion coefficient and server rate. That construction relationship alone is not an actual electrical-draw measurement.

## Model domain and next questions

The new model accepts finite cached heads, four nonnegative species amounts, positive capacity, finite temperature, initially non-overfull contents and explicit expandable flags. Every port represents distinct contents. Input guards define this tool's scope; they are not claimed restrictions of the game.

Eight tests cover mixtures, the multi-source capacity counterexample, stock priority, equal-head stability, expandable contents, equal-head non-equalization, input preservation and 300 seeded cases preserving species, total quantity and the volume-weighted temperature moment. That last invariant is not physical heat-energy conservation for arbitrary liquid mixtures.

The model excludes null contents, shared-content aliases such as engine manifold ports, initial overfill, geometry, graph discovery, pump execution, native math contracts and group revisit cadence. It is not a creation validator or a complete fluid solver. In particular, the per-source capacity example should not be generalized to exceptional negative/overfull candidate arithmetic.

Next research remains vehicle-focused: finish gas and mechanical preparation, close shared-content and group-visit behavior, then revalidate electrical allocation, generation and controls. Other engines and gearbox variants, creation mass and geometry, full structural validity, flight and marine chains remain unfinished. Combat, projectiles, explosions and AI remain parked. The full audit is incomplete.

Continuation, 2026-10-22: [electrical storage and controls](ELECTRIC-CONTROLS-20261022.md) completes the full-body review of gas-node and mechanical-node preparation that was pending at this checkpoint. Gas preparation suppresses cached pressure for nonpositive capacity, while the direct gas-content helper has a zero-only guard. Electrical storage registration also exposes shared-content accounting boundaries; the distinct-content liquid model remains explicitly scoped.
