# Task 02.5 — Status and Provenance Report

## Status

Task 02.5 environment and reproducibility checks completed successfully.

## Environment

Python:
3.13.15

Pinned packages:

- numpy==2.1.3
- pandas==2.2.3
- scipy==1.16.3
- xarray==2025.12.0
- netCDF4==1.7.4
- h5py==3.16.0
- geopandas==1.1.4
- shapely==2.1.2
- pyproj==3.7.2
- rasterio==1.5.1
- scikit-learn==1.6.1
- matplotlib==3.10.0
- pyarrow==23.0.1
- PyYAML==6.0.3
- pytest==8.4.2

## Functional tests

Test file:

`tests/test_environment.py`

Command:

`pytest -q /content/test_environment.py`

Result:

`5 passed in 2.41s`

Tests passed:

1. CSV write/read
2. Parquet write/read
3. Labeled figure creation
4. Geographic coordinate transformation
5. Deterministic numerical output

## Secure access test

NASA Earthdata authentication was tested successfully.

SMAP collection:

`SPL3SMP_E`, Version `006`

A small SMAP granule search succeeded and one granule was downloaded successfully.

Credentials were not stored in the notebook or repository.

## Secret scan

Command:

`git grep -n -I -E "AKIA[0-9A-Z]{16}|BEGIN (RSA|EC|OPENSSH|DSA) PRIVATE KEY"`

Result:

No matching credentials or private-key patterns were found.

## Provenance

Code commit:

`4272a1a2fba1173782a8676f353c7b10c0b78f14`

Configuration file:

`config/protocol_v1.yaml`

Configuration SHA256:

`1489d22e218a80dd4524f73fda45c066cd9e404afe9f7061c7fe49afd2e22dd9`

Input checksums:

Not applicable to the environment tests. No project data files were used as test inputs.

Outputs:

Temporary CSV, Parquet, and PNG files were created during testing and removed after each test.

Exceptions:

No functional test failures.

## Reviewer status

Pending reviewer verification.

## Task status

PASS — Task 02.5 environment, testing, secure-access, and provenance requirements completed.