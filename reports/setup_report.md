# Task 02.5 — Status and Provenance Report

## Status

Task 02.5 environment and reproducibility checks completed successfully.

## Environment

Python:

`3.13.15`

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

`python -m pytest -q tests\test_environment.py`

Result:

`5 passed, 1 warning in 2.51s`

The warning was:

`pyproj unable to set PROJ database path.`

The coordinate transformation test nevertheless passed after explicitly configuring the PROJ data directory to the active conda environment:

`%CONDA_PREFIX%\Library\share\proj`

Tests passed:

1. CSV write/read
2. Parquet write/read
3. Labeled figure creation
4. Geographic coordinate transformation
5. Deterministic numerical output

## Secret scan

Command:

`git grep -n -I -E "(password|passwd|api[_-]?key|secret|token|access[_-]?key|private[_-]?key|BEGIN (RSA|OPENSSH|EC|DSA) PRIVATE KEY)"`

Result:

No actual credentials or private keys were identified.

The matches returned by the scan were documentation, `.gitignore` patterns, and notebook references to token handling; no credential values were present.

## Provenance

Code commit containing the environment-test fix:

`d8fc152`

Full commit:

`d8fc152 Fix PROJ path in environment test`

Configuration file:

`config/protocol_v1.yaml`

Input checksums:

Not applicable to the environment tests. No project data files were used as test inputs.

Outputs:

Temporary CSV, Parquet, and PNG files were created during testing and removed after each test.

Exceptions:

Initial coordinate transformation test failed because the PROJ database was not available to the pytest process.

The PROJ database was confirmed to exist at:

`%CONDA_PREFIX%\Library\share\proj\proj.db`

The test was updated to explicitly configure the PROJ data directory. The full functional test suite subsequently passed.

## Reviewer status

Pending reviewer verification.

## Task status

PASS — Task 02.5 environment, testing, secret-scan, and provenance requirements completed.