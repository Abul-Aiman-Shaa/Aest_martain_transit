"""
thermal_management.py  (v3 — multijunction dock scenario added)
====================================================================
AEST Module 3: Day/Night Thermal Survival Cycle

v3 changes from v2
---------------------
Adds a multijunction (VMJ) receiver dock scenario alongside the existing
single-junction one (photon_conversion.py v4 / ADR-005). A higher PV
efficiency at the dock means LESS optical power is needed to replenish
the same bank energy in the same dwell time, AND a smaller fraction of
that (now-smaller) optical power is wasted as heat — the two effects
compound. Net effect: the day-tier PCM sizing requirement drops
substantially under the multijunction scenario. Night and storm-safing
math (eps*, bay temperature) are UNCHANGED by this — PV efficiency has
no bearing on radiative heat loss once the vehicle is parked and dark.

v2 changes from v1

v2 changes from v1
---------------------
1. CORRECTED MODEL: v1 modeled night heat loss with an ad hoc linear
   "U-value" (W/m^2K) sweep. That's not how MLI is actually
   characterized. Real spacecraft MLI performance is reported as an
   EFFECTIVE EMISSIVITY (eps*) used directly in the Stefan-Boltzmann
   radiative form: Q = eps* * sigma * A * (T_hot^4 - T_cold^4). This
   session found real measured values:
     - Best real-world spacecraft MLI (25-layer Mylar/Dacron,
       aluminized, with normal seams/penetrations): eps* = 0.015-0.03
       [COBEM 2013 experimental paper; TTU thesis on MLI performance]
     - Laboratory-only best case (not realistic for a fielded vehicle):
       eps* = 0.005
   v2 uses eps*=0.02 as the realistic design-point (mid of the
   real-world range), replacing the v1 U-value sweep entirely.

2. CORRECTED BAY TEMPERATURE TARGET: v1 targeted -60C, arbitrarily
   split between the architecture's claimed -100C floor and a working
   margin. Literature research found NO source supporting -100C
   operation for any supercapacitor chemistry. Real commercial
   hardware (Skeleton SkelCap D60, see supercap_sizing.py) rates to
   -40C. The best documented COLD-temperature research result is -75C
   [NASA Tech Briefs / NTRS 20090011272], achieved with a specialized
   co-solvent electrolyte, at the cost of ~50% capacitance loss and
   increased ESR at that temperature. v2 uses -40C as the baseline bay
   target (matches buildable, real hardware) and reports -75C as an
   explicit aggressive alternative with its capacity penalty stated,
   NOT as a free assumption.

Net effect of both corrections together: the physically-correct
radiative model with real eps* values produces LOWER heat-loss numbers
than v1's ad hoc U-value sweep, even at the warmer -40C bay target —
genuinely good news that emerged from doing the literature check
properly, partially offsetting the bad news elsewhere in this update
(see photon_conversion.py v3, supercap_sizing.py v2).

Run: `python3 thermal_management.py`
"""

from __future__ import annotations

STEFAN_BOLTZMANN = 5.670374419e-8

# ---------------------------------------------------------------------------
# Shared thermal assumptions
# ---------------------------------------------------------------------------
RADIATOR_EMISSIVITY = 0.90
RADIATOR_TEMP_K = 350.0
MARS_AMBIENT_DAY_K = 210.0
MARS_AMBIENT_NIGHT_K = -125.0 + 273.15

PCM_LATENT_HEAT_J_KG = 200_000.0

# ---------------------------------------------------------------------------
# Day: dock transient (using conservative-PV dock sizing as the design case —
# see supercap_sizing.py v2; conservative scenario, 150kg/9.0Wh/kg bank)
# ---------------------------------------------------------------------------
PV_EFFICIENCY = 0.25               # single-junction conservative/field-demonstrated
DOCK_DWELL_MIN = 30.0
DOCK_OPTICAL_POWER_W = 13_720.0    # 150kg/9.0Wh/kg bank, single-junction conservative PV, 30min dwell (Module 2)
DOCK_RADIATOR_AREA_M2 = 6.0

PV_EFFICIENCY_MJ_CONSERVATIVE = 0.45   # VMJ receiver (photon_conversion.py v4 / ADR-005)
# Same bank/dwell target as above; optical power needed scales ~1/pv_eff for a
# fixed delivered energy, so this is DOCK_OPTICAL_POWER_W rescaled, not re-derived
# from scratch (Module 2's dock table gives the from-scratch numbers per bank size).
MJ_DOCK_OPTICAL_POWER_W = DOCK_OPTICAL_POWER_W * (PV_EFFICIENCY / PV_EFFICIENCY_MJ_CONSERVATIVE)

# ---------------------------------------------------------------------------
# Night: survival heat balance — CORRECTED physical model
# ---------------------------------------------------------------------------
HULL_AREA_M2 = 15.0
MLI_EFFECTIVE_EMISSIVITY = 0.02    # real-world spacecraft MLI (COBEM 2013 / TTU thesis)
MARS_NIGHT_HOURS = 12.3

# Two bay-temperature scenarios instead of one arbitrary number
BAY_TARGET_SCENARIOS_C = {
    "commercial (-40C, SkelCap-rated, buildable now)": -40.0,
    "aggressive R&D (-75C, JPL co-solvent electrolyte, ~50% capacity derate)": -75.0,
}


def net_radiative_flux_w_m2() -> float:
    return RADIATOR_EMISSIVITY * STEFAN_BOLTZMANN * (RADIATOR_TEMP_K**4 - MARS_AMBIENT_DAY_K**4)


def day_pcm_sizing(pv_eff: float = PV_EFFICIENCY,
                    dock_optical_w: float = DOCK_OPTICAL_POWER_W) -> tuple:
    dwell_h = DOCK_DWELL_MIN / 60
    waste_heat_w = dock_optical_w * (1 - pv_eff)
    energy_to_buffer_j = waste_heat_w * dwell_h * 3600
    q_net = net_radiative_flux_w_m2()
    reject_during_dock_j = q_net * DOCK_RADIATOR_AREA_M2 * dwell_h * 3600
    excess_j = max(0.0, energy_to_buffer_j - reject_during_dock_j)
    pcm_mass_kg = excess_j / PCM_LATENT_HEAT_J_KG
    return waste_heat_w, energy_to_buffer_j, reject_during_dock_j, excess_j, pcm_mass_kg


def night_heat_loss_w(bay_temp_c: float, eps_star: float = MLI_EFFECTIVE_EMISSIVITY) -> float:
    """Physically-correct radiative form using effective emissivity, not an ad hoc U-value."""
    t_bay_k = bay_temp_c + 273.15
    return eps_star * STEFAN_BOLTZMANN * HULL_AREA_M2 * (t_bay_k**4 - MARS_AMBIENT_NIGHT_K**4)


def main() -> None:
    print("=" * 78)
    print("AEST Module 3 (v3): Day/Night Thermal Survival Cycle — literature-validated")
    print("=" * 78)

    waste_w, buffer_j, reject_j, excess_j, pcm_kg = day_pcm_sizing()
    print(f"\n[DAY] Dock session (single-junction): {DOCK_OPTICAL_POWER_W/1000:.2f}kW optical "
          f"(PV={PV_EFFICIENCY}), {DOCK_DWELL_MIN:.0f}min dwell")
    print(f"    Waste heat power: {waste_w/1000:.2f}kW")
    print(f"    Total heat energy during dock: {buffer_j/1e6:.2f}MJ")
    print(f"    Radiator ({DOCK_RADIATOR_AREA_M2}m^2) sheds during session: {reject_j/1e6:.2f}MJ")
    print(f"    Excess needing PCM buffering: {excess_j/1e6:.2f}MJ")
    print(f"    PCM mass required: {pcm_kg:.1f}kg")
    pcm_kg_design = round(pcm_kg * 1.2, 1)
    pcm_latent_wh = pcm_kg_design * PCM_LATENT_HEAT_J_KG / 3600
    print(f"    Design PCM mass with 20% margin: {pcm_kg_design}kg "
          f"(latent capacity: {pcm_latent_wh:.0f}Wh)")

    waste_w_mj, buffer_j_mj, reject_j_mj, excess_j_mj, pcm_kg_mj = day_pcm_sizing(
        PV_EFFICIENCY_MJ_CONSERVATIVE, MJ_DOCK_OPTICAL_POWER_W)
    pcm_kg_mj_design = round(pcm_kg_mj * 1.2, 1)
    pcm_latent_wh_mj = pcm_kg_mj_design * PCM_LATENT_HEAT_J_KG / 3600
    print(f"\n[DAY, v3] Dock session (multijunction, ADR-005): "
          f"{MJ_DOCK_OPTICAL_POWER_W/1000:.2f}kW optical (PV={PV_EFFICIENCY_MJ_CONSERVATIVE}), "
          f"same {DOCK_DWELL_MIN:.0f}min dwell / delivered energy")
    print(f"    Waste heat power: {waste_w_mj/1000:.2f}kW (vs {waste_w/1000:.2f}kW single-junction)")
    print(f"    PCM mass required: {pcm_kg_mj:.1f}kg -> design with margin: {pcm_kg_mj_design}kg "
          f"(latent capacity: {pcm_latent_wh_mj:.0f}Wh)")
    print(f"    A higher-efficiency receiver needs LESS optical power for the same delivered")
    print(f"    energy AND wastes a smaller fraction of it -- both effects compound to cut the")
    print(f"    day-tier PCM requirement by roughly {(1 - pcm_kg_mj_design/pcm_kg_design)*100:.0f}%.")
    print(f"    CAUTION: this does NOT mean the vehicle needs {pcm_kg_mj_design}kg of PCM overall --")
    print(f"    see [NIGHT]/[STORM-SAFING] below. Under the multijunction dock scenario, the")
    print(f"    BINDING constraint on PCM mass flips from the day heat spike to night/storm")
    print(f"    survival -- a real architectural shift, not a mass-budget win to bank twice.")
    # Night/storm-safing use whichever design PCM mass is adopted; both are reported
    # below against the single-junction (larger, more conservative) PCM mass unless noted.

    print(f"\n[NIGHT] Survival heat balance — CORRECTED radiative model "
          f"(eps*={MLI_EFFECTIVE_EMISSIVITY}, real-world MLI)")
    print(f"    {'bay scenario':<62} {'Q_loss(W)':>10} {'Wh/night':>10} {'PCM covers?':>12}")
    for label, t_c in BAY_TARGET_SCENARIOS_C.items():
        q = night_heat_loss_w(t_c)
        wh = q * MARS_NIGHT_HOURS
        covers = "YES" if wh <= pcm_latent_wh else f"short {wh-pcm_latent_wh:.0f}Wh"
        print(f"    {label:<62} {q:>10.1f} {wh:>10.0f} {covers:>12}")

    print(f"\n[STORM-SAFING] 3-sol (73.8h) zero-beam survival, eps*={MLI_EFFECTIVE_EMISSIVITY}")
    for label, t_c in BAY_TARGET_SCENARIOS_C.items():
        q = night_heat_loss_w(t_c)
        energy_wh = q * 73.8
        pcm_needed_kg = energy_wh * 3600 / PCM_LATENT_HEAT_J_KG
        print(f"    {label:<62} energy={energy_wh:7.0f}Wh -> PCM={pcm_needed_kg:6.1f}kg")

    print(f"""
[SYNTHESIS]
Using the physically-correct radiative model with a real-world MLI
effective emissivity (eps*=0.02) instead of v1's ad hoc U-value sweep,
night heat loss is LOWER than v1 estimated — even at the corrected,
WARMER -40C commercial bay target (which has a bigger delta-T to the
-125C night than v1's -60C target did). This is good news that only
showed up once the model was checked against real spacecraft MLI data.

The -75C "aggressive R&D" scenario needs LESS heating power (smaller
delta-T to ambient) but only becomes usable if AEST commits to the
JPL-style co-solvent electrolyte and accepts ~50% supercap capacity
loss at that temperature — a real trade between thermal ease and
energy-storage capacity, not a free upgrade.

[DECISION, reaffirmed] No radioisotope heater as baseline equipment.
Primary night survival remains operational (park within fission-hub
corridor coverage) backed by the PCM+MLI system, now sized against
real, cited component data rather than assumed round numbers.

[STORM-SAFING, updated] The 3-sol zero-beam target is now cheaper to
meet than v1/ADR-003 estimated, because the corrected radiative model
with real eps* produces lower heat-loss numbers across the board. See
docs/literature_review.md and ADR-004 for the full before/after
comparison and all source citations.
""")


if __name__ == "__main__":
    main()
