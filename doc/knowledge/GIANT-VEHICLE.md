# Giant engine and test vehicle — 15–16 October

## Starter and liquids

The user first tried a medium engine wheel that spun at 7.5 rps without turning the engine over. Compatibility mattered; restoring the correct large wheel only achieved roughly 3 engine rps with the original drive. Documentation required 6 rps. The accepted revision uses a **60 kW motor (62)** and fixed gear **104**, configured input 1 / output 3 with reverse enabled, driving the large engine-wheel belt. Nominal 90 small-pulley rps / 6.675 = **13.48 engine rps** is the static starting calculation; later combustion was confirmed by the user's game test, not by calculation alone.

Full-throttle operation initially reduced internal oil/coolant to ~50 mL while reservoirs and pump chambers still held substantial liquid. Throttling down let engine contents rise. Native traces showed no claimed 50-rps liquid-pump ceiling. Positive effective pump rotation moves chamber 0→1; reverse negates speed. Fitted ports sort by component ID before chamber assignment. Engine-wheel sign and the pulley/pump mate sign changes must both be included.

| Circuit | Chamber 0 external path | Chamber 1 external path | Accepted reverse flag |
| --- | --- | --- | --- |
| Oil, pump 17 | port35 → reducer33 → tank port61; later filter inserted in this feed | port36 → reducer34 → bracket37 → engine manifold11 | **OFF** |
| Coolant, pump 20 | port31 → reducer30 → engine manifold4 | port32 → reducer29 → radiator port15 | **ON** |
| Fuel, pumps 84/85 | ports86/88 → fuel manifolds100/101 | ports87/89 → tank ports48/49 | **ON** |

Oil manifold12→tank port60 and coolant manifold5→radiator port16 are the other return paths. The original oil/coolant flags made pumped extraction increase with RPM while refill was passive. Reversing these two pumps positively feeds the engine. Both manifolds of a given engine fluid reach its common internal volume, so there is no universal “intake manifold by surface index” rule.

| User screenshot after correction | 20% | 100% |
| --- | ---: | ---: |
| Speed | 16.8 rps | 72.8 rps |
| Oil | 23.6 L | 23.6 L |
| Coolant | 24.5 L | 24.3 L |
| Temperature | 27.1 °C | 34.9 °C |
| Displayed power | 80.5 kW | 499.5 kW |

The oil filter was subsequently added as component105, ports106/107, inline upstream of the oil pump. Preserve orange fuel/red oil/blue coolant/white air. At 100% the air line remained red at 454.7 L/s; no separate air-system optimization or loaded power test was completed.

[Circulation evidence](archive/toolset/output/giant-engine-circulation-03/LIVE-RESULT.md) contains the original failure and later successful test. [Direction trace](archive/toolset/output/giant-engine-circulation-03/color-coded-direction-report.json) records the saved layout.

## Structural failures and mounting correction

The first generated vehicle looked connected but lost nine parts on spawn: idle control75, starter key83, inverter124, shift tank127 and port128, valves130/131 and vents132/133. Electric starter motor62 remained. Frame/panel attachment must be checked independently of hoses, controls and power. Some new panels faced downwards rather than supporting parts above them.

The conservative native-informed attachment audit predicted the exact missing set. Correcting winding and adding explicit mounting frame contacts resolved this assembly. [structural_mounts.py](archive/toolset/structural_mounts.py) covers cardinal frames, rectangular panels and axis-aligned beam spans; unsupported inclined/complex geometry still needs investigation. Never infer attachment from a single body ID or a cable.

## Why the gearbox would not shift

Several faults were investigated in sequence. The moved lever established user input reached the shifter, not that commands reached or correctly selected pneumatic valves. The lit-0 display also failed to establish program execution: diagnostic conditions later showed an editor type error. Explicit integer comparisons fixed that diagnostic.

The correct saved valve mapping is common=1, activated=2, resting=3. Native construction passes gas-node ordinals0/1/2 through a definition lookup; an earlier attempt treated them as absolute indexes and depleted precharge. Keep those namespaces separate.

Even with ports fixed, raw +1 and inverted −1 activated both valves because native thresholded input responds to either sign above magnitude0.75, with a central reset interval. Simultaneous up/down prevented engagement. The accepted fix uses two native mechanical Max junctions:

```
up valve request   = max( shifter, 0)
down valve request = max(-shifter, 0)
```

Only one valve now sees positive1; the other receives0. The user's successful diagnostic save records SawGear=true and SawBothValves=false, and the user confirmed gears1/2 and reverse indication. [Operating diagnostic snapshot](archive/toolset/output/shift-repair/shifting-success-no-drive.data) preserves that evidence. No extra shift microcontroller is necessary.

The pneumatic system has finite precharge. Geometry-derived chamber capacity differs from fields that merely scale geometry. For the accepted layout, each large gearbox shift chamber is approximately0.536165 native volume units, tank geometry9.694431, and the stored precharge contents sum to80. Do not call the stored80 an80-L geometric tank. An automatic air replenishment system was not added or tested.

## Gear indicator and the final no-drive cause

Powered microcontroller134, electric/data ports135/136/137, numeric display138 and reverse lamp139 provide the indicator. Keep power connected to battery82 upstream of the starter relay. The clean script is:

```
on_tick
{
    in Gear.display_value = to_fractional (out DriveGearbox.current_gear)
    in Gear.is_illuminated = true
    in Reverse.is_illuminated = out DriveGearbox.current_gear < 0
}
```

The numeric display shows0/1/2; negatives clamp to0, so reverse has its own red lamp. Data aliases must resolve on the powered network.

The save that shifted but did not move showed the engine running around36.31 rps and the handbrake ON. Handbrake simultaneously brakes all four wheels and disconnects rear differential drive. Key1 released it and the user confirmed movement, then said “Everything seems to work now.” This was the final drive blockage in that test, not evidence that the fixed gearbox failed again.

The clean103-part file removes three temporary logging ports140/141/142 from the successful106-part diagnostic vehicle, retains positive-only selectors143/144, restores neutral/handbrake ON and precharges shift air. See [clean native file](archive/toolset/output/shift-repair/20261016-100456/Giant_Engine_Test_Vehicle_01.data), [metadata](archive/toolset/output/shift-repair/20261016-100456/Giant_Engine_Test_Vehicle_01.meta), [acceptance report](archive/toolset/output/shift-repair/20261016-100456/report.json) and [controls](archive/toolset/output/shift-repair/20261016-100456/CONTROL-GUIDE.md). User confirmation covers shifting, indication and movement; sustained driving, handling and endurance remain untested.
