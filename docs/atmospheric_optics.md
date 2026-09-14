# Atmospheric Optics: Dust Attenuation at 975nm

## The claim that needed checking

The original architecture spec states "975nm light suffers virtually
zero atmospheric scattering in Mars' thin 95% CO2 atmosphere at ~610Pa."
That's **true for the gas phase** — Rayleigh scattering from CO2
molecules at this pressure and wavelength is genuinely negligible. It is
**not true for suspended dust**, which is present in the Martian
atmosphere essentially always, at a level that varies from "background
haze" to "planet-obscuring global storm." The spec conflated two
different attenuation mechanisms; only one of them is actually
negligible.

## Beer-Lambert attenuation

Transmission `T = exp(-tau)`, where `tau` is the dust optical depth
along the beam path (a real, measured Mars atmospheric quantity, not a
modeled abstraction — dust optical depth has been tracked by every
Mars lander/rover mission since Viking).

| Optical depth (tau) | Transmission | Power loss | Typical condition |
|---|---|---|---|
| 0.3 | 74.1% | 25.9% | Clear-ish day, background dust loading |
| 0.5 | 60.7% | 39.4% | Typical seasonal dust loading |
| 1.0 | 36.8% | 63.2% | Regional dust event |
| 2.0 | 13.5% | 86.5% | Severe regional storm |
| 5.0 | 0.7% | 99.3% | Global dust storm (comparable to what ended Opportunity's mission in 2018) |

Two consequences follow directly:

1. **There is no such thing as a zero-loss baseline.** Even on an
   ordinary day, tau~0.3-0.5 is typical — a 26-39% power loss that the
   original spec's "near-zero loss" framing did not budget for at all.
   Every power/thermal calculation in this repo (Modules 1-4) should
   carry an explicit dust-loss margin, not assume free-space
   propagation. Recommended baseline design margin: **size hub
   transmitter power assuming tau=0.5** (60.7% transmission) as the
   "normal operations" case, not tau=0.
2. **Global storms don't attenuate the beam a little — they kill it.**
   At tau=5 (documented on Mars), 99.3% of the beam is lost. There is no
   power-budget fix for this; the link should be assumed **unavailable**
   during a declared global dust storm, for both the dock and corridor
   trickle tiers, regardless of hub power source. (Fission hubs solve
   the "hub has no power" half of the dust-storm problem from ADR-001 —
   they do NOT solve "the beam can't get through the dust" half. These
   are separate failure modes and only one of them was addressed.)

Wavelength dependence: Martian dust particles (~1-2 micron effective
radius) scatter somewhat less efficiently in the NIR than in visible
light (Mie scattering regime, size parameter of order 1 at 975nm), so
NIR optical depth is generally lower than the visible optical depth
usually reported by mission dust-monitoring instruments — but "lower"
is not "negligible," and the exact NIR/visible ratio needs a real
literature value, not an assumption. **Flagged for validation.**

## Design consequence: storm-safing target

Given the beam is assumed unavailable during a global storm, the
vehicle's day/night thermal survival system (`thermal_management.py`,
ADR-002) needs to survive a storm's duration on stored thermal capacity
alone, not just get through one ordinary night. Global Mars dust storms
have historically lasted on the order of weeks; a **partial mitigation
target of 3 sols (73.8 hours) of zero-beam survival** is adopted here as
a first design point — enough to ride out a storm's onset while other
contingencies (return to a sheltered dock, draw down reserve supercap
energy, accept a longer full outage) are activated, not a claim that 3
sols covers every storm.

Re-sizing the PCM thermal buffer (from `thermal_management.py`) against
this target:

| Storm-safing target | Insulation U (W/m²K) | PCM mass required |
|---|---|---|
| 1 sol | 0.05 | 21.6 kg |
| 1 sol | 0.10 | 43.2 kg |
| 3 sols | 0.05 | 64.8 kg |
| 3 sols | 0.10 | 129.5 kg |
| 3 sols | 0.15 | 194.3 kg |
| 5 sols | 0.05 | 107.9 kg |
| 5 sols | 0.10 | 215.9 kg |

**Decision:** adopt the 3-sol target at U≤0.10 W/m²K as the design
point — **~130kg PCM**, up from the day-only baseline of ~31kg
(`thermal_management.py`). This is a real, non-trivial mass addition,
and it is the direct, honest cost of taking dust-storm risk seriously
rather than assuming it away. Beyond U=0.15, PCM mass balloons past
~195kg for the same 3-sol target — this reinforces MLI insulation
quality as the single highest-leverage thermal investment in the whole
vehicle, not a detail to defer.

## Hop-length-dependent transmission (added — ADR-005)

The tau=0.3-0.5 / tau=4-6 figures above are *vertical column* optical
depths — the quantity Mars missions actually report, from near-vertical
Sun-photometer measurements. AEST's beam path is a near-*horizontal*
corridor link close to the surface. Applying the column tau directly to
the (original) 10km hop, as the table above does, only works because Mars's
dust vertical scale height happens to be **H = 11.1km**
[NTRS 20160013317] — close to that original hop length. For a shorter or
longer hop, a horizontal extinction coefficient is needed:

```
beta_0 = tau_vertical / H          (near-surface extinction, 1/m)
tau_horizontal(L) = beta_0 * L     (L << H, true for every hop considered)
T(L) = exp(-tau_horizontal(L))
```

| Hop length | T, normal (tau_v=0.4) | T, global storm (tau_v=5.0) |
|---|---|---|
| 10 km (original) | 69.7% | **1.1%** (full outage) |
| 5 km | 83.5% | 10.5% |
| 3 km | 89.8% | 25.9% |
| 2 km | 93.0% | 40.6% |
| 1.5 km | 94.7% | 50.9% |
| 1 km | 96.5% | 63.7% |
| 0.5 km | 98.2% | 79.8% |

Full derivation and the accompanying hub-density economics trade in
`simulations/corridor_economics.py` (Module 5). Key finding: shortening
the hop barely changes *normal-day* transmission (a secondary effect)
but transforms *storm* behavior from a hard outage into graded
degradation — this is the real case for shortening the hop, and it is a
resilience/uptime argument, not a per-photon-efficiency one. See
ADR-005 for the full hop-length recommendation (~3km) and its capital-
cost cost (roughly 2.5x more hub reactor units than the 10km baseline
for a fixed corridor length — a real, honestly-stated trade, not a free
win).

## Open items

1. Get a real NIR-specific dust optical depth dataset (rover
   Sun-photometer or orbital data) instead of assuming a visible/NIR
   ratio.
2. Decide the actual storm-safing target with real mission-ops input
   (3 sols is a starting point, not a validated requirement).
3. Determine whether corridor operations should have an automatic
   "storm mode" that pre-emptively routes rovers to shelter/dock when
   optical depth crosses a threshold, rather than discovering the link
   is down mid-transit.
