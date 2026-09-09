# AEST — Active Energy Supplied Transit

Open-source systems engineering for a zero-chemical-battery Mars surface
transit architecture: fission-powered ground hubs beam power to rovers
via 975nm NIR optical links, rovers store it in solid-state graphene
supercapacitors and drive on BLDC in-wheel motors.

## Why

Chemical batteries (Li-ion/LFP) are a poor fit for Mars surface transit:

- **Mass-to-orbit cost.** ~$10,000+/kg to land mass on Mars penalizes
  every kilogram of battery pack carried instead of payload.
- **Cryogenic failure.** Li-ion electrolytes degrade and can freeze at
  Martian surface temperatures (avg -60°C, down to -125°C).

AEST decouples power *generation* and *storage* from the vehicle, and
uses a storage medium (graphene supercapacitors) chosen for power
density, thermal tolerance, and cycle life rather than energy density —
deliberately, and with the consequences of that choice worked through
rather than glossed over (see `docs/decisions/`).

## Architecture at a glance

```
[ Fission Hub ]──(975nm NIR, corridor trickle, ≤10km LOS)──> [ Rover, moving ]
[ Fission Hub ]──(975nm NIR, dock fast-charge, short range)─> [ Rover, parked ]
                                                                     │
                                                          [ InGaAs receiver ]
                                                                     │
                                              ┌──────────────────────┴──────────────────────┐
                                              │                                              │
                                   [ Graphene Supercap Bank ]                    [ PCM buffer + LHP ]
                                              │                                   (day: absorbs dock heat spike
                                   [ Power Electronics, SiC/GaN ]                  night: releases it as cabin/
                                              │                                    electronics keep-alive heat)
                                   [ BLDC in-wheel direct-drive ]
```

- **Hubs:** fixed nuclear fission reactors (chosen over solar specifically
  because dust storms that block sunlight also scatter the optical
  beam — fission decouples hub power from atmospheric visibility and
  from day/night).
- **Two power tiers**, not one (ADR-001): a continuous low-power
  **corridor trickle** while driving, and a bounded-dwell **dock
  fast-charge** for full recharges. This is what makes the thermal and
  reactor-sizing math close — a single always-on full-power beam does
  not (see Module 1's original finding, preserved in the ADRs).
- **Storage:** solid-state graphene supercapacitor bank, sized for
  *energy* (range/buffering) — its *power* spec (10kW/kg) is so far
  above what a 50-100kW vehicle needs that bank mass is never
  power-constrained (ADR-002).
- **Traction:** BLDC in-wheel direct-drive motors — no gearbox, so no
  lubricant cold-tolerance failure mode across the -125°C to +50°C
  range (ADR-002).
- **Thermal:** a single PCM (phase-change material) buffer does double
  duty — absorbing the dock session's transient heat spike by day, then
  releasing that same stored heat overnight to keep electronics and the
  supercap bank above their rated floor (ADR-002).

## Status

| Module | File | Status |
|---|---|---|
| Photon-to-electron chain efficiency | `simulations/photon_conversion.py` | done (v4, multijunction scenarios added) |
| Supercap bank sizing (power vs. energy, dock power, sortie range) | `simulations/supercap_sizing.py` | done (v3, multijunction scenarios added) |
| Day/night thermal survival cycle | `simulations/thermal_management.py` | done (v3, multijunction dock scenario added) |
| Beam divergence, spot/receiver matching, corridor hand-off | `simulations/beam_tracking_sim.py` | done (v2, intensity/margin trade added) |
| Hop-length dust transmission & hub-density economics | `simulations/corridor_economics.py` | done (v1, new) |
| Dust attenuation & storm-safing thermal target | `docs/atmospheric_optics.md` | done, hop-length model added |
| Terrain line-of-sight masking methodology | `docs/route_planning.md` | scoped, not executed (needs orbital terrain data) |
| Literature validation of open parameters | `docs/literature_review.md` | done (10 items) |

**Key findings so far** (full derivations in `docs/decisions/`):

- Single-tier continuous full-power beaming is thermally infeasible
  (v1: 98m² radiator). Fixed by splitting into corridor-trickle +
  dock-fast-charge tiers (ADR-001).
- Peak vehicle power (50kW+) is supplied by the supercap bank
  discharging, not by real-time beam power — conflating the two in v1
  overstated the dock-hub reactor requirement by roughly 10x. Corrected
  sizing: ~5 Kilopower-class fission units per dock, not ~49 (ADR-002).
- Night thermal survival, unaddressed in the original spec, is solved
  for the common case (parking within fission-hub corridor coverage)
  at zero added hardware, and for the day's PCM buffer to double as a
  night thermal battery at the rest (ADR-002). A small radioisotope
  heater is documented as an optional contingency for off-corridor
  overnight sorties only — not standard equipment.
- Minimizing beam spot size (diffraction-limited) creates an
  unnecessarily hard pointing problem. Deliberately matching spot size
  to ~40% of receiver diameter gives 15-50x more tracking margin for a
  manageable flux cost — a 3cm transmit aperture, not a 30cm+ one
  (ADR-003).
- The "near-zero atmospheric loss" claim holds for CO2 gas but not for
  suspended dust, which costs 26-39% of beam power even on an ordinary
  day (tau~0.3-0.5) and effectively kills the link during a global
  storm (tau>=2). Modules 1-3's power budgets are pre-dust-margin,
  best-case numbers pending re-derivation at tau=0.5. Thermal survival
  is re-targeted to 3 sols of zero-beam storm-safing, needing ~130kg of
  PCM (up from 31kg day-only) at good insulation (ADR-003).
- **Literature validation (ADR-004) turned up the single biggest open
  risk in the architecture:** real laser-power-beaming field
  demonstrations (DARPA POWER, 2025) show only ~20-25% optical-to-
  electrical PV efficiency, versus the 45-50% the original spec (and
  this repo's earlier modules) assumed. All modules now carry BOTH a
  conservative (25%) and target (50%) scenario rather than one number.
  At the conservative end, the corridor-trickle tier can no longer
  cover assumed average cruise draw on its own — this is now the top
  unresolved risk, and it's a hardware R&D question, not a modeling one.
- **The architecture's own claimed -100C supercap floor did not survive
  a literature check** — no source supports it. Real hardware (Skeleton
  SkelCap D60) rates to -40C; the best documented cold-temperature
  research result is -75C with a ~50% capacity penalty. Corrected to
  -40C baseline throughout.
- Good news alongside the bad: the corrected, physically-proper MLI
  thermal model (effective emissivity, not an ad hoc U-value) produces
  LOWER night/storm heat-loss numbers than earlier estimated, and the
  day-tier PCM buffer now comfortably covers night survival AND the
  3-sol storm-safing target at once.
- Real component data (Skeleton Technologies SkelCap D60 datasheet) now
  anchors supercap specific energy (6.8-11.1Wh/kg) and specific power
  (22.1-28.4, up to 80kW/kg) — full citations in
  `docs/literature_review.md`.
- **A multijunction (VMJ) receiver — one beam, one chip, several
  series-connected subcells — substantially closes ADR-004's PV-
  efficiency gap, with zero new beam-pointing complexity.** Real
  literature demonstrates 59-67% efficiency, robust to both low
  intensity and partial/off-center illumination. Adopted as a second
  scenario pair (0.45 conservative / 0.60 target) alongside the
  single-junction pair. At the standard corridor radiator, the target
  scenario makes the corridor-trickle tier self-sufficient for the
  first time — no bank drawdown needed (ADR-005).
- **Hop length and PV efficiency are independent design questions —
  the user's own proposal conflated them, and separating them was this
  session's central finding.** Shortening the hub-to-hub distance does
  NOT raise PV efficiency; what it changes is dust transmission and,
  far more consequentially, dust-*storm* resilience: at the original
  10km hop a global storm leaves 1.1% transmission (full outage,
  ADR-003's assumption); at a recommended ~3km hop it leaves ~26%
  (degraded, not dead). The blunt trade-off, stated plainly: shorter
  hops COST MORE in hub/reactor capital (~2.5x more Kilopower-class
  units for the same corridor length at 3km vs. 10km) because
  Kilopower's 8kWe unit granularity outpaces the per-hub power savings.
  Recommended as a resilience/uptime investment, not a capital-
  efficiency one (ADR-005, `simulations/corridor_economics.py`).

## Repository layout

```
aest-mars-transit/
├── README.md
├── LICENSE
├── docs/
│   ├── decisions/
│   │   ├── adr-001-two-tier-power-architecture.md
│   │   ├── adr-002-efficiency-bldc-thermal-day-night.md
│   │   ├── adr-003-beam-tracking-and-dust-storm-resilience.md
│   │   ├── adr-004-literature-validation.md
│   │   └── adr-005-hop-length-and-multijunction-receiver.md
│   ├── literature_review.md       ✅ done — citations for all validated parameters
│   ├── whitepaper.md              (planned — next phase, per project direction)
│   ├── atmospheric_optics.md      ✅ done
│   └── route_planning.md          ✅ scoped (methodology only, needs orbital data)
├── simulations/
│   ├── photon_conversion.py       ✅ done (v4)
│   ├── supercap_sizing.py         ✅ done (v3)
│   ├── thermal_management.py      ✅ done (v3)
│   ├── beam_tracking_sim.py       ✅ done (v2)
│   └── corridor_economics.py      ✅ done (v1, new — Module 5)
├── hardware_spec/
│   ├── receiver_ports.md          (planned — mosaic PV array spec per ADR-003)
│   └── transmitter_hub.md         (planned — incl. beam-safety case per ADR-003)
└── cad/
    └── rovers/                    (planned)
```

## Next priorities

1. **Commission or fund 975nm-specific VMJ receiver characterization**
   (supersedes ADR-004's #1): no source at the actual operating
   wavelength exists for either single- or multi-junction receivers;
   808nm/1064nm/1470nm are the closest analogs. This remains the single
   highest-leverage validation AEST could do.
2. **Pick a hop length in the 2-5km range with a real $-costing
   exercise** (ADR-005 action item #2) — `corridor_economics.py` uses a
   reactor-unit proxy, not $, and the ~3km recommendation should be
   sharpened (or overturned) once real hub/reactor/optics cost data
   exists.
3. Re-derive Modules 1-3's power/thermal numbers with the tau=0.5 dust
   margin adopted in ADR-003, now combined with the chosen hop length's
   transmission figure from ADR-005/`corridor_economics.py`.
4. `hardware_spec/receiver_ports.md` and `transmitter_hub.md` — turn the
   VMJ mosaic-array (ADR-005), tracking-margin (ADR-003), and beam-
   safety requirements into concrete specs.
5. Re-derive end-to-end PCM sizing now that the multijunction dock
   scenario shifts the binding constraint from day heat-spike toward
   night/storm survival (ADR-005 action item #5).
6. Bring MOLA/HiRISE terrain data into `docs/route_planning.md` for a
   real LOS-chain validation once candidate corridor sites (and hop
   length) are chosen.
7. Whitepaper, CAD, and figures — next phase, once the above validation
   items are closed or explicitly accepted as open risks.

## License

MIT (see `LICENSE`).
