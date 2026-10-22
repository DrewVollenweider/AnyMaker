# Functional mating, storage ports and drivetrain variants

Build 26113663; researched offline on 2026-10-22. GCL SHA-256: `a3fd2df2fd62e38b629f6a0df824269a34d77d57caf66d596362d7e5e53c3b22`. Installed GCL, executable and 2,968 cataloged definition files match the isolated baseline. The game was not executed or attached to, and installation files and active saves were untouched.

The preceding [electrical/control checkpoint](ELECTRIC-CONTROLS-20261022.md) exposed shared-content accounting boundaries. This continuation traces functional mating and finds that two separate resolved battery-face candidates can satisfy the local mating predicates without their explicit voxel boxes overlapping the battery or each other. Full placement, collision, authority and valid shared-storage reachability remain unproven. This is a narrower result than a usable creation certificate.

The same continuation freshly reviews electric motors, clutches, fixed-ratio gearboxes, differential link changes and the shared shaft solver. An unexpected differential branch is retained as an exact internal-link trace; conventional open/locked differential behavior is not assumed.

## Evidence and tools

Six new export batches provide **39 methods**, all read in full as approximate C. Five previously reviewed current-build methods are reused. The combined current reader now contains **179 methods, 36,031 checked instructions and 207,688 instruction bytes**. Counts include previous batches and are not a measure of whole-game understanding.

- [Selected evidence](versions/build-26113663/mating-drive-20261022/evidence.json): 44 method identities, 51 typed scalars, selected strings, 33 call sites, 45 instruction examples, 12 reflected layouts/enums and selected fields from 12 component definitions.
- [Verification](versions/build-26113663/mating-drive-20261022/verification.json): source checks, review counts, model checks and limits.
- [surface_mating.py](../../../scripts/research/surface_mating.py): functional mating with explicit, already transformed cardinal bounds in a shared mounting grid.
- [Ten tests](../../../scripts/research/test_surface_mating.py), including an independent 2,304-case interface-pair oracle and 300 translation/symmetry cases. The full research-tool suite passes **327 tests**.

Approximate C is checked against original bytes, reflected fields and selected assembly; it is not recovered original source or a complete ABI. Full game exports and databases remain local. These are offline implementation findings and analytical examples, not new gameplay tests.

## Functional mating has additional requirements

The older [structural attachment work](VEHICLE-ATTACHMENTS-20261021.md) distinguished support from service connectivity. The current functional path checks interface type, gender and, for generic ports, component port compatibility in addition to geometry.

The server grid's mating builder iterates a component's definition surfaces, resolves each surface's extended and rotated bounds, finds adjacent mating surfaces, and invokes `add_mating_component` on both components for each accepted match outside the supplied exclusion list. The reviewed loop does not stop after the first matching component.

The finder clears its output, shifts the query bounds by one voxel along the query normal and gathers octree candidates. It requires the same mounting-grid origin/direction, then tests the candidate's transformed definition surfaces. Candidate gathering, interface compatibility and structural support are separate steps.

The declared cardinal directions are X-negative, X-positive, Y-negative, Y-positive, Z-negative and Z-positive, numbered 0-5. The current direction helpers return their axis normals and opposites. Model inputs use only these declared ordinary directions; invalid-enum fallback behavior is not generalized.

For ordinary resolved surfaces A and B, the reviewed mating predicate requires:

1. Opposing directions.
2. Compatible interface types and genders.
3. Inclusive overlap between B's bounds and A's bounds shifted one voxel along A's normal.
4. The applicable containment rule below.

| Genders and interface case | Additional geometry after overlap |
| --- | --- |
| Neither surface has gender | Overlap is sufficient in this branch |
| A male, B female | B must encompass shifted A |
| A female, B male | Shifted A must encompass B |
| Male generic `port` against the permitted empty-type, genderless counterpart | The counterpart must encompass the plug; argument order is handled in both directions |

Both overlap and encompassing comparisons include their boundaries. A male footprint merely touching or partially overlapping a socket is insufficient if the whole footprint is not contained.

The generic type/gender helper normally requires matching type strings and a none/none, male/female or female/male pairing. It has special branches for a male `port`: a female `port` or an empty-type genderless counterpart must also have a nonempty intersection of the two component definitions' allowed-port bitsets. The reflected port-type labels include electric, data, liquid, gas, air, fuel, exhaust, oil and coolant.

The analytical model uses explicit integer masks and ordinary bit intersection for that bitset operation. Complete native bitset representation, parser conversion and ABI recovery are not claimed by the model.

## Surface bounds and omitted fields

The current surface constructor initializes size to **1 by 1**, direction and gender to **0**, and strings to empty; its position field invokes the vector constructor. These constructor observations are not a complete generic JSON-default parser contract.

The freshly read surface-bound helper retains the earlier axis arrangement: X-facing sizes span Z/Y, Y-facing sizes span X/Z, and Z-facing sizes span X/Y. Inclusive maximum coordinates use size minus one. Extension tests use physical half-voxel bounds and the **0.25-voxel** deadband around stretch center. The component wrapper rotates and translates both resulting corners, then orders coordinate minima and maxima.

The new mating model takes resolved bounds directly. It does not parse omitted fields, reproduce the octree, resolve rotation constraints, certify structural attachment or emulate s32 overflow. Saved omissions remain omissions in the evidence rather than being silently rewritten as defaults.

## What this establishes about battery ports

Both shipped battery component definitions have several female `port` surfaces and allowed-port value **3**. The two shipped electric-port variants declare a male `port` face and allowed-port value **1**. The selected definitions retain their original source/JSON Pointer identities and omissions.

Electric-port creation registers its electrical node. Its mating callback records the component attached through a surface whose type is `port`; the removal callback clears that pointer when it matches. The grid builder invokes the battery-side callback too, which was traced in the preceding checkpoint to node-group registration with the battery's one stored-content pointer.

The resolved geometry model checks a female face on each opposing X side of a two-voxel-wide battery-shaped box and a one-voxel plug outside each side. Both local mating tests pass; the explicit plug voxel boxes are disjoint from the battery box and each other. This is a mathematical witness for the reviewed local predicates. It does not establish the entire client/server placement process or loading a native creation with that arrangement.

The reviewed mating/registration paths therefore provide no basis for assuming that battery contents always have only one registered port reference. Equally, the local witness does not prove the previously documented repeated-reference accounting states are reachable in an accepted, operating vehicle. Remaining work includes placement overlap/attachment gates, allowed rotations, callback lifecycle, graph merging and representative saved-state reconstruction. No exploit creation or active-save change was made.

## Electric motors: target tracking and demand

The current shipped motor definitions declare **10,000, 60,000 and 120,000 W**, each with a maximum target of **30 RPS**. Their creation method initializes target RPS to the definition maximum and derives shaft-node mass from definition wattage, the torque conversion coefficient and server rate.

Update clamps target to the positive/negative definition limit and the data power factor to 0-1. The saved reverse flag and data reverse flag combine by inequality: differing flags invert the target; matching flags preserve its sign.

```text
demand = clamp((signed_target - shaft_rps) / maximum_rps, -1, 1)

if target >= 0 and shaft_rps > target:
    demand = 0
if target <= 0 and shaft_rps < target:
    demand = 0

requested_energy = definition_wattage * output_power_factor
                   * data_power_factor * dt * abs(demand)
```

The accepted electrical fraction scales reported consumption and the applied signed shaft quantity. In the positive-supply branch, the motor also writes shaft gear and clutch factors to 1. The reviewed tick does not establish every transition of those factors when supply disappears.

At zero target, either nonzero direction of shaft rotation is beyond the target in its direction, so this demand branch becomes zero. It does not establish regenerative braking. For a 30-RPS target, an actual 40 RPS also yields zero demand in the reviewed branch. Full braking behavior must follow actual brake components and the shaft network.

The output-power property is separate from the data power factor. Its UI declares **10-100% in ten-percentage-point steps**, with saved default **100%**. The reviewed runtime clamp applies to the data factor; the property UI range alone does not prove arbitrary edited saved output factors are clamped.

These current traces support the scoped motor arithmetic already in [powertrain_models.py](../../../scripts/research/powertrain_models.py), alongside fresh current-build constants. This is a bounded rule recheck, not a declaration that all archived powertrain behavior transfers unchanged.

## Clutch and fixed-ratio gearbox

The clutch creates two shaft nodes and an internal link. Its update passes mechanical input through the previously calibrated boolean threshold helper. Either sign beyond the strict outer magnitude threshold can set `m_is_disengaged`; release occurs inside the open central interval. On a state change to disengaged, it disconnects link 0; on a change back, it reconnects node 0 to node 1.

The reviewed control is therefore thresholded link switching. A proportional clutch factor is a separate shaft-solver field and is not what this component's input helper writes in these methods. This distinction matters when selecting controls for a vehicle.

The fixed-ratio gearbox's update assigns:

```text
link_ratio = output_factor / input_factor * (reverse ? -1 : 1)
```

A changed ratio requests shaft-network rebuilding. Its save parser defaults each factor to **1**; its property UI declares integer factors **1-8**. UI range and save defaults do not close malformed saved states, zero divisors or every mating/load case. Ratio sign in the internal graph must also be distinguished from the final physical rotation after other connection inversions.

## Gearbox C inheritance

Current reflection declares gearbox C as a subclass of gearbox B, with no additional fields. Its selected virtual declarations use B's update and gear-count methods. The already reviewed B count remains clamped from 2 plus local Z extension to 2-8 at that scope.

C's freshly read mating override connects torque nodes, registers pneumatic port groups, registers data ports, and records a mated component when the relevant surface type is `torque_engine_c`. The shipped C definition contains that large-engine mating surface. A missing C-specific update function is therefore consistent with inheritance, rather than evidence that the component lacks shifting logic.

This closes that selected inheritance question. Complete C construction, every allowed extension/rotation, pressure topology, ratios and whole-vehicle acceptance still require their own checks.

## Differential: exact internal-link trace

The reviewed differential creation path looks for a surface ID `out`. Without it, the component creates three nodes named `in`, `left` and `right`, with two links. With it, it creates an additional `out` node and a third link.

| Link | Created endpoints | Created ratio |
| --- | --- | --- |
| 0 | in (0) to left (1) | -(output_factor/input_factor) |
| 1 | left (1) to right (2) | -1 |
| 2, when an `out` surface exists | in (0) to out (3) | -1 |

The update feeds mechanical input into the boolean threshold helper using the reflected field named `m_is_locked`. When that state changes to true, the reviewed branch disconnects links **0 and 1**. When it changes to false, it reconnects those links to their original endpoints. It also refreshes link 0's negative output/input ratio when changed. The two numeric factors default to 1 and have UI range 1-8.

This state change is counterintuitive if interpreted as a conventional differential lock. The report retains the actual branch rather than substituting a conventional mechanism. `disconnect_link` writes **-1** to both endpoint indices and requests rebuilding; the freshly read shaft flood rejects links with negative or out-of-range indices. The optional third link is not disconnected by those two calls.

Thus the reviewed internal lateral paths are disconnected when the field named locked becomes true. Whole-vehicle motion can depend on additional external connections and lifecycle state. Intended lock semantics, complete differential behavior under load, all control bindings and runtime acceptance remain unresolved. No generic open/locked driving guarantee is inferred from the component name or description.

## Shared shaft solver recheck

Current shaft graph flooding follows adjacent nodes, valid internal links, registered cross-body connections and recognized belt paths. Adjacent and cross-body propagation invert the accumulated ratio. Internal links multiply forward and divide backward. Nodes already assigned to an island are skipped; inconsistent ratio cycles and belt geometry remain separate questions.

The build pass consumes pending speed delta, applies retention **0.9998** and clears that delta. When a nonzero vehicle-mass factor is present, node mass is derived from the supplied vehicle mass, with a positive maximum limiting the vehicle-mass term before multiplication by the factor.

For already established islands, the current post-build rechecks the earlier arithmetic:

```text
q = node.gear_ratio * node.island_gear_ratio
w = node.mass * node.clutch_factor * q^2
P = sum((node.rps * node.clutch_factor / q) * w)
M = sum(w)
P *= product(1 - node.brake_factor)
```

With positive M, each node interpolates toward (P/M) * q using its own clutch factor. The second clutch contribution in P and the multiplication of brakes across the shared numerator remain present. These are game-specific formulas, not a recovered SI inertia/torque model. The model assumes resolved topology and ordinary nonzero ratios; it does not resolve every native physics call.

## Remaining work

The local battery-face witness narrows the shared-storage question without closing full placement or operating reachability. Follow the client/server overlap and attachment gates, callback/port occupancy rules, structural reconstruction and merged-group visits. Continue differential intent/bindings and drivetrain variants, then steering/brakes, creation mass and plate/edge geometry, aircraft and marine systems. Combat, projectiles, explosions and AI remain parked. The full audit is active and incomplete.
