# Project Understanding — Task 01.1
*Catchment Memory and Transition-Specific Model Error During Drought-to-Flood Whiplash*


## Why two basins with similar surface wetness might behave differently after rain

The satellite state (S) we observe is a single snapshot of surface soil moisture on one selected date in the five complete days before onset (t0). Two basins can share that snapshot and still diverge once rain falls, because S does not carry the same information as the basin's drought history (H) or its basic weather/river context (B):

- **Different antecedent discharge or dry-spell depth.** Two basins can reach the same surface-moisture value from different trailing dry runs — one shallow and short, one long and severe — with different subsurface storage deficits that S alone doesn't register.
- **Different subsurface state.** Surface soil moisture reflects the top layer; root-zone storage, water-table depth, and connectivity to the channel are not observed by S at all. A basin with the same surface reading but a smaller deficit below it will convert rain to flow faster.
- **Different basin structure.** Drainage density, geology, land cover, and management screens shape how quickly infiltrated water reaches the gauge, independent of the surface-moisture snapshot.

This is the premise the project is built to test, not an assumed conclusion: whether H (and separately S) carries predictive information about the transition beyond what B already gives us.

## Why an observed difference could be something other than a real effect

- **Measurement error.** S is a single quality-screened SMAP retrieval on one date, aggregated by intersection-area weights over common-support cells. Retrieval noise, coarse footprint averaging, or a common-support threshold that admits basins with only ~50% coverage can make two basins look alike (or unlike) for reasons that have nothing to do with catchment behavior.
- **Later rainfall.** The response window (t0…t0+29) is 30 days long, and only the initial pulse (t0…t0+6) is what qualified the event. Two basin-events matched on antecedent state can still receive very different realized rainfall later in the response window — this is allowed by design (realized weather is used, since the outcome is retrospective, not forecast) but it means a difference in Y30 need not reflect H or S at all.
- **Inadequate baseline.** "Similar" is only meaningful relative to a reference: the seasonal daily-Q95 outcome threshold, the P7_P95 pulse threshold, and the W30_P10 dry-spell threshold are all seasonal and basin-specific. If the reference window is short, seasonally misaligned, or has thin support (few qualifying years), two basins can appear matched only because the baseline is too coarse to separate them.

Note also: crossing seasonal daily-Q95 is a **low-flow-to-high-flow transition**, not an independently verified flood, bankfull exceedance, or a response attributable to a single storm — so "different behavior" here means a different Y30 label, not necessarily a different flood outcome. And because the models are scored using realized response-period weather, this is a **retrospective information test**, not an operational forecast: it tells us whether H/S carried information after the fact, not whether the transition could have been predicted in real time.

## The two information tests

Both are paired-prediction-loss comparisons against the same frozen full model (B+H+S), on the same rows, out of region:

- **Primary history comparison:** dH = loss(B+S) − loss(B+H+S). This is the change in Brier loss when the drought-history block is removed from the full model. It asks whether H carries information about the transition beyond B and S — not whether any specific hydrologic mechanism (e.g., groundwater depletion, storage deficit) is responsible for it.
- **Secondary satellite comparison:** dS = loss(B+H) − loss(B+H+S). This is the change in loss when the satellite-state block is removed instead. It asks the parallel question for S: does it add information beyond B and H.

Neither test is compared to zero alone — both are compared against the prespecified meaningful-gain margin (delta* = 0.0025) to distinguish a real information gain from an equivalent-to-negligible one. A **nonsignificant or negligible dH does not prove there is no catchment memory effect**: it can instead reflect limited statistical power (rare events, thin common support), a history proxy that doesn't capture the memory that actually matters, or genuinely negligible information content in *this* specification. The tests speak to information content of H and S as operationalized here — they don't, by themselves, identify or confirm any particular physical mechanism.

## Reviewer checklist (pass condition)

Pre-onset (all measured strictly before t0): the dry-history interval, the selected satellite date (t0−5…t0−1), and antecedent discharge (t0−7…t0−1). Post-onset: initial rain (t0…t0+6, used to qualify the event) and the response interval (t0…t0+29, where realized weather is allowed as a co-observed variable but no future river observation is ever used as a predictor).
