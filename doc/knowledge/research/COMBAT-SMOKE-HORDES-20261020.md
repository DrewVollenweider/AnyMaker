# Character combat, weapon entry points, smoke and hordes

Build **25904830**, 2026-10-20. This continues [creature sensing and ambient spawning](CREATURES-SENSING-SPAWN-20261020.md). The game and active saves were not executed or changed. Complete weapon variants, projectile/armour physics, creature brains and navigation remain unfinished.

The selected reader now contains **1,275 functions / 184,600 checked instructions / 1,042,178 instruction bytes**. [GCL identities and selected bytes](versions/build-25904830/combat-smoke-hordes-20261020/evidence.json), [reflected declarations](versions/build-25904830/combat-smoke-hordes-20261020/reflection-evidence.json), [native binding evidence](versions/build-25904830/combat-smoke-hordes-20261020/native-evidence.json) and [verification](versions/build-25904830/combat-smoke-hordes-20261020/verification.json) retain exact source boundaries. These counts measure access and checks, not whole-game understanding.

## NPC equipment selection and combat timing

Character combat controller **41459691** refreshes gun, melee and torch IDs each tick. Helpers **41730943 / 41732996 / 41735060** scan the **10 hotbar slots in order**, resolve the item recursively by ID and return the first matching subtype. They return zero when none qualifies. Despite their names, these helpers do not rank damage, range, ammunition or battery energy.

Equipment helper **41421678** selects an existing hotbar slot, assigns an unlisted item to slot zero, or selects an empty slot when unequipping. If unequipping with no empty slot, it clears slot zero first. This traces the helper's calls; complete hotbar movement/replication remains separate.

The controller has twelve declared states: idle, equipping/equipped gun, reloading, attacking gun, equipping/equipped melee, beginning/performing melee attack, equipping/equipped torch and unequipping. It handles one branch per call. Selected initialized durations are:

| Operation | Reviewed value |
| --- | --- |
| Equip gun/melee/torch | Nominal tick rate, **60 eligible calls** |
| Unequip | Integer rate / 2, **30 eligible calls** |
| Base NPC reload wait | 3 × rate, **180 eligible calls** |
| Internal-magazine extra reload wait | `(ammo_capacity+1) × rate` |
| First gun attack gate | Attack request and prior ADS counter **>60** |
| Melee charge delay | **0.125** simulation seconds |
| Melee recovery | **1 + random(0.2,0.5)** simulation seconds |

Equip/reload waits count calls; attack/charge cooldowns subtract simulation delta. The controller updates the ADS counter at the end, resets the attack request and sets the actor's ADS property through **41430788**. Exact wall-clock response depends on its caller and state entry; these values are not a universal animation-speed promise.

An equipped gun uses the target-visible flag for ADS. A non-repeating weapon starts with no additional burst rounds; a repeating weapon draws an integer with call bounds **2 and 5**, then subtracts one. Native RNG endpoint inclusion is still open. Between bursts it adds random **0.2..0.5** to the weapon's virtual fire-cooldown getter.

NPC reload completion is distinct from normal inventory loading. The detachable path destroys the old grid-zero item and creates a magazine using the weapon's virtual magazine-definition getter. The internal path writes the definition's ammo capacity and marks the weapon chambered. This code does not consume an inventory ammo box in that completion branch. Complete magazine constructors and all weapon overrides still require review.

Torch helpers manage both a held torch and torch attachments on guns. A missing battery can be created from definition `battery_cell`; an existing battery receives `reset_energy()` **47510875**, which writes initialized energy capacity. The capacity initializer calls the kWh-to-joules helper with **0.016**. This is the NPC controller path, not a claim that player batteries replenish automatically.

Torch-on preference **41761270** compares daylight strictly below `0.5 + random(-0.05,0.05)`, using a local random object seeded by `(actor_id % 1000)*2000`. Recovering that seed does not establish the full native RNG sequence.

## Shared gun and melee entry points

Gun ammo helper **47647557** adds one for a chambered round to either the internal magazine count or a valid detachable magazine's count. The shared firing entry **47656301** requires chambered state for ability index zero. It emits events, consumes the next magazine/internal round when available, or clears chambered state when no next round exists. The currently chambered shot can still be emitted.

In this method, a server projectile is added when `actor.m_peer_authority` is null. Its starting velocity includes the actor physics object's linear velocity plus the view-rotated muzzle velocity. The muzzle position uses local offset **(0,-0.018,0.43)**. Other authority/client projectile paths are still open; do not infer that peer-controlled characters have no projectiles.

The gunshot environment-event call uses **250**, multiplied by **0.2** when a silencer is present. The complete event attenuation/AI response path and its units are not established here.

Ability index two is a separate inventory-ammo operation: it resolves the ammunition definition, finds a matching ammo-box item, debits one unit, chambers a round or increases the internal count, and destroys the depleted box. This must not be conflated with the NPC reload-completion branch above.

Base gun getters return fire cooldown **0.03**, false for internal/repeat firing, `machine_pistol_magazine`, muzzle vector **(0,0,400)** and a projectile enum. These are **base-class values**; the shipped concrete weapons override virtual methods. They are not a specification for every pistol, rifle or shotgun.

Melee entry **48029096** separates the begin event from the damage attempt. In its null-peer-authority damage path it casts **1.2** forward, filters physical terrain/tree/entity/prop/vehicle hits, then performs an actor raycast excluding the attacker and limited by the retained physical distance. An actor replaces the hit only when strictly nearer. Reflected armour index selects `actor` versus `actor_armour`; only the ordinary actor branch calls actor damage in this method. Vehicle and prop handling have separate calls. Full armour resolution, native actor raycast and damage propagation remain unfinished.

Melee damage comes from a virtual getter; the base getter returns **1.4**. The physical filter and this base number are not proof of identical reach/damage behavior for all concrete items or player-authority paths.

## Smoke is a separate occlusion system

Smoke manager **48465605** loops its stored occlusion spheres and returns true on the first native ray/sphere intersection. A sphere starts with lifetime zero (**24224940**), and push **48467359** records position, velocity and minimum/maximum radius.

Sphere tick **48472558**:

1. Samples wind at its position and time cycle.
2. Interpolates velocity toward horizontal wind by `1 × dt`.
3. Adds **0.8 × dt** to vertical velocity, then advances position by the updated velocity × dt.
4. Advances normalized lifetime by **0.1 × dt**.

Radius **48471077** is `lerp(radius_min,radius_max,lifetime)`. Manager tick **48468969** updates then removes spheres whose lifetime is **>=1**. An ordinary newly initialized sphere therefore lasts about **10 simulation seconds**; rendered particle density and total grenade burn duration are separate.

The two emitters **47639155 / 48195391** add recurring spheres with radii **0 to 24**. The next emission wait is `0.2 / max(wind_factor,0.02)`; stronger wind increases emission frequency in this formula. Emission here requires the grenade to be the matching floor item in the supplied tick context. The discharger also emits an initial **5-to-10** sphere when its fuse expires in that context. Complete trigger/fuse initialization, loaded-state persistence and all mounted contexts remain open.

### Native ray extent: smoke beyond a target can count

The PE registration binds the exact signature `(bool) collision.test3d_ray_intersect_sphere (...)` to wrapper RVA **0x11cf60**, which calls implementation **0xbba0**. Selected disassembly and constants corroborate the quadratic intersection and its nonnegative-root gate. It has **no maximum-distance argument or target-distance comparison**.

The actor-point and vehicle sight callers construct a normalized direction toward the target. Their physics cast receives the target distance separately; their later smoke-manager call receives only the ray. The manager accepts any forward sphere hit, without comparing its returned hit distance with the target distance.

For example, a ray from **(0,0,0)** toward a target at **(0,0,10)** intersects a radius-one sphere centered at **(0,0,100)** at parameter **99**. The native forward-ray test accepts that intersection, and this smoke call does not reject it for lying beyond the target. This is a static consequence of the reviewed chain, not a new gameplay observation. Degenerate/NaN inputs and the full native loader remain outside the claim.

## Hordes differ from ambient zombie spawning

Horde manager **59397474** updates/removes existing controllers, then attempts a spawn when fewer than **one** controller remains. Spawn **59392429** rejects sandbox/debug-disabled zombie spawning and requires **current actor count + 25 < 300**. It chooses a loaded tile with nonempty creature spawn points and nonnegative tile height, then requires a candidate point at height **>=8** and outside the strict **200** spawn-position exclusion.

This horde method has no equivalent peer-position exclusion loop from the ambient producer. Its local seed combines **world seed, scene version and tile coordinates**. That differs from the selected ambient branch's version/coordinate seed; retain the two paths separately.

Creation **59381791** uses definition `zombie_basic` and initialized horde size **25**. It offsets members by random-call bounds **1..5** in each horizontal coordinate and **2** vertically, creates them and sets logical flag `is_horde_spawned`. Native random endpoints and world collision/navmesh acceptance remain separate questions.

Controller tick **59385792** prunes missing, non-zombie or incapacitated IDs and supplies flock positions to retained members. Destruction predicate **59384296** selects sandbox/debug-disabled states or a member count **<5**. Cleanup **59383712** clears the controller's ID vector; it does not destroy all actor objects in that helper. Ordinary actor lifecycle/despawn remains separate.

## Verification and remaining scope

No executable research tool changed after the **159-test** checkpoint. New GCL exports, reflected declarations, native registration/wrapper/implementation spans and selected constants were checked against matching resources; installed GCL/PE and all **2,968** indexed data files were rehashed. Documentation links and publication checks passed.

Continue concrete weapon and ammunition variants, projectiles/explosions/armour, individual creature/zombie/character states, pathing, dungeon producers, remaining native contracts, world/persistence/authority and every other open [audit-register area](AUDIT-REGISTER.md). Neither this selected combat chain nor a successful offline export completes the full-game audit.
