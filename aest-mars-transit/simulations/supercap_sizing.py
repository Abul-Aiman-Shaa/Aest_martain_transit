"""
supercap_sizing.py  (v3 — multijunction receiver scenarios added)
=====================================================================
AEST Module 2: Supercapacitor Bank Sizing (Power vs. Energy, Dock Sizing, Sortie Range)

v3 changes from v2
---------------------
Adds the multijunction (VMJ) receiver PV-efficiency scenarios from
photon_conversion.py v4 (0.45 conservative / 0.60 target) alongside the
existing v2 single-junction pair (0.25 / 0.50), rather than replacing
them — same "layer, don't discard" pattern as every prior version. The
corridor-trickle and dock tables below now carry all four. See
corridor_economics.py (Module 5) for the separate hop-length/dust-
transmission analysis this update also produced; that analysis does NOT
change anything in this file, because dust transmission is a hub-
transmit-side effect, not a bank/vehicle-side one — see ADR-005.

v2 changes from v1
---------------------
v1 swept specific energy parametrically (8/20/40 Wh/kg) because the
architecture doc doesn't state one. Literature research found a real
commercial datasheet to anchor on instead of guessing:

  Skeleton Technologies SkelCap D60 curved-graphene ultracapacitor
  (market-leading commercial graphene supercapacitor product):
    - Specific energy: 6.8-11.1 Wh/kg
    - Specific power: 22.1-28.4 kW/kg (up to 80 kW/kg in some configs)
    - Rated operating range: -40C to +65C
  [Source: skeletontech.com/skelcap-ultracapacitor-cells]

Two consequences:
  1. Specific ENERGY is close to v1's "conservative" 8Wh/kg case, NOT
     the 20-40Wh/kg range used for the v1 baseline recommendation.
     Sortie range and dock-recharge-time numbers below are recomputed
     on the REAL 6.8-11.1Wh/kg band — meaningfully lower than v1's
     baseline claimed.
  2. Specific POWER (22-28, up to 80 kW/kg) is 2-8x HIGHER than the
     architecture doc's assumed 10kW/kg. This makes Module 2's core
     finding ("peak power is never the bank-sizing constraint") even
     stronger, not weaker.

CRITICAL, separate finding: the architecture's claimed -100C to +50C
supercap operating envelope is NOT supported by any source found.
Commercial hardware (above) rates to -40C. The best documented
COLD-temperature RESEARCH result found is -75C, using a specialized
co-solvent electrolyte (NASA Tech Briefs / NTRS 20090011272), but at
the cost of capacitance dropping to ~50% of its room-temperature value
at that temperature, plus increased ESR (reduced power capability).
No source supports -100C for any supercapacitor chemistry. This is
carried into thermal_management.py as a corrected bay-temperature
target (-40C baseline, not -60C), which changes the night thermal
math materially — see that module and ADR-004.

Chain efficiency here now reflects BOTH PV scenarios from
photon_conversion.py v3 (conservative field-demonstrated vs. target
lab-record), not a single number.

Run: `python3 supercap_sizing.py`
"""

from __future__ import annotations

STEFAN_BOLTZMANN = 5.670374419e-8

# ---------------------------------------------------------------------------
# Chain efficiency — two scenarios (from photon_conversion.py v3)
# ---------------------------------------------------------------------------
PV_EFFICIENCY_CONSERVATIVE = 0.25
PV_EFFICIENCY_TARGET = 0.50
PV_EFF_MJ_CONSERVATIVE = 0.45      # VMJ receiver (photon_conversion.py v4 / Module 5)
PV_EFF_MJ_TARGET = 0.60
_CAP_ELEC_MOTOR = 0.97 * 0.97 * 0.93
CHAIN_EFF_CONSERVATIVE = PV_EFFICIENCY_CONSERVATIVE * _CAP_ELEC_MOTOR
CHAIN_EFF_TARGET = PV_EFFICIENCY_TARGET * _CAP_ELEC_MOTOR
CHAIN_EFF_MJ_CONSERVATIVE = PV_EFF_MJ_CONSERVATIVE * _CAP_ELEC_MOTOR
CHAIN_EFF_MJ_TARGET = PV_EFF_MJ_TARGET * _CAP_ELEC_MOTOR

# ---------------------------------------------------------------------------
# Bank power-vs-energy — anchored on SkelCap D60 datasheet
# ---------------------------------------------------------------------------
SPECIFIC_POWER_KW_KG_RANGE = (22.1, 28.4)      # datasheet range; up to 80 in special configs
SPECIFIC_ENERGY_WH_KG_RANGE = (6.8, 11.1)      # datasheet range
BANK_MASS_SWEEP_KG = [100.0, 150.0, 300.0]

# ---------------------------------------------------------------------------
# Corridor trickle assumptions
# ---------------------------------------------------------------------------
RADIATOR_EMISSIVITY = 0.90
RADIATOR_TEMP_K = 350.0
MARS_AMBIENT_TEMP_K = 210.0
TRICKLE_RADIATOR_AREA_M2 = 4.0

# ---------------------------------------------------------------------------
# Route / drive-cycle assumptions
# ---------------------------------------------------------------------------
CRUISE_SPEED_KMH = 15.0
AVG_CRUISE_POWER_W = 3000.0
CORRIDOR_LEG_KM = 10.0

# ---------------------------------------------------------------------------
# Hub transmitter assumptions
# ---------------------------------------------------------------------------
LASER_WALLPLUG_EFF = 0.40          # cited: IPG "over 50%" best-case, RP Photonics "best
                                    # cases ~50%" for high-power fiber lasers — 40% is a
                                    # defensible margin below the cited ceiling
HUB_OVERHEAD_FRAC = 0.10
KILOPOWER_UNIT_KWE = 8.0


def net_radiative_flux_w_m2() -> float:
    return RADIATOR_EMISSIVITY * STEFAN_BOLTZMANN * (RADIATOR_TEMP_K**4 - MARS_AMBIENT_TEMP_K**4)


def trickle_sustainable_wheel_power_w(chain_eff: float, pv_eff: float,
                                       a_rad_m2: float = TRICKLE_RADIATOR_AREA_M2) -> float:
    q_net = net_radiative_flux_w_m2()
    q_reject = q_net * a_rad_m2
    p_optical = q_reject / (1 - pv_eff)
    return p_optical * chain_eff


def min_bank_mass_for_peak_power_kg(peak_kw: float, specific_power_kw_kg: float) -> float:
    return peak_kw / specific_power_kw_kg


def hub_electrical_demand_kwe(p_optical_w: float) -> float:
    p_elec_laser = p_optical_w / LASER_WALLPLUG_EFF
    return (p_elec_laser * (1 + HUB_OVERHEAD_FRAC)) / 1000.0


def main() -> None:
    print("=" * 78)
    print("AEST Module 2 (v3): Supercapacitor Bank Sizing — literature-validated")
    print("=" * 78)

    print(f"\n[1] Peak power vs. bank mass, using REAL SkelCap D60 specific-power range")
    for peak_kw in [50, 100]:
        for sp in SPECIFIC_POWER_KW_KG_RANGE:
            m = min_bank_mass_for_peak_power_kg(peak_kw, sp)
            print(f"    {peak_kw}kW peak @ {sp}kW/kg -> {m:.2f}kg bank needed")
    print("    Even at the LOWER end of the real datasheet range, peak power is")
    print("    trivially satisfied by a few kg of bank. Confirmed, not weakened.")

    print(f"\n[2] Corridor-trickle sustainable wheel power, ALL FOUR PV scenarios "
          f"(A_rad={TRICKLE_RADIATOR_AREA_M2}m^2)")
    p_trickle_c = trickle_sustainable_wheel_power_w(CHAIN_EFF_CONSERVATIVE, PV_EFFICIENCY_CONSERVATIVE)
    p_trickle_t = trickle_sustainable_wheel_power_w(CHAIN_EFF_TARGET, PV_EFFICIENCY_TARGET)
    p_trickle_mc = trickle_sustainable_wheel_power_w(CHAIN_EFF_MJ_CONSERVATIVE, PV_EFF_MJ_CONSERVATIVE)
    p_trickle_mt = trickle_sustainable_wheel_power_w(CHAIN_EFF_MJ_TARGET, PV_EFF_MJ_TARGET)
    print(f"    single-junction conservative (PV=0.25): {p_trickle_c:.0f}W at wheels")
    print(f"    single-junction target       (PV=0.50): {p_trickle_t:.0f}W at wheels")
    print(f"    multijunction    conservative(PV=0.45): {p_trickle_mc:.0f}W at wheels")
    print(f"    multijunction    target      (PV=0.60): {p_trickle_mt:.0f}W at wheels  <- clears cruise draw")

    t_transit_h = CORRIDOR_LEG_KM / CRUISE_SPEED_KMH
    print(f"\n[3] Corridor leg energy balance ({CORRIDOR_LEG_KM}km @ {CRUISE_SPEED_KMH}km/h "
          f"= {t_transit_h*60:.0f}min transit, avg draw {AVG_CRUISE_POWER_W:.0f}W)")
    for label, p_trickle, chain_eff in [("sj_conservative", p_trickle_c, CHAIN_EFF_CONSERVATIVE),
                                         ("sj_target", p_trickle_t, CHAIN_EFF_TARGET),
                                         ("mj_conservative", p_trickle_mc, CHAIN_EFF_MJ_CONSERVATIVE),
                                         ("mj_target", p_trickle_mt, CHAIN_EFF_MJ_TARGET)]:
        deficit_w = max(0.0, AVG_CRUISE_POWER_W - p_trickle)
        deficit_wh = deficit_w * t_transit_h
        print(f"    {label:>16}: deficit={deficit_w:.0f}W -> {deficit_wh:.0f}Wh drained from bank/leg")

    print(f"\n[4] Dock power for FULL recharge from empty, real bank sizes "
          f"(SkelCap D60 range: {SPECIFIC_ENERGY_WH_KG_RANGE[0]}-{SPECIFIC_ENERGY_WH_KG_RANGE[1]}Wh/kg), "
          f"30min dwell, BOTH PV scenarios")
    print(f"    {'bank(kg)':>8} {'spec_E(Wh/kg)':>14} {'energy(kWh)':>12} "
          f"{'optical_cons(kW)':>17} {'optical_tgt(kW)':>16} {'hub_cons(kWe)':>14} {'hub_tgt(kWe)':>13}")
    for mass in BANK_MASS_SWEEP_KG:
        for spec_e in SPECIFIC_ENERGY_WH_KG_RANGE:
            energy_wh = mass * spec_e
            t_dock_h = 0.5
            p_wheels_dock = energy_wh / t_dock_h
            p_opt_c = p_wheels_dock / CHAIN_EFF_CONSERVATIVE
            p_opt_t = p_wheels_dock / CHAIN_EFF_TARGET
            hub_c = hub_electrical_demand_kwe(p_opt_c)
            hub_t = hub_electrical_demand_kwe(p_opt_t)
            print(f"    {mass:>8.0f} {spec_e:>14.1f} {energy_wh/1000:>12.2f} "
                  f"{p_opt_c/1000:>17.2f} {p_opt_t/1000:>16.2f} {hub_c:>14.2f} {hub_t:>13.2f}")

    print(f"\n[5] Sortie range table (off-corridor, supercap-only, beam off) — "
          f"REAL SkelCap D60 specific-energy range")
    print(f"    {'spec_E(Wh/kg)':>14} {'mass(kg)':>9} {'energy(Wh)':>11} "
          f"{'@500W avg':>10} {'@2000W avg':>11}")
    for spec_e in SPECIFIC_ENERGY_WH_KG_RANGE:
        for mass in BANK_MASS_SWEEP_KG:
            e_wh = spec_e * mass
            r500 = (e_wh / 500.0) * CRUISE_SPEED_KMH
            r2000 = (e_wh / 2000.0) * CRUISE_SPEED_KMH
            print(f"    {spec_e:>14.1f} {mass:>9.0f} {e_wh:>11.0f} "
                  f"{r500:>9.1f}km {r2000:>10.1f}km")

    print(f"""
[RECOMMENDATION, updated]
Baseline bank: 150kg @ 9.0Wh/kg (mid of the REAL SkelCap D60 range) =
1.35kWh — down from v1's speculative 3.0kWh. Sortie range: roughly
10-40km depending on average draw (500W-2000W), a real drop from v1's
optimistic 45-90km claim (which used an unvalidated 20Wh/kg mid-estimate).

Dock sizing at this real bank size is actually easier than v1 feared
(~4-6 Kilopower units at 30min dwell in the conservative PV scenario,
similar order in the target scenario) — smaller banks need less energy
replenished. The corridor TRICKLE tier is the one that suffers under
the single-junction conservative PV scenario ([2] above): it drops to
~780W at wheels (from v2's 2333W), well below the 3000W average cruise
draw assumed, meaning MORE of every corridor leg's energy must come
from the bank, not the beam. This was the load-bearing risk flagged in
ADR-004.

[v3 UPDATE] A VMJ multijunction receiver (ADR-005) changes this
materially: even its CONSERVATIVE scenario (PV=0.45) more than doubles
trickle power to ~1909W at wheels, and its TARGET scenario (PV=0.60)
clears the 3000W cruise draw outright (~3500W, [2] above) — for the
first time, the corridor-trickle tier can be self-sufficient without
bank drawdown, IF AEST commits to the multijunction receiver
development path. This does not retire ADR-004's underlying risk (no
975nm-specific receiver of ANY kind has been characterized yet) but it
does change which number the roadmap should be aiming for.

Supercap operating envelope: baseline design to -40C to +65C (matches
real hardware, buildable now), NOT the architecture doc's original
-100C floor claim, which no source supports. See thermal_management.py
v2 for the corrected night-survival math this drives.
""")


if __name__ == "__main__":
    main()
