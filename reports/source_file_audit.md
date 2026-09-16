# Task 03 — Source File Audit

## Status

Task 03 metadata, source inventory, deterministic sample selection, and canonical variable mapping were completed.

## 03.1 — Source metadata and inventory

### CAMELSH observed streamflow

- DOI: 10.5281/zenodo.16729675
- Record: CAMELSH observed streamflow
- Archive: `Hourly2.zip`
- Archive size: 4,176,462,827 bytes
- MD5: `8bab1c99329db3fa6b1b6cb464a2a573`
- Coverage: 1980-01-01 through 2024-12-31 23:00
- Data type: observed streamflow/water-level NetCDF
- Observed discharge is distinguished from modeled/reanalysis runoff.

### CAMELSH NLDAS-2

- DOI: 10.5281/zenodo.15066778
- Files include:
  - `timeseries.7z`
  - `attributes.7z`
  - `info.csv`
  - `shapefiles.7z`
- NLDAS-2 forcing source verified.

### CAMELSH ERA5-Land

- DOI: 10.5281/zenodo.15264813
- Files include the CAMELSH shapefile, description PDF, ERA5-Land time-series archives, and README.
- ERA5-Land source record verified.

### SMAP

- Product: `SPL3SMP_E`
- Version: 006
- Source ID: `SMAP_SPL3SMP_E_V006`
- Early granules inspected in inventory:
  - 2015-03-31
  - 2015-04-01
  - 2015-04-02
- Later granules inspected in inventory:
  - 2024-12-20
  - 2024-12-21
  - 2024-12-22

## 03.2 — Outcome-blind sample

Three CAMELS-US basins were selected deterministically by gauge-ID ordering:

| Position | Gauge ID | HUC-02 | Basin |
|---:|---|---:|---|
| 0 | 01013500 | 01 | Fish River near Fort Kent, Maine |
| 335 | 06278300 | 10 | Shell Creek above Shell Creek Reservoir, Wyoming |
| 670 | 14400000 | 17 | Chetco River near Brookings, Oregon |

Selection was based on identifier ordering only and was not based on flood behavior or known outcomes.

## CAMELS metadata verification

The three sample basins were successfully located in CAMELS metadata.

Verified fields include:

- `gauge_id`
- `huc_02`
- `gauge_name`
- `gauge_lat`
- `gauge_lon`
- `area_gages2`
- precipitation and PET climatology
- hydrologic characteristics

Important limitation: the CAMELS 671-basin standard attributes do not provide all final study-screening fields required by the proposal (for example, exact AI, irrigation, open-water, and wetland screening variables). CAMELS attributes are therefore not used as substitutes for the required GAGES-II/CAMELSH eligibility fields.

## 03.3 — Canonical variable mapping

The canonical mappings are stored separately in:

`config/source_mapping.csv`

Required variables include:

- Q
- P
- PET
- Tair
- SWE
- SM
- retrieval quality
- acquisition time
- basin ID
- basin area

No undocumented surrogate field was substituted for a required source variable.

## 03.4 — Quality and uncertainty fields

SMAP retrieval and surface-quality flag families were identified from the V006 product documentation.

The following items remain pending direct sample-granule inspection:

- exact SMAP soil-moisture fill value
- exact retrieval flag values
- exact acquisition-time field encoding
- finite/non-fill count for `soil_moisture_error`

These values were not fabricated or inferred.

The protocol requirement remains that fill values represent missing data and are not converted to zero.

## 03.5 — Practical data handling

Large national archives are not loaded into memory as a whole.

Verified archive handling includes:

- CAMELSH observed-flow archive: approximately 3.9 GB
- CAMELSH NLDAS-2 time-series archive: approximately 19.8 GB
- CAMELSH ERA5-Land archives: approximately 14.8–15.1 GB each
- CAMELS time-series archive: approximately 3.4 GB

The CAMELS time-series ZIP supports byte-range retrieval from the Zenodo endpoint. A central-directory inspection successfully identified the expected sample-basin observed-flow and forcing files without downloading the entire archive.

## Exceptions / limitations

Direct extraction of compressed members from partial ZIP downloads was not reliable because the partial archive does not contain the full compressed member data. Individual archive members therefore were not treated as directly readable from the partial tail.

No missing codes, field names, or quality values were invented to compensate.

## Provenance

Source inventory:

`manifests/source_inventory.csv`

Outcome-blind sample:

`manifests/task03_sample_basins.csv`

Canonical mapping:

`config/source_mapping.csv`

Task status: PASS with documented direct-sample-file inspection limitation.

Reviewer status: Pending.
