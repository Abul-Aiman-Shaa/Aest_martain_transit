"""
thermal_management_gen2.py  (v1 — new, Architecture Gen 2)
===============================================================
AEST Module 8: Day/Night Thermal Survival Cycle — Gen 2 (Inductive Transfer)

Why this is a NEW file, not an edit to thermal_management.py
------------------------------------------------------------------
Gen 1's thermal model (`thermal_management.py`, unchanged, preserved)
was built around a PV receiver's waste heat: one big, infrequent heat
spike during a bounded dock dwell, requiring a PCM buffer sized against
that spike, PLUS a 3-sol zero-beam dust-storm-safing target. Neither
input applies to Gen 2 (ADR-006 Action Item #1). This module re-derives
from Gen 2's actual heat sources rather than patching the old one.

Two structural simplifications this module found, not assumed
--------------------------------------------------------------------
1. **No storm-safing margin needed at all.** Gen 1's 3-sol PCM
   over-sizing (ADR-003) existed because dust storms killed the NIR
   beam. Near-field inductive coupling is not meaningfully attenuated by
   suspended dust (ADR-006 Decision 2) — the link does not go dark
   during a storm, so there is no "ride out N sols with zero power"
   design case to size against. This removes the single largest PCM
   mass driver in the whole Gen 1 thermal budget.
2. **The heat load is continuous, not spiky.** Gen 1's dock was a rare,
   long, high-power event (30min dwell every so often) — a genuine
   spike needing a buffer. Gen 2's coil clusters are frequent and short
   (every few minutes at the recommended few-hundred-meter spacing,
   Module 6) — close enough together that, thermally, the vehicle sees
   something closer to a continuous average heat load than a spike.
   That converts the day-side problem from "buffer a spike" (PCM) to
   "reject a continuous flow" (radiator), which is a smaller, simpler
   design problem.

Night-survival physics (bay temperature target, MLI effective
emissivity, Stefan-Boltzmann radiative form) is UNCHANGED from
`thermal_management.py` v3 — that physics has nothing to do with the
power-transfer mechanism, so it is reused here as-is, not re-derived.

Run: `python3 thermal_management_gen2.py`
"""

from __future__ import annotations

STEFAN_BOLTZMANN = 5.670374419e-8

# ---------------------------------------------------------------------------
# Chain stages, from inductive_transfer_sim.py (Module 6) — dynamic design
# scenario, 3000W at wheels
# ---------------------------------------------------------------------------
WHEEL_POWER_W = 3_000.0
MOTOR_EFF = 0.93
FLYWHEEL_ROUNDTRIP_EFF = 0.90
DYNAMIC_TRANSFER_EFF = 0.65

# What fraction of the TRANSFER stage's loss is dissipated on the VEHICLE
# side (receiver coil + rectifier) versus the STATION side (transmit coil +
# cable)? No source found gives a real primary/secondary loss split for a
# resonant coupled system — this module assumes a symmetric 50/50 split as
# an explicitly flagged placeholder, consistent with this repo's practice
# of stating assumptions rather than hiding them (see ADR-007 Action Items).
VEHICLE_SIDE_TRANSFER_LOSS_FRACTION = 0.50

# ---------------------------------------------------------------------------
# Radiator / night-survival physics — UNCHANGED from thermal_management.py v3
# ---------------------------------------------------------------------------
RADIATOR_EMISSIVITY = 0.90
RADIATOR_TEMP_K = 350.0
MARS_AMBIENT_DAY_K = 210.0
MARS_AMBIENT_NIGHT_K = -125.0 + 273.15
MLI_EFFECTIVE_EMISSIVITY = 0.02
HULL_AREA_M2 = 15.0
MARS_NIGHT_HOURS = 12.3
PCM_LATENT_HEAT_J_KG = 200_000.0

BAY_TARGET_SCENARIOS_C = {
    "commercial (-40C, SkelCap-rated -- retained as thermal design reference)": -40.0,
    "aggressive R&D (-75C, JPL co-solvent electrolyte-class)": -75.0,
}


def net_radiative_flux_w_m2() -> float:
    return RADIATOR_EMISSIVITY * STEFAN_BOLTZMANN * (RADIATOR_TEMP_K**4 - MARS_AMBIENT_DAY_K**4)


def gen2_continuous_heat_loads_w() -> tuple:
    """Vehicle-onboard continuous heat sources under Gen 2's transfer chain."""
    p_flywheel_out = WHEEL_POWER_W / MOTOR_EFF
    p_received_vehicle = p_flywheel_out / FLYWHEEL_ROUNDTRIP_EFF
    p_grid = p_received_vehicle / DYNAMIC_TRANSFER_EFF

    total_transfer_loss_w = p_grid - p_received_vehicle
    receiver_rectifier_loss_w = total_transfer_loss_w * VEHICLE_SIDE_TRANSFER_LOSS_FRACTION
    flywheel_loss_w = p_received_vehicle - p_flywheel_out
    motor_loss_w = p_flywheel_out - WHEEL_POWER_W   # distributed at wheel hubs, out of
                                                      # scope for the central PCM/radiator
                                                      # system, same as Gen 1's scoping
    return p_grid, receiver_rectifier_loss_w, flywheel_loss_w, motor_loss_w


def night_heat_loss_w(bay_temp_c: float, eps_star: float = MLI_EFFECTIVE_EMISSIVITY) -> float:
    t_bay_k = bay_temp_c + 273.15
    return eps_star * STEFAN_BOLTZMANN * HULL_AREA_M2 * (t_bay_k**4 - MARS_AMBIENT_NIGHT_K**4)


def main() -> None:
    print("=" * 78)
    print("AEST Module 8: Day/Night Thermal Survival Cycle — Gen 2 (Inductive)")
    print("=" * 78)

    p_grid, recv_loss, fw_loss, motor_loss = gen2_continuous_heat_loads_w()
    central_load_w = recv_loss + fw_loss
    print(f"\n[DAY -- continuous, not spiky] At {WHEEL_POWER_W:.0f}W wheels, "
          f"{p_grid:.0f}W drawn from grid per vehicle (Module 6)")
    print(f"    Receiver+rectifier loss (vehicle-side, {VEHICLE_SIDE_TRANSFER_LOSS_FRACTION*100:.0f}% "
          f"of transfer loss, FLAGGED assumption): {recv_loss:.0f}W")
    print(f"    Flywheel round-trip loss (continuous, mechanical):              {fw_loss:.0f}W")
    print(f"    Motor loss (distributed at wheel hubs, out of central-PCM scope): {motor_loss:.0f}W")
    print(f"    CENTRAL continuous heat load needing rejection: {central_load_w:.0f}W")

    q_net = net_radiative_flux_w_m2()
    radiator_area_needed_m2 = central_load_w / q_net
    print(f"\n    Steady-state radiator area needed (no PCM buffering required for this")
    print(f"    load -- it's continuous, not spiky): {radiator_area_needed_m2:.2f}m^2")
    print(f"    Compare to Gen 1: 4m^2 (trickle) + 6m^2 (dock) = 10m^2 total, PLUS a")
    print(f"    67.9kg day-PCM buffer for the dock spike. Gen 2 needs a smaller radiator")
    print(f"    and NO day-side PCM at all -- the heat load never spikes.")

    print(f"\n[NIGHT -- unchanged physics from thermal_management.py v3, eps*="
          f"{MLI_EFFECTIVE_EMISSIVITY}]")
    print(f"    {'bay scenario':<62} {'Q_loss(W)':>10} {'Wh/night':>10} {'PCM(kg)':>9}")
    for label, t_c in BAY_TARGET_SCENARIOS_C.items():
        q = night_heat_loss_w(t_c)
        wh = q * MARS_NIGHT_HOURS
        pcm_kg = (wh * 3600) / PCM_LATENT_HEAT_J_KG
        print(f"    {label:<62} {q:>10.1f} {wh:>10.0f} {pcm_kg:>9.1f}")

    print(f"""
[STORM-SAFING -- DROPPED, not carried forward]
Gen 1 sized ~130kg of PCM against a 3-sol zero-beam dust-storm target
(ADR-003), because the NIR beam went dark during storms. Near-field
inductive coupling is not meaningfully attenuated by dust (ADR-006) --
there is no "link goes dark" storm failure mode to size against. This
is the single largest PCM mass reduction in this re-derivation, and it
falls out of the architecture change itself, not a relaxed requirement.

[SYNTHESIS]
Gen 2's thermal subsystem is smaller and simpler on every axis: a
~{radiator_area_needed_m2:.1f}m^2 steady-state radiator instead of Gen 1's 10m^2 plus a
67.9kg day-PCM buffer, a night-only PCM requirement (single-digit-to-
tens of kg depending on bay-temperature scenario, same physics as
Gen 1), and NO storm-safing margin at all. This closes ADR-006 Action
Item #1. The VEHICLE_SIDE_TRANSFER_LOSS_FRACTION=0.50 assumption is the
one open modeling input here -- flagged, not hidden, per ADR-007.
""")


if __name__ == "__main__":
    main()
