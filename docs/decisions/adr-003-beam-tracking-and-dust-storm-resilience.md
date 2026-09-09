# ADR-003: Spot-Matched Beam Tracking and Dust-Storm Thermal Resilience

**Status:** Accepted
**Date:** 2026-09-09
**Deciders:** Abul Aiman Shaa, Claude (systems engineering collaborator)

## Context

Two items were carried forward from ADR-001/ADR-002 as unresolved: build `beam_tracking_sim.py` realistically, and quantify the residual dust-storm risk flagged (but not sized) in ADR-002.

## Decision

### 1. Spot-matched beam design (not diffraction-limited)

A naive diffraction-limited beam is tight enough that a 30cm transmit aperture produces a ~6cm spot at 10km — impressive optics, but it turns pointing into a near-impossible problem (single-digit microradian tolerance to keep a 6cm spot on a 1.5m receiver). **Decision: deliberately size the spot as ~40% of the receiver diameter** (a design choice via a *smaller*, cheaper transmit aperture, ~3cm) rather than minimizing it. This gives ~45 microradians of real geometric tracking margin — 15-50x more forgiving than the diffraction-limited case — at a manageable flux cost (single-digit to tens of W/cm²). Consequence: receiver should be a **mosaic/tiled PV array** with independent cells and bypass diodes, not a single monolithic cell, so it produces power gracefully under partial/off-center illumination rather than requiring exact full-panel coverage.

Corridor hand-off (FSM slew rate, acquisition time) checks out comfortably against commercial hardware capability at any plausible hub standoff distance — not a bottleneck, provided the assumed hub-to-hub LOS overlap zone (500m, currently a placeholder) is validated against real terrain (see `docs/route_planning.md`, item 3 below).

**Beam safety is elevated to a hard, explicit requirement**, not modeled numerically but stated as non-negotiable: fail-safe cutoff on loss of retroreflector lock (default state OFF), exclusion zones sized to worst-case flux, and independent range-gating before firing. This belongs in `hardware_spec/` and any future safety case.

### 2. Dust attenuation is real and must be budgeted, not assumed away

The architecture's "near-zero atmospheric loss" claim is correct for CO2 gas (Rayleigh scattering) but does not cover suspended dust, which is present at some level essentially always on Mars. Beer-Lambert attenuation at typical background optical depth (tau~0.3-0.5) already costs 26-39% of beam power — this was not budgeted anywhere in Modules 1-3. **Decision: adopt tau=0.5 as the "normal operations" design margin** for all future power-budget work (supersedes the implicit tau=0 assumption in Modules 1-3; those modules' numbers should be understood as best-case, pre-dust-margin figures until revisited).

At storm-level optical depth (tau>=2), the link is not degraded, it is effectively dead (86-99%+ loss). **Decision: treat global dust storms as a full link outage, not a derated one**, for both corridor trickle and dock tiers, independent of hub power source (fission solves "hub has power" during a storm; it does not solve "the beam gets through," which is a separate physical mechanism).

### 3. Storm-safing thermal target

Since a storm means zero beam, the PCM+MLI night-survival system (ADR-002) must be re-sized to survive a storm, not just a night. **Decision: adopt a 3-sol (73.8h), zero-beam storm-safing target at MLI insulation U<=0.10 W/m²K**, requiring **~130kg of PCM** — up from the day/night baseline of ~31kg. This is accepted as a real, necessary mass cost of taking the risk seriously, and it sharpens (again) that insulation quality, not brute-force PCM mass, is the highest-leverage thermal lever: the same 3-sol target at U=0.15 nearly triples the PCM mass required (~194kg).

## Options Considered

### Beam spot sizing
- **A (rejected): diffraction-limited minimum spot.** Technically achievable but creates an unnecessary sub-2-microradian pointing requirement for no operational benefit.
- **B (accepted): spot matched to ~40% of receiver diameter.** Trades a modest, manageable flux increase for an order-of-magnitude easier tracking problem.

### Dust storm handling
- **A (rejected): ignore, per original spec's "near-zero loss" framing.** Contradicted by real Mars dust optical depth data.
- **B (accepted): budget tau=0.5 for normal ops, treat tau>=2 as full outage, size PCM for 3-sol storm-safing.** Honest about both the everyday cost and the storm-mode failure behavior.

## Consequences

- All prior power-budget figures (Modules 1-3) are now understood as pre-dust-margin, best-case numbers. Re-deriving them at tau=0.5 is a follow-on task, not done in this ADR.
- PCM mass grows from ~31kg (day-only) to ~130kg (day + 3-sol storm-safing) — a real vehicle mass increase that needs to be carried in any future mass budget rather than discovered late.
- Receiver hardware spec now has a concrete requirement (mosaic/tiled PV array) driven directly by the tracking analysis, not an arbitrary design preference.
- Beam safety is now an explicit, named requirement feeding `hardware_spec/`, not an implicit assumption.
- `docs/route_planning.md` is opened as a placeholder: the 500m hub-to-hub overlap zone and the whole LOS-chain concept depend on real Mars terrain data (MOLA/HiRISE) that has not yet been brought into this repository.

## Action Items

1. [ ] Re-derive Modules 1-3's power budgets at tau=0.5 dust margin (currently implicit tau=0).
2. [ ] Get a real NIR-specific Mars dust optical depth dataset; validate the assumed visible/NIR attenuation ratio.
3. [ ] Bring MOLA/HiRISE terrain data into the repo for real LOS-chain/viewshed validation (`docs/route_planning.md`).
4. [ ] Write `hardware_spec/receiver_ports.md` incorporating the mosaic/tiled PV array requirement from this ADR.
5. [ ] Draft an initial beam-safety case (interlock response times, exclusion zone sizing) for `hardware_spec/transmitter_hub.md`.
