# Coil-Cluster Transmitter Spec

**Status:** done (v1) — replaces the Gen 1 `receiver_ports.md` /
`transmitter_hub.md` concepts (laser/PV-specific, superseded per
ADR-006).
**Depends on:** `simulations/inductive_transfer_sim.py` (Module 6),
`simulations/coil_infrastructure_costing.py` (Module 9), ADR-006.

## What a coil cluster is

A short sequence of primary (transmit) coils embedded in or alongside
the route surface, spaced at 70%-pitch within a cluster (per ORNL's
dynamic-charging design practice, ADR-006), energized by a power cable
run back to the centralized FSP fission plant — NOT an independent
generation site, unlike a Gen 1 hub. Clusters are spaced hundreds of
meters to a few kilometers apart (Module 6); the onboard flywheel
bridges the powerless gap between them.

## Core requirements

1. **Conductor material: aluminum, not copper** (Module 9). Copper is
   not credibly ISRU-sourceable on Mars (crustal abundance ~50ppm vs.
   Earth ore-grade ~10,000ppm); aluminum is tied up in common feldspar
   minerals, abundant in basaltic regolith, and is independently the
   lighter choice for equal electrical resistance regardless of the
   ISRU argument.
2. **Fail-safe default-OFF energization.** Each coil segment energizes
   only when a vehicle's presence is confirmed overhead (analogous to
   Gen 1's beam-safety default-OFF requirement, ADR-003) — both for
   transmission efficiency (no wasted power on empty track) and safety
   (no standing field where none is needed).
3. **Per-cluster power rating: sized to AEST's per-vehicle grid draw**
   (~5.5kW at the dynamic-design chain-efficiency scenario, Module 6),
   not to the SAE J2954 11kW passenger-EV reference used only as a
   scaling anchor for conductor mass (Module 9) — a real coil design
   would re-derive from AEST's actual power level via FEA, not linear
   scaling (flagged open item, Module 9).
4. **Coupling geometry:** coil diameter ≈ 3x magnetic air gap, per ORNL
   design practice (ADR-006) — the vehicle's ground clearance sets the
   air gap, which in turn sets the minimum practical coil diameter.
   Vehicle ground-clearance requirement for rough Martian terrain is NOT
   yet reconciled against this constraint — open item.
5. **Dust tolerance:** near-field magnetic coupling is not meaningfully
   attenuated by suspended dust (ADR-006's central finding), but slow
   accumulation of magnetically-susceptible dust fines directly ON the
   coil/core surface is a separate, monitorable (not blocking) risk —
   Mars dust's bulk saturation magnetization (~4 A·m²/kg, largely
   non-magnetic silicate with a minor magnetic fraction) suggests this
   is a slow degradation mode, not an acute failure mode, but it has not
   been quantified here.

## What this spec does NOT cover (open items)

1. Power electronics per cluster (inverter, resonant tuning capacitors,
   control system) — entirely uncosted (Module 9's biggest caveat).
2. Real EM coil design (turns count, ferrite core geometry, frequency)
   — this document uses a scaled terrestrial reference design (SAE
   J2954 / WiTricity), not a from-scratch design.
3. Structural mounting and Martian-terrain installation method — not
   addressed.
4. Cable run distribution losses from the centralized FSP plant to each
   cluster — not modeled; `inductive_transfer_sim.py`'s chain efficiency
   starts at "grid," i.e., after distribution, not at the reactor
   busbar.
5. A real spatially-resolved dynamic coupling efficiency profile (the
   single biggest open item carried from ADR-006 Action Item #2) — this
   spec still relies on the same two-point ORNL bracket (static 91.3%,
   dynamic-midpoint 50%-of-peak) rather than a validated curve.
