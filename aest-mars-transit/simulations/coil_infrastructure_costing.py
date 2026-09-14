"""
coil_infrastructure_costing.py  (v1 — new, Architecture Gen 2)
===================================================================
AEST Module 9: Coil-Cluster Conductor Mass & Material Costing

Why this module exists
-----------------------
ADR-006 Action Item #5 flagged the coil-cluster infrastructure as
costed only by a reactor/flywheel-mass proxy, not real material figures.
This module puts a real, cited conductor-mass floor under it — and finds
a real, previously-unflagged complication along the way: COPPER is not
an ISRU-friendly material on Mars, unlike the iron this whole
architecture's vehicles depend on.

The complication, found not assumed
----------------------------------------
Mars crustal copper abundance is only ~50ppm [Marspedia, citing
planetary geochemistry surveys] versus Earth ore-grade concentrations of
~1% (10,000ppm) — roughly 200x more dilute. No concentrated Mars copper
deposit has been confirmed. Copper for coil windings would very likely
need to be EARTH-IMPORTED, reintroducing exactly the ~$10,000+/kg launch
penalty this whole Gen 2 pivot was designed to escape for the vehicle
fleet — just for a different subsystem.

**Decision: evaluate an ALUMINUM-WOUND coil design instead.** Aluminum
is "much more common than copper, by many orders of magnitude" in Mars
regolith [same source] — it is a major constituent of feldspar/
plagioclase minerals, which are abundant in basaltic Mars regolith,
unlike copper's rarity. Aluminum is also lighter for EQUAL electrical
resistance, not just more abundant — a real, independent engineering
argument computed from first principles below, not just an ISRU
convenience.

Run: `python3 coil_infrastructure_costing.py`
"""

from __future__ import annotations

# ---------------------------------------------------------------------------
# Conductor material properties
# ---------------------------------------------------------------------------
RESISTIVITY_OHM_M = {"copper": 1.68e-8, "aluminum": 2.65e-8}
DENSITY_KG_M3 = {"copper": 8_960.0, "aluminum": 2_700.0}
MARS_CRUSTAL_ABUNDANCE_PPM = {"copper": 50.0, "aluminum": None}  # aluminum: no single
                                                                   # figure cited here,
                                                                   # but qualitatively
                                                                   # "orders of magnitude"
                                                                   # more abundant, tied up
                                                                   # in common feldspar
                                                                   # minerals [Marspedia]

# ---------------------------------------------------------------------------
# Reference design point: real terrestrial wireless-EV-charging hardware
# ---------------------------------------------------------------------------
# WiTricity (via International Copper Association): ~1.7kg copper in a fixed
# ground charging pad rated to 11kW (SAE J2954 passenger-vehicle limit).
REFERENCE_PAD_COPPER_KG = 1.7
REFERENCE_PAD_RATED_W = 11_000.0

# AEST per-vehicle grid draw at the dynamic-design chain efficiency
# (inductive_transfer_sim.py, Module 6)
AEST_PER_VEHICLE_GRID_W = 5_514.0

COPPER_PRICE_USD_KG = 12.5   # ~EUR 11.55/kg (Feb 2026 LME-linked spot,
                              # mercatometalli.com), converted at an
                              # approximate EUR/USD rate -- FLAGGED as an
                              # approximate Earth commodity price, not a
                              # Mars-delivered price (see [3] below for why
                              # that distinction is the whole point)
MARS_LAUNCH_MASS_COST_USD_KG = 10_000.0   # from the project's own founding
                                            # figure, used throughout this repo

CLUSTER_SCENARIOS_PER_100KM = {
    "1km spacing": 99,
    "500m spacing": 193,
    "200m spacing": 455,
}


def conductor_mass_ratio_equal_resistance(material_a: str, material_b: str) -> float:
    """Mass of material_a needed for the same resistance & length as material_b,
    expressed as a ratio (mass_a / mass_b)."""
    r_a = RESISTIVITY_OHM_M[material_a] * DENSITY_KG_M3[material_a]
    r_b = RESISTIVITY_OHM_M[material_b] * DENSITY_KG_M3[material_b]
    return r_a / r_b


def main() -> None:
    print("=" * 78)
    print("AEST Module 9: Coil-Cluster Conductor Mass & Material Costing")
    print("=" * 78)

    print(f"\n[1] Mars ISRU-sourceability check")
    print(f"    Copper crustal abundance on Mars: ~{MARS_CRUSTAL_ABUNDANCE_PPM['copper']:.0f}ppm "
          f"vs. Earth ore-grade ~10,000ppm (~200x more dilute)")
    print(f"    No confirmed concentrated Mars copper deposit -- copper is very likely")
    print(f"    an EARTH-IMPORT material for this architecture, unlike the iron the")
    print(f"    vehicle chassis and flywheel depend on (ADR-006).")
    print(f"    Aluminum: tied up in common feldspar/plagioclase minerals, abundant in")
    print(f"    basaltic Mars regolith -- 'orders of magnitude' more common than copper")
    print(f"    [Marspedia]. Evaluated below as the coil-winding material instead.")

    ratio = conductor_mass_ratio_equal_resistance("aluminum", "copper")
    print(f"\n[2] Aluminum vs. copper, EQUAL electrical resistance (same first-principles")
    print(f"    check this repo has applied to every other material choice)")
    print(f"    Aluminum conductor mass / copper conductor mass (same R, same length): "
          f"{ratio:.3f}")
    print(f"    Aluminum needs {1/conductor_mass_ratio_equal_resistance('copper','aluminum'):.2f}x the "
          f"cross-sectional area of copper for equal resistance,")
    print(f"    but at {DENSITY_KG_M3['copper']/DENSITY_KG_M3['aluminum']:.2f}x lower density -- net, "
          f"aluminum wiring is LIGHTER than copper for the same")
    print(f"    electrical job. This is the same physics that makes aluminum standard for")
    print(f"    long-distance overhead power transmission on Earth -- not a Mars-specific")
    print(f"    argument, an independently-true one that happens to also solve the ISRU gap.")

    pad_copper_scaled_kg = REFERENCE_PAD_COPPER_KG * (AEST_PER_VEHICLE_GRID_W / REFERENCE_PAD_RATED_W)
    pad_aluminum_scaled_kg = pad_copper_scaled_kg * ratio
    print(f"\n[3] Per-cluster conductor mass, scaled from the WiTricity reference design")
    print(f"    (11kW pad = {REFERENCE_PAD_COPPER_KG}kg copper) to AEST's "
          f"{AEST_PER_VEHICLE_GRID_W:.0f}W per-vehicle draw")
    print(f"    (linear power scaling assumed -- a real EM coil design would need FEA, not")
    print(f"    just linear scaling; flagged as an approximation, not a detailed design)")
    print(f"    Copper, scaled:   {pad_copper_scaled_kg:.3f}kg/cluster")
    print(f"    Aluminum, scaled: {pad_aluminum_scaled_kg:.3f}kg/cluster")

    print(f"\n[4] Total conductor mass & cost per 100km corridor, by cluster spacing "
          f"(Module 6 scenarios)")
    print(f"    {'spacing':<14} {'clusters/100km':>15} {'Al mass(kg)':>12} "
          f"{'Earth $ (raw material)':>23} {'IF Earth-imported ($)':>22}")
    for label, n_clusters in CLUSTER_SCENARIOS_PER_100KM.items():
        total_al_kg = n_clusters * pad_aluminum_scaled_kg
        earth_material_usd = total_al_kg * COPPER_PRICE_USD_KG  # conservative: price aluminum
                                                                   # at copper's $/kg as an
                                                                   # upper-bound placeholder;
                                                                   # aluminum is normally
                                                                   # cheaper per kg on Earth
        launch_cost_usd = total_al_kg * MARS_LAUNCH_MASS_COST_USD_KG
        print(f"    {label:<14} {n_clusters:>15} {total_al_kg:>12.1f} "
              f"{earth_material_usd:>23,.0f} {launch_cost_usd:>22,.0f}")

    print(f"""
[SYNTHESIS]
Even at the DENSEST spacing evaluated (200m), total conductor mass is on
the order of a few hundred kg per 100km -- trivial next to a single FSP
reactor unit's 6,000kg mass, and a genuine confirmation that raw
conductor material is NOT the coil-cluster cost bottleneck this repo
worried about in ADR-006. The real bottleneck (unresolved, still open)
is per-unit POWER ELECTRONICS and installation labor, which this module
does not have data for -- see ADR-007 Action Items.

If aluminum must be Earth-imported (the honest worst case, pending
confirmation that Mars regolith aluminum is practically extractable at
this scale), the launch-mass-cost column shows even that worst case is
a low-single-digit-million-dollar cost across a long corridor -- small
next to what importing vehicle CHASSIS mass at the same $/kg would have
cost, which is the whole reason ADR-006 moved the chassis to ISRU steel
in the first place. The pivot's core economic logic holds even under
the most conservative reading of the copper/aluminum sourcing question.

[OPEN ITEMS]
1. Linear power-scaling from the WiTricity reference pad is a rough
   approximation, not a real coil EM design -- flagged, not resolved.
2. Whether Mars regolith aluminum is practically ISRU-extractable AT
   THIS SCALE (not just present in trace/mineral form) is unconfirmed --
   same category of open dependency as the steel-chassis precondition
   in ADR-006.
3. Power electronics (inverters, resonant tuning capacitors, control
   systems) per coil cluster are entirely uncosted here -- likely the
   real cost driver, not the conductor.
""")


if __name__ == "__main__":
    main()
