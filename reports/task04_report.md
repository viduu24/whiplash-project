# Task 04 — Basin Screening and Final Audit

## Status
Task 04 screening and final audit completed.

## Screening summary
- Canonical basin list: 629 unique GAGEIDs.
- Area screen (2,000–10,000 km²): 48 candidates.
- GAGES-II reference-basin screen: 48 candidates.
- Irrigation ≤5%: 45 candidates.
- Open water ≤5%: 42 candidates.
- Wetlands ≤10%: 40 candidates.
- All explicit percentage screens: 33 retained.
- Management: 21 keep, 12 unknown, 0 excluded.
- NOAA regions: 33/33 assigned across 9 regions; region fractions sum to approximately 1.
- Final audit: 33 retained; 15 land-cover failures among the 48 candidates; no ID, geometry, area, management, or attribute failures.

## Retained basin list
See `manifests/task04_retained_basins.csv`.

## Important exception
Basin `06775500` was retained. Its geometry-derived area is 7314.887075 km², while the GAGES-II/CAMELS area metadata used in the screening was missing. This is documented rather than silently excluding the basin.

## Source artifacts
The Task 04 analysis produced identifier crosswalk and duplicate/unmatched-ID audit artifacts in the project Drive. The lightweight retained list and screening summary are committed here so the final selection is version-controlled without committing large raw spatial datasets.
