# ADR-007: Gen 2 Action-Item Closure — Thermal, Bearings, Burst Safety, Coil Material

**Status:** Accepted
**Date:** 2026-09-14
**Deciders:** Abul Aiman Shaa

## Context

ADR-006 adopted the Gen 2 architecture (fission-fed dense coil clusters,
steel flywheel buffer, carbon-steel ISRU chassis) and left 7 explicit
action items open. This ADR closes out that action-item list as far as
literature research and first-principles analysis can take it. It does
**not** claim closure of items that genuinely require physical Mars
experimentation — those are restated as open below, not quietly dropped.

Four new artifacts back this ADR:
`simulations/thermal_management_gen2.py` (Module 8),
`simulations/coil_infrastructure_costing.py` (Module 9),
`hardware_spec/flywheel_safety_spec.md`, and
`hardware_spec/coil_cluster_spec.md`. Six new citation sections
(`docs/literature_review.md` §11–§16) support every decision below.

## Decisions

### 1. Thermal architecture re-derived for Gen 2 (closes Action Item #1)

Gen 1's thermal model was built around a PV receiver's waste heat during
a rare, long dock dwell — a spike needing PCM buffering — plus a 3-sol
storm-safing PCM margin, because the NIR beam went dark in dust storms.
Neither input applies to Gen 2. Module 8 re-derives from Gen 2's actual
heat sources (receiver/rectifier + flywheel round-trip loss) and finds
two structural simplifications, not assumed but discovered:

- **No storm-safing margin at all.** Near-field inductive coupling is
  not meaningfully attenuated by suspended dust (ADR-006 Decision 2) —
  there is no "link goes dark" case to size against. This eliminates the
  single largest PCM mass driver in the Gen 1 budget (~130kg).
- **The heat load is continuous, not spiky.** Frequent short coil-cluster
  passes (every few minutes at recommended spacing) average out
  thermally, unlike Gen 1's rare long dock event. This converts the
  day-side problem from "buffer a spike" (PCM) to "reject a continuous
  flow" (radiator) — smaller and simpler.

Result: a ~2m² steady-state radiator (vs. Gen 1's 10m² + 67.9kg day-PCM),
a night-only PCM requirement (single-digit to ~9kg depending on bay
target, same physics as Gen 1, unchanged), and zero storm-safing mass.
One open modeling input remains: `VEHICLE_SIDE_TRANSFER_LOSS_FRACTION =
0.50`, a flagged symmetric-split placeholder for primary/secondary
resonant-coupling loss (no source found gives a real split).

### 2. Coil conductor material: aluminum, not copper (partially closes Action Item #5)

Not previously flagged in ADR-006: copper is **not** credibly
ISRU-sourceable on Mars (~50ppm crustal abundance vs. Earth ore-grade
~10,000ppm — no confirmed concentrated deposit). Left unaddressed, this
would have reintroduced the exact Earth-import mass penalty this whole
pivot exists to escape, just for a different subsystem.

**Decision: aluminum windings.** This is not purely an ISRU
concession — aluminum is independently the *lighter* choice for equal
electrical resistance (a first-principles check, same discipline applied
to every other material decision in this repo), the same physics that
makes aluminum standard for terrestrial long-distance transmission
lines. Module 9 finds total conductor mass across a 100km corridor is a
few hundred kg even at the densest (200m) spacing evaluated — trivial
next to a single 6,000kg FSP reactor unit, confirming conductor material
is not the coil-cluster cost bottleneck. The real bottleneck — per-unit
power electronics and installation labor — remains uncosted and is
carried forward as open (see below).

### 3. Flywheel bearings: magnetic, not mechanical (closes Action Item #4)

Extends the same reasoning ADR-002 used to reject gearboxes for BLDC
motors: any oil/grease-lubricated bearing is a Martian-night failure
point across the -125°C to +50°C range. **Decision: magnetic bearings**
(AMB or hybrid active/passive), which have real spacecraft reaction-wheel
heritage (NTRS 19760020248). Cost stated plainly, not hidden: AMB needs
continuous power draw and control electronics this repo has not sized at
AEST's rotor scale, and that electronics package is — at least initially
— an Earth-sourced dependency, carried forward the same way the Mars
steel industry itself is (real, load-bearing, not assumed away).

### 4. Flywheel burst safety: prevention, not containment (closes Action Item #6)

An early instinct — wrap the rotor in a containment ring — does not
survive contact with real flywheel engineering practice. Sandia
(SAND2015-10759) states containment "would multiply the weight and cost
... defeating the objective of providing cost effective energy storage."
**Decision: prevention-based safety** — design margin 2.0 (burst stress
vs. maximum allowable operating stress), production rotors operated at
≤70% of qualification test speed. This also retroactively grounds Module
7's previously-arbitrary `REAL_WORLD_REALIZATION_FRACTION = 0.40`
discount in a real engineering source rather than an assumed fraction.

### 5. Hybrid flywheel + supercap buffer: evaluated, not adopted (resolves Action Item #7)

The flywheel alone already covers Module 6's gap-bridging requirement
(57–114kg at recommended 500m–1km spacing) with headroom. A hybrid system
would add a second storage technology's full set of failure modes and
qualification burden for a capability (faster response, more density)
this architecture does not currently need. **Not adopted.** Revisit only
if a future load case shows the flywheel alone is insufficient.

## What remains genuinely OPEN (not fabricated closed)

Two of ADR-006's seven action items **cannot** be closed by literature
research alone and are restated here, explicitly, rather than quietly
dropped:

- **Action Item #2 — spatially-resolved dynamic coupling efficiency
  profile.** Still bracketed only by two ORNL data points (static 91.3%,
  dynamic-midpoint ~50%-of-peak), not a validated curve across the full
  inter-coil transit. Requires either a real dynamic-WPT test rig or a
  detailed EM simulation this repo has not performed.
- **Action Item #3 — ISRU steel real mechanical/fatigue properties.**
  Directionally supported by lab-stage carbothermic-reduction literature,
  but real tensile strength, fatigue life, and flywheel-grade
  homogeneity of Mars-regolith-derived steel cannot be resolved without
  actual Mars-representative smelting and material-testing experiments.

New open items surfaced this round (tracked here, not silently absorbed):

1. Per-cluster power electronics (inverter, resonant tuning capacitors,
   control system) are entirely uncosted — likely the real coil-cluster
   cost driver, not conductor mass (Module 9).
2. `VEHICLE_SIDE_TRANSFER_LOSS_FRACTION = 0.50` is an unsourced symmetric
   placeholder (Module 8).
3. AMB control-electronics mass/power draw at AEST's rotor scale is
   unquantified; AMB vs. PMB trade study deferred until real rotor
   mass/dynamics exist (`flywheel_safety_spec.md`).
4. Mars regolith aluminum ISRU-extractability *at coil-winding scale*
   (not just mineral presence) is unconfirmed — same category of
   dependency as the steel-chassis precondition in ADR-006.
5. Cable-run distribution losses from the centralized FSP plant to each
   coil cluster are not modeled; Module 6's chain efficiency starts at
   "grid," after distribution.
6. No burst kinetic-energy-vs-occupant-safety-distance analysis performed
   for crewed vehicle variants — deferred to a future crew-safety pass.

## Consequences

- The repository's Gen 2 thermal, materials, and safety subsystems are
  now internally consistent and citation-backed to the same standard as
  Gen 1.
- Every file that referenced "ADR-007" by name prior to this document's
  existence (`hardware_spec/flywheel_safety_spec.md`,
  `hardware_spec/coil_cluster_spec.md`,
  `simulations/coil_infrastructure_costing.py`,
  `simulations/thermal_management_gen2.py`,
  `docs/literature_review.md` §11–§16) now resolves correctly.
- Two action items remain open by necessity, not oversight — they mark
  the genuine boundary between what literature research can settle and
  what requires physical Mars-representative experimentation. Closing
  them later should be done with real test data, not further literature
  synthesis.

## Delivered this round

- `simulations/thermal_management_gen2.py` (Module 8)
- `simulations/coil_infrastructure_costing.py` (Module 9)
- `hardware_spec/flywheel_safety_spec.md`
- `hardware_spec/coil_cluster_spec.md`
- `docs/literature_review.md` §11–§16
- This ADR
