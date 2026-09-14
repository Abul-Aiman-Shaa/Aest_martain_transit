"""
beam_tracking_sim.py  (v2 — multijunction intensity trade added)
=====================================================================
AEST Module 4: Beam Divergence, Spot/Receiver Matching, and Corridor Hand-off

v2 addition — answering an open pointing-complexity worry
-------------------------------------------------------
The original "modular beaming" proposal explicitly worried that reaching
higher receiver efficiency would come at the cost of beam-pointing
complexity ("multiple intake ports though beam pointing becomes
complicated"). ADR-005's literature research found the
efficiency gain does NOT require multiple beams — it requires a
multijunction (VMJ) receiver CHIP, still fed by ONE beam. The remaining
question this module had to check, not assume: does hitting that
receiver's efficient intensity WINDOW require shrinking the spot enough
to cost the ~45 microradian tracking margin ADR-003 deliberately bought
by ENLARGING the spot?

Checked in [6] below: no. Shrinking the spot from ADR-003's 0.6m (40% of
receiver) down to the ~0.3m needed to enter the multijunction target
intensity band actually IMPROVES geometric margin at a fixed range,
because margin is (receiver_diameter - spot_diameter)/2/range — a
SMALLER spot leaves MORE clearance to the receiver edge, not less. The
real, if more subtle, cost of a smaller spot is not edge-clearance
margin but sensitivity to non-uniform illumination and centering
accuracy on a segmented cell array — and the multijunction literature
found for ADR-005 shows that risk is smaller than expected too (tested
tolerant to partial illumination as low as ~7% area coverage with only
~2 percentage points of efficiency loss). Net finding: the multijunction
receiver upgrade is compatible with — and does not require reopening —
ADR-003's spot-matched tracking design.

The realistic finding this module leads with
-----------------------------------------------
A naive diffraction-limited design (minimize spot size) is the WRONG
goal for this system. A well-collimated fiber laser stays remarkably
tight over 10km even with a small transmit aperture — a 30cm aperture
produces roughly a 6cm spot at 10km. That sounds impressive, but a 6cm
spot inside a 1.5m receiver panel means the FSM has to hold pointing to
within about a spot-radius (~1 microradian-class tolerance) or the beam
walks entirely off the receiver. That is an unnecessarily hard problem
that the architecture doesn't need to accept.

Instead, this module treats spot size as a DESIGN CHOICE (via transmit
aperture), deliberately sized as a fraction of the receiver's own
diameter. A bigger, still-small transmit aperture requirement (a few cm)
combined with a spot at ~40% of receiver diameter gives tens of
microradians of REAL geometric tracking margin — two orders of
magnitude easier than the diffraction-limited case — at the cost of a
higher peak flux per unit area, which is still comfortably in a
manageable range (single-digit to tens of W/cm^2, not hundreds).

This is the standard trade in real laser power-beaming and free-space
optical comm system design: match beam footprint to receiver footprint,
don't minimize it just because you can.

Scope
-----
1. Beam divergence vs. transmit aperture (M^2-corrected, realistic for a
   combined multi-emitter fiber laser transmitter, not a single-mode lab
   demonstration).
2. Spot-vs-receiver matching trade table -> transmit aperture size,
   real geometric pointing margin, resulting flux.
3. Corridor hand-off: required FSM slew rate at closest approach, and
   acquisition-time budget in the hub-to-hub overlap zone.
4. Beam safety: the interlock requirement this flux level imposes,
   stated as a hard requirement rather than modeled in depth (this is
   a Class 4 laser system; treat it as such).

Run: `python3 beam_tracking_sim.py`
"""

from __future__ import annotations
import math

# ---------------------------------------------------------------------------
# Assumptions
# ---------------------------------------------------------------------------
WAVELENGTH_M = 975e-9
CORRIDOR_RANGE_M = 10_000.0        # worst-case hub-to-rover distance (ADR-001)
BEAM_QUALITY_M2 = 1.5              # realistic for a combined multi-emitter fiber laser
                                    # (single-emitter M^2~1.1-1.3; combining several for
                                    # power degrades this — flagged for validation against
                                    # a real transmitter design)

RECEIVER_DIAMETER_M = 1.5          # rover PV receiver panel (needs reconciling with
                                    # hardware_spec/receiver_ports.md when written)
DOCK_OPTICAL_POWER_W = 13_714.0    # from supercap_sizing.py baseline recommendation

CRUISE_SPEED_MS = 15.0 * 1000 / 3600
HUB_STANDOFF_SWEEP_M = [200, 500, 1000, 2000]   # hub offset from route centerline
HANDOFF_OVERLAP_ZONE_M = 500.0     # assumed LOS overlap between adjacent hub coverage cells

GAUSSIAN_PEAK_TO_AVG_FACTOR = 2.0  # real beam profile peak vs uniform-equivalent average


def full_angle_divergence_rad(d_tx_m: float, m2: float = BEAM_QUALITY_M2) -> float:
    """Embedded-Gaussian full-angle divergence."""
    return 4 * m2 * WAVELENGTH_M / (math.pi * d_tx_m)


def spot_diameter_m(d_tx_m: float, range_m: float = CORRIDOR_RANGE_M) -> float:
    return full_angle_divergence_rad(d_tx_m) * range_m


def transmit_aperture_for_spot_m(target_spot_m: float, range_m: float = CORRIDOR_RANGE_M) -> float:
    theta_needed = target_spot_m / range_m
    return 4 * BEAM_QUALITY_M2 * WAVELENGTH_M / (math.pi * theta_needed)


def main() -> None:
    print("=" * 78)
    print("AEST Module 4: Beam Divergence, Spot/Receiver Matching, Corridor Hand-off")
    print("=" * 78)

    print(f"\n[1] Naive diffraction-limited spot size vs. transmit aperture "
          f"(M2={BEAM_QUALITY_M2}, range={CORRIDOR_RANGE_M/1000:.0f}km)")
    for d_tx in [0.1, 0.2, 0.3, 0.5, 1.0]:
        spot = spot_diameter_m(d_tx)
        print(f"    D_tx={d_tx:>4.1f}m -> spot={spot*100:6.2f}cm "
              f"(pointing tolerance ~spot-radius: {spot/2/CORRIDOR_RANGE_M*1e6:5.2f} urad -- TIGHT)")
    print("    Minimizing spot size is the wrong goal: it creates a pointing problem")
    print("    the architecture doesn't need to accept. See [2].")

    print(f"\n[2] Spot-matched design: spot sized as a fraction of the "
          f"{RECEIVER_DIAMETER_M}m receiver diameter")
    print(f"    {'spot_frac':>9} {'spot_d(m)':>9} {'D_tx(cm)':>9} "
          f"{'geom_margin(urad)':>18} {'avg_flux(W/cm2)':>16} {'peak~2x(W/cm2)':>15}")
    recommended_frac = 0.4
    for frac in [0.2, 0.4, 0.6, 0.8]:
        spot_d = frac * RECEIVER_DIAMETER_M
        d_tx = transmit_aperture_for_spot_m(spot_d)
        geom_margin_urad = ((RECEIVER_DIAMETER_M - spot_d) / 2) / CORRIDOR_RANGE_M * 1e6
        area_m2 = math.pi * (spot_d / 2) ** 2
        avg_flux = DOCK_OPTICAL_POWER_W / area_m2 / 1e4
        peak_flux = avg_flux * GAUSSIAN_PEAK_TO_AVG_FACTOR
        marker = "  <- recommended" if frac == recommended_frac else ""
        print(f"    {frac:>9.1f} {spot_d:>9.2f} {d_tx*100:>9.2f} "
              f"{geom_margin_urad:>18.1f} {avg_flux:>16.2f} {peak_flux:>15.2f}{marker}")

    rec_spot = recommended_frac * RECEIVER_DIAMETER_M
    rec_d_tx = transmit_aperture_for_spot_m(rec_spot)
    rec_margin = ((RECEIVER_DIAMETER_M - rec_spot) / 2) / CORRIDOR_RANGE_M * 1e6
    print(f"""
    RECOMMENDATION: spot at {recommended_frac*100:.0f}% of receiver diameter
    ({rec_spot:.2f}m). Transmit aperture needed: just {rec_d_tx*100:.1f}cm
    (cheap, compact optics). Real geometric tracking margin:
    {rec_margin:.0f} microradians before the spot edge reaches the
    receiver edge — roughly 15-50x more forgiving than the naive
    diffraction-limited case in [1], for a modest, manageable flux
    increase. This also argues for a MOSAIC/TILED receiver PV array
    (independent cells, bypass diodes) rather than a single monolithic
    cell, so power generation degrades gracefully if the spot is only
    partially centered rather than requiring exact full-panel
    illumination.
    """)

    print(f"[3] Corridor hand-off: FSM slew rate required at closest approach "
          f"(cruise {CRUISE_SPEED_MS*3.6:.0f}km/h)")
    for standoff in HUB_STANDOFF_SWEEP_M:
        omega = CRUISE_SPEED_MS / standoff
        print(f"    hub standoff={standoff:>4}m -> {omega*1000:6.2f} mrad/s")
    print("    Commercial FSM slew capability is typically many mrad/s to rad/s --")
    print("    not a bottleneck at any plausible hub standoff distance.")

    t_overlap = HANDOFF_OVERLAP_ZONE_M / CRUISE_SPEED_MS
    print(f"\n[4] Hand-off acquisition time budget")
    print(f"    Assumed LOS overlap zone between adjacent hubs: {HANDOFF_OVERLAP_ZONE_M}m")
    print(f"    Time available for the incoming hub to acquire lock: {t_overlap:.1f}s")
    print("    Typical LiDAR coarse-acquisition + quad-detector fine-lock: sub-second")
    print("    to a few seconds. Ample margin; hand-off is not a bottleneck at this")
    print("    corridor geometry, PROVIDED the overlap zone is verified against real")
    print("    terrain (see docs/route_planning.md and docs/atmospheric_optics.md for the")
    print("    LOS-masking and dust-transmission risks this assumes away).")

    print(f"\n[5] Multijunction receiver intensity trade — does a smaller, higher-intensity "
          f"spot cost tracking margin? (ADR-005)")
    corridor_received_w = 6_666.0   # multijunction-target scenario, corridor trickle (Module 1/2)
    mj_target_intensity_w_cm2 = 30.0   # bottom of the 30-75 W/cm^2 peak-efficiency band, MDPI 13(3):246
    spot_area_m2 = corridor_received_w / (mj_target_intensity_w_cm2 * 1e4)
    mj_spot_d = 2 * math.sqrt(spot_area_m2 / math.pi)
    mj_d_tx = transmit_aperture_for_spot_m(mj_spot_d)
    mj_margin_urad = ((RECEIVER_DIAMETER_M - mj_spot_d) / 2) / CORRIDOR_RANGE_M * 1e6
    print(f"    Target: enter the {mj_target_intensity_w_cm2:.0f}-75 W/cm^2 multijunction peak-efficiency")
    print(f"    band (MDPI Photonics 13(3):246) at {corridor_received_w:.0f}W received (corridor")
    print(f"    trickle, multijunction-target scenario, photon_conversion.py v4).")
    print(f"    Required spot: {mj_spot_d*100:.1f}cm ({mj_spot_d/RECEIVER_DIAMETER_M*100:.0f}% of receiver) "
          f"-> D_tx={mj_d_tx*100:.1f}cm -> geometric margin={mj_margin_urad:.0f} urad")
    print(f"    Compare to ADR-003's spot-matched baseline: 0.6m spot (40% of receiver), 45 urad margin.")
    print(f"    A SMALLER spot gives MORE edge-clearance margin at fixed range, not less --")
    print(f"    {mj_margin_urad:.0f} urad here vs. 45 urad baseline. This is the ADR-005 finding")
    print(f"    that resolves the original pointing-complexity worry: reaching the")
    print(f"    multijunction efficiency band does not reopen ADR-003's tracking-margin trade,")
    print(f"    it improves it. The finer-grained risk (illumination uniformity/centering on a")
    print(f"    segmented cell) is addressed in photon_conversion.py v4's citations, not here --")
    print(f"    literature shows multijunction receivers tolerant to partial/off-center")
    print(f"    illumination down to ~7% area coverage with only ~2 percentage points of")
    print(f"    efficiency loss (see docs/literature_review.md #9), so this is a real but")
    print(f"    secondary risk, not a blocking one.")

    print(f"""
[6] BEAM SAFETY (stated as a hard requirement, not modeled in depth here)
This is a Class 4 laser system by any classification standard, even at
the reduced spot-matched flux levels above. Required, non-negotiable
design elements:
  - Fail-safe cutoff: beam shuts down within milliseconds of losing
    retroreflector lock, LOS confirmation, or valid rangefinder return
    (i.e. the default failure state is OFF, not "keep transmitting and
    hope").
  - Exclusion zones around the beam path and around hub transmitter
    apertures, sized for the worst-case flux in [2], enforced
    procedurally for any crewed operations near a route or hub.
  - Independent range-gating: don't fire at a target unless its
    ranged distance matches the expected rover/beacon return — guards
    against beaming into an unintended object that wanders into the
    path.
This is a systems/ops requirement to carry into hardware_spec/ and any
future safety case, not a simulation output — flagging it here so it
isn't silently dropped while we focus on power/thermal math.
""")


if __name__ == "__main__":
    main()
