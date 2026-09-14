# Flywheel Buffer: Bearing Selection & Burst-Safety Spec

**Status:** done (v1) — closes ADR-006 Action Items #4 and #6.
**Depends on:** `simulations/flywheel_buffer_sizing.py` (Module 7), ADR-006.

## 1. Bearing selection: magnetic, not mechanical

Gen 1 already established the reasoning pattern this follows: mechanical
gearboxes were rejected in favor of BLDC in-wheel direct-drive motors
specifically to remove the lubricant cold-tolerance failure mode across
Mars's -125°C to +50°C range (ADR-002). The flywheel rotor has the same
problem in a different place — any oil- or grease-lubricated bearing is
a Martian-night failure point.

**Decision: magnetic bearings** (active magnetic bearings, AMB, or a
hybrid active/passive configuration). This is established, if
specialized, technology — magnetic bearing reaction wheels have real
spacecraft heritage going back decades [NASA Technical Reports Server,
"Magnetic bearing reaction wheel," NTRS 19760020248], and remain an
active research area for satellite momentum/reaction wheels today.

**What this decision costs, stated plainly:** an AMB system needs its
own control electronics and continuous power draw to maintain
levitation — this repo has not found a specific power-draw figure at
AEST's rotor scale (an open item, not fabricated here), and that control
electronics package is, at least initially, an Earth-sourced component
AEST's ISRU-manufacturability goal (ADR-006) does not yet reach. This is
carried forward as an explicit dependency, the same way the Mars steel
industry itself is: real and load-bearing, not assumed away.

**Alternative considered:** passive magnetic bearings (PMB) avoid the
continuous power draw and control-electronics dependency but provide
less stiffness and control authority than AMB. Not selected as the
baseline here, but worth a dedicated trade study once real rotor mass
and dynamics are fixed (see Open Items).

## 2. Burst safety: prevention, not containment

**An early design instinct — "wrap it in a containment ring" — does
not survive contact with real flywheel engineering practice, so it is
dropped here rather than carried forward.** Sandia National
Laboratories' flywheel engineering guidance
states plainly: "successful containment requires a structure many times
more massive than the rotor itself," and that "the incorporation of
adequate containment would multiply the weight and cost of the flywheel
system defeating the objective of providing cost effective energy
storage" [Sandia Report SAND2015-10759].

**Decision: adopt a prevention-based safety philosophy**, per the same
source's recommended practice:
- Treat the flywheel rotor as a **safety-critical / life-critical
  component** engineered to avoid burst over the system's operating
  life, not a component expected to fail safely into a containment
  structure.
- **Design margin of 2.0** (ratio of burst stress to maximum allowable
  operating stress).
- **Operate production rotors at ≤70% of qualification test speed** —
  i.e., every flight/field rotor is spun to a higher speed than it will
  ever see in service, during qualification testing, with a real margin
  held in reserve for the rest of its life.

This directly informs `flywheel_buffer_sizing.py`'s
`REAL_WORLD_REALIZATION_FRACTION=0.40` engineering-margin discount
(Module 7) — that discount is not just a generic "real systems
underperform theory" placeholder, it is specifically consistent with
operating at a fraction of burst-limited tip speed for safety margin,
now grounded in a real engineering source rather than an assumed
fraction.

## 3. Hybrid buffer question (ADR-006 Action Item #7) — resolved, not adopted

A hybrid flywheel + small supercapacitor buffer was flagged as
unevaluated. Quick resolution: the flywheel alone already comfortably
covers Module 6's gap-bridging requirement (57-114kg at the recommended
500m-1km spacing) with headroom, and a hybrid system would add a second
storage technology's worth of failure modes, qualification burden, and
BOM complexity for a capability this architecture does not currently
need (neither faster response — flywheels already excel at burst power
— nor materially more energy density, per Module 7's parity finding).
**Not adopted.** Worth revisiting only if a future finding shows the
flywheel alone is insufficient for some load case not yet identified.

## Open Items

1. AMB control-electronics mass, power draw, and Earth-sourcing
   dependency not yet quantified at AEST's actual rotor scale.
2. PMB-vs-AMB trade study deferred until real rotor mass/dynamics exist.
3. This spec assumes a single-rotor-per-vehicle design; a multi-rotor
   (smaller, distributed) configuration might reduce individual-failure
   consequence at the cost of more bearings/control loops — not
   evaluated.
4. No burst kinetic-energy-vs-vehicle-occupant-safety-distance analysis
   performed — the "prevention, not containment" philosophy still needs
   a stated minimum keep-out/mounting-location requirement for occupied
   vehicle variants, deferred to a future crew-safety-specific pass.
