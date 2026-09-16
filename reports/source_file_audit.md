# Task 03 — Source File Audit

## Status

Task 03 source audit is in progress with direct inspection completed for the primary
sample source files and one SMAP V006 AM granule.

No source field, missing-value code, quality flag, or uncertainty interpretation was
invented when it was not documented by the inspected source.

---

## 1. Observed streamflow

### Source

CAMELS-US observed USGS streamflow archive:

`basin_dataset_public_v1p2/usgs_streamflow/{HUC}/{GAGEID}_streamflow_qc.txt`

Representative inspected file:

`basin_dataset_public_v1p2/usgs_streamflow/01/01013500_streamflow_qc.txt`

### Direct inspection

The file contains 12,784 daily records with five fields:

1. GAGEID
2. Year
3. Month
4. Day
5. Streamflow (cubic feet per second)
6. QC_flag

The source README confirms that the files contain five data columns after the
identifier/date fields and identifies streamflow units as cubic feet per second.

### Missing values

The official streamflow README specifies:

- `-999.0` = missing streamflow
- `A` = USGS-certified actual daily mean flow
- `A:e` = USGS-certified estimated daily mean flow
- `M` = missing from USGS record

The inspected sample contained:

- `A`: 9,724 records
- `A:e`: 2,968 records
- `M`: 92 records
- `-999.0`: 92 discharge values

Therefore `-999.0` will be converted to missing during processing.
Zero discharge values will not be converted to missing.

The source is observed USGS discharge, not stage, reanalysis runoff, or model
simulation.

---

## 2. NLDAS-2 basin mean forcing

### Source

CAMELS-US NLDAS basin mean forcing:

`basin_dataset_public_v1p2/basin_mean_forcing/nldas/{HUC}/{GAGEID}_lump_nldas_forcing_leap.txt`

Representative inspected file:

`basin_dataset_public_v1p2/basin_mean_forcing/nldas/01/01013500_lump_nldas_forcing_leap.txt`

### Direct inspection

The inspected file has a four-line header followed by daily forcing records.

The observed fourth-line field structure is:

`Year Mnth Day Hr Dayl PRCP SRAD SWE Tmax Tmin Vp`

The directly observed units/meanings are:

- `Dayl`: seconds
- `PRCP`: mm/day
- `SRAD`: W/m2
- `SWE`: mm
- `Tmax`: degrees C
- `Tmin`: degrees C
- `Vp`: Pa

The CAMELS basin mean forcing README states that Daymet, Maurer, and NLDAS are
distinct forcing datasets provided at a daily timestep.

The README also states that the first three header lines contain:

1. gauge latitude
2. gauge elevation in meters
3. basin area in square meters

The inspected file contains `Hr = 12`, even though the archived README states that
the hour is set to zero for daily values. The workflow will preserve the actual
source field and treat the product as daily, rather than silently changing the
stored value.

### Missing values

The inspected forcing README does not specify a missing-value code.

Therefore no NLDAS missing-value code has been assigned in the source mapping.
Actual values will be inspected during implementation before bulk processing.

---

## 3. PET

PET is not mapped to an independently observed source field in the inspected NLDAS
file.

The project protocol derives PET using the specified Hargreaves-Samani procedure
from temperature inputs. This is therefore recorded as a protocol-derived variable,
not as a source variable that was observed in the NLDAS file.

---

## 4. SMAP SPL3SMP_E V006

### Source

NASA SMAP Level 3 Enhanced Passive Soil Moisture Product, version 006:

`SPL3SMP_E`, Version `006`

Representative audited granule:

`SMAP_L3_SM_P_E_20150331_R19240_001.h5`

Temporal coverage of audited granule:

`2015-03-31T00:00:00.000Z` through `2015-03-31T23:59:59.999Z`

The AM retrieval group was used for the audit:

`Soil_Moisture_Retrieval_Data_AM`

### Directly verified datasets

The AM group contains:

- `soil_moisture`
- `soil_moisture_error`
- `retrieval_qual_flag`
- `surface_flag`
- `tb_time_seconds`
- `tb_time_utc`
- latitude/longitude fields
- freeze/thaw and surface-condition fields

### Soil moisture

`soil_moisture`:

- units: `cm**3/cm**3`
- `_FillValue`: `-9999.0`
- valid minimum: approximately `0.02`
- valid maximum: `0.5`

For the audited granule:

- total pixels: 6,262,144
- valid soil-moisture pixels: 87,273
- valid percentage: 1.39366%
- fill pixels: 6,174,871

Fill values are missing and must not be treated as zero.

### Soil-moisture uncertainty

`soil_moisture_error`:

- units: `cm**3/cm**3`
- `_FillValue`: `-9999.0`
- valid minimum: `0.0`
- valid maximum: `0.2`

The metadata describes this as a net uncertainty measure and states that the
calculation method is TBD.

For the audited 2015-03-31 AM granule:

- valid uncertainty values: 0
- fill values: 6,262,144
- valid percentage: 0%

Therefore the uncertainty field is unavailable in this audited granule.

The workflow will NOT interpret this field as a standard deviation or variance and
will NOT fabricate a numerical variance from it.

### Retrieval quality flag

`retrieval_qual_flag` is a uint16 bit-field with:

- `_FillValue`: `65534`

Documented flag meanings:

- Retrieval_recommended
- Retrieval_attempted
- Retrieval_success
- FT_retrieval_success

Observed values in the audited AM granule:

| Flag | Pixel count | Percentage |
|---:|---:|---:|
| 0 | 20,351 | 0.32% |
| 1 | 19,125 | 0.31% |
| 5 | 5,145 | 0.08% |
| 7 | 5,383,658 | 85.97% |
| 8 | 17,251 | 0.28% |
| 9 | 14,656 | 0.23% |
| 13 | 12,365 | 0.20% |
| 15 | 789,593 | 12.61% |

These values will be treated as bit flags and decoded according to the product
metadata rather than interpreted as ordinary categorical numbers.

### Surface flags

`surface_flag` is a uint16 bit-field with `_FillValue = 65534`.

The audited metadata documents flags for conditions including:

- static water body
- radar water-body detection
- coastal proximity
- urban area
- precipitation
- snow or ice
- permanent snow or ice
- radiometer frozen ground
- model frozen ground
- mountainous terrain
- dense vegetation
- nadir region

These fields are relevant to the project's retrieval screening. Protocol-defined
screening rules will be applied explicitly rather than treating all retrievals as
equally usable.

### Acquisition time

Two acquisition-time datasets are available:

`tb_time_utc`

- UTC timestamp
- arithmetic average acquisition time of brightness-temperature footprints
- example observed timestamp:
  `2015-03-31T20:40:12.309Z`

`tb_time_seconds`

- seconds since noon on January 1, 2000 UTC
- `_FillValue = -9999.0`

The workflow will retain UTC timing for temporal matching.

---

## 5. Sample basin selection

Three deterministic CAMELS-US sample basins were inspected for outcome-blind
sample handling:

- `01013500`
- `06278300`
- `14400000`

Selection was based on deterministic gauge-ID ordering and was not based on event
outcomes or model performance.

CAMELS-US metadata fields inspected include climate, geology, hydrology, basin
name, soil, topography, and vegetation attributes.

The standard CAMELS-US attribute files inspected do not directly provide all final
proposal screening variables such as irrigation fraction, open-water fraction, and
wetland fraction. These variables will therefore not be silently substituted with
unrelated CAMELS attributes.

---

## 6. Source-control decisions

The audit follows these rules:

1. No missing-value code is invented when the source does not document one.
2. Fill values are treated as missing, not zero.
3. Observed discharge is distinguished from modeled or reanalysis runoff.
4. SMAP uncertainty is not converted into a variance without documentation.
5. SMAP retrieval and surface-condition flags are preserved as explicit quality
   information.
6. Actual source values are preserved when they conflict with generic README
   statements; discrepancies are documented rather than silently corrected.
7. Large national archives are not loaded into memory for routine inspection.
8. Small representative files and one SMAP granule are used for direct field-level
   verification before bulk processing.
9. No credentials or authentication material are stored in GitHub.
10. No source version is silently substituted.

---

## 7. Remaining implementation checks

Before bulk processing, the following should still be explicitly tested:

- NLDAS actual missing/special-value behavior across additional sample files.
- Consistency of NLDAS field structure across the three deterministic sample basins.
- CAMELS basin-area consistency between metadata and forcing-file headers.
- SMAP quality-flag decoding against the V006 product documentation.
- Temporal matching of SMAP acquisition times to daily UTC analysis dates.
- Final source inventory completeness for all archived Zenodo files.

These are implementation/audit checks and do not change the verified source mappings above.
