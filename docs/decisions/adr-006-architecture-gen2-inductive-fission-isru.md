# ADR-006: Architecture Generation 2 — Dynamic Inductive Power Transfer, Centralized Fission, ISRU Carbon-Steel Vehicles

**Status:** Accepted
**Date:** 2026-09-10
**Deciders:** Abul Aiman Shaa

## Context

A major pivot was proposed, reasoning from first principles about
Mars-side manufacturing scale rather than Earth-launch-mass economy:

1. Vehicle and station cost/weight should be minimized for **large-scale,
   reliable Mars manufacturing**, not Earth-launch efficiency.
2. Vehicles should be made of **carbon steel** — a material Mars can
   plausibly produce locally.
3. Stations, grounded along the route ("side-lane"), draw from a
   **centralized fusion reactor core** and supply energy to hundreds of
   cheap vehicles.
4. The **supercapacitor bank should be removed or replaced**.
5. Power should reach moving vehicles via **fields (e.g. magnetic)**
   instead of power-beaming, specifically because fields "can't be
   blocked out by Martian dust."

This ADR records the physics check run against each claim, and the
resulting architecture. Two claims needed real correction (not just
refinement) before anything could be built on them; three were sound and
are adopted, one with a significant geometric correction.

## Decision

### 1. Fusion is rejected; centralized fission (NASA/DOE Fission Surface Power) is adopted

No fusion reactor has been connected to an electrical grid anywhere, as
of 2026 — the most advanced private programs
(Commonwealth Fusion's SPARC, Helion) target first grid connections in
the **late 2020s to early 2030s**, on Earth, with full industrial
support, and the industry itself estimates needing tens of billions of
dollars more investment before a first commercial plant. A Mars-deployed
fusion reactor would need to be more mature, more compact, and more
autonomously maintainable than the first Earth-grid-connected unit —
there is no credible timeline for this within any planning horizon this
repo can responsibly design against. **This is a straightforward
"unviable physics" call, not a close judgment.**

**Decision: adopt NASA/DOE's Fission Surface Power (FSP) program as the
centralized source** — 40kWe per unit, under 6 metric tons, designed for
a 10-year operating life (1-year demonstration + 9 operational years),
explicitly scoped by NASA to extend from lunar demonstration to Mars
designs. This replaces Gen 1's per-hub Kilopower-class tiling
(ADR-002/005) with fewer, larger, centralized units — a better fit for
the original "centralized source" framing than the old distributed-hub
approach was.

### 2. Field-based transfer is sound — but the geometry had to be corrected first

Near-field magnetic (inductive resonant) coupling genuinely is
dust-immune, confirming the original intuition: magnetic fields are not
scattered by suspended particulates the way NIR light is (this was the
whole basis of Gen 1's dust-attenuation problem, ADR-003/005). Real
terrestrial precedent exists and is mature relative to laser power
beaming: ORNL has demonstrated static wireless EV charging up to 270kW,
with 91.3% DC-to-battery efficiency validated at 120kW.

**But the initial mental model carried over Gen 1's geometry** — discrete
stations kilometers apart, each independently serving a passing vehicle.
That does not transfer to a field-based mechanism. Collimated laser
light stays a tight beam over kilometers *because it is collimated*;
near-field inductive coupling has no such property. ORNL's own design
literature uses a rule of thumb of coil diameter ≈ 3x magnetic air gap
for useful coupling — for a vehicle-scale receiver coil (order of
0.5-1.5m), that puts the *useful* coupling range at meters, not
kilometers. **A field-based corridor cannot be sparse hubs; it has to be
a chain of coil clusters spaced far more densely than any Gen 1 hub.**

Further research also found the honest complication ORNL's own dynamic
(in-motion, not static-aligned) analysis reports: coupling strength dips
to ~50% of its peak value at the midpoint between adjacent primary coils
(70%-pitch spacing case) as a vehicle passes overhead — dynamic transfer
is not a flat, constant-efficiency process the way a tracked laser spot
was designed to be (ADR-003).

**Decision: adopt sparse coil clusters (not continuous track), spaced
using the onboard flywheel (Decision 3) to bridge the powerless gaps
between them.** `simulations/inductive_transfer_sim.py` (Module 6) shows
even a 1km powerless gap costs only ~215Wh of flywheel energy to
cross — trivial against a bank sized in the hundreds of Wh — so cluster
spacing in the hundreds-of-meters-to-few-kilometers range is entirely
viable without approaching continuous track. This keeps clusters/100km
in the same order of magnitude as Gen 1's hub count (ADR-005: ~33-100
hubs/100km at 2-3km spacing), while each cluster is a simple coil
module — wire and a ferrite core, essentially — not a precision
laser/FSM/LiDAR installation. **This is a better match for the original
"reliable large-scale Mars manufacturing" goal than the literal
sparse-hub proposal would have been**, since coil modules are exactly
the kind of simple, repeated, low-precision component a nascent Martian
industrial base can plausibly mass-produce, unlike laser optics.

Grid-to-wheel chain efficiency (Module 6): static-aligned chain
efficiency is 76.4%; the adopted dynamic design value (bracketed,
flagged for validation) is 54.4%; even the conservative dynamic lower
bound is 38.2% — against Gen 1's 52.5% best case (multijunction-target
scenario, ADR-005). The dynamic design value already beats Gen 1's best
case, and even the conservative lower bound is in the same range.
**The entire photon-conversion efficiency problem that dominated
ADR-004/ADR-005 simply does not exist in this architecture** — there is
no PV cell, no quantum defect, no adjacent-wavelength literature gap to
bridge.

### 3. Steel flywheel replaces the graphene supercapacitor bank — roughly at parity on energy density, adopted for different reasons

`simulations/flywheel_buffer_sizing.py` (Module 7) computed steel
flywheel specific energy from first principles (e = K·σ/ρ, K=0.5 flat
disk, discounted 60% for real-world engineering margins) across a
tensile-strength sweep bracketing plausible ISRU steel quality:
conservative ISRU-grade (2.8 Wh/kg), good structural steel (5.7 Wh/kg),
high-strength steel (10.6 Wh/kg) — against the real graphene supercap
range of 6.8-11.1 Wh/kg (SkelCap D60, ADR-004). **This is honestly a
wash on energy density, not a decisive win either way** — stated
plainly rather than oversold.

**Decision: adopt the steel flywheel anyway, for reasons independent of
energy density:**
- **ISRU manufacturability**: steel, not an imported exotic graphene
  ultracapacitor product — consistent with the vehicle chassis material
  decision below.
- **Different, arguably simpler cold-temperature failure physics**: a
  flywheel's limits are bearing/material (brittle fracture toughness),
  not electrolyte chemistry — there is no equivalent of the unsupported
  -100°C supercap claim ADR-004 had to correct.
- Sized against Module 6's gap-bridging requirement, the bank comes out
  substantially SMALLER than Gen 1's 150kg baseline at the recommended
  spacing (57-114kg at 500m-1km cluster gaps vs. 150kg), because this
  buffer only bridges short gaps and damps transfer ripple rather than
  carrying the vehicle across multi-kilometer beam-free stretches.

Genuine open items carried forward, not smoothed over: ISRU steel's
real mechanical/fatigue properties are uncharacterized (lab-simulant
carbothermic-reduction experiments only, per `docs/literature_review.md`);
cold-temperature bearings (likely magnetic, to avoid the same
lubricant-freezing failure mode already flagged for gearboxes in
ADR-002) are undecided and need their own control electronics; and
burst-containment safety is a real hardware requirement, not modeled
here, analogous to ADR-003's beam-safety mandate.

### 4. Carbon-steel vehicle chassis — adopted, with the ISRU precondition stated plainly

Active 2025-era research (multiple ScienceDirect papers, CSIRO)
demonstrates pure iron and liquid iron-silicon alloy formation from Mars
regolith simulant via carbothermic reduction, using atmospheric CO2 as
the carbon source, at lab scale. This is real and directionally
supports the underlying vision, but it is **explicitly still experimental** —
none of the cited sources report a real-Mars-surface demonstration, at
scale, of the sort that would need to precede a Mars steel industry
capable of hull-quality material. **Decision: adopt carbon steel as the
target chassis material, with the Mars steel industry itself recorded as
a precondition/bootstrap dependency of this architecture, not an assumed
given.**

The underlying logic reversal is sound and worth stating
explicitly: Gen 1 implicitly optimized for Earth-launch mass efficiency
(minimize kg launched, accept exotic/lightweight materials). A vehicle
that is MANUFACTURED on Mars, not launched from Earth, is not subject to
the ~$10,000+/kg launch penalty at all — so optimizing for local,
reliable manufacturability (heavier but simple, ISRU-producible carbon
steel) over Earth-launch-mass efficiency is a legitimately different,
and for this vehicle, better-justified objective function. This reversal
is adopted as a standing design principle for AEST Gen 2, not just a
one-off material choice.

## What is superseded vs. carried forward from Gen 1 (ADR-001 through 005)

**Superseded** (Gen 1 mechanism-specific, kept in the repo as historical
record, not deleted):
- 975nm NIR laser beaming, wall-plug/dust-transmission modeling
  (`photon_conversion.py`, `corridor_economics.py`'s dust-optical-depth
  analysis, `docs/atmospheric_optics.md`)
- InGaAs/VMJ photovoltaic receivers and the whole PV-efficiency-gap
  question (ADR-004, ADR-005 Decision 1)
- LiDAR/FSM beam tracking and spot-matching (`beam_tracking_sim.py`,
  ADR-003 Decision 1)
- Graphene supercapacitor bank as primary storage (`supercap_sizing.py`
  — its bank-sizing METHOD remains a valid reference pattern, its
  material choice is superseded)
- Kilopower-tiled per-hub generation, hub-count-scales-with-corridor-
  length economics (ADR-005 Decision 2)

**Carried forward** (validated in Gen 1, still load-bearing in Gen 2):
- The two-tier power-delivery INSIGHT (peak power ≠ average power;
  storage handles bursts, generation/transfer handles average energy
  replenishment) — now expressed as coil-cluster transfer + flywheel
  buffer, the same underlying principle as ADR-001/002's corridor-
  trickle/dock split.
- BLDC in-wheel direct-drive motors (unchanged).
- PCM+MLI day/night/storm-safing thermal architecture (unchanged in
  method; will need re-derivation against Gen 2's heat-load profile —
  see Action Items).
- Fission over any more exotic centralized source (upgraded from
  Kilopower-class to FSP-class for a genuinely centralized architecture,
  not overturned).
- The core project discipline: cite real literature, carry conservative-
  vs-target scenarios rather than one confident number, and state
  capital/mass costs honestly even when they complicate the original
  proposal.

## Consequences

- **Good:** the single biggest unresolved risk carried through ADR-004/
  005 (the PV-efficiency gap) is eliminated by construction — there is
  no photovoltaic conversion step in this architecture at all.
- **Good:** dust-storm outage risk (ADR-003's worst-case finding) is
  structurally avoided rather than mitigated — magnetic coupling is not
  materially attenuated by suspended dust the way NIR light is.
- **Good:** reactor sizing decouples from corridor length entirely
  (Module 6) — it now scales with concurrent fleet size, which is
  arguably the more natural sizing driver for "hundreds of vehicles."
- **Real, stated cost:** the coil-cluster infrastructure, even sparsely
  spaced, is a large-QUANTITY buildout (hundreds to low-thousands of
  units per 100km depending on chosen spacing) — a fundamentally
  different capital profile than Gen 1's few-dozen hubs, trading unit
  complexity for unit count. Whether this is cheaper overall depends on
  real per-unit coil manufacturing cost, which this repo has not costed
  (same category of open item as ADR-005's hub-economics caveat).
- **Real, unresolved dependency:** this entire architecture assumes a
  functioning Mars steel industry exists to build both the vehicles and
  (implicitly) much of the coil/cluster hardware — a precondition, not
  a detail, and worth carrying forward explicitly rather than assuming.
- Thermal management (`thermal_management.py`) needs re-derivation:
  Gen 2's heat-load profile is dominated by coil/rectifier/flywheel
  losses, not a PV receiver's waste-heat fraction — the existing PCM
  sizing logic is structurally reusable but its inputs are now wrong.

## Action Items

1. [ ] Re-derive `thermal_management.py` against Gen 2's actual waste-heat
   sources (coil/rectifier I²R losses, flywheel windage/bearing losses)
   instead of the Gen 1 PV-receiver heat-spike model.
2. [ ] Find or commission a real spatially-resolved dynamic coupling
   efficiency profile (not just the two ORNL bracket points used here)
   to replace `inductive_transfer_sim.py`'s flagged 65% design-value
   placeholder.
3. [ ] Characterize real ISRU steel mechanical properties (tensile
   strength, fatigue life) once a Mars-representative smelting process
   exists — both the vehicle chassis and flywheel rotor depend on this.
4. [ ] Decide the cold-temperature flywheel bearing solution (magnetic
   bearings vs. an alternative) and its control-electronics dependency.
5. [ ] Cost the coil-cluster infrastructure buildout in real terms
   (copper/iron mass, power electronics per cluster, cable run losses)
   to validate or overturn the "hundreds-of-meters spacing" recommendation
   — this repo used a reactor/flywheel-mass proxy, not $ or launch-mass
   costing, same open-item discipline as ADR-005.
6. [ ] Draft a burst-containment safety case for the flywheel bank,
   parallel to ADR-003's beam-safety requirement.
7. [ ] Revisit whether a hybrid buffer (small flywheel + small
   supercap) beats either pure option — not yet evaluated.

## Delivered this round

- `simulations/inductive_transfer_sim.py` (new — Module 6: dynamic
  inductive transfer chain efficiency, FSP reactor sizing vs. concurrent
  fleet size, coil-cluster gap-bridging economics)
- `simulations/flywheel_buffer_sizing.py` (new — Module 7: steel
  flywheel first-principles specific energy, bank sizing against
  Module 6's gap-bridging targets)
- This ADR.
