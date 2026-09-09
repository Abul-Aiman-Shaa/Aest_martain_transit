# ADR-005: Hop-Length Selection and Multijunction (VMJ) Receiver Adoption

**Status:** Accepted
**Date:** 2026-09-09
**Deciders:** Abul Aiman Shaa, Claude (systems engineering collaborator)

## Context

The user proposed a single change bundling two distinct claims: shorten
hub-to-hub beaming distance (away from the original 10km, ADR-001) to be
"much closer... economical," AND raise PV receiver efficiency above 50%
via "modular" power beaming with "multiple intake ports" — while
explicitly flagging that the latter might reintroduce the beam-pointing
complexity ADR-003 had just resolved. This ADR records the literature
research and physics done to evaluate both claims, and finds they are
**independent questions with independent answers**, not one architectural
change.

## Decision

### 1. The PV-efficiency gap is closed by a receiver-technology swap, not by hop length or multiple beams

Adopt a **vertical multi-junction (VMJ) receiver** — several
photovoltaic subcells connected in series within ONE receiver chip, fed
by ONE beam — in place of the single-junction InGaAs assumption used
through ADR-004. Real literature (`docs/literature_review.md` #9)
demonstrates 59-67% efficiency at 808-811nm, robust across both high
intensity (30-242 W/cm²) and low intensity/partial illumination (down
to ~7% area coverage, ~2 percentage points of efficiency loss). The
"multiple intake ports" the user intuited maps onto multiple **subcells
inside one receiver**, not multiple **transmitters** — this closes the
efficiency gap with *zero* new beam-pointing complexity, directly
answering the user's own stated concern.

`photon_conversion.py` v4 adds this as a second scenario pair —
`PV_EFF_MULTIJUNCTION_CONSERVATIVE = 0.45`, `PV_EFF_MULTIJUNCTION_TARGET
= 0.60` — alongside (not replacing) ADR-004's single-junction pair
(0.25/0.50). At the standard 4m² corridor-trickle radiator, the
multijunction-target scenario delivers ~3500W at wheels — for the first
time, enough to cover the assumed 3000W average cruise draw without
drawing on the supercap bank at all (`supercap_sizing.py` v3). The
multijunction-conservative scenario (~1909W) does not fully close the
gap but roughly doubles the single-junction-conservative figure (~778W).

`beam_tracking_sim.py` v2 verified the remaining concern directly rather
than assuming it away: does the smaller, higher-intensity spot needed to
enter the multijunction efficiency band cost ADR-003's tracking margin?
**No** — a 16.8cm spot (needed to reach 30 W/cm² at the corridor
trickle's received power) gives 67 microradians of geometric margin,
*better* than ADR-003's 0.6m/45-microradian baseline, because margin
scales with receiver-minus-spot clearance, which grows as the spot
shrinks. This is a genuine, checked result, not an assumption.

### 2. Hop length is shortened for storm resilience, not for capital economy or PV efficiency — and the capital cost is real

`corridor_economics.py` (new Module 5) modeled Mars dust attenuation as
a function of horizontal path length for the first time, using the dust
vertical scale height H=11.1km (`docs/literature_review.md` #10) to
convert the existing vertical-column optical depth figures into a
horizontal extinction coefficient. Two findings, both important, that
point in different directions:

- **Normal-day transmission barely changes with hop length** (69.7% at
  10km -> 89.8% at 3km -> 96.5% at 1km) — a real but secondary effect.
- **Storm transmission changes dramatically**: at the original 10km
  hop, a global dust storm (tau_v~5) leaves 1.1% transmission — a full
  outage, exactly what ADR-003 assumed. At 3km, the same storm leaves
  ~26% transmission — degraded, but alive. At 1km, ~64%.
- **Hub capital cost gets WORSE as hops shorten, not better.**
  Kilopower's 8kWe unit granularity means most hop lengths at or below
  ~5km round up to the same 3-reactor-unit-per-hub requirement — so the
  linear growth in hub COUNT as hops shorten is not offset by any
  further reduction in per-hub power. A 100km reference corridor needs
  ~40 total reactor units at 10km hops, ~100 at 3km, ~300 at 1km, ~600
  at 0.5km (`corridor_economics.py` [2]). **The user's own "it needs to
  be economical" framing does not survive contact with Kilopower's
  granularity if "economical" means hub capital cost** — this is the
  "challenge unviable physics" finding this ADR is obligated to state
  plainly, even though it complicates the user's own proposal.

**Decision: adopt ~3km as the new baseline hub-to-hub hop spacing** (2-5km
defensible range), justified specifically by storm-availability economics
(converting total outage into graded degradation for a modest ~2.5x hub
capital increase), NOT by capital efficiency or by any claimed link to PV
efficiency. Going shorter than ~2km buys comparatively little additional
storm margin for a steeply worse capital bill and is not recommended
without a dedicated $-costing exercise (see literature_review.md open
items).

## Options Considered

### Receiver-side "modularity"
- **A (rejected): literal multi-beam / multiple independently-tracked
  transmitters per hub.** Real literature (phased-array power beaming,
  e.g. lunar/cislunar concepts) supports this for mass/redundancy
  reasons, but it is not what closes the efficiency gap, and it
  reintroduces exactly the pointing complexity the user flagged as a
  cost. Not adopted as part of this efficiency fix; left open as a
  possible FUTURE addition for redundancy/multi-vehicle servicing, on
  its own separate merits.
- **B (accepted): single beam, multijunction (VMJ) receiver chip.**
  Closes the efficiency gap with no new tracking complexity; literature-
  validated at both high and low intensity and under partial
  illumination.

### Hop length
- **A (rejected): shortest hop tested (0.5-1km), maximizing dust-
    transmission and storm-resilience.** Marginal transmission gain over
    2-3km options at 3-15x the hub capital cost. Rejected as
    uneconomical on the same "be rigorous about economics" grounds the
    user themselves invoked.
- **B (rejected): keep the original 10km baseline.** Cheapest in hub
    capital, but leaves the corridor fully dark (1.1% transmission)
    during any global dust storm — the single-outage-mode risk ADR-003
    already flagged as the worst failure behavior in the architecture.
- **C (accepted): ~3km baseline (2-5km defensible range).** Converts
    storm outages to graded degradation (~26% transmission at 3km) for
    a real but bounded ~2.5x hub capital increase relative to 10km.

## Consequences

- **Good:** the PV-efficiency gap that ADR-004 called the single
  biggest open risk in the architecture is substantially narrowed by a
  receiver-technology decision that costs nothing in beam-pointing
  complexity — the multijunction-target scenario makes the corridor-
  trickle tier self-sufficient for the first time.
- **Good:** the "storm = full outage" failure mode from ADR-003 is
  converted from a hard binary into a graded-degradation behavior at
  the recommended ~3km hop spacing.
- **Bad, stated plainly:** total hub/reactor capital for a fixed
  corridor length rises by roughly 2.5x at the recommended 3km spacing
  relative to the original 10km baseline (about 100 vs 40 Kilopower-
  class units per 100km) — a real, non-trivial cost that the user's own
  "economical" framing did not anticipate would cut the other way on
  the capital axis. This is exactly the kind of finding this
  collaboration's mandate requires surfacing rather than smoothing over.
- **Good, dock tier:** because the multijunction receiver also applies
  at the dock, `thermal_management.py` v3 shows the day-tier PCM heat-
  spike requirement drops sharply under the multijunction-conservative
  scenario — but this does NOT reduce the vehicle's overall PCM mass
  budget, because night/storm-safing survival (unaffected by PV
  efficiency) becomes the binding constraint instead. A real
  architectural shift in which requirement drives PCM sizing, not a
  free mass win.
- No 975nm-specific multijunction data exists (same category of gap as
  ADR-004's #5), and the hub-density economics use a reactor-unit proxy,
  not real $ costing. Both are carried forward as open items.

## Action Items

1. [ ] Commission or fund 975nm-specific VMJ receiver characterization —
   supersedes ADR-004 action item #1 as the highest-value validation,
   now with a specific target technology (VMJ, not generic InGaAs).
2. [ ] Decide the target hop length within the 2-5km defensible range
   with a real $-costing exercise (reactor procurement, transmitter
   optics, structure, Mars launch mass) rather than the reactor-unit
   proxy used here — a programmatic choice, like ADR-004 action item #2.
3. [ ] Re-evaluate whether a literal multi-beam/phased-array transmitter
   is worth adding LATER for redundancy or multi-vehicle servicing —
   explicitly NOT required for the efficiency gain this ADR closes.
4. [ ] Re-derive `hardware_spec/receiver_ports.md` (not yet written) around
   the VMJ mosaic array, incorporating both the ADR-003 tracking-margin
   requirement and this ADR's intensity-window finding.
5. [ ] Revisit the day/night/storm PCM sizing end-to-end now that the
   binding constraint has shifted from day heat-spike toward night/storm
   survival under the multijunction dock scenario.

## Delivered this session

- `simulations/corridor_economics.py` (new — Module 5: hop-length dust
  transmission and hub-density economics)
- `simulations/photon_conversion.py` v4 (multijunction PV scenarios)
- `simulations/supercap_sizing.py` v3 (multijunction scenarios threaded
  through corridor-trickle and dock sizing)
- `simulations/thermal_management.py` v3 (multijunction dock PCM
  scenario, binding-constraint-shift finding)
- `simulations/beam_tracking_sim.py` v2 (intensity-vs-tracking-margin
  check that resolves the user's own pointing-complexity worry)
- `docs/atmospheric_optics.md` (hop-length-dependent transmission model)
- `docs/literature_review.md` #9-10 (multijunction receiver literature,
  Mars dust scale height)
- This ADR.
