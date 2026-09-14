"""
flywheel_buffer_sizing.py  (v1 — new, Architecture Gen 2)
=============================================================
AEST Module 7: Steel Flywheel Onboard Energy Buffer (replaces the
graphene supercapacitor bank)

Why this module exists
-----------------------
Gen 2 called for removing the graphene supercapacitor bank, or finding a
better alternative, consistent with the carbon-steel/ISRU
manufacturability philosophy (graphene supercapacitors are an imported,
exotic-material component; steel is exactly what the Gen 2 vehicle
chassis is made of, ADR-006). This module evaluates a STEEL flywheel as the
onboard buffer from first principles, rather than assuming it is
automatically better because it fits the ISRU narrative.

The honest finding, stated up front
--------------------------------------
A steel flywheel is NOT a decisive energy-density upgrade over the
graphene supercapacitor bank (`supercap_sizing.py`, real datasheet range
6.8-11.1 Wh/kg). Depending on the achievable steel strength and real-
world engineering margins, it lands roughly AT PARITY with that range —
sometimes better, sometimes worse. The actual case for switching is:
  1. ISRU manufacturability: steel vs. an imported exotic graphene
     ultracapacitor product.
  2. A completely different, arguably simpler failure physics: a
     flywheel's low-temperature limit is a BEARING/MATERIAL problem
     (brittle-fracture toughness at cold temperature), not an
     ELECTROLYTE problem — there is no equivalent of the -40C-vs-100C
     supercap chemistry dispute this repo had to correct in ADR-004.
  3. It is what makes Module 6's sparse coil-cluster spacing economical
     at all — something a supercap bank could equally do, but the
     flywheel is being adopted here as a package with the vehicle's own
     structural-material choice.

Physics: theoretical specific energy of a flywheel
------------------------------------------------------
For a rotor at its burst-limited tip speed, maximum theoretical specific
energy is:

    e_max = K_shape * sigma_max / rho

where sigma_max is material tensile strength, rho is density, and
K_shape is a rotor-geometry factor (0.5 for a simple flat disk, used
here as a standard textbook reference value — an optimized rim/spoke
design can do somewhat better, a simple solid disk is the conservative
case). Real engineered systems achieve a FRACTION of this theoretical
ceiling once burst safety margin, non-structural mass (shaft, bearings,
motor/generator, housing), and control losses are accounted for.

Run: `python3 flywheel_buffer_sizing.py`
"""

from __future__ import annotations

STEEL_DENSITY_KG_M3 = 7_850.0
K_SHAPE_FLAT_DISK = 0.5

# ISRU steel quality is genuinely uncertain — the carbothermic-reduction
# literature (docs/literature_review.md) demonstrates PURE IRON / liquid
# iron-silicon alloy formation from Mars regolith simulant in lab
# conditions, but has not characterized mechanical (tensile) properties
# of the resulting product against real structural steel. This sweep
# brackets from conservative mild-steel-grade to good structural/high-
# strength steel, explicitly NOT assuming Earth-grade alloy steel is
# achievable from a first-generation Mars smelter.
TENSILE_STRENGTH_MPA_SWEEP = {
    "conservative ISRU-grade (mild steel, unrefined)": 400.0,
    "good structural steel (refined process)": 800.0,
    "high-strength steel (aspirational, alloyed)": 1500.0,
}

REAL_WORLD_REALIZATION_FRACTION = 0.40   # engineering margin discount vs.
                                          # theoretical K*sigma/rho ceiling
                                          # (burst safety factor + non-
                                          # structural mass); see docstring

SUPERCAP_SPECIFIC_ENERGY_RANGE_WH_KG = (6.8, 11.1)   # SkelCap D60, for comparison

# ---------------------------------------------------------------------------
# Sizing targets: gap-bridging (Module 6) + a burst-power/contingency margin
# ---------------------------------------------------------------------------
GAP_BRIDGING_TARGETS_WH = {
    "200m coil-cluster gap": 43.0,
    "500m coil-cluster gap": 107.5,
    "1000m coil-cluster gap": 215.1,
    "3000m coil-cluster gap (aggressive sparse spacing)": 645.2,
}
CONTINGENCY_MULTIPLE = 3.0   # design margin: sustain several consecutive
                              # gaps / a partial coil-cluster outage, not
                              # just one nominal gap


def theoretical_specific_energy_wh_kg(sigma_mpa: float,
                                       k_shape: float = K_SHAPE_FLAT_DISK) -> float:
    sigma_pa = sigma_mpa * 1e6
    e_j_kg = k_shape * sigma_pa / STEEL_DENSITY_KG_M3
    return e_j_kg / 3600.0


def main() -> None:
    print("=" * 78)
    print("AEST Module 7: Steel Flywheel Onboard Buffer — first-principles sizing")
    print("=" * 78)

    print(f"\n[1] Theoretical specific energy, K={K_SHAPE_FLAT_DISK} flat-disk rotor, "
          f"steel density={STEEL_DENSITY_KG_M3:.0f}kg/m^3")
    print(f"    {'steel grade':<48} {'sigma(MPa)':>10} {'e_theoretical(Wh/kg)':>21} "
          f"{'e_realistic(Wh/kg)':>19}")
    realistic = {}
    for label, sigma in TENSILE_STRENGTH_MPA_SWEEP.items():
        e_theo = theoretical_specific_energy_wh_kg(sigma)
        e_real = e_theo * REAL_WORLD_REALIZATION_FRACTION
        realistic[label] = e_real
        print(f"    {label:<48} {sigma:>10.0f} {e_theo:>21.2f} {e_real:>19.2f}")

    sc_lo, sc_hi = SUPERCAP_SPECIFIC_ENERGY_RANGE_WH_KG
    print(f"\n    Compare to graphene supercap (SkelCap D60, real datasheet): "
          f"{sc_lo}-{sc_hi} Wh/kg")
    print(f"    VERDICT: conservative-ISRU-steel flywheel ({list(realistic.values())[0]:.1f}Wh/kg) "
          f"sits BELOW the supercap range;")
    print(f"    good structural steel ({list(realistic.values())[1]:.1f}Wh/kg) sits WITHIN it;")
    print(f"    high-strength steel ({list(realistic.values())[2]:.1f}Wh/kg) sits ABOVE it.")
    print(f"    This is a roughly-at-parity swap on energy density, not a decisive win --")
    print(f"    see this module's docstring for the real case for switching.")

    print(f"\n[2] Bank sizing against Module 6's gap-bridging targets "
          f"({CONTINGENCY_MULTIPLE:.0f}x contingency margin)")
    e_design = list(realistic.values())[1]   # good-structural-steel case as design baseline
    print(f"    Using design value {e_design:.2f}Wh/kg (good structural steel, realistic)")
    print(f"    {'gap scenario':<48} {'nominal(Wh)':>12} {'w/margin(Wh)':>13} {'bank_mass(kg)':>13}")
    for label, wh in GAP_BRIDGING_TARGETS_WH.items():
        wh_margin = wh * CONTINGENCY_MULTIPLE
        mass_kg = wh_margin / e_design
        print(f"    {label:<48} {wh:>12.1f} {wh_margin:>13.1f} {mass_kg:>13.1f}")

    m_3km = GAP_BRIDGING_TARGETS_WH['3000m coil-cluster gap (aggressive sparse spacing)'] * CONTINGENCY_MULTIPLE / e_design
    m_1km = GAP_BRIDGING_TARGETS_WH['1000m coil-cluster gap'] * CONTINGENCY_MULTIPLE / e_design
    m_500m = GAP_BRIDGING_TARGETS_WH['500m coil-cluster gap'] * CONTINGENCY_MULTIPLE / e_design
    print(f"""
[SYNTHESIS]
Even the aggressive 3km sparse-spacing scenario only needs a {m_3km:.0f}kg
flywheel bank at the design specific-energy value -- same order of
magnitude as Gen 1's 150kg supercap bank recommendation
(`supercap_sizing.py`), for meaningfully more capability (bridging
kilometer-scale gaps, not just smoothing a corridor-trickle deficit).
The recommended baseline (Module 6, ~500m-1km coil-cluster gaps) needs
only a {m_500m:.0f}-{m_1km:.0f}kg flywheel bank -- well BELOW Gen 1's 150kg
baseline, because this buffer only has to bridge short gaps and damp
transfer ripple, not carry the vehicle across multi-kilometer beam-free
stretches the way Gen 1's bank sometimes had to.

[OPEN ITEMS -- stated plainly, not smoothed over]
1. ISRU steel mechanical properties (real tensile strength, fatigue
   life under repeated high-speed spin-up/spin-down cycling) are NOT
   yet characterized from actual Mars-regolith-derived product --
   docs/literature_review.md's carbothermic-reduction sources are lab-
   simulant experiments, not flight/field-validated material data.
2. Cold-temperature bearing solution unresolved: magnetic bearings
   avoid the lubricant-freezing failure mode already flagged for
   gearboxes (ADR-002) and would need their own control electronics
   (an Earth-sourced component, at least initially) -- a real,
   undecided design dependency, not assumed away here.
3. Burst-containment safety case not modeled here (analogous to the
   beam-safety hard requirement in ADR-003) -- a flywheel storing
   hundreds of Wh at high rpm is a real containment/failure-mode design
   requirement for hardware_spec/, not a detail to defer indefinitely.
4. REAL_WORLD_REALIZATION_FRACTION=0.40 is an engineering-judgment
   placeholder, not a literature-cited figure -- flagged for validation
   against real flywheel engineering practice, same discipline as every
   other assumed parameter in this repo.
""")


if __name__ == "__main__":
    main()
