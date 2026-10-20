# Creature variants, shared sensing and ambient spawning

Build **25904830**, 2026-10-20. This continues the [survival/schedule checkpoint](SURVIVAL-SCHEDULE-20261020.md) within the [full-game audit](AUDIT-REGISTER.md). Matching isolated resources were read without executing the game or changing its installation or active saves. Complete creature brains, combat, navigation, horde/dungeon spawning and world generation remain unfinished.

The selected reader contains **1,228 functions / 176,005 checked instructions / 996,711 instruction bytes**. [Source evidence](versions/build-25904830/creatures-sensing-spawn-20261020/evidence.json), [reflection](versions/build-25904830/creatures-sensing-spawn-20261020/reflection-evidence.json), [all 40 selected variant records](versions/build-25904830/creatures-sensing-spawn-20261020/creature-variants.json) and [verification](versions/build-25904830/creatures-sensing-spawn-20261020/verification.json) retain source identities and limits. Access counts are not complete semantic coverage.

## Forty definitions, eight actor types, distinct ambient eligibility

Creature definition parser **22112739** explicitly defaults omitted actor type to `creature_regular`, behavior to `prey`, animator to `quadruped` and group size to **1**. Other selected defaults are crouch/walk/run/swim speed **0.5 / 2 / 6 / 2**, maximum blood **1**, attack damage **0.1**, jump-force coefficient **200** and knockback coefficient **600**. These are parser defaults, not values guessed from names or another game.

Factory **41097191** constructs `server_scene.actor_` plus the actor-type enum label, requests a subtype of the creature base, assigns the definition and transform, then invokes creation/post-load. All eight resulting class names have reflected descriptors. This verifies the name-construction/declaration chain, not every constructor, physical shape or lifecycle.

| Resolved actor type | Shipped definitions |
| --- | --- |
| Regular | 33 |
| Large | 1 |
| Large centipede | 1 |
| Large burrower | 1 |
| Large acid | 1 |
| Large crusher | 1 |
| Large carrier | 1 |
| Large eel | 1 |

Resolved behavior counts are **25 prey / 14 predator / 1 monster**. Actor type, behavior and animator are separate fields. The animator literals include ten birds and two quadruped-tail overrides; animator implementation is not established by those counts.

Ambient manager **44753872** only puts definitions with **positive group size** into its creature pools. In the matching shipped data, these pools contain:

- Monster-behavior pool: **monster_s**.
- Other-creature pool: **black_bear, opossum, bighorn_sheep, black_tailed_deer, bobcat, interior_wolf, peccary**.
- The other **32 definitions have group size zero** and are excluded from these ambient pools. This is not proof that they cannot appear through dungeon, manual or other producers.

The seven other-creature definitions include three predators and four prey. Larger group-size fields on these definitions do not automatically mean this ordinary ambient branch creates a whole group: the reviewed non-monster branch creates one actor per accepted tile iteration. The separate monster branch has an explicit group-size draw and loop.

## Shared target eligibility and ordering

Sensor eligibility **40997510** rejects equal teams when the observer's team is nonzero. It honors separate character, creature, zombie and incapacitated flags, then admits characters/zombies or creatures whose behavior is predator/monster, and rejects invisible actors. This particular shared predicate excludes prey definitions; it is not a claim that every AI system uses it for every decision.

Vehicle predicate **41000881** requires dynamic motion type, the vehicle-sensing flag and hostility helper **41010048**. That helper qualifies a vehicle when its linear speed squared is **greater than 1**, or a character with peer authority has `dist_sq_to_vehicle < 25`. It does not add an alive/invisible check to that nearby-character test here. The distance helper **41051673** builds an oriented box from vehicle bounds and transform and calls a native point/box-distance intrinsic; it is not a center-distance calculation. The complete native inside/edge contract remains open.

Sensor collection **41016080** uses strict `distance_squared < range_squared` gates. Visible targets must also pass view/obstruction checks; actor hearing excludes incapacitated targets but has no obstruction test in this collection method. Vehicle hearing uses its distance gate. The method appends to its supplied result rather than clearing it. Complete caller result lifetimes remain separately reviewable.

Four add helpers store the actor/vehicle pointer, squared distance and position. Insertion helper **41032042** orders each visible/audible list by increasing squared distance, swapping only when the prior distance is greater. Equal distances retain insertion order. This establishes result ordering, not how every brain chooses among those lists.

## Sensing distances and update timing

For ordinary finite inputs in 0..1 where applicable, actor-distance helper **41047223** uses:

```text
S = clamp((target_speed-1)/3, 0, 1)
D = 1 if day_factor >= 0.7 else clamp((day_factor-0.4)/0.3, 0, 1)
D = max(D, target_light_volume_factor)
V = base_visible * lerp(0.8,1,S) * (1-0.7*fog) * lerp(0.4,1,D)
A = base_audible * S
if target_crouched: V *= 0.5; A *= 0.02
V = max(V,3); A = max(A,1)
if observer_sleeping: V *= 0.1; A *= 0.4
```

Vehicle helper **41050129** instead uses `max(base_visible*(1-0.7*fog)*lerp(0.2,1,D), 3)` and `max(base_audible,1)`, with the same daylight interpolation but no target-light maximum. It does **not** apply the observer-sleep parameter in the reviewed calculation. Do not reuse the actor formula for vehicles.

For a zombie observer, modifier **44016604** multiplies both ranges afterward by `0.8 + ((actor_id % 9)/8)*0.2` for ordinary nonnegative IDs. Floors happen before sleep and this modifier; they are not final minimum ranges. Native angle/physics and invalid-input contracts remain outside these ordinary arithmetic models.

Sensor tick **41039448** advances a sensed timer and periodically checks nearest other, non-incapacitated, visible actors without applying the full target-category/team filter to that proximity optimization. A nearby actor can shorten the current sensing delay through integer interpolation. Collection runs only when **timer > delay**, then resets timer to zero and delay to maximum.

Saved parser **41021891** defaults proximity cooldown to 0, its min/max fields to 1/1, sensed timer/delay to 0, minimum delay to **3**, and maximum delay to **5 × nominal tick rate = 300**. Begin/tick use literal random-call bounds **1 and 10** for the proximity counter in the reviewed methods. Native RNG endpoint inclusion and integer-lerp rounding remain open; do not turn these into an exact real-time response promise for every NPC.

## Sight geometry differs between actor points and vehicles

Combined sight helpers **41223462 / 41224701** require `(view cone OR close sphere) AND unobstructed`. Cone **41225932** compares absolute native angle with half the actor's FOV getter. Sphere **41227458** tests **distance squared < 0.5**, not radius 0.5. Full FOV overrides and the native angle contract remain open.

Point obstruction **41211025** casts from the observer's primary physics-object position. Terrain, vehicle, entity and prop groups block. It also has a conditional same-team character obstruction path for nonzero teams, excluding the observer's own physics object. This is not a universal rule that all actors or all vegetation block sight.

Vehicle obstruction **41218111** uses the observer's view-transform position and the transformed vehicle-bounds midpoint. Terrain/entity/prop groups block; vehicle hits block except for the target vehicle's own physics object. This path has no equivalent same-team-character branch. The outer vehicle view gate uses its transform translation, while recorded target position uses the separate vehicle-center field.

Both obstruction paths consult the smoke-occlusion helper after physical obstruction checks. That helper's complete ray-extent/particle lifetime behavior is still open. These sight tests differ from the rain filter and cabin water sealing; visual appearance alone does not establish a shared occlusion rule.

## Ambient spawn cadence, pools and placement gates

Manager tick **44783901** runs the zombie-horde manager first. With creature spawning enabled and nonempty peer positions, it accumulates calls; at **8 × nominal tick rate = 480 eligible calls**, it runs spawn then ordinary despawn and resets the counter. Dome despawn runs on every eligible manager call. Debug/no-peer gates affect this path; actual wall-clock timing depends on outer scheduling.

Spawn **44753872** skips sandbox mode and checks the actor-container size against initialized **300** before work and at tile-loop guards. This is a guard in this producer, not a recovered hard cap across every spawn producer.

Let T be the loaded-tile count collected by this method and L the subset whose tile height is nonnegative. It collects existing actor counts before the spawn loops and uses these selected budget expressions:

| Pool/count gate | Expression |
| --- | --- |
| Other creatures | 3 × L |
| Predators within that pool | Integer L / 3 |
| Ordinary zombies | 5 × L |
| Monster-behavior creatures | T + native_round(T × (1-day_factor)) |

These prepass counts are distinct from the actor-container size checks in each tile loop. Exact native rounding is not reconstructed here. Pool selection, definition group-size gates and actual accepted spawn points further constrain births.

Monster spawning requires loot level **greater than 1** and cycle **strictly before dawn 0.25 or after dusk 0.8**. Its candidate point must be at height **<=128**, outside the strict **150** distance exclusion around every supplied peer position, and pass the reviewed navmesh check. The selected point's distance squared from the tile's nearest-ocean position must be at most `(4096*(1-day_factor))²`; point height **<8** bypasses that distance by substituting zero. These are separate height/night/ocean gates, not a general biome claim.

Other creatures and ordinary zombies use candidate height **>=8** and the same strict peer-distance exclusion. They also reject points strictly inside initialized distance **200** from `scene.get_spawn_position()`. The ordinary creature branch applies its predator budget check; the zombie branch excludes classes `tank` and `ambush`, requires positive group size and sufficient loot level for the definition's spawn tier, then selects from spawn-probability weights. At an exact cumulative-weight boundary the current bucket is retained. Native random generation and all zero-weight behavior remain separate questions.

Tile-local random seeds combine **scene.m_version** and tile coordinates using branch-specific integer coefficients. This field is the saved scene version, not the simulation tick or an assumed world seed. Other random, generation and migration paths remain open.

## Despawn and AI entry points

Ordinary despawn **44738098** skips actors inside dungeons. For monster-behavior creatures, it removes them in the strict dawn-to-dusk interval, or at position Y **<=-40** outside that interval; otherwise loaded-tile checks apply. Other creature/zombie paths also remove them when their tile is not loaded. Character handling preserves an actor ID matched to a peer's authority-actor ID before its unloaded-tile removal path. This does not establish all disconnect/save/death persistence.

Dome despawn **44744337** removes creatures/zombies inside a creative dome and has a separate unmatched-authority character path. Do not generalize behavior enum `monster` to every monster-named definition: the variant records deliberately retain actor type and behavior separately.

Character AI entry **41419041** ticks its state machine first. When inactive it returns default actor inputs; when active it updates combat then locomotion. State-machine entry **41639343** ends the old state, installs/begins a pending state, then ticks the current state. Locomotion entry **40994284** orders default-look, behavior, path-request/plan/execution, override-look and stuck-state helpers. Complete state implementations, combat, pathing and other creature-specific brains are still open.

## Verification and continuation

`ai_models.py` retains selected ranges, category eligibility, nonnegative-ID modifiers and weighted selection for a supplied draw. Eight added tests include sleep/floor order, actor/vehicle differences, 500 seeded monotonicity checks, category/flag boundaries, ID periodicity and cumulative-weight equality. All **159** research tests pass. The models exclude casts, native angles/RNG/rounding, placement and actual brains.

Selected exports, source identities/constants/calls, declared fields/enums and all 40 variant hashes/defaulted values are independently checked. Installed/snapshot GCL/PE and all 2,968 indexed data files still match. Complete behavior/lifecycle coverage is not inferred from these checks.

Continue creature/zombie/character brains and combat/navigation, horde/dungeon producers, native geometry/smoke/RNG contracts, world/time/version migrations and every other remaining full-register area. No game-runtime result is claimed.
