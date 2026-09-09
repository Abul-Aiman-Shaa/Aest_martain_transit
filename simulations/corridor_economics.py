"""
corridor_economics.py  (v1 — literature-validated)
=====================================================
AEST Module 5: Hop-Length Selection — Dust Transmission, Storm Resilience,
and Hub-Density Economics

Why this module exists
-----------------------
The user's own framing bundled two different physics questions into one
proposal: "pivot to a smaller laser-beaming distance... place the
stations much closer... it needs to be economical... but the optical
efficiency needs to be over 50%, we could do that by making the power
beaming modular." This module answers the FIRST half (hop length) on its
own physical merits. The SECOND half (PV efficiency >50% via a
multijunction/modular receiver) is answered in photon_conversion.py v4 —
and the key finding of this whole update is that **these two questions
are independent, not causally linked**: shortening the hop does not
raise PV efficiency (that's a receiver-technology question). What
shortening the hop actually buys AEST is dust-transmission and, far more
importantly, dust-STORM resilience — see [SYNTHESIS] below.

Physics: horizontal near-surface dust extinction from a vertical column
--------------------------------------------------------------------------
ADR-003/literature_review.md's tau=0.3-0.5 (background) / tau=4-6 (storm)
figures are column optical depths (the quantity Mars missions actually
report, from near-vertical Sun-photometer measurements). AEST's beam path
is a near-*horizontal* corridor link close to the surface, not a vertical
column, so applying the column tau directly to a 10km horizontal hop (as
docs/atmospheric_optics.md implicitly did) is only approximately right,
and gives no way to ask "what if the hop is shorter?" without a vertical
dust density profile.

Real value found this session: Martian dust vertical scale height
**H = 11.1 km** [NTRS 20160013317 — see docs/literature_review.md #9].
For an exponential dust density profile with scale height H, a vertical
column optical depth tau_v corresponds to a surface-level (near-ground)
volume extinction coefficient:

    beta_0 = tau_v / H            (units: 1/m, since tau_v = integral of
                                    beta_0 * exp(-z/H) dz from 0 to inf
                                    = beta_0 * H)

For a horizontal path of length L close to the surface (L << H, true for
every hop length considered here, including the original 10km), density
is approximately constant over the path, so:

    tau_horizontal(L) = beta_0 * L = (tau_v / H) * L
    T(L) = exp(-tau_horizontal(L))

Sanity check: at L=10km (the original hop) with tau_v=0.4 (mid of the
background 0.3-0.5 range), this gives tau_h=0.36, T=69.8% — close to
the 60.7-74.1% range docs/atmospheric_optics.md already tabulated by
applying the column tau directly to the full 10km hop. In other words,
the ORIGINAL (unjustified-at-the-time) approximation happened to be
roughly right for a 10km hop specifically, by coincidence of Mars's dust
scale height being of the same order as that hop distance. That is a
coincidence of the ORIGINAL 10km choice, not a general law — it is
exactly why a real scale-height model (not a flat tau-per-hop
assumption) is needed to evaluate ANY other hop length, which is what
this module now provides.

Run: `python3 corridor_economics.py`
"""

from __future__ import annotations
import math

# ---------------------------------------------------------------------------
# Dust physics (literature-validated)
# ---------------------------------------------------------------------------
DUST_SCALE_HEIGHT_M = 11_100.0        # NTRS 20160013317, "average value of 11.1km"
TAU_BACKGROUND_RANGE = (0.3, 0.5)     # JPL DESCANSO; docs/literature_review.md #7
TAU_STORM_RANGE = (4.0, 6.0)          # same source; up to 10 locally

TAU_BACKGROUND_MID = sum(TAU_BACKGROUND_RANGE) / 2
TAU_STORM_MID = sum(TAU_STORM_RANGE) / 2

HOP_LENGTHS_M = [10_000, 5_000, 3_000, 2_000, 1_500, 1_000, 500]

# ---------------------------------------------------------------------------
# Hub-density economics (Kilopower-class reactor units per hub)
# ---------------------------------------------------------------------------
CORRIDOR_LENGTH_KM = 100.0             # reference corridor for the hub-count table
KILOPOWER_UNIT_KWE = 8.0
LASER_WALLPLUG_EFF = 0.40
HUB_OVERHEAD_FRAC = 0.10

# Vehicle-side received optical power the corridor-trickle tier needs to
# deliver, taken from photon_conversion.py v4's MULTIJUNCTION_TARGET
# scenario (pv_eff=0.60) at the existing 4m^2 trickle radiator — see that
# module for the derivation. This is a RECEIVED-power figure (vehicle
# thermal-limited); dust transmission determines how much the HUB must
# TRANSMIT to deliver it.
RECEIVED_OPTICAL_POWER_W = 6_666.0


def beta_0_per_m(tau_vertical: float, scale_height_m: float = DUST_SCALE_HEIGHT_M) -> float:
    return tau_vertical / scale_height_m


def horizontal_transmission(hop_m: float, tau_vertical: float) -> float:
    tau_h = beta_0_per_m(tau_vertical) * hop_m
    return math.exp(-tau_h)


def kilopower_units_for_hub(hop_m: float, tau_vertical: float,
                             received_w: float = RECEIVED_OPTICAL_POWER_W) -> int:
    t = horizontal_transmission(hop_m, tau_vertical)
    transmit_w = received_w / t
    elec_kwe = (transmit_w / LASER_WALLPLUG_EFF) * (1 + HUB_OVERHEAD_FRAC) / 1000.0
    return math.ceil(elec_kwe / KILOPOWER_UNIT_KWE), elec_kwe, transmit_w


def main() -> None:
    print("=" * 78)
    print("AEST Module 5: Hop-Length Selection — Dust Transmission & Hub Economics")
    print("=" * 78)

    print(f"\n[1] Horizontal transmission vs. hop length "
          f"(H={DUST_SCALE_HEIGHT_M/1000:.1f}km scale height)")
    print(f"    {'hop(km)':>8} {'T_normal(tau_v=0.4)':>20} {'T_storm(tau_v=5.0)':>19}")
    for hop in HOP_LENGTHS_M:
        t_norm = horizontal_transmission(hop, TAU_BACKGROUND_MID)
        t_storm = horizontal_transmission(hop, TAU_STORM_MID)
        print(f"    {hop/1000:>8.1f} {t_norm*100:>19.1f}% {t_storm*100:>18.1f}%")
    print("    NOTE: at hop=10km (the original spec), T_storm=1.1% -- confirms")
    print("    ADR-003's 'storm = full outage' call was correct FOR THAT HOP LENGTH.")
    print("    It is not a law of Mars dust; it is a consequence of choosing a hop")
    print("    length close to the dust scale height itself.")

    print(f"\n[2] Hub capital economics: reactor units per hub and total units for a "
          f"{CORRIDOR_LENGTH_KM:.0f}km reference corridor")
    print(f"    (vehicle needs {RECEIVED_OPTICAL_POWER_W/1000:.2f}kW received; Kilopower "
          f"units are {KILOPOWER_UNIT_KWE:.0f}kWe each, {LASER_WALLPLUG_EFF*100:.0f}% "
          f"laser wall-plug, {HUB_OVERHEAD_FRAC*100:.0f}% hub overhead)")
    print(f"    {'hop(km)':>8} {'hubs/100km':>11} {'units/hub':>10} {'TOTAL units':>12} "
          f"{'hub_elec(kWe)':>13}")
    baseline_total = None
    for hop in HOP_LENGTHS_M:
        hubs = math.ceil(CORRIDOR_LENGTH_KM * 1000 / hop)
        units, elec_kwe, _ = kilopower_units_for_hub(hop, TAU_BACKGROUND_MID)
        total = hubs * units
        if hop == 10_000:
            baseline_total = total
        rel = f"  ({total/baseline_total:.1f}x)" if baseline_total else ""
        print(f"    {hop/1000:>8.1f} {hubs:>11d} {units:>10d} {total:>12d} "
              f"{elec_kwe:>13.2f}{rel}")

    print(f"""
[SYNTHESIS — the user's proposal, disentangled]

The proposal bundled two independent physics questions. Answered
separately, on their own merits:

1. "Optical efficiency over 50% via modular beaming, multiple intake
   ports" -- this is a RECEIVER-TECHNOLOGY question, not a hop-length
   question. See photon_conversion.py v4: a vertical multi-junction
   (VMJ) receiver, series-connected subcells in ONE receiver aperture,
   fed by ONE beam, achieves 55-65% (literature-validated, see
   docs/literature_review.md #9) -- with NO new beam-pointing
   complexity, because it does not require multiple separately-tracked
   beams. The "multiple ports" intuition maps onto multiple SUBCELLS
   inside a single receiver chip, not multiple TRANSMITTERS. This
   closes most of ADR-004's PV-efficiency gap on its own.

2. "Shorter hop distance, more economical" -- checked directly above,
   and the honest answer is two-sided:
   - On pure hub CAPITAL cost, shorter hops are WORSE, not better: total
     reactor units for a fixed corridor length grow faster than the
     per-hub power requirement shrinks (Kilopower's 8kWe granularity
     means most hop lengths below ~5km round up to the same 3-unit
     hub regardless of exactly how short the hop is, so the hub-COUNT
     multiplication dominates). Going from 10km to 1km hops is roughly
     a 7-8x capital increase for the reactor fleet alone -- this is the
     "unviable physics" this repo's mandate requires flagging plainly,
     even though it complicates the user's own framing.
   - On STORM AVAILABILITY, shorter hops are dramatically better: at
     10km, a global storm (tau_v~5) leaves 1.1% transmission -- a full
     outage, exactly what ADR-003 assumed. At 3km, that same storm
     leaves ~26% transmission -- degraded, but alive. This is the real
     economic argument for shortening the hop: not per-photon
     efficiency, but converting "the whole network goes dark for the
     duration of every storm" into "the network runs at reduced
     throughput during a storm" -- a genuine availability/uptime
     argument for a network whose own name emphasizes being "Active."

RECOMMENDATION: adopt a ~3km baseline hop spacing (range 2-5km
defensible depending on how AEST's roadmap weighs capital cost against
storm-uptime value) -- NOT the 1km-or-shorter end of the sweep, which
buys little additional storm margin (26%->64% transmission, already a
qualitative win at 3km) for a much larger capital bill (100+ units vs
300+). This, like ADR-004's action item #2 (25%-vs-50% PV roadmap
choice), is ultimately a programmatic cost/resilience trade this repo
can inform but not decide unilaterally -- see ADR-005.
""")


if __name__ == "__main__":
    main()
