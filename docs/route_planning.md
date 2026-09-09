# Route Planning: Terrain Line-of-Sight Masking

## What's already validated

ADR-001 checked the 10km transit-tier line-of-sight assumption against
planetary curvature only: a 2m rover beacon plus a ~5.9m hub tower
clears 10km of Mars curvature on flat terrain. That check holds — Mars
curvature is not the constraint.

## What isn't validated yet

Real Martian terrain is not flat. Crater rims, dune fields, boulder
fields, and channel walls can break line-of-sight locally at ranges far
shorter than the curvature limit, independent of tower height. A hub
sited without checking this can have "10km LOS" on paper and a dead
zone 2km out in practice.

## Recommended methodology (not yet executed — this is a scope note)

1. **Use existing Mars orbital elevation data** (e.g. MOLA global
   topography, HiRISE DEMs for candidate corridor regions) to compute a
   line-of-sight viewshed from each candidate hub site before
   committing to its placement — this is a standard GIS viewshed
   calculation, not new science.
2. **Prefer topographic highs for hub siting** (crater rims, ridgelines)
   over crater floors or channel bottoms — consistent with the tower-
   height-vs-range relationship already validated in ADR-001: siting on
   a natural elevation reduces the tower height needed for a given LOS
   range, or extends achievable range for a given tower height.
3. **Treat the hub-to-hub overlap zone assumed in
   `beam_tracking_sim.py` (500m) as a placeholder**, not a validated
   number — it needs to be checked against the actual viewshed at each
   hub pair once real terrain data is brought in, since local masking
   could shrink or eliminate the assumed overlap.
4. **Corridor route selection should be a joint optimization** between
   "shortest/most useful path" and "maximizes LOS chain reliability,"
   not chosen for terrain access alone and then hoped to work
   optically.

## Status

This is a placeholder identifying the methodology and the specific
numbers in this repo (hub tower height, 500m overlap zone) that depend
on it. No orbital data has been brought into this repository yet —
flagged as a concrete next step once real site candidates are chosen,
not before.
