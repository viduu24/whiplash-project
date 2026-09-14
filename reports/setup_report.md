# Task 02.5 — Setup Report

## Task
02.5 — Status and provenance templates

## Purpose
Record the environment setup, configuration provenance, tests, and repository status required before bulk processing.

## Repository
Repository: `whiplash-project`

## Configuration
Configuration file:

`config/protocol_v1.yaml`

Master random seed:

`20260909`

Task-specific seeds were derived deterministically from the master seed and task ID.

## Data Inputs
No project-scale scientific data were consumed during Task 02.5.

The environment tests use small, temporary synthetic inputs generated during the test run. These files are deleted after testing.

Therefore, no external data checksums are required for this setup-only task.

## Tests

The following environment tests are required:

- CSV write/read
- Parquet write/read
- Labeled figure creation
- Geographic coordinate transformation
- Deterministic numerical output

Test file:

`tests/test_environment.py`

## Expected Test Result

All tests should pass successfully before proceeding to bulk processing.

Expected result:

`5 passed`

## Commands

Test command:

```text
pytest -q tests/test_environment.py
