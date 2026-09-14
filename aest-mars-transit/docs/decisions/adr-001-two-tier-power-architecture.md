# ADR-001: Two-Tier Optical Power Architecture for AEST (Corridor Trickle + Dock Fast-Charge)

**Status:** Accepted
**Date:** 2026-09-08 (accepted 2026-09-09)
**Deciders:** Abul Aiman Shaa
**Project renamed:** MSTN → **AEST (Active Energy Supplied Transit)**.

## Context

Module 1 (`photon_conversion.py` v1) found that continuous drive-while-beaming at the original 50kW wheel-power target requires ~125.6kW optical power at the receiver and dumps ~65.3kW of waste heat continuously — a load that needs ~98m² of rover-mounted radiator to reject, which does not fit on any plausible vehicle. Single-tier continuous beaming, as originally specified, is thermally unsupportable.

The mission profile was set to **long-range exploration support**, not settlement-scale fixed-route transit. That reopens the founding premise: graphene supercapacitors are chosen for specific *power* (~10kW/kg), not specific *energy*. Real specific-energy figures (5-40Wh/kg depending on chemistry maturity) cap supercap-only range at tens to low-hundreds of km per charge — not "long-range exploration" by itself.

## Decision

Adopt a **two-tier optical power architecture**:

1. **Transit tier (corridor trickle).** A chain of hub towers at ≤10km line-of-sight intervals continuously beams a low, thermally-sustainable power level while the rover drives. With a 4m² rover radiator: ~5.1kW optical in → ~2.0-2.3kW continuous at the wheels (see v2 numbers in ADR-002), indefinitely.
2. **Dock tier (fast recharge).** Higher-power hubs deliver a full recharge over a bounded dwell time. Sized in ADR-002/`supercap_sizing.py` against actual energy replenishment, not peak wheel power (see ADR-002 — this halves the reactor-sizing problem from v1).
3. **Supercap bank sizing shifts role**: sized for burst power above the trickle floor and a bounded **sortie range**, not for carrying the whole mission.

This gives **corridor range** (effectively unlimited, bounded by hub network extent) plus **sortie range** (finite, supercap-limited). Range comes from infrastructure reach, not stored energy density — consistent with the zero-chemical-battery premise.

## Options Considered

### Option A: Single-tier continuous full power (original spec) — REJECTED
Fails thermally (98m² radiator required).

### Option B: Two-tier corridor trickle + dock fast-charge — ACCEPTED
Thermally closes; range model matches "long-range exploration" if the corridor network is built out; higher complexity (hub-to-hub handoff, route/corridor planning).

### Option C: Hybrid storage (Li-ion capacitor) for higher specific energy — REJECTED, CONFIRMED CLOSED (2026-09-09)
Ruled out early as "pointless to reopen." Not pursued further. Reason on record: reintroduces the cryogenic degradation risk AEST exists to eliminate.

## Trade-off Analysis

Central trade: infrastructure density vs. vehicle autonomy. More/closer hubs → more corridor range, less sortie dependence.

The 10km transit-tier line-of-sight assumption checks out geometrically: a 2m rover beacon plus a ~5.9m hub tower clears 10km of Mars curvature on flat terrain. The real constraint is Martian terrain masking (craters, dunes, boulders), not planetary curvature — a route-planning problem, not a physics wall.

## Consequences

- AEST is a **powered-corridor network with battery-free rovers on it**, not a general-purpose free-roaming rover.
- Range claims must specify corridor vs. sortie mode.
- Dock-hub reactor sizing was flagged as the long pole here — **resolved in ADR-002** by correcting the dock-power derivation (average energy replenishment, not peak power).
- `beam_tracking_sim.py` (future module) needs to model hub-to-hub handoff along a corridor, not a single static link.
- Terrain-driven LOS masking is a first-class route-planning constraint.

## Action Items (status)

1. [x] Dock-tier power target resolved in ADR-002 — sized against energy replenishment, not peak power.
2. [ ] Confirm laser wall-plug efficiency assumption (40% in v2) against a real fiber-laser datasheet.
3. [x] Repo renamed `mstn-mars-transit` → `aest-mars-transit`.
4. [x] `simulations/supercap_sizing.py` built.
5. [ ] Scope `simulations/beam_tracking_sim.py` for corridor handoff (not yet built).
6. [x] Day/night thermal survival addressed in ADR-002 / `thermal_management.py`. Dust-storm storm-safing sizing remains a follow-on trade study.
