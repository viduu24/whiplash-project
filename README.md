# Whiplash Project

Reproducible research workspace for the catchment-memory / drought-to-flood
whiplash study.

## Data locations

Large scientific data are intentionally kept outside GitHub.

- Google Drive: CAMELS/CAMELSH inputs, streamflow, pixel index, metadata, and
  generated NetCDF files.
- Hugging Face: Daymet pixel chunks.
- GitHub: code, notebooks, configuration, tests, decisions, reports, and
  reproducibility metadata.

## Important

Do not commit credentials, NASA Earthdata tokens, Hugging Face tokens,
`.netrc`, `.env`, or large NetCDF/HDF/Parquet/raster files.

The Daymet extraction notebook currently uses the Google Drive path
`/content/drive/MyDrive/whiplash-project` when executed in Colab.

## Current Daymet extraction

The uploaded extraction workflow covers:

- 629 CAMELS basins
- 483,042 Daymet pixels
- 1995-01-01 through 2020-12-30
- 2,000 pixels per chunk
- 242 chunks
- NPZ variables: `tmin`, `tmax`, `prcp`, `pet`

Existing chunks are checked and skipped, and the workflow verifies the
Hugging Face repository after extraction.

## Reproducibility

The approved research protocol should be copied into
`config/protocol_v1.yaml` before the protocol is treated as frozen.
