# Task 05 — Daily Data Products

Task 05 converts approved source records into dependable daily
basin-level data products for the 33 retained basins.

## Study period

1995-01-01 through 2010-12-31.

## Primary aggregation rule

Daily discharge uses the primary 24-valid-hour rule.

A daily discharge value is considered complete only when all
24 hourly observations required by the primary rule are valid.

Missingness is preserved. No outcome imputation is performed.

## Streamflow units

Discharge:

m3/s

Runoff depth:

mm/day

Conversion:

q_mmday = 86.4 * q_m3s / area_km2

## Main scientific data products

The following files remain in external storage and are NOT committed
to GitHub:

- daily_q_33basins.parquet
- daily_basins_33.parquet

These are the main daily scientific datasets.

## GitHub-tracked Task 05 products

The following small reproducibility products are included:

- tables/data_completeness_by_year.csv
- tables/basin_by_year_availability.csv
- figures/supplement/S01_record_availability.pdf
- manifests/task05_output_manifest.csv

## Empty files

Any zero-byte intermediate files found during export were excluded
from the GitHub export rather than treated as valid deliverables.

## Data policy

Large scientific data remain in external storage. GitHub contains
code, configuration, manifests, small tables, figures, tests,
decisions, and reproducibility metadata.

Task 05 source data and outputs should therefore be retrieved from
the project's external data storage when reproducing the analysis.
