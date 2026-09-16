# Decisions

## 2026-09-14 — Repository/data separation

1. GitHub is used for version-controlled code, configuration, tests, documentation, notebooks, and provenance.
2. Large scientific datasets are not stored in GitHub.
3. Google Drive remains the working location for existing CAMELS/CAMELSH, streamflow, pixel-index, metadata, and generated large files.
4. Daymet chunks remain on Hugging Face.
5. NASA Earthdata and Hugging Face credentials remain outside the repository.
6. The existing `code/` directory is retained rather than renaming it to `src/`, so existing project paths are not unnecessarily broken.
7. The uploaded Colab Daymet extraction notebook is preserved as the starting reproducibility artifact; its outputs/execution counts are cleared before committing.

## Protocol status

The full approved Appendix A values have not been copied into this repository yet. Do not treat the current configuration file as the final frozen protocol until those values are transferred and reviewed.

## 2026-09-16 — Task 01 operational definitions

### Prediction target and response interval

For a drought-to-flood event beginning at time `t0`, the primary response interval is:

`t0` to `t0 + 29` days.

Realized weather observations available by the prediction time are allowed as predictors; future river observations are not allowed as predictors.

This is a retrospective prediction setup. Future observed streamflow is used to evaluate the response and is not used as a predictor.

### Weather-first and streamflow-first catalogs

Two event catalogs will be maintained separately:

1. A weather-first catalog based on meteorological conditions, constructed without using streamflow to define candidate events.
2. A streamflow-first catalog based on observed streamflow transitions, used separately for model evaluation.

The weather-first candidate catalog will be frozen before streamflow conversion is examined.

### Seasonal thresholds and event definition

The project will use the operational event-definition choices specified in the proposal rather than tuning definitions against evaluation results.

The weather-first workflow uses:

- a 30-day rolling water-balance quantity based on precipitation minus potential evaporation;
- a seasonal 10th-percentile threshold for the dry state;
- a minimum dry-state duration of approximately two weeks;
- a 7-day rainfall wet-pulse threshold based on the seasonal 95th percentile;
- a maximum 30-day interval for the subsequent wet pulse.

Thresholds will be estimated using the training data.

### Interpretation of high flow

A seasonal Q95 threshold represents statistically unusual high flow for a given season. It is not automatically equivalent to damaging flooding.

Therefore, the terms "high-flow threshold" and "damaging flood" will not be treated as interchangeable.

### Management and land-cover screens

The management and land-cover screening criteria specified in the project protocol will be used as the operational basin-selection criteria.

These criteria will not be changed in response to model performance or event counts without a documented pre-analysis amendment.

### Satellite comparison

The satellite-derived state measure specified in the project protocol will be treated as a secondary comparison.

The primary history/state comparison and the secondary satellite comparison will remain distinct in the analysis.

### Filter support

The predefined filter-support requirement specified in the project protocol will be retained.

No additional filtering will be introduced solely to improve model performance or statistical significance.

### Episode grouping

The predefined episode-grouping rule will be applied consistently when multiple candidate events occur close together.

Events will not be manually merged or separated based on observed results.

### Delta-star

The project will use the predefined value:

`delta* = 0.0025`

This value will remain fixed unless a documented pre-analysis amendment is made.

### Interpretation of nonsignificant results

A nonsignificant gain from adding history/state information will not be interpreted as proof that catchment memory does not exist.

A nonsignificant result may also reflect limited statistical power, measurement limitations, model limitations, or an effect smaller than the study can reliably detect.

### Protocol changes

Any change to the operational definitions, thresholds, event windows, screening criteria, episode grouping, filter support, satellite comparison, or `delta*` value after analysis begins must be recorded as a dated pre-analysis amendment before the affected analysis is treated as confirmatory.

### Supervisor approval

Supervisor approval of the Task 01 operational additions is pending and will be recorded here once obtained.

## Protocol status

The full approved Appendix A values have not been copied into this repository
yet. Do not treat the current configuration file as the final frozen protocol
until those values are transferred and reviewed.
