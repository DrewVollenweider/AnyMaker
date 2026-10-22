# Electrical storage, mechanical routing and controller power

Build 26113663; researched offline on 2026-10-22. GCL SHA-256: `a3fd2df2fd62e38b629f6a0df824269a34d77d57caf66d596362d7e5e53c3b22`. Installed GCL, executable and 2,968 cataloged definition files match the isolated baseline. No game process was executed or attached to; installation files and active saves were untouched.

This checkpoint freshly traces electrical allocation, settlement and redistribution, storage registration, relay hysteresis, mechanical-control delivery and controller power gating. It also completes the two full-body reviews left by the [liquid-network checkpoint](LIQUID-NETWORK-20261022.md). The full audit remains incomplete, with vehicle systems first.

## Scope and evidence

Six new export batches contain 45 methods, all read in full as approximate C. Gas-node and mechanical-node preparation from the preceding checkpoint were also read in full. The selected evidence therefore contains 47 reviewed identities. This does not claim every method in the combined reader has a closed semantic contract.

The current reader contains 140 methods, 29,559 byte-checked instructions and 172,331 instruction bytes. The archived build-25904830 reader remains separate. Matching bytes, reflected fields and selected assembly checks support the interpretation; unresolved virtual/native dispatch and exceptional arithmetic remain explicit limits.

- [Evidence](versions/build-26113663/electric-controls-20261022/evidence.json): 47 identities, 46 typed scalars, two strings, 29 selected call sites, 117 selected instructions and 12 layouts.
- [Verification](versions/build-26113663/electric-controls-20261022/verification.json): source/version checks, reader counts, model calibration and tests.
- [electric_balance.py](../../../scripts/research/electric_balance.py): one producer redistribution pass and one deferred settlement pass, with explicit resolved contents and optional repeated producer references.
- [Fifteen tests](../../../scripts/research/test_electric_balance.py), including 500 seeded distinct-store cases. The full research-tool suite passes 317 tests. These are analytical checks, not new gameplay acceptance.

Full game exports and databases remain local. The small public evidence set is not a full decompilation.

## Electrical demand is accepted in call order

The current consumption helpers confirm the earlier [electrical-ordering findings](OFFLINE-SYSTEMS-20261019.md). Both require a connected island/group and a positive request in the ordinary finite domain.

Let available be the group's cached total energy, pending its already accepted demand, and remaining = available - pending.

| Helper | Reviewed behavior |
| --- | --- |
| `consume_binary` | Accept the entire request only when remaining is at least the request; equality succeeds. Add it to pending. Otherwise return false. |
| `consume_factor` | With positive remaining, accept min(request, remaining), add it to pending and return accepted/request. Otherwise return zero. |

Allocation is sequential rather than a simultaneous proportional split between consumers. For 10 available units, binary 8 then fractional 8 accepts 8 and 2. Fractional 8 then binary 8 accepts 8 and 0, leaving 2 unused. Component-vector order is not established as a stable creation-ID or geometric priority across all loads and splits.

There is also a diagnostic distinction: the reviewed fractional helper adds accepted energy to the calling node's `m_energy_delta`; the binary helper updates group pending demand without that same node-field addition. A node diagnostic alone is therefore not a universal ledger of all consumption.

## Previous demand is settled before topology rebuilding

Electrical `pre_build` first resets local node energy deltas. For each existing referenced group, positive pending demand and positive cached available energy produce:

```text
fraction = clamp(pending / previous_available, 0, 1)
for each producer-node reference in the group:
    removed = current_contents_energy * fraction
    current_contents_energy -= removed
    node_energy_delta -= removed
```

The group pending, total-energy and total-capacity caches are then reset. Dirty topology rebuilding follows this settlement. For distinct sources with charges 25 and 75, cached available 100 and pending 20, settlement leaves 20 and 60. The divisor is the cached previous available value, not a freshly recomputed sum at this point.

The established scheduling runs connection passes before component ticks. Component consumption reserves budget; a subsequent connection preparation settles that pending amount. This is an update-order statement, not a guaranteed wall-clock latency or a complete proof of every topology mutation.

## Producer sharing targets a common fill ratio

Electrical `post_build` enters its group work when cached total energy is zero. It sums producer energy and capacity per registered producer node. Positive total capacity gives a target fill ratio:

```text
ratio = counted_energy / counted_capacity
need_i = capacity_i * ratio - energy_i
released = sum(-need_i * share_rate_i for negative need_i)
demand = sum(need_i for nonnegative need_i)
```

The application loop recomputes each producer's need against its current contents. A donor changes by need * its share rate. A recipient changes by need * released / demand when demand is positive. Both content energy and the node's energy delta are adjusted.

For distinct contents, ordinary non-overfull stocks and share rates between zero and one, this bounded pass conserves total energy and moves stocks toward the common fill ratio. Recipients share the released amount proportionally to deficits. Recipient share rate does not limit receipt in this reviewed pass; donor share rate controls release.

The base electric-content constructor initializes `m_share_rate` to **0.001**. Battery construction calls that constructor, and the reviewed battery create/load/accessory paths preserve it. Alternator creation explicitly sets its contents' share rate to **1**.

Example with distinct equal-capacity stores: a full store at 100 and an empty one at 0, using the default donor rate, become 99.95 and 0.05 after one modeled pass. No energy was lost. With unit donor share, the same stores reach 50 and 50 in that pass. These coefficients are per eligible pass; no delta-time operand appears in this redistribution arithmetic. Do not convert them into universal charging times.

The share coefficient is consequently not, by itself, a conversion-efficiency loss. Alternator generation has a separate efficiency factor described below.

## Required terminals and shared-content references

`vehicle_electric_node_group.is_fully_connected` checks only whether the registered-node vector has at least `m_required_nodes` entries. It does not inspect available energy or directly prove that those nodes share a powered island. Later consumption helpers check the relevant island/group state.

The default node-group constructor sets required count to **0**. In registration, zero is a sentinel meaning all registered nodes. An explicit positive count selects that many nodes once the count requirement is met.

Group `_create` sorts nodes by component ID, then node index. It assigns the supplied content pointer and internal-flood component pointer to every selected node. `push` rejects an already-present node pointer, releases old assignments, adds the new node and recreates assignments. `pop` releases, removes a matching pointer and recreates assignments. Release clears selected content/flood pointers and requests electrical rebuilding.

Battery construction uses the default group; battery mating passes its one stored-content pointer to that group. Alternator construction explicitly requires **one** node, so its reviewed group creation selects one sorted port. These are registration rules, not a complete certificate for physically valid port placement or all component families.

The electrical flood adds each non-null-content node to the island producer list. The reviewed producer collection and accounting loops do not deduplicate those entries by content pointer. Node-pointer deduplication in `push` is a different operation.

This makes shared-content accounting an important boundary. The indexed model accepts repeated references explicitly rather than pretending that each producer node necessarily represents independent energy.

### Analytical repeated-reference counterexamples

In deferred settlement, one content holding 100 referenced twice can contribute a counted budget of 200. With pending demand 100, the fraction is 0.5. Sequential visits reduce the shared stock from 100 to 50 to 25: actual content loss is 75. This differs from the distinct-store interpretation of a 100-unit accepted request.

In redistribution, a synthetic donor containing 100, capacity 100 and share rate 1, referenced twice alongside a distinct empty capacity-100 recipient, yields counted energy 200 and capacity 300. The application leaves about 66.667 in each actual content, whose distinct total is about 133.333. The repeated donor's second visit sees the first visit's result, while the recipient allocation still uses the earlier pooled accounting.

These are counterexamples to extending the distinct-content conservation proof to repeated references. The unit-share case is an explicit generic model input; it does not claim that an ordinary battery has unit share rate. Valid creation placement, reachable shared groups, complete component restrictions and runtime acceptance are not established here. No creation exploiting these cases was built. The implementation paths expose a question to close, not a demonstrated in-game accounting exploit.

## Batteries and alternators

Electric-content setters assign energy and capacity directly: the one-value overload sets both to that value; the two-value overload takes capacity then energy. The reviewed save parser reads `energy` and `capacity` with zero defaults and does not parse share rate in that body. Wider parser validation is separate.

Battery creation sets zero content. Accessory building and post-load copy the installed battery item's capacity and energy into component contents. Without an installed item, the reviewed accessory-build branch sets both to zero. On update, pending accessory damage zeros energy while retaining capacity, then clears its pending flag. A present battery item receives the component's energy/capacity values, and the accessory update is called.

Battery consumption display is calculated from previous energy minus current energy, multiplied by server rate. That includes net stock changes in this method's sampling interval, not just calls by consumers. Charging can produce a negative value. It should not be interpreted as a pure consumer-only meter without following the whole interval.

Current alternator creation and update confirm the earlier selected generation path. Speed fraction uses absolute shaft speed relative to the definition limit, clamped to 0-1. In ordinary non-overfull storage:

```text
candidate = min(free_capacity, definition_wattage * speed_fraction * dt)
electrical_gain = candidate * 0.75
shaft_feedback = -candidate * torque_conversion * sign(rps)
```

The stored gain and reported power use the 0.75 factor; shaft feedback uses the candidate before that reduction. Full native shaft units, malformed/overfull states and all generator variants remain open. This electrical generation loss is distinct from charge redistribution's share rate.

## Mechanical-control routing preserves raw signs

Mechanical `pre_build` rebuilds routes when dirty. It resolves output/input grid origins, extended positions and opposing normals for direct pairs, follows saved directional links when no direct pair is selected, and asks components for internal mechanical-flood outputs.

Output visitation is guarded during the flood. An input with no internal-flood outputs is treated as a terminal: its `m_pair_count` increments and a source-output/input pair is recorded. After flooding, pairs targeting an input with pair count **greater than one** are erased. This count is of recorded terminal routes; it is not a proven count of unique physical sources. Full graph behavior, cycles and component-specific flood variants remain open.

Every preparation pass resets input values to **0**, then copies each retained pair's output value into its input. The setter and getter are direct f64 copies; they do not rectify, clamp, sum or take a maximum in these helpers. A negative source value can therefore survive this reviewed delivery path. Source and receiving component behavior still need their own checks.

Cross-body mechanical-manager build reads its registered input and writes its registered output after all local preparation passes. That adds a distinct propagation stage: a later local input copy is not retroactively rerun by the bridge write. Do not assign a universal wall-clock delay without the relevant update cadence and surrounding producer paths.

This narrows the historical shift diagnosis: the routing helpers do not generally reject negative commands. Receiver thresholds and intentionally selected source channels must be traced separately.

## Relay hysteresis and controller power

The boolean `thresholded_input` helper activates a false state for input strictly below **-0.75** or strictly above **0.75**. An active state releases only inside the open interval **(-0.25, 0.25)**. The boundary values themselves retain state. Both input signs can activate this boolean helper.

The signed overload has states -1, 0 and 1. From neutral it selects a sign beyond the strict outer thresholds. A negative state returns to neutral above -0.25; a positive state returns to neutral below 0.25. A reversal through this helper passes through neutral over separate calls rather than directly changing from -1 to 1 in one reviewed branch.

Electric relay update uses the boolean helper. A state change requests electrical-network rebuilding and emits the corresponding ability event. Its internal electric-flood getter returns its node group only while on. A relay's control input is consequently sign-insensitive at these thresholds; positive-only selection is needed when the intended logic requires directional commands to stay separate.

Microcontroller update requests **10 * dt** electrical energy when its node group meets the count check. It records accepted factor * 10 as displayed consumption. A factor strictly greater than **0.01** enables data power distribution and participates in script execution eligibility. Compile-error and pending-connection-update flags also gate the reviewed execution branch; adequate power alone does not establish that a program will run.

When that branch is ineligible, the method clears step mode and visits private variable values. Values of the analogue type are reset by a helper that sets analogue type to **-1** and numeric value to **0**. This is not proof that every boolean/integer/floating component output resets on power loss. Wider binding, compiler, load-error, execution-context and persistence behavior remain unfinished.

## Gas continuation and remaining questions

The newly completed gas-node preparation review computes cached pressure as volume/capacity only for positive capacity; nonpositive capacity produces zero. This is distinct from the direct gas-content pressure helper's ordered zero-capacity guard. Neither statement should replace the other.

Gas direct pairing requires matching grids, adjacent positions and opposing normals. Its flood follows the direct pair instead of saved links at a paired node, then follows component-internal flood nodes. Nodes are inserted into each island's list in descending cached pressure, preserving equal-pressure order in the reviewed comparison.

The gas-group temperature helper iteratively blends by current node volume divided by accumulated-plus-current volume. It does not skip non-null zero-volume contents before that division. Empty and shared-content cases require further native-math and caller analysis; a general safe-empty-temperature contract is not established.

The two formerly pending preparation bodies are now reviewed at this checkpoint's scope. Complete graph closure, shared-content reachability, group visit counts, native units and all variant behavior remain open. Next vehicle work includes these boundaries, other motors/generators and gearbox variants, steering/brake controls, structural geometry/mass, aircraft and marine systems. No whole-game or whole-electrical-system completion is claimed.

Continuation, 2026-10-22: [functional mating and drivetrain variants](MATING-DRIVE-20261022.md) finds two separate resolved battery-face candidates satisfying the local interface and containment predicates. That narrows the shared-content reachability question, while full placement, collision, authority and operating-network acceptance remain open. No repeated-reference accounting exploit was built or observed.
