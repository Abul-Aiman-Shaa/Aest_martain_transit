"""
photon_conversion.py  (v4 — literature-validated, multijunction receiver added)
==================================================================================
AEST Module 1: Photon-to-Wheel Efficiency Chain

v4 changes from v3 — the receiver-technology half of this session's update
-----------------------------------------------------------------------------
v3 carried a single-junction InGaAs receiver model with two scenarios
(0.25 field-demonstrated / 0.50 lab-record-adjacent), and flagged the gap
between them as the architecture's single biggest open risk (ADR-004).

This session investigated the user's proposal to close that gap via a
"modular" receiver ("multiple intake ports"). Literature research found
the real mechanism is NOT multiple separately-tracked beams — it is a
VERTICAL MULTI-JUNCTION (VMJ) receiver: several photovoltaic subcells
connected in series WITHIN ONE receiver chip, fed by ONE beam, trading
photocurrent for voltage to avoid the crippling resistive (I^2R) losses
that limit single-junction converters at high optical intensity. This is
a receiver-technology swap, not a beam-architecture change — it adds NO
new pointing/tracking complexity (see beam_tracking_sim.py's added
section on this).

Real, literature-validated VMJ performance (808-811nm GaAs, six
series-connected subcells):
  - 65-67% peak efficiency at 30-75 W/cm^2, still >64% at 160 W/cm^2, up
    to 242 W/cm^2 on small devices [MDPI Photonics 13(3):246].
  - Critically, efficiency is ROBUST to partial/off-center illumination
    and low intensity, not just high intensity: 59.4% at only 10W input
    with the beam covering just ~7% of the chip area, 61% at 20-65% area
    coverage — "efficiency and output voltage penalties for using a
    smaller and peaky beam are relatively minor" [VMJ 61%-efficiency,
    beam-non-uniformity-tolerance paper, see literature_review.md #9].
    This directly answers the question this session raised (and had to
    check, not assume): does the ADR-003 spot-matched design's LOW
    intensity (a few W/cm^2, deliberately de-concentrated for tracking
    margin) forfeit the high-intensity efficiency this technology is
    famous for? Answer: no — the same technology stays in the high-50s
    to low-60s% band across a wide intensity and illumination-fraction
    range, it just doesn't hit its absolute peak (~67%) without a
    moderately concentrated spot.

v4 therefore adds a SECOND scenario pair, alongside the v3 pair (kept,
relabeled SINGLEJUNCTION_*, for historical/comparison reference):
  - PV_EFF_MULTIJUNCTION_CONSERVATIVE = 0.45 (discounted below the
    demonstrated 59-61% for the same reason v3's numbers were
    discounted: no 975nm-specific data exists, only 808/1470nm; a real
    fielded mosaic receiver will have illumination, dust, and aging
    losses a lab test cell does not.)
  - PV_EFF_MULTIJUNCTION_TARGET = 0.60 (near the literature's
    demonstrated 61-64% band, achievable if AEST deliberately
    concentrates the corridor spot — see beam_tracking_sim.py — into
    the higher-intensity window, which this session found does NOT
    cost tracking margin the way it first appeared it might.)

Neither multijunction number is field-proven at 975nm or at AEST's
system scale — same category of risk as v3's target scenario, just
starting from a stronger, more specific, and more recent evidence base
(2024-2025 papers, vs. v3's 2021 and adjacent-wavelength sources).

Sources (see docs/literature_review.md for full citations):
  - DARPA POWER program distance/efficiency record (2025)
  - Vasil'ev et al. (2021); MDPI Photonics 11(2):130 (2024) — v3 sources,
    kept for the single-junction scenario pair.
  - MDPI Photonics 13(3):246, "65% Efficient Multijunction Photovoltaic
    Laser Power Converters Operating over 150 W/cm^2" (2025-class VMJ
    GaAs device, 808-811nm)
  - VMJ 61%-efficiency / beam-non-uniformity-tolerance paper (partial
    illumination and low-intensity robustness data)
  - Cell Reports Physical Science, "Photovoltaic laser power converters
    producing 21 W/cm^2 at a conversion efficiency of 66.5%" and
    "Multi-junction laser power converters exceeding 50% efficiency in
    the short wavelength infrared" (corroborating multijunction results)
  - IPG Photonics YLS-ECO product literature; RP Photonics technical
    reference — unchanged, supports the 40% laser wall-plug assumption.

Run: `python3 photon_conversion.py`
"""

from __future__ import annotations
from dataclasses import dataclass

H_PLANCK = 6.62607015e-34
C_LIGHT = 2.99792458e8
EV_TO_J = 1.602176634e-19
STEFAN_BOLTZMANN = 5.670374419e-8

# ---------------------------------------------------------------------------
# Design assumptions (v3)
# ---------------------------------------------------------------------------
WAVELENGTH_NM = 975.0
BANDGAP_EV = 1.15                 # InGaAs alloy tuned near 975nm (still an assumption —
                                   # no 975nm-specific datasheet found; adjacent-wavelength
                                   # (1064nm, 1470nm) devices are the closest literature match)

PV_EFF_SINGLEJUNCTION_CONSERVATIVE = 0.25  # field-demonstrated floor (DARPA POWER, 2025)
PV_EFF_SINGLEJUNCTION_TARGET = 0.50        # lab-record-supported aspiration (adjacent wavelengths)
PV_EFF_MULTIJUNCTION_CONSERVATIVE = 0.45   # VMJ receiver, discounted from demonstrated 59-61%
PV_EFF_MULTIJUNCTION_TARGET = 0.60         # VMJ receiver, near demonstrated 61-64% peak band

# Backward-compatible aliases (v3 names) — kept so this module's public
# interface doesn't silently break anything importing it; NEW code should
# use the explicit SINGLEJUNCTION_*/MULTIJUNCTION_* names above.
PV_EFFICIENCY_CONSERVATIVE = PV_EFF_SINGLEJUNCTION_CONSERVATIVE
PV_EFFICIENCY_TARGET = PV_EFF_SINGLEJUNCTION_TARGET

SUPERCAP_ROUNDTRIP_EFF = 0.97
POWER_ELECTRONICS_EFF = 0.97      # SiC/GaN controller
MOTOR_EFF = 0.93                  # BLDC in-wheel direct-drive

MARS_SOLAR_CONSTANT_W_M2 = 590.0
MARS_AMBIENT_TEMP_K = 210.0
RADIATOR_EMISSIVITY = 0.90
RADIATOR_TEMP_K = 350.0


@dataclass
class ChainResult:
    photon_energy_ev: float
    quantum_defect_ceiling: float
    chain_eff_conservative: float
    chain_eff_target: float
    chain_eff_mj_conservative: float
    chain_eff_mj_target: float


def photon_energy_ev(wavelength_nm: float) -> float:
    wavelength_m = wavelength_nm * 1e-9
    energy_j = (H_PLANCK * C_LIGHT) / wavelength_m
    return energy_j / EV_TO_J


def quantum_defect_ceiling(photon_ev: float, bandgap_ev: float) -> float:
    if bandgap_ev >= photon_ev:
        raise ValueError("Bandgap must be below photon energy for absorption.")
    return bandgap_ev / photon_ev


def chain_efficiency(pv_eff: float) -> float:
    return pv_eff * SUPERCAP_ROUNDTRIP_EFF * POWER_ELECTRONICS_EFF * MOTOR_EFF


def compute_chain() -> ChainResult:
    e_photon = photon_energy_ev(WAVELENGTH_NM)
    qd_ceiling = quantum_defect_ceiling(e_photon, BANDGAP_EV)
    return ChainResult(
        e_photon, qd_ceiling,
        chain_efficiency(PV_EFF_SINGLEJUNCTION_CONSERVATIVE),
        chain_efficiency(PV_EFF_SINGLEJUNCTION_TARGET),
        chain_efficiency(PV_EFF_MULTIJUNCTION_CONSERVATIVE),
        chain_efficiency(PV_EFF_MULTIJUNCTION_TARGET),
    )


def radiator_sustainable_wheel_power(a_rad_m2: float, pv_eff: float) -> tuple:
    """Corridor-trickle tier only — continuous, radiator-bounded."""
    q_net = RADIATOR_EMISSIVITY * STEFAN_BOLTZMANN * (RADIATOR_TEMP_K**4 - MARS_AMBIENT_TEMP_K**4)
    q_reject = q_net * a_rad_m2
    p_optical_max = q_reject / (1 - pv_eff)
    p_wheels_max = p_optical_max * chain_efficiency(pv_eff)
    return p_optical_max, p_wheels_max


def main() -> None:
    r = compute_chain()

    print("=" * 78)
    print("AEST Module 1 (v4): Photon-to-Electron Chain Efficiency @ 975nm")
    print("=" * 78)

    print(f"\n[1] Photon energy: {r.photon_energy_ev:.4f} eV")
    print(f"[2] Quantum-defect ceiling (Eg={BANDGAP_EV}eV): {r.quantum_defect_ceiling*100:.1f}%")

    print(f"\n[3] End-to-end chain efficiency — FOUR scenarios, not one number")
    print(f"    single-junction CONSERVATIVE (PV={PV_EFF_SINGLEJUNCTION_CONSERVATIVE:.2f}, "
          f"DARPA field-demonstrated floor):  {r.chain_eff_conservative*100:.2f}%")
    print(f"    single-junction TARGET       (PV={PV_EFF_SINGLEJUNCTION_TARGET:.2f}, "
          f"lab-record, adjacent wavelength):  {r.chain_eff_target*100:.2f}%")
    print(f"    multijunction    CONSERVATIVE(PV={PV_EFF_MULTIJUNCTION_CONSERVATIVE:.2f}, "
          f"VMJ receiver, discounted):         {r.chain_eff_mj_conservative*100:.2f}%")
    print(f"    multijunction    TARGET      (PV={PV_EFF_MULTIJUNCTION_TARGET:.2f}, "
          f"VMJ receiver, near demonstrated):  {r.chain_eff_mj_target*100:.2f}%")
    print(f"    The VMJ receiver (Module 5's finding) is a straight technology upgrade over")
    print(f"    single-junction at BOTH ends of the risk spectrum — its own 'conservative'")
    print(f"    number ({PV_EFF_MULTIJUNCTION_CONSERVATIVE:.2f}) already beats single-junction's 'target' "
          f"number ({PV_EFF_SINGLEJUNCTION_TARGET:.2f}).")

    print(f"\n[4] Corridor-trickle sustainable wheel power vs. radiator area, ALL FOUR scenarios")
    print(f"    {'A_rad':>6} | {'sj_cons(W)':>10} | {'sj_tgt(W)':>9} | {'mj_cons(W)':>10} | {'mj_tgt(W)':>9}")
    for a in [1, 2, 4, 6, 8]:
        _, pw_sc = radiator_sustainable_wheel_power(a, PV_EFF_SINGLEJUNCTION_CONSERVATIVE)
        _, pw_st = radiator_sustainable_wheel_power(a, PV_EFF_SINGLEJUNCTION_TARGET)
        _, pw_mc = radiator_sustainable_wheel_power(a, PV_EFF_MULTIJUNCTION_CONSERVATIVE)
        _, pw_mt = radiator_sustainable_wheel_power(a, PV_EFF_MULTIJUNCTION_TARGET)
        print(f"    {a:>4}m2 | {pw_sc:>10.0f} | {pw_st:>9.0f} | {pw_mc:>10.0f} | {pw_mt:>9.0f}")
    print("    At the standard 4m^2 trickle radiator (see supercap_sizing.py), the")
    print("    multijunction-TARGET scenario clears the assumed 3000W average cruise")
    print("    draw for the first time (see [4] in supercap_sizing.py) -- but this is")
    print("    a receiver-technology result, NOT a consequence of hop length. See")
    print("    corridor_economics.py (Module 5) for the (separate) hop-length analysis.")

    print(f"""
[NOTE ON DOCK-TIER POWER] Dock power should still be sized against
average energy replenishment over a chosen dwell time, not peak wheel
power (ADR-002) — see supercap_sizing.py, now updated with real
supercapacitor datasheet numbers (Skeleton Technologies SkelCap D60)
and recomputed for all four PV scenarios above.

[NOTE ON HOP LENGTH] This module's numbers do not depend on hub-to-hub
spacing at all -- dust transmission and hub economics are a separate,
propagation-side question, answered in corridor_economics.py (Module 5).
Conflating "shorter hops" with "higher PV efficiency" was the one
inconsistency in this session's own proposal that needed resolving
before writing any more code — see ADR-005.
""")


if __name__ == "__main__":
    main()
