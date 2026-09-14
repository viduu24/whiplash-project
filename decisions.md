# Decisions

## 2026-09-14 — Repository/data separation

1. GitHub is used for version-controlled code, configuration, tests,
   documentation, notebooks, and provenance.
2. Large scientific datasets are not stored in GitHub.
3. Google Drive remains the working location for existing CAMELS/CAMELSH,
   streamflow, pixel-index, metadata, and generated large files.
4. Daymet chunks remain on Hugging Face.
5. NASA Earthdata and Hugging Face credentials remain outside the repository.
6. The existing `code/` directory is retained rather than renaming it to
   `src/`, so existing project paths are not unnecessarily broken.
7. The uploaded Colab Daymet extraction notebook is preserved as the
   starting reproducibility artifact; its outputs/execution counts are
   cleared before committing.

## Protocol status

The full approved Appendix A values have not been copied into this repository
yet. Do not treat the current configuration file as the final frozen protocol
until those values are transferred and reviewed.
