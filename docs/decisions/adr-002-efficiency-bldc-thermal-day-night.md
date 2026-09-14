# ADR-002: Efficiency Chain Upgrade, BLDC Direct-Drive, and Day/Night Thermal Survival

**Status:** Accepted
**Date:** 2026-09-09
**Deciders:** Abul Aiman Shaa

## Context

Three design directives, all treated as decisions to make and document rather than open questions:

1. Graphene supercapacitors stay — Li-ion hybrid capacitors are closed, not reopened (confirms ADR-001 Option C rejection).
2. Overall architecture efficiency must improve, and the thermal management cycle must handle **both** Martian day (heat rejection) and night (heat retention) — the original spec addressed only the day/rejection side.
3. Traction motors are BLDC.

Working through these together surfaced a deeper problem with ADR-001's own dock-power number: it was derived by assuming beam power must instantaneously equal peak wheel power, which is the wrong model once an energy buffer (the supercap bank) exists. Fixing that turned out to matter more than any single component efficiency bump.

## Decision

### 1. Efficiency chain, v1 → v2

| Stage | v1 | v2 | Change |
|---|---|---|---|
| InGaAs PV | 48% | 50% | upper end of doc's own 45-50% target, flagged as an aggressive design goal needing cell-level R&D, not a demonstrated number |
| Supercap round-trip | 97% | 97% | unchanged |
| Power electronics | 95% | 97% | SiC/GaN motor controllers instead of generic assumption |
| Traction | 90% (generic motor+gearbox) | 93% (BLDC in-wheel direct-drive) | see below |
| **Chain total** | **39.8%** | **43.75%** | **+3.9 points** |

### 2. BLDC in-wheel direct-drive traction motors

Per direction, BLDC motors are adopted. Specifically **in-wheel (hub) direct-drive**, not a geared BLDC: this removes the gearbox stage entirely, which does two things at once — it improves the raw efficiency number (93% single-stage vs. ~90% for a motor+gearbox combination), and, more importantly for Mars, **it removes a lubricant cold-tolerance failure mode**. A gearbox needs lubricant that stays functional from -125°C to +50°C; grease viscosity/embrittlement at cryogenic Mars-night temperatures is a real, historically-relevant failure risk that the original spec never addressed. Direct-drive sidesteps it structurally rather than solving it with an exotic lubricant.

Consequence: peak torque at low speed is a real design constraint for in-wheel BLDC (they need more pole pairs / torque density than a high-speed geared motor), but this is a solved, mature commercial technology (EV in-wheel motors, robotics) — not a research risk.

### 3. Corrected dock-power derivation (the deeper fix)

ADR-001 flagged dock-hub reactor sizing (~49 Kilopower units) as the sharpest open problem. Re-deriving it against the right physical model resolves most of that:

- **Peak wheel power is supplied by the supercap bank discharging**, not by the beam in real time. At the architecture's own 10kW/kg specific-power spec, even a 5-10kg bank segment can supply 50-100kW bursts — peak power is essentially never the sizing constraint for a bank already sized for energy (below).
- **Dock/trickle beam power only needs to satisfy average energy replenishment** over a chosen duty cycle (dwell time), not match peak power instantaneously.

Re-sized this way (see `supercap_sizing.py`), a 150kg / ~20Wh/kg bank (3.0kWh) with a 30-minute full-recharge-from-empty dwell needs **~13.7kW optical, ~37.7kWe hub electrical demand, ~4.7 Kilopower-class units** — down from v1's ~49-unit figure by an order of magnitude, because the earlier number was answering the wrong question (peak power) rather than the right one (energy replenishment rate).

This is the single most consequential fix in this ADR: it turns dock-hub reactor sizing from "probably infeasible" into "a tractable, small fission cluster," without needing to compromise on the 50kW peak-performance capability at all.

### 4. Day/night thermal survival cycle

**Day (heat rejection, transient):** the dock session's waste heat (~6.9kW over 30min at the baseline sizing) exceeds what a rover-scale radiator (6m²) can reject in real time. A **Phase-Change Material (PCM) buffer** (~31kg, paraffin/salt-hydrate class, ~200kJ/kg latent heat) absorbs the excess during the dock session and bleeds it to the radiator via the LHP loop during the following corridor-trickle leg.

**Night (heat retention, continuous):** not addressed at all in the original spec. Resolution, in order of preference:

1. **Operational, zero new hardware:** park overnight within fission-hub corridor coverage. Hubs don't care about daylight — the trickle beam can keep running at token wattage through the night. Covers the overwhelming majority of nights for free, and was only possible because ADR-001 already chose fission over solar for hubs.
2. **Passive, zero *added* hardware:** the same PCM buffer sized for the day problem doubles as a night thermal battery (it was charged/melted by the day's dock heat). At good MLI insulation (U~0.05-0.10 W/m²K, realistic for a well-executed multi-layer blanket), the ~31kg PCM's ~1.7kWh latent capacity covers a full 12.3-hour Mars night's heat loss (~600Wh) with margin. At poorer insulation (U=0.3), it falls short by ~1.9kWh and either better MLI or a supplemental source is needed.
3. **Contingency only, NOT baseline:** a small radioisotope heater unit (RHU) — proven Mars technology since Viking — for vehicles whose mission profile requires routine overnight stays *outside* corridor coverage. Explicitly not adopted as standard equipment on every vehicle: at fleet scale, a radioisotope source per vehicle is a cost/licensing/launch-safety liability for a problem (1) already solves for the on-corridor case. Off-corridor sorties are already time/range-bounded (tens of km, a few hours per `supercap_sizing.py`), so a "return to corridor before dark" operating rule is a lighter-weight alternative to equipping every vehicle with an RHU.

## Trade-off Analysis

The BLDC/efficiency gains (+3.9 points chain efficiency) are real but modest on their own. The peak-vs-average power correction is what actually resolves ADR-001's open reactor-sizing question — it's a modeling fix, not a hardware upgrade, and it's the kind of inconsistency that's easy to miss because the wrong number (125.6kW) wasn't unphysical, just answering a question the architecture didn't actually need answered that way.

The night-thermal PCM/MLI solution is elegant specifically because it's dual-use — no new mass beyond what the day problem already required. Its weak point is the insulation-quality dependency: the whole synthesis only holds together at U≲0.10 W/m²K, which needs to be validated against a real MLI design, not assumed.

## Consequences

- Dock-hub fission cluster is now ~5 Kilopower-class units at the recommended baseline sizing, not ~49 — a materially different (and now credible) infrastructure ask.
- Traction subsystem is specified as BLDC in-wheel direct-drive; drivetrain lubrication is no longer a Mars-night risk.
- Night survival has a concrete, mostly-free answer for on-corridor operation, and an explicit, bounded gap (off-corridor overnight sorties) with two named mitigations rather than an unaddressed risk.
- PCM/MLI sizing is now coupled across both day and night requirements — changing one (e.g. a bigger dock session) means re-checking the other (night coverage), not treating them independently.
- Residual, still-open risk: multi-sol dust storms can attenuate the optical link via aerosol scattering (not just gas absorption, which the original "near-zero atmospheric loss" claim correctly covers but doesn't fully address). Storm-safing duration (survive N sols with zero beam) is flagged as a follow-on trade study, not yet sized.

## Action Items

1. [ ] Validate PV efficiency target (50%) and laser wall-plug efficiency (40%) against real component datasheets.
2. [ ] Get real supercap specific-energy data (Wh/kg) from a vendor/lab source — currently swept parametrically (8-40Wh/kg), not measured.
3. [ ] Define and size a storm-safing scenario (N sols, zero beam) for the PCM+MLI system.
4. [ ] Scope `beam_tracking_sim.py` for corridor hand-off tracking (carried over from ADR-001).
5. [ ] Validate the U~0.05-0.10 W/m²K MLI target against a real insulation stack-up design.
