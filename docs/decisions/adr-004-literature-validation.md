# ADR-004: Literature Validation of the Five Open Parameters

**Status:** Accepted
**Date:** 2026-09-09
**Deciders:** Abul Aiman Shaa, Claude (systems engineering collaborator)

## Context

ADR-002/ADR-003 flagged five parameters as assumed or swept rather than measured: supercap specific energy, laser wall-plug efficiency, MLI effective U-value, Mars NIR dust optical depth, and terrain data availability. This ADR records the literature research done to close them (see `docs/literature_review.md` for full citations) and the resulting decisions.

## Decision

Adopt the following, in place of the prior assumptions, each cited in `docs/literature_review.md`:

1. **Supercap specific energy:** 6.8-11.1 Wh/kg (Skeleton Technologies SkelCap D60 datasheet), replacing the unanchored 8-40Wh/kg sweep.
2. **Supercap specific power:** 22.1-28.4 kW/kg, up to 80 in some configs (same datasheet) — higher than the architecture's assumed 10kW/kg.
3. **Supercap operating envelope — CORRECTED, not just refined:** -40C to +65C baseline (real commercial hardware), with -75C available only as an aggressive R&D path (NASA-funded co-solvent electrolyte research) that costs ~50% capacitance at that temperature. **No source supports the architecture's original -100C claim.** This is flagged as a correction to the project's own founding spec, not an AEST modeling choice.
4. **Laser wall-plug efficiency:** 40% design value confirmed adequate against a cited ~50% industry/technical-reference ceiling (IPG, RP Photonics). No change needed.
5. **PV receiver efficiency — the load-bearing finding:** carry TWO scenarios instead of one number. Conservative/field-demonstrated: 25% (rounded from DARPA POWER program's real >20% outdoor demonstration). Target/lab-record: 50% (supported by adjacent-wavelength — 1064nm, 1470nm, not 975nm — lab records up to 67.5% under cryogenic conditions). The gap between these is real technology-development risk, not noise.
6. **MLI thermal model — corrected, not just re-parametrized:** replace the ad hoc U-value sweep with the physically correct radiative form using effective emissivity (eps* = 0.02, real-world spacecraft data), per standard spacecraft thermal engineering practice.
7. **Mars dust optical depth:** confirmed — background tau=0.3-0.5, storm tau=4-6 (locally to 10), matching an authoritative JPL/DESCANSO source. The NIR-gets-a-discount hedge from ADR-003 is removed; literature says visible/NIR optical depth ratios don't vary much for Mars dust.
8. **Terrain data:** MOLA (463m/pixel global, 200m/pixel blended) is real and public but too coarse for meter-scale LOS analysis; HiRISE stereo (~1m/pixel) exists only for targeted campaigns. Recorded as a scoped next step in `docs/route_planning.md`, not resolved here.

## Consequences

**Bad news, stated plainly:** the PV-efficiency finding (#5) roughly halves the corridor-trickle tier's sustainable power at the conservative end (2333W → 778W at wheels, 4m² radiator) compared to v2's single-number assumption. Under conservative PV, the trickle tier can no longer cover the assumed 3000W average cruise draw on its own (778W vs. 3000W) — most of every corridor leg's energy has to come from the bank, not the beam, unless PV efficiency lands closer to the target scenario. This is now the single biggest open risk in the architecture, bigger than the dust-storm or reactor-sizing questions already resolved. It is a hardware R&D question (can AEST's cell development close the 25%→50% gap), not something more modeling can fix.

**Good news, also real:** the corrected radiative MLI model (#6) produces lower night/storm heat-loss numbers than the cruder v1 model did, even at the corrected, warmer -40C bay target — genuinely better than previously estimated. The day-tier PCM buffer, resized for the conservative-PV dock scenario (~68kg with margin), turns out to comfortably cover BOTH the nightly heat loss AND the full 3-sol storm-safing target simultaneously — one component doing three jobs, which simplifies the thermal subsystem rather than complicating it.

**Sortie range is lower than v2 claimed** (real ~10-40km on a 150kg bank vs. the earlier unvalidated ~45-90km), a direct consequence of using real 6.8-11.1Wh/kg instead of an optimistic 20Wh/kg placeholder.

**The architecture's own founding spec had an error** (-100C supercap floor) that this vehicle-level analysis would have inherited silently if not checked. Worth noting as a general lesson: even the original problem statement's technical claims need the same scrutiny as AEST's own design choices.

## Action Items

1. [ ] Commission or fund 975nm-specific InGaAs/graphene PV receiver characterization — the single highest-value validation AEST could do, since no source at the actual operating wavelength was found.
2. [ ] Decide whether AEST's roadmap targets the 25% conservative baseline (buildable sooner, weaker corridor performance) or commits to closing the gap toward 50% (stronger performance, real R&D risk) — a programmatic choice, not something this repo can decide alone.
3. [ ] Evaluate whether the -75C aggressive supercap path (with its 50% capacity penalty) is worth pursuing given the day-tier PCM already comfortably covers the -40C baseline's thermal needs — the case for it is weaker than ADR-002/003 assumed.
4. [ ] Bring targeted HiRISE stereo imaging into scope once candidate corridor sites are chosen (route_planning.md).
5. [ ] Formally correct the -100C claim in any future whitepaper/external-facing document — this repo's docs are now internally consistent, but the original problem statement is not.

## Delivered this session

- `docs/literature_review.md` (new — full citations for all 5+1 parameters)
- `simulations/photon_conversion.py` v3 (dual PV-efficiency scenarios)
- `simulations/supercap_sizing.py` v2 (real SkelCap D60 datasheet numbers)
- `simulations/thermal_management.py` v2 (corrected radiative MLI model, corrected bay-temperature scenarios)
- This ADR.
