# Task 02 — Setup Report

## Status
Starter repository skeleton created. Environment is not yet fully pinned.

## Inputs
- Approved research protocol: to be copied into `config/protocol_v1.yaml`.
- Working Colab notebook: `hugging_face+daymet_extraction.ipynb`.

## Data separation
Large data remain outside GitHub. Daymet chunks remain on Hugging Face.

## Security
No credentials are included in the repository. The notebook uses interactive
Hugging Face login rather than storing a token.

## Remaining Task 02 checks
- [ ] Verify all required Python imports.
- [ ] Write/reread tiny CSV.
- [ ] Write/reread tiny Parquet.
- [ ] Plot labeled figure.
- [ ] Transform known geographic coordinate.
- [ ] Confirm deterministic rerun.
- [ ] Save fully pinned environment.
- [ ] Run secret scan.
- [ ] Record checksums, config hash, commit, command, outputs, tests,
      exceptions, and reviewer status.
