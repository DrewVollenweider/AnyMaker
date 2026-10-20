# Survival reserves, clothing, damage and scene scheduling

Build **25904830**, 2026-10-20. This continues the [sensor/data research](SENSORS-DATA-20261020.md) and the [full-game audit](AUDIT-REGISTER.md). Matching isolated resources were analyzed without executing the game or editing installation/active saves. Full actor movement, AI, combat, world generation and persistence remain unfinished.

The combined reader contains **1,191 functions / 167,289 checked instructions / 947,427 instruction bytes**. [Selected source evidence](versions/build-25904830/survival-schedule-20261020/evidence.json), [declared fields/enums](versions/build-25904830/survival-schedule-20261020/reflection-evidence.json) and [verification](versions/build-25904830/survival-schedule-20261020/verification.json) retain exact source identities. Export counts do not establish complete semantic coverage.

## Update order and eligibility

Scene tick **51836326** processes environment events, builds ocean data, updates creature/dome/dungeon/weather/navigation/projectile/item systems, then vehicles, hatch manager, peers and actors, followed by other containers. Physics update and collision-event handling come later, followed by post-physics callbacks. Each collision event is dispatched with both endpoint orders. These are calls in this method; complete internals and outer application scheduling are separate work.

The debug pause/step fields change the physics-update delta in this method. Earlier actor/container calls are outside that particular branch. This is not proof that every user-facing pause mode continues survival; an outer caller can gate the whole scene update.

Actor container tick **41149200** calls each actor's virtual tick, then its despawn predicate, destroys/erases eligible actors, and finally runs separation. Character tick **41917657** first calls the base actor tick. Its no-authority-data branch handles AI movement. The reviewed survival calls occur in the other branch, and only while the character is not incapacitated:

```text
tick_stamina -> tick_oxygen -> tick_conditions
```

Authority-data getter **41231153** requires the peer/data pointers and an actor-ID match against the primary or dragged authority record. This is more specific than merely having a nonnull peer. The full character movement method has not been semantically reviewed in its entirety; the stated schedule follows its enclosing branches and selected calls.

Nominal server-rate initialization is **60**, and delta-time initialization is **1 / rate**. Condition tick **41949825** increments an integer counter, runs the expensive condition pass only when the counter is **greater than 60**, then resets it to zero. From counter zero, that is **61 eligible calls**, not 60. At the nominal simulation delta, uninterrupted eligible calls span 61/60 simulation seconds per condition pass. Real wall-clock frequency, pauses, loads and incapacitation cannot be inferred from the global's name alone.

## Vital values and network precision

The six hunger/thirst/oxygen/hot/cold/infection setters clamp their reserves to **0..1**. Each sets its warning flag for **0 < reserve <= 0.5**, and critical flag at **reserve <= 0**. The decoded global warning threshold is **0.5**. The separate **0.25** threshold below belongs to stamina. Wetness uses a different flag: **wetness >= 0.5**.

Compressed-property getter **38843662** returns the address of its internal f64. Setter **38846811** stores the supplied f64 first, then computes a separate `round(clamp(value*255/range, 0, 255))` byte. It marks the property modified when that byte changes. Tiny internal reserve changes therefore accumulate even when the wire-level byte is unchanged; do not round the actual reserve to 1/255 at every update. Complete client display/replication timing remains open.

| Initialized coefficient | Value | Reviewed use |
| --- | --- | --- |
| Hunger maximum | 7200 | Subtract 1/7200 per ordinary condition pass |
| Thirst maximum | 3600 | Subtract 1/3600 per ordinary condition pass |
| Infection maximum | 600 | Baseline reserve gain 0.2/600 per ordinary pass; other conditions can subtract |
| Blood maximum duration | 600 | Condition damage count divided by 600 |
| Hot / cold maximum durations | 600 each | Reserve change from effective-temperature deviation |
| Oxygen depletion / drowning / recovery | 30 / 30 / 10 | Separate oxygen tick and condition-damage paths |
| Stamina drain / recovery | 45 / 90 | Delta-time-scaled stamina changes |

These are initialized coefficients and their actual uses, not universal real-time survival promises. The ordinary condition pass doubles hunger/thirst debits when the newly updated stamina is **strictly below 0.25**. Other changes, clamping, eligibility and update order affect endurance.

Food/drink self-use **47580036 / 47555655** have event stages 0/1 and a consumption stage 2. The last stage attempts the character cast, then invokes the corresponding reducer. Reducers **41891479 / 41891940** actually add **+0.5** to the reserve. This does not by itself establish every item's use count, permission checks or upstream consumption lifecycle.

## Stamina and oxygen

Stamina tick **41966834**, using movement speed v, calculates `F=clamp((v-2)*0.5, 0, 1)`:

- Sprinting with F>0 subtracts `F*dt/45` and marks the update as draining.
- Swimming with v>0.5 subtracts `dt/45` and also marks it draining. Both branches can contribute.
- A rising jump input subtracts **0.05**, then stores the current jump state.
- If neither sprint nor swim branch marked draining, it adds `dt/90`.
- The resulting reserve is clamped to 0..1.

The jump debit does **not** itself set the draining flag. A standing jump can therefore incur the edge debit and recovery in the same update. A held jump does not repeat that edge cost. The model retains these distinctions rather than replacing them with a generic movement drain.

Oxygen tick **41964849** skips its ordinary path when invulnerable. Otherwise it tests the **view position** against the ocean-submersion helper: submerged subtracts `dt/30`, otherwise adds `dt/10`. Body submergence and head/view submergence are separate measurements. Full ocean/dungeon/vehicle air-space behavior remains a dependency, not a recovered general underwater-breathing model.

## Clothing, wetness and temperature

Inventory construction **24125670** sizes its slot array using wearable-slot enum metadata; it has a separate primary-hand reference. Parser **47335864** serializes numbered slot references and the hand separately, with load-time invalid-item removal. The exact full load/reference/container lifecycle remains open.

Resistance helper **47325270** sums temperature/wetness resistance fields of valid definitions in that slot array. Clothing wetness **47362006** additionally requires the clothing class. These helpers do not traverse bag contents in their reviewed loops; do not infer benefits from arbitrary carried items.

For each eligible clothing item, with current wetness w:

```text
if submergence > 0 and submergence >= w:
    w = min(submergence, w + 1/15)
else if rain > 0:
    w += rain * (1-clamp(wetness_resistance/25, 0, 1)) / 90
else:
    w -= 1/(1200 if temperature <= 15 else 600)
w = clamp(w, 0, 1)
```

It returns the average updated clothing wetness, or zero without eligible clothing. Submergence below the current wetness falls through to the rain/drying branches. The separate splash coefficient 0.05 exists, but is not used in this reviewed helper.

Body-temperature helpers **781169 / 780126** calculate:

```text
insulation = clamp(total_temperature_resistance/90, 0, 1) * 30 * (1-wetness*0.7)
effective = weather_temperature + insulation
          - (0 if sheltered else wind_factor*10)
          - wetness*6 + (1-stamina)*5 - body_submergence*10
```

Comfort bounds initialize to **12 and 30**. Outside a bound, the corresponding temperature reserve decreases by `0.1*distance_outside/600` per condition pass; inside, it recovers using distance from that bound. Slightly-hot/cold flags are separate from the warning/critical reserve flags.

In this condition path, shelter for the wind term is determined by the actor position being inside any vehicle's transformed outer bounding box. Rain protection is a separate 100-length raycast along a wind/snow-derived direction; qualifying hit groups are **terrain, tree, vehicle, entity or prop**. This is not a recovered watertight-cabin or roof-connectivity test. Keep weather exposure, collision, visual surfaces and [water sealing](SEALING.md) separate.

## Damage and exceptional paths

Ordinary condition damage counts bleeding twice and each relevant critical reserve once. Cold warning and bleeding also debit infection reserve, in addition to its baseline recovery. Blood drain is the larger of count/600 and the critical-oxygen candidate 1/30, with an injury event when the count is positive. Exact flags and coefficients are retained in selected evidence; every source of those flags and every actor override remain separate review work.

Base damage **41151584** subtracts its damage argument through virtual blood modification. Melee/gun source types emit blood-impact events; the melee branch uses a decoded **0.25** knockdown chance. It applies a normal-based impulse with coefficient **-40**, plus a ragdoll impulse event. These are native coefficients, not asserted SI impulse units or proof of every weapon's damage behavior.

Base blood modification **41276026** and character override **41840492** calculate `clamp(old_factor*maximum + delta, 0, maximum)/maximum`; the character override skips a zero-magnitude modification. The reviewed base maximum getter returns **1**. Complete other creature overrides, armor, weapons, death/respawn and item-drop paths remain open.

Invulnerability getter **41820212** requires peer/data pointers, then checks creative mode, creative-dome membership or the primary authority record's invulnerability field. This getter uses that primary record even though the authority-data getter can also return a dragged record. This observation is not an authorization/security conclusion; complete control and validation paths are unreviewed. The invulnerable condition branch adds to the vital reserves, clears bleeding/broken-leg inputs, and writes **wetness 1.0** as encoded. Do not silently describe that last write as a dry-clothing reset.

## Verification and continuation

`survival_models.py` retains selected counter, vital-flag, stamina, clothing and thermal arithmetic. Eight added tests include the 61-call cadence, warning/critical boundaries, jump-plus-recovery counterexample, additive drains/time partition, soaking/drying priority and 500 seeded resistance/insulation monotonicity checks. All **151** research tests pass. The model excludes native physics, full actor scheduling/authority, item lifecycle and network encoding.

All selected exports passed exact instruction/source checks. The combined reader re-audited its batches; published identities/constants/calls/fields/enums are independently checked. Installed/snapshot GCL/PE and all **2,968** catalogued installed data files still match. No new gameplay result is claimed.

Continue actor movement and authority handoff, all creature/AI variants, combat/projectiles/explosions, world generation/time/weather, save/load and the other full-register domains. Vehicle, native-helper, script/compiler and interface/lifecycle questions also remain in scope.
