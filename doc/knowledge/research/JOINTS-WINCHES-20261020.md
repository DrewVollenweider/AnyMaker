# Hinges, mounts, latches, rails, tow links and winches

Build **25904830**, 2026-10-20. This continues the [actuator/track checkpoint](ACTUATORS-TRACKS-RAYCAST-20261020.md). The [full-game audit](AUDIT-REGISTER.md) remains active. Matching isolated resources were read without executing the game or changing its installation or active saves.

The combined reader now contains **1,110 functions / 154,167 checked instructions / 877,643 instruction bytes**. These are access and byte-verification counts, not semantic completion. [Selected identities and constants](versions/build-25904830/joints-winches-20261020/evidence.json), [declared fields](versions/build-25904830/joints-winches-20261020/reflection-evidence.json), and [verification](versions/build-25904830/joints-winches-20261020/verification.json) accompany the findings.

## Hinge suppression belongs to a pair of bodies

`vehicle.update_constraint_tiers` **52674950** gathers links from the vehicle's dynamic-component vector. Each link contains a component, another vehicle/body ID and a tier. For each link, it takes the highest tier among links naming that same peer ID, starting at zero, then notifies that component.

| Connection family | Reported tier | Selected gather implementations |
| --- | --- | --- |
| Hinge pin / knuckle | 1 | 55259852 / 55214354 |
| Fixed mounting pin / knuckle | 2 | 57030185 / 56993519 |
| Latch handle / knuckle / pin | 2 | 56101509 / 56144352 / 56168579 |

The hinge pin's notification **55268611** checks that the peer ID matches its connected component's current body, then sets suppression when the reported tier is **greater than 1**. Its tick **55282013** removes an added hinge constraint while suppressed, while retaining the connection state. When unsuppressed, it can add the created constraint again and wake both bodies.

A fixed mount or latch between the same pair can therefore suppress that hinge's constraint. A higher tier to an unrelated body does not satisfy this peer-ID comparison. This is a local maximum-by-peer pass, not a recovered graph-depth or cycle-breaking algorithm.

## Hinge and fixed-mount construction

Hinge connection **55241004** casts the other component to the hinge-knuckle family, writes reciprocal pointers and IDs, marks both connected, disables collision between the bodies, creates/adds the hinge constraint, wakes both bodies and requests tier updates. It uses the first configured constraint orientation. Opposite world-axis directions cause a pi rotation of the second frame around its X axis.

The definition's anchor helper **62564822** returns:

```text
constraint_position_in_cells × 0.08 + constraint_offset
```

Hinge connection and manual interaction use this helper. The reviewed mount, latch, rail and tow construction paths instead calculate their anchors directly from the grid position; do not silently add the offset to every joint family.

Hinge saved fractions default to **0 and 1**. Each fraction maps into the definition's angular interval. If the resulting upper limit is less than or equal to the lower, connection/tick repair the interval to midpoint minus/plus **0.01**. The shipped hinge-pin definition uses **0..pi**. This small interval repair is distinct from rejecting the saved input.

Manual hinge interaction **55264472** requires its own body to be added to the physics scene. An already connected hinge disconnects; otherwise it searches eligible components, checks the configured other definition and knuckle compatibility, and requires anchor distance squared to be **strictly below 0.08 squared**. No equivalent direction-dot gate appears in this reviewed search; connection later aligns frames.

Fixed mounting connection **57019740** uses each endpoint's saved orientation index and creates a fixed constraint. Its parser **57043932** defaults that index to **0** and connected IDs to **-1**. Hinge disconnect **55257857** removes/destroys the owned constraint, restores pair collision, clears reciprocal IDs/pointers/state, wakes both bodies and requests tier updates. Ownership delegation and loaded-state reconstruction require their own valid-state assumptions; no invalid-state recursion bug is asserted here.

Hinge tick and fixed-mount tick **57055362** compare the lengths of their position/rotation constraint lambdas with **100000**, disconnecting only when a length is strictly greater. The vector dimensions differ by constraint kind. Native solver calibration and units remain unresolved, so this is not a claim of a 100000-newton rating.

## Latch release and automatic capture

Latch-pin tick **56185555** sets its activation state false for input below **0.5**, true at or above **0.5**, then runs its multibody update. Both reviewed handle/pin multibody updates (**56130449**, **56189241**) require their own body to be added. A connected activated latch releases; an inactive latch with no connected peer is eligible to capture.

Capture searches the available-component list, requires the configured other definition and a compatible available knuckle, and checks:

```text
anchor_distance_squared < 0.08²
world_direction_dot >= 0.7
own_constraint_not_created
```

The distance boundary is exclusive; the dot boundary is inclusive. Handle connection **56094682** writes reciprocal pointers/IDs and connected states, disables pair collision, creates/adds a fixed constraint, wakes both bodies and requests tier updates. Reviewed connected updates also use the strict lambda break test. The construction of the available list and every loaded/repaired/tool path remain separate questions.

## Rails and ballscrews have different release thresholds

| Component input | Release when input is at least | Tick |
| --- | --- | --- |
| Ordinary rail | 0.5 | 57200343 |
| Ordinary rail slider | 1.0 | 57301246 |
| Ballscrew slider | 0.5 | 57266275 |

Both slider ticks also check position/rotation lambda lengths against the strict break threshold while connected. These differing constants are directly decoded; do not substitute a universal digital threshold.

Ordinary slider connection **57271360** casts a rail, adds its entry, writes IDs, creates/adds a slider constraint and wakes both bodies. The lower travel coordinate is `definition.center_stretch_grid.z × 0.08`; the upper includes the rail's Z extension. Its disconnect **57277414** removes/destroys the owned constraint, wakes bodies, clears IDs and removes its parent-list entry. The reviewed connection has no explicit pair-collision toggle.

Ordinary rail add/remove **57175928 / 57198215** and ballscrew add/remove **57212145 / 57236382** maintain the parent's slider list. Add can rehydrate a null-pointer record whose vehicle/component IDs match; otherwise it appends. This helper does not deduplicate an already live pointer. Remove finds a matching pointer and erases that entry. Reachability of duplicate or unresolved entries needs lifecycle review.

Ballscrew connection **57247667** reads the created constraint's actual position into its slide-position field, then calls the motor setter with **20.0, 1.0, position**. Update **57267975** only advances an added constraint, clamps its stored target to the bounds and calls the same motor setter. The first two native argument meanings/units are not recovered here.

For each listed slider, ballscrew tick **57240738** computes:

```text
M = 1 + slider_body_mass
advance = shaft_rps × delta_time × 2pi
torque_argument = -M × 10 × advance
brake = 0 if lower < position+advance < upper else 0.99
```

It writes the shaft-node mass and brake for each entry, applies torque, and updates that slider's motor target. The last entry's mass/brake write therefore wins, while torque contributes to accumulated pending speed change. With the previously traced `apply_torque(A) -> pending += A/M` and ordinary positive M, each contribution simplifies to **-10 × advance**. This is native arithmetic, not an SI torque or screw-lead model. An exact endpoint sets the brake even if the clamped motor target remains there.

With a nonempty list, the parent accumulates shaft advance. Once its absolute pending distance exceeds **0.0001**, and its own body is added, it clears that accumulator and wakes itself and valid added slider bodies. Full scheduling, limits under external load and invalid list entries are not closed by this trace.

## Tow connections are point constraints

Tow-bar/hitch connection **57820649 / 57859436** creates a point constraint, not a fixed constraint. The endpoint that performs connection owns the created constraint; the other receives a reciprocal pointer/IDs. Disconnect **57828198 / 57867657** delegates to the peer when necessary to reach that owned constraint, then removes/destroys it and clears both endpoints.

The multibody updates **57848259 / 57888296** decrement a positive cooldown by one and skip the remaining work for that update. Once eligible, they require an added body, the configured exact other definition and compatible endpoint. Capture requires distance squared **strictly below 0.08 squared**, and direction dot satisfying **both endpoints' configured minima**, inclusively. Reviewed connection/cleanup paths do not explicitly toggle pair collision or update tiers.

The hitch's release input uses **1.0**. Its `can_connect` also requires input below 1.0, preventing immediate automatic recapture while release remains held. The source's `is_parent` definition field does not establish constraint ownership in these reviewed methods. Cooldown initialization/setters, default dot thresholds and full tool/load paths remain open. Shipped ordinary and truck kingpin/hitch pairs are separate configured definition pairs.

## Winch length gates and rope stretch

Winch tick **58126118** sets node mass **10**, clutch `1-abs(release_input)`, and advance to `shaft_rps × delta_time × 2pi` when that clutch is positive, otherwise zero. It applies torque argument `-10 × advance`, resets brake to zero, and evaluates attached ropes using the same precomputed advance.

A rope can change its nominal length only when the proposed length is **strictly between 0.5 and 20**, and it is not being shortened while stretch is **greater than 1.2**. A blocked rope sets shaft brake **0.99**. A later valid rope may still receive its length update and does not reset that brake in this loop. This differs from ballscrew's repeated per-slider brake writes.

Rope stretch **51094075** is `get_world_length / nominal_length`, with no zero-denominator guard in that helper. World-length method **51095346** obtains the two endpoint positions from connected endpoint transforms, otherwise the first/last rope physics objects when available, otherwise the stored fallback. It returns the **straight distance between those two endpoints**. It does not sum the sagging chain's intermediate segment lengths. The complete rope particle solver, failure/lifecycle behavior and endpoint-transform implementation remain open.

## Checks and continuation

`joint_models.py` retains selected tier, hinge-limit, ballscrew and winch arithmetic with explicit ordinary-domain guards. Eight additional tests include peer isolation, 500 seeded tier-order checks, collapsed angular intervals, travel endpoints, mass cancellation, ordering counterexamples and rope length/stretch boundaries. All **143** research tests pass. The model does not implement native collision, constraint forces, structural mounting, rope particles or complete dispatch.

The input GCL/PE and all **2,968** catalogued installed data files were rechecked against the isolated source. Selected source/constant/reflection evidence is independently checked. Full decompilations remain local. Continue control/sensor/data chains, all remaining joint lifecycle and track/tool states, compiler/native contracts and every other area in the full register; this checkpoint does not complete those domains.
