# AEST — Active Energy Supplied Transit

Open-source systems engineering for a zero-chemical-battery Mars surface
transit architecture. **Now on Generation 2 (ADR-006):** centralized
fission power delivered to moving carbon-steel vehicles via dynamic
inductive (near-field magnetic) coupling from trackside coil clusters,
buffered onboard by a steel flywheel, driving BLDC in-wheel motors.
Generation 1 (975nm NIR laser power beaming + InGaAs/VMJ photovoltaic
receivers + graphene supercapacitors) is preserved in full below and in
`docs/decisions/adr-001` through `adr-005` as a validated but superseded
design — not deleted, because its two-tier power-delivery insight and
its research discipline both carry forward into Gen 2.

## Why (unchanged across both generations)

Chemical batteries (Li-ion/LFP) are a poor fit for Mars surface transit:

- **Mass-to-orbit cost.** ~$10,000+/kg to land mass on Mars penalizes
  every kilogram of battery pack carried instead of payload.
- **Cryogenic failure.** Li-ion electrolytes degrade and can freeze at
  Martian surface temperatures (avg -60°C, down to -125°C).

Generation 2 adds a second, equally load-bearing principle (ADR-006):
**a vehicle manufactured on Mars, not launched from Earth, is not
subject to the Earth-launch mass penalty at all** — so optimizing for
local, reliable manufacturability (carbon steel, simple coil modules)
over Earth-launch-mass efficiency is a legitimately different, and for
this vehicle, better-justified objective function than Generation 1
implicitly used.

## Architecture at a glance — Generation 2 (current, ADR-006)

```
[ Centralized FSP Fission Plant, 40kWe/unit ]
                 │  (power distribution cable along the corridor)
                 ▼
[ Coil Cluster ]···gap···[ Coil Cluster ]···gap···[ Coil Cluster ]···  (~500m-1km pitch)
        │ (near-field inductive coupling, dust-immune)
        ▼
[ Vehicle pickup coil + rectifier ]
        │
        ├──────────────────────┐
        ▼                      ▼
[ Steel Flywheel Buffer ]   [ Thermal: radiator + night-PCM ]
   (bridges inter-cluster   (re-derived, ADR-007 — no
    gaps, damps ripple,     storm-safing, no day-PCM;
    burst power)            continuous not spiky load)
        │
        ▼
[ BLDC in-wheel direct-drive ]
        │
        ▼
[ Carbon-steel chassis (ISRU-manufactured) ]
```

- **Centralized source:** NASA/DOE Fission Surface Power (FSP)-class
  units, 40kWe each, <6 metric tons, 10-year design life — chosen over
  an initial fusion concept because no fusion reactor has reached grid
  connection anywhere as of 2026; earliest Earth commercial targets are
  late-2020s to early-2030s. Fission remains the only near/mid-term-real
  centralized nuclear option (ADR-006).
- **Transfer:** dynamic inductive (near-field magnetic resonant)
  coupling from sparse trackside coil clusters — genuinely dust-immune,
  unlike Gen 1's NIR beam, and structurally avoids the dust-storm
  full-outage failure mode that was Gen 1's worst-case risk (ADR-003).
  Clusters are spaced hundreds of meters to a few kilometers apart, NOT
  continuously along the route and NOT kilometers-apart like Gen 1's
  hubs — near-field coupling range is set by coil size (meters), so the
  onboard flywheel is what bridges the gaps between clusters, not the
  field itself (ADR-006, `simulations/inductive_transfer_sim.py`).
- **Storage:** steel flywheel, roughly at parity with Gen 1's graphene
  supercapacitor bank on energy density (not a decisive upgrade there),
  adopted instead for ISRU manufacturability and simpler cold-failure
  physics (mechanical, not electrochemical) — see
  `simulations/flywheel_buffer_sizing.py`.
- **Vehicle structure:** carbon steel, chosen for local Mars
  manufacturability rather than Earth-launch mass efficiency — real,
  active (if still lab-stage) ISRU carbothermic-reduction research
  supports this being physically achievable, with the Mars steel
  industry itself recorded as a precondition, not an assumed given
  (ADR-006).
- **Traction:** BLDC in-wheel direct-drive motors — carried forward
  unchanged from Gen 1 (ADR-002).
- **Thermal:** re-derived from Gen 2's actual heat sources
  (coil/rectifier + flywheel losses, not a PV receiver's waste heat) —
  closes ADR-006 Action Item #1. Night-survival physics (MLI, PCM) is
  unchanged from Gen 1; storm-safing PCM is dropped entirely (dust
  doesn't block coupling) and the day-side problem shrinks from
  "buffer a spike" to "reject a continuous flow" — a ~2m² radiator vs.
  Gen 1's 10m² + 67.9kg day-PCM (ADR-007,
  `simulations/thermal_management_gen2.py`).

## Status — Generation 2

| Module | File | Status |
|---|---|---|
| Dynamic inductive transfer chain efficiency, FSP reactor sizing, coil-cluster gap economics | `simulations/inductive_transfer_sim.py` | done (v1, new — Module 6) |
| Steel flywheel first-principles sizing | `simulations/flywheel_buffer_sizing.py` | done (v1, new — Module 7) |
| Thermal re-derivation for Gen 2 heat sources | `simulations/thermal_management_gen2.py` | done (v1, new — Module 8, closes Action Item #1) |
| Coil conductor material & mass costing | `simulations/coil_infrastructure_costing.py` | done (v1, new — Module 9, partially closes Action Item #5 — power electronics still uncosted) |
| Flywheel bearing selection & burst-safety philosophy | `hardware_spec/flywheel_safety_spec.md` | done (v1, closes Action Items #4, #6, resolves #7) |
| Coil-cluster hardware requirements | `hardware_spec/coil_cluster_spec.md` | done (v1) |
| Dynamic coupling efficiency profile (real, spatially-resolved) | — | **open — Action Item #2, requires test rig or EM simulation** |
| ISRU steel mechanical property characterization | — | **open — Action Item #3, requires physical Mars-representative smelting** |

**Key Generation 2 findings** (full derivation in `docs/decisions/adr-006...md`):

- **Fusion rejected, fission adopted** — not a close call. No fusion
  reactor has reached grid connection as of 2026; a Mars deployment
  would need to lag Earth maturity further still.
- **My initial "stations spaced as required by physics" mental model
  needed a geometric correction, not just a mechanism swap.** Near-field
  magnetic coupling has nowhere near a laser beam's range — useful
  coupling is meters, not kilometers, so field-based transfer requires a
  dense CHAIN of simple coil clusters, not sparse hubs. This correction
  turns out to serve the underlying manufacturing-scale goal *better*
  than the original concept would have: many simple, mass-producible
  coil modules beat few complex precision hubs on exactly the criterion
  this pivot was optimizing for.
- **The onboard flywheel, not continuous track, is what makes sparse
  coil-cluster spacing viable** — even a 1km powerless gap only costs
  ~215Wh of flywheel energy to bridge, trivial against a bank sized in
  the hundreds of Wh.
- **Reactor sizing decouples from corridor length entirely** — it now
  scales with concurrent fleet size, a structurally different (and
  arguably more favorable, for "hundreds of vehicles") economics
  profile than Gen 1's hub-count-scales-with-distance sizing (ADR-005).
- **The entire PV-efficiency-gap risk that dominated ADR-004/005 is
  eliminated by construction** — there's no photovoltaic conversion
  step in this architecture at all. Grid-to-wheel chain efficiency
  (38-76% depending on static/dynamic assumptions) beats Gen 1's best
  laser-chain case (52.5%) even at its conservative bound.
- **Steel flywheel vs. graphene supercap is honestly a wash on energy
  density** (2.8-10.6 Wh/kg depending on achievable ISRU steel quality,
  vs. 6.8-11.1 Wh/kg for the real supercap datasheet) — stated plainly
  rather than oversold. The real case for switching is
  manufacturability and cold-failure physics, not a capacity win.
- **The Gen 2 thermal re-derivation (ADR-007) found two structural
  simplifications, not just new numbers:** no storm-safing PCM margin
  is needed at all (dust doesn't block near-field coupling, unlike Gen
  1's NIR beam), and the heat load is continuous rather than spiky
  (frequent short coil passes vs. Gen 1's rare long dock dwell) — a
  ~2m² steady-state radiator replaces Gen 1's 10m² + 67.9kg day-PCM.
- **Copper is not ISRU-sourceable on Mars** (~50ppm crustal abundance
  vs. Earth ore-grade ~10,000ppm) — a real complication found, not
  assumed, this round. Resolved with aluminum windings, which are
  independently lighter for equal resistance regardless of the ISRU
  argument (ADR-007, Module 9). Total conductor mass across a 100km
  corridor is a few hundred kg even at the densest spacing evaluated —
  conductor material is not the coil-cluster cost bottleneck; uncosted
  power electronics likely are.
- **Flywheel burst safety follows real engineering practice
  (Sandia): prevention, not containment** — an early containment-ring
  concept was dropped once real sources showed it would defeat the
  point of the flywheel entirely. Design margin 2.0, operation at ≤70%
  of qualification speed (ADR-007).
- **Real, unresolved costs and dependencies, stated rather than
  smoothed over:** per-cluster power electronics are entirely uncosted;
  the whole architecture depends on a Mars steel industry that does not
  yet exist; ISRU steel's real mechanical properties are
  uncharacterized; the dynamic coupling efficiency profile is still
  only bracketed by two data points, not a validated curve; and AMB
  control-electronics power draw at AEST's rotor scale is unquantified
  (full list: ADR-007).

## Generation 1 — 975nm NIR Laser Beaming (superseded by ADR-006, preserved as validated history)

Gen 1's full architecture, findings, and 5 completed simulation modules
remain in the repository and are summarized here for reference. Nothing
below this line describes the current recommended design — see
Generation 2 above and ADR-006 for why, and for exactly which Gen 1
components carry forward (the two-tier insight, BLDC motors, PCM+MLI
*method*, fission-over-exotic-sources, and the research discipline
itself) versus which are superseded (the laser/PV transfer mechanism,
beam tracking, dust-optical-depth modeling, and the graphene
supercapacitor as the storage material).

### Gen 1 architecture at a glance

```
[ Fission Hub ]──(975nm NIR, corridor trickle, ≤10km LOS)──> [ Rover, moving ]
[ Fission Hub ]──(975nm NIR, dock fast-charge, short range)─> [ Rover, parked ]
                                                                     │
                                                          [ InGaAs/VMJ receiver ]
                                                                     │
                                              ┌──────────────────────┴──────────────────────┐
                                              │                                              │
                                   [ Graphene Supercap Bank ]                    [ PCM buffer + LHP ]
                                              │                                   (day: absorbs dock heat spike
                                   [ Power Electronics, SiC/GaN ]                  night: releases it as cabin/
                                              │                                    electronics keep-alive heat)
                                   [ BLDC in-wheel direct-drive ]
```

### Gen 1 status

| Module | File | Status |
|---|---|---|
| Photon-to-electron chain efficiency | `simulations/photon_conversion.py` | done (v4, multijunction scenarios added) |
| Supercap bank sizing (power vs. energy, dock power, sortie range) | `simulations/supercap_sizing.py` | done (v3, multijunction scenarios added) |
| Day/night thermal survival cycle | `simulations/thermal_management.py` | done (v3, multijunction dock scenario added) — inputs now superseded, see Gen 2 Action Item #1 |
| Beam divergence, spot/receiver matching, corridor hand-off | `simulations/beam_tracking_sim.py` | done (v2, intensity/margin trade added) |
| Hop-length dust transmission & hub-density economics | `simulations/corridor_economics.py` | done (v1) |
| Dust attenuation & storm-safing thermal target | `docs/atmospheric_optics.md` | done, hop-length model added |
| Terrain line-of-sight masking methodology | `docs/route_planning.md` | scoped, not executed (needs orbital terrain data) |
| Literature validation of open parameters | `docs/literature_review.md` | done (10 items) |

### Gen 1 key findings (full derivations in `docs/decisions/`)

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
  night thermal battery at the rest (ADR-002).
- Minimizing beam spot size (diffraction-limited) creates an
  unnecessarily hard pointing problem. Deliberately matching spot size
  to ~40% of receiver diameter gives 15-50x more tracking margin for a
  manageable flux cost (ADR-003).
- The "near-zero atmospheric loss" claim holds for CO2 gas but not for
  suspended dust, which costs 26-39% of beam power even on an ordinary
  day and effectively kills the link during a global storm (ADR-003) —
  the specific failure mode Gen 2's field-based transfer structurally
  avoids.
- **Literature validation (ADR-004) turned up the single biggest open
  risk in Gen 1:** real laser-power-beaming field demonstrations
  (DARPA POWER, 2025) show only ~20-25% optical-to-electrical PV
  efficiency, versus the 45-50% originally assumed.
- **The architecture's own claimed -100C supercap floor did not survive
  a literature check** — corrected to -40C baseline throughout.
- Real component data (Skeleton Technologies SkelCap D60 datasheet)
  anchors supercap specific energy (6.8-11.1Wh/kg) and specific power
  (22.1-28.4, up to 80kW/kg).
- **A multijunction (VMJ) receiver substantially closed ADR-004's PV-
  efficiency gap with zero new beam-pointing complexity** (0.45
  conservative / 0.60 target scenarios, ADR-005).
- **Hop length and PV efficiency were independent design questions** —
  shortening hub-to-hub distance did not raise PV efficiency; it
  changed dust-storm resilience, at a real hub-capital cost (ADR-005).

## Repository layout

```
aest-mars-transit/
├── README.md
├── LICENSE
├── docs/
│   ├── decisions/
│   │   ├── adr-001-two-tier-power-architecture.md          (Gen 1)
│   │   ├── adr-002-efficiency-bldc-thermal-day-night.md     (Gen 1)
│   │   ├── adr-003-beam-tracking-and-dust-storm-resilience.md (Gen 1)
│   │   ├── adr-004-literature-validation.md                 (Gen 1)
│   │   ├── adr-005-hop-length-and-multijunction-receiver.md (Gen 1)
│   │   ├── adr-006-architecture-gen2-inductive-fission-isru.md (Gen 2)
│   │   └── adr-007-action-item-closure-thermal-safety-materials.md (Gen 2 — current)
│   ├── literature_review.md       ✅ done — citations for all validated parameters (Gen 1 §1-10, Gen 2 §11-16)
│   ├── whitepaper.md              (planned — next phase, per project direction)
│   ├── atmospheric_optics.md      ✅ done (Gen 1)
│   └── route_planning.md          ✅ scoped (Gen 1, methodology reusable for Gen 2)
├── simulations/
│   ├── photon_conversion.py       ✅ done (v4) — Gen 1, superseded
│   ├── supercap_sizing.py         ✅ done (v3) — Gen 1, superseded
│   ├── thermal_management.py      ✅ done (v3) — Gen 1, superseded (see thermal_management_gen2.py)
│   ├── beam_tracking_sim.py       ✅ done (v2) — Gen 1, superseded
│   ├── corridor_economics.py      ✅ done (v1) — Gen 1, superseded
│   ├── inductive_transfer_sim.py  ✅ done (v1, new) — Gen 2, Module 6
│   ├── flywheel_buffer_sizing.py  ✅ done (v1, new) — Gen 2, Module 7
│   ├── thermal_management_gen2.py ✅ done (v1, new) — Gen 2, Module 8
│   └── coil_infrastructure_costing.py ✅ done (v1, new) — Gen 2, Module 9
├── hardware_spec/
│   ├── flywheel_safety_spec.md    ✅ done (v1) — Gen 2, bearings + burst safety
│   └── coil_cluster_spec.md       ✅ done (v1) — Gen 2, replaces Gen 1 receiver/transmitter-hub concepts
└── cad/
    └── rovers/                    (planned)
```

## Next priorities

1. **Find or commission a real spatially-resolved dynamic coupling
   efficiency profile** to replace `inductive_transfer_sim.py`'s
   flagged 65% design-value placeholder (ADR-006 Action Item #2,
   genuinely open — requires a test rig or EM simulation, not more
   literature research).
2. **Characterize real ISRU steel mechanical/fatigue properties** once
   a Mars-representative smelting process exists (ADR-006 Action Item
   #3, genuinely open — requires physical experimentation).
3. Cost per-coil-cluster power electronics (inverter, resonant tuning
   capacitors, control system) — the likely real cost driver, left
   uncosted by Module 9's conductor-mass-only analysis (ADR-007).
4. Quantify AMB control-electronics mass/power draw at AEST's actual
   rotor scale, and run the deferred AMB-vs-PMB trade study once real
   rotor dynamics exist (ADR-007, `flywheel_safety_spec.md`).
5. Confirm Mars regolith aluminum is ISRU-extractable at coil-winding
   scale, not just present in feldspar minerals (ADR-007).
6. Model cable-run distribution losses from the FSP plant to each coil
   cluster (currently out of scope — Module 6 starts at "grid").
7. Burst kinetic-energy-vs-occupant-safety-distance analysis for
   crewed vehicle variants (deferred, `flywheel_safety_spec.md`).
8. Whitepaper, CAD, and figures — next phase, once the above validation
   items are closed or explicitly accepted as open risks.

## License

MIT (see `LICENSE`).
