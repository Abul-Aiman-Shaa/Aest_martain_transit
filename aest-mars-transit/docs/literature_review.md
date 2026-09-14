# Literature Review: Validating AEST's Open Parameters

Five parameters were flagged across ADR-001 through ADR-003 as
assumed/swept rather than measured. This document records what was
found, with sources, and what changed in the code as a result.

## 1. Supercapacitor specific energy

**Assumed (v1):** swept parametrically, 8-40Wh/kg, no anchor.

**Found:** Skeleton Technologies SkelCap D60 curved-graphene
ultracapacitor — the market-leading commercial graphene supercapacitor
product — specifies **6.8-11.1 Wh/kg** gravimetric energy density.
[Skeleton Technologies SkelCap product page](https://www.skeletontech.com/skelcap-ultracapacitor-cells)

Academic claims of much higher energy density (60-100+ Wh/kg) exist in
the literature — e.g. the widely-cited ["Graphene-Based Supercapacitor with an Ultrahigh Energy Density" (Nano Letters, 2010)](https://pubs.acs.org/doi/10.1021/nl102661q)
— but these are material/cell-level lab results, not validated
pack-engineering numbers for a vehicle-scale bank. Treated as
aspirational, not adopted as the design baseline.

**Action taken:** `supercap_sizing.py` now uses the real 6.8-11.1Wh/kg
range as its baseline sweep. This lowers the sortie-range and
dock-energy numbers from v1's speculative 20Wh/kg mid-estimate.

## 2. Supercapacitor specific power

**Assumed:** 10kW/kg, per the original architecture spec.

**Found:** the same SkelCap D60 datasheet specifies **22.1-28.4 kW/kg**,
with up to **80kW/kg** in some configurations — 2-8x higher than the
architecture doc's own figure.
[Skeleton Technologies SkelCap product page](https://www.skeletontech.com/skelcap-ultracapacitor-cells)

**Action taken:** updated in `supercap_sizing.py`. Strengthens the
existing "peak power is never the bank-sizing constraint" finding —
real hardware is even less power-limited than assumed.

## 3. Supercapacitor operating temperature — the architecture's -100C claim did not survive this check

**Assumed (original spec):** -100C to +50C operational range.

**Found:**
- Real commercial hardware (SkelCap D60): rated **-40C to +65C**.
  [Skeleton Technologies SkelCap product page](https://www.skeletontech.com/skelcap-ultracapacitor-cells)
- Best documented COLD-temperature research result: **-75C**, using a
  specialized acetonitrile/1,3-dioxolane co-solvent electrolyte, but
  with capacitance dropping to **~50% of room-temperature value** at
  that point and increased ESR (reduced power capability).
  [NASA Tech Briefs / NTRS 20090011272, "Low-Temperature Supercapacitors"](https://ntrs.nasa.gov/api/citations/20090011272/downloads/20090011272.pdf)
- No source found supporting -100C operation for any supercapacitor
  chemistry, commercial or research-stage.

**This is a genuine correction to the architecture's own stated spec**,
not a refinement of an AEST assumption. **Action taken:**
`thermal_management.py` now uses -40C as the baseline bay-temperature
design target (matching real, buildable hardware) and reports -75C as
an explicit "aggressive R&D" alternative with its capacity penalty
stated, not as a free assumption. The original -100C figure should be
considered unsupported until a specific source is found that
contradicts this search.

## 4. Laser wall-plug efficiency (electrical → optical)

**Assumed:** 40% design value (v1 already conservative relative to
industry claims).

**Found:** IPG Photonics (market-leading fiber laser manufacturer)
states wall-plug efficiency **"over 50%"** for its YLS-ECO high-power
CW fiber laser line.
[IPG YLS-ECO product page](https://www.ipgphotonics.com/en/products/lasers/high-power-cw-fiber-lasers/1-micron-3/yls-eco-1-10-kw)
Independent technical reference RP Photonics confirms **"best cases ~50%"**
for high-power fiber lasers generally, with diode-pumped solid-state
lasers more typically around 25% and thin-disk designs above 30%.
[RP Photonics: Wall-plug Efficiency](https://www.rp-photonics.com/wall_plug_efficiency.html)

**Action taken:** none needed — the existing 40% design value sits
comfortably below the cited ~50% ceiling, which is exactly the
intended margin. Confirmed, not changed.

## 5. Photovoltaic receiver efficiency — the most consequential finding

**Assumed (v2):** 48-50% design target, citing the architecture doc's
own 45-50% claim.

**Found — a real gap between lab records and field demonstrations:**
- Lab records at adjacent wavelengths: **>50%** at 1064nm, room
  temperature [Vasil'ev et al., "Optimization of photoelectric
  parameters of InGaAs metamorphic laser (1064nm) power converters
  with over 50% efficiency," Solar Energy Materials and Solar Cells,
  2021](https://www.sciencedirect.com/science/article/abs/pii/S0927024820303093);
  up to **67.5%** at 1470nm, but only at **77K (liquid nitrogen)
  temperature** [Photonics 11(2):130, 2024](https://www.mdpi.com/2304-6732/11/2/130).
- Real field demonstration: DARPA's POWER program (2025) — an actual
  outdoor laser power-beaming system, 800W delivered over 8.6km —
  measured only **">20%"** optical-to-electrical efficiency at its
  best case (shorter distances). [DARPA POWER program news release, 2025](https://www.darpa.mil/news/2025/darpa-program-distance-record-power-beaming)

No 975nm-specific data was found in either category — the closest
matches are 1064nm and 1470nm devices, a real gap in the literature
for this exact wavelength.

**This is the single most consequential correction from this
research pass.** A 50%-vs-20% split is not a rounding difference — it
roughly doubles or halves every downstream power/thermal number
depending which one is used. **Action taken:** `photon_conversion.py`
v3 now carries BOTH as named scenarios — `PV_EFFICIENCY_CONSERVATIVE
= 0.25` (rounded up slightly from the demonstrated >20% floor) and
`PV_EFFICIENCY_TARGET = 0.50` (lab-record-supported aspiration) —
rather than picking one. All downstream modules (`supercap_sizing.py`,
`thermal_management.py`) now compute both scenarios explicitly. See
ADR-004 for the architectural consequences.

## 6. MLI effective emissivity (bonus — corrects the v1 thermal model itself)

**Assumed (v1):** an ad hoc linear "U-value" sweep (0.05-0.3 W/m^2K),
not how MLI performance is actually characterized or reported.

**Found:** real spacecraft MLI is characterized by an **effective
emissivity (eps\*)** used directly in the Stefan-Boltzmann radiative
form. Measured values:
- Real-world spacecraft MLI (with normal seams, penetrations,
  mounting hardware): **eps\* = 0.015-0.03**
  [COBEM 2013 experimental paper, 25-layer Mylar/Dacron MLI](https://www.abcm.org.br/anais/cobem/2013/PDF/1126.pdf);
  [TTU thesis on MLI blanket performance](https://ttu-ir.tdl.org/server/api/core/bitstreams/c10fabaa-e1b4-40b0-b62b-f166e87480cc/content)
- Laboratory-only best case (not realistic for a fielded vehicle):
  **eps\* = 0.005**

**Action taken:** `thermal_management.py` v2 replaces the entire v1
U-value model with the physically correct radiative form using
eps\*=0.02 (mid of the real-world range). Net effect: night heat-loss
numbers came out LOWER than v1's ad hoc model, even at the warmer,
corrected -40C bay target — a genuine improvement that only surfaced
because the model itself was checked against real data, not just the
input numbers.

## 7. Mars dust optical depth (validates ADR-003, one correction)

**Assumed (ADR-003):** background tau=0.3-0.5, storm tau>=2 treated as
full outage, with a hedge that NIR might be somewhat lower than
visible.

**Found — confirms the numbers, corrects the hedge:**
- Background/clear conditions: **tau = 0.3-0.5** at 0.67 micron.
  [JPL DESCANSO, "Martian Dust Storms and Their Effects on Propagation"](https://descanso.jpl.nasa.gov/propagation/mars/MarsPub_sec5.pdf)
- Global storm conditions: **tau = 4-6**, locally **up to 10**. Same
  source; corroborated by the [2018 Mars global dust storm](https://en.wikipedia.org/wiki/2018_Mars_global_dust_storm)
  record (tau up to 5, locally 10+) that ended Opportunity's mission.
- Wavelength dependence: contrary to the hedge in ADR-003, the MSL
  optical-depth record paper found **"visible and near-infrared
  optical depth ratios do not typically vary much for Mars's dust"**
  [arXiv:2309.07378, MSL record of optical depth measurements](https://arxiv.org/pdf/2309.07378).

**Action taken:** the tau=0.5 normal-ops margin and tau>=2 storm-outage
threshold from ADR-003 are confirmed by an authoritative NASA/JPL
source and require no change. The implicit "NIR gets a discount"
hedge is removed — apply the same tau to 975nm as to visible
measurements, not a reduced figure.

## 8. Mars terrain elevation data (methodology, not a single value)

**Found:** MOLA global topography is publicly available via USGS
Astrogeology / NASA PDS at **463m/pixel** (global DEM), with a
MOLA+HRSC blended product at **200m/pixel** in some regions.
[USGS Astrogeology: Mars MGS MOLA DEM 463m](https://astrogeology.usgs.gov/search/map/mars_mgs_mola_dem_463m);
[USGS Astrogeology: Mars MGS MOLA-MEX HRSC Blended DEM 200m](https://astrogeology.usgs.gov/search/map/mars_mgs_mola_mex_hrsc_blended_dem_global_200m)

**Resolution problem:** 200-463m/pixel is far too coarse to resolve
the meter-scale terrain features (boulders, small ridges, crater rims)
relevant to a 2m-tall rover beacon's line-of-sight at hub spacing of a
few km. HiRISE-derived stereo DEMs reach ~1m/pixel but only exist for
specifically-targeted imaging campaigns, not globally — a real AEST
corridor siting effort would need new targeted HiRISE stereo coverage
of candidate routes, not just the existing global MOLA product.

**Action taken:** recorded in `docs/route_planning.md` as the concrete
next step once candidate corridor sites are chosen; not resolved by
this pass, since it requires site-specific decisions this repo doesn't
yet make.

## 9. Multijunction (VMJ) receiver efficiency — the "modular beaming" question resolved

**Prompted by:** the original proposal to close the PV-efficiency gap
(#5 above) via "modular" power beaming with "multiple intake ports."

**Found — the real mechanism is a receiver-chip technology, not a
multi-beam architecture:**

- **65-67% efficiency at 30-75 W/cm², still >64% at 160 W/cm², up to 242
  W/cm² on small devices**, 808-811nm, GaAs, six series-connected
  subcells in ONE receiver chip, room temperature (10-50°C tested,
  -40 to +85°C rated). Trades photocurrent for voltage across the
  series-connected subcells to avoid the resistive (I²R) losses that
  limit single-junction converters at high intensity.
  ["65% Efficient Multijunction Photovoltaic Laser Power Converters
  Operating over 150 W/cm²," Photonics 13(3):246](https://www.mdpi.com/2304-6732/13/3/246)
- **Critically, this is not just a high-intensity result.** A companion
  device (same VMJ family) demonstrated **59.4% efficiency at only 10W
  input with the beam covering just ~7% of the chip area**, 60% at 20W/
  ~22% coverage, 61% at ~35% coverage — "efficiency and output voltage
  penalties for using a smaller and peaky beam are relatively minor." A
  second (InP, 1470nm) device showed only **1.8% relative efficiency
  variation across 23-88% illumination coverage.**
  ["Vertical Multi-Junction Laser Power Converters with 61% Efficiency
  at 30W Output Power and with Tolerance to Beam Non-Uniformity, Partial
  Illumination, and Beam Displacement"](https://www.researchgate.net/publication/373205649)
- Corroborating results at other wavelengths/configurations: **66.5% at
  21 W/cm²** ["Photovoltaic laser power converters producing 21 W/cm²
  at a conversion efficiency of 66.5%," Cell Reports Physical Science](https://www.cell.com/cell-reports-physical-science/fulltext/S2666-3864(24)00568-X);
  **>50% efficiency in the short-wavelength infrared**
  ["Multi-junction laser power converters exceeding 50% efficiency in
  the short wavelength infrared," Cell Reports Physical Science](https://www.cell.com/cell-reports-physical-science/fulltext/S2666-3864(25)00209-7).

**What this resolves:** the original proposal worried that a
"modular"/higher-efficiency receiver would need "multiple intake
ports," reopening the beam-pointing problem ADR-003 had just closed.
The literature shows the efficiency mechanism is internal to a single
receiver chip (multiple series-connected SUBCELLS, not multiple
separately-tracked BEAMS) and is robust to both low intensity and
partial/off-center illumination — meaning AEST does not need a second
beam, a phased array, or a reopened tracking-margin trade to capture
most of this gain. See `simulations/beam_tracking_sim.py` Module 4 [5]
for the specific check that a spot small enough to enter the peak
30-75 W/cm² efficiency band actually IMPROVES geometric tracking
margin versus ADR-003's baseline, not the reverse.

**What remains open, same category as finding #5 above:** no
975nm-specific multijunction data exists (808nm and 1470nm are the
closest analogs, same gap as the single-junction case); these are lab
test-cell results, not a fielded mosaic receiver under real dust,
thermal cycling, and radiation exposure. **Action taken:**
`photon_conversion.py` v4 adds `PV_EFF_MULTIJUNCTION_CONSERVATIVE = 0.45`
and `PV_EFF_MULTIJUNCTION_TARGET = 0.60` as a second scenario pair
alongside the existing single-junction pair (0.25/0.50), not a
replacement — see ADR-005.

## 10. Mars dust vertical scale height — needed to model hop-length effects

**Found:** the Martian atmosphere's dust vertical scale height has "an
average value of **11.1 km**," used in Mars Exploration Rover mission
analysis to convert atmospheric dust column measurements into a
density-vs-altitude profile.
[NTRS 20160013317](https://ntrs.nasa.gov/api/citations/20160013317)

**Action taken:** `docs/atmospheric_optics.md` and
`simulations/corridor_economics.py` (Module 5, new this round) use
this to convert the vertical column optical depths from #7 above into a
horizontal near-surface extinction coefficient, enabling (for the first
time) a real hop-length-vs-dust-transmission model instead of applying
the vertical column value directly to whatever hop length happens to be
chosen. See ADR-005 for the resulting hop-length recommendation.

## 11. Fusion vs. fission for a centralized Mars power source (ADR-006)

**Prompted by:** the original proposal of a "centralized fusion reactor
core."

**Found:** no fusion reactor has been connected to an electrical grid
anywhere, as of 2026. The most advanced private programs
(Commonwealth Fusion Systems' SPARC, Helion) target first grid
connections in the late-2020s to early-2030s, on Earth, with the
industry itself estimating it needs tens of billions of dollars more
investment before a first commercial plant.
["The State of Fusion Energy in 2026," Earth911](https://earth911.com/eco-tech/the-state-of-fusion-energy-in-2026-real-reactors-real-grids-real-caveats/)

**Action taken:** adopted NASA/DOE's Fission Surface Power (FSP)
program instead — 40kWe/unit, <6 metric tons, 10-year design life,
explicitly scoped by NASA to extend from lunar demonstration to Mars.
["NASA's Fission Surface Power Project Energizes Lunar Exploration," NASA Glenn](https://www.nasa.gov/centers-and-facilities/glenn/nasas-fission-surface-power-project-energizes-lunar-exploration)
See ADR-006.

## 12. Dynamic inductive (wireless) power transfer for moving vehicles

**Found:** ORNL has demonstrated static wireless EV charging up to
270kW, and validated 91.31% DC-input-to-battery efficiency at 120kW in
its 200kW dynamic-charging system design.
["Design and Analysis of a 200 kW Dynamic Wireless Charging System for Electric Vehicles," ORNL](https://www.ornl.gov/publication/design-and-analysis-200-kw-dynamic-wireless-charging-system-electric-vehicles);
["Polyphase wireless power transfer system achieves 270-kilowatt charge," ORNL](https://www.ornl.gov/news/polyphase-wireless-power-transfer-system-achieves-270-kilowatt-charge-sets-another-world)

**Critical geometry finding:** ORNL's own dynamic (in-motion) analysis
found coupling drops to ~50% of peak at the midpoint between adjacent
primary coils (70%-pitch spacing), and uses a design rule of thumb of
coil diameter ≈ 3x magnetic air gap for useful coupling.
["ORNL Experience and Challenges Facing Dynamic Wireless Power Charging of EV's"](https://www.osti.gov/servlets/purl/1265561)

**Action taken:** this is what forced the sparse-hub Gen 1 geometry to
be corrected to dense coil clusters bridged by an onboard flywheel — see
ADR-006 Decision 2 and `simulations/inductive_transfer_sim.py`.

## 13. Mars regolith carbothermic reduction to iron/steel (ISRU)

**Found:** active 2025-era lab research demonstrates pure iron
formation (~1000°C) and liquid iron-silicon alloy formation (~1400°C)
from Mars regolith simulant, using atmospheric CO2 as the reducing
carbon source.
["How to make metals from Martian dirt," CSIRO](https://www.csiro.au/en/news/All/Articles/2025/August/Metals-out-of-martian-dirt);
["Iron (alloy) extraction on Mars through carbothermic reduction of regolith," ScienceDirect](https://www.sciencedirect.com/science/article/abs/pii/S0094576525002814);
["Metals extraction on Mars through carbothermic reduction: MGS-1 simulant characterization," ScienceDirect](https://www.sciencedirect.com/science/article/abs/pii/S0094576525002498)

**What remains open:** explicitly lab-simulant-only — no real-Mars-
surface demonstration, and mechanical (tensile/fatigue) properties of
the resulting product are uncharacterized against structural or
flywheel-rotor requirements. **Action taken:** adopted as the vehicle
chassis and flywheel rotor material with this precondition stated
plainly, not assumed resolved — see ADR-006 Decision 4.

## 14. Martian dust magnetic properties — does dust interfere with inductive coupling?

**Found:** Martian dust does contain a magnetic mineral component
(probably maghemite, γ-Fe2O3), directly studied by the Viking,
Pathfinder, and MER magnetic-properties experiments, with a measured
bulk saturation magnetization of only **~4 A·m²/kg** — low relative to
pure magnetic iron oxides (magnetite ~92-100 A·m²/kg, maghemite
~60-80 A·m²/kg), consistent with dust being dominated by non-magnetic
silicates with a minor magnetic fraction.
["Magnetic Properties Experiments on the Mars Pathfinder Lander," Science](https://science.sciencemag.org/content/278/5344/1768)

**Action taken:** treated as reassuring for near-field magnetic
coupling (bulk dust is only weakly magnetic, unlikely to meaningfully
perturb the field) but flagged as a slow, monitorable — not
acute-blocking — risk if magnetic fines accumulate directly on coil
surfaces over time. Not quantified further; see
`hardware_spec/coil_cluster_spec.md`.

## 15. Flywheel physics: specific energy, and burst-safety engineering practice

**Found — specific energy is a strength-to-density question, not a
material-name question:** flywheel theoretical specific energy follows
e = K·σ/ρ (K a rotor-shape factor); real engineered systems achieve only
a fraction of this theoretical ceiling. Commercial systems commonly cite
~11 Wh/kg against composite theoretical maxima of 100-130+ Wh/kg.
["Flywheel energy storage," Wikipedia](https://en.wikipedia.org/wiki/Flywheel_energy_storage)

**Found — burst containment is a dead end, prevention is the real
practice:** "successful containment requires a structure many times
more massive than the rotor itself... [it] would multiply the weight
and cost of the flywheel system defeating the objective of providing
cost effective energy storage." Real practice: treat the rotor as
safety-critical, design margin 2.0 (burst stress / max allowable
stress), operate production units at ≤70% of qualification test speed.
["SAND2015-10759, Sandia National Laboratories"](https://www.sandia.gov/ess-ssl/publications/SAND2015-10759.pdf)

**Found — magnetic bearing reaction wheels have real spacecraft
heritage:** a mature, if specialized, technology line going back
decades, directly applicable to a cold-tolerant (no lubricant) flywheel
bearing.
["Magnetic bearing reaction wheel," NASA NTRS 19760020248](https://ntrs.nasa.gov/citations/19760020248)

**Action taken:** `simulations/flywheel_buffer_sizing.py` (Module 7)
and `hardware_spec/flywheel_safety_spec.md` — steel flywheel sizing
with a 40% realization-fraction engineering discount (now grounded in
the Sandia margin/speed-derate practice, not an arbitrary number),
magnetic bearings adopted, containment rejected in favor of prevention.
See ADR-006 and ADR-007.

## 16. Mars copper vs. aluminum ISRU-sourceability

**Found:** Mars crustal copper abundance is only ~50ppm versus Earth
ore-grade concentrations of ~10,000ppm (~200x more dilute); no
confirmed concentrated Mars copper deposit exists. Aluminum, by
contrast, is tied up in common feldspar/plagioclase minerals and is
"much more common than copper, by many orders of magnitude" in Mars
regolith.
["Copper," Marspedia](https://marspedia.org/Copper)

**Action taken:** `simulations/coil_infrastructure_costing.py` (Module
9) evaluates aluminum instead of copper for coil-cluster windings — an
independent first-principles check (equal-resistance mass comparison)
confirms aluminum is also the lighter choice regardless of the ISRU
argument, the same physics that makes it standard for terrestrial
long-distance power transmission. See ADR-007.

## What's still genuinely open

- No 975nm-specific data exists for InGaAs monochromatic PV
  efficiency in the literature found — 1064nm and 1470nm are the
  closest analogs. AEST would need to fund or commission cell-level
  characterization at the actual operating wavelength.
- The PV-efficiency gap (20% demonstrated vs. 50% lab-record-adjacent)
  is the single biggest unresolved risk in the whole architecture.
  Closing it is a hardware R&D program, not a literature search.
- The -75C aggressive supercap scenario depends on a specific research
  electrolyte (NASA-funded, not commercialized) — adopting it as a
  baseline would be a real technology bet, not a documented product
  choice.
- No 975nm-specific multijunction receiver data exists either (#9) —
  same fundamental gap as the single-junction case, just with a
  stronger, more specific mechanism behind the extrapolation now.
- The hub-density economics in `corridor_economics.py` use a
  "Kilopower reactor units" proxy, not real $ costing — a genuine
  costing exercise (reactor procurement, transmitter optics, structure,
  launch mass to Mars) would sharpen or possibly overturn the ~3km hop
  recommendation in ADR-005.
