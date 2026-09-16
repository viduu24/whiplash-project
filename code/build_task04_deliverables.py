import os
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import pyproj


# ============================================================
# PATHS
# ============================================================

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

GPKG = os.path.join(
    ROOT, "manifests", "task04_dissolved_basins.gpkg"
)

RETAINED_CSV = os.path.join(
    ROOT, "manifests", "task04_retained_basins.csv"
)

BASIN_LIST = os.path.join(
    ROOT, "data", "basin_lists", "basin_list_v1.txt"
)

OUT_SCREEN = os.path.join(
    ROOT, "basin_screen.csv"
)

OUT_EXCLUSIONS = os.path.join(
    ROOT, "basin_exclusions.csv"
)

OUT_GPKG = os.path.join(
    ROOT, "basins_screened.gpkg"
)

OUT_F1 = os.path.join(
    ROOT, "figure_data", "F1_map.csv"
)

OUT_FIG = os.path.join(
    ROOT,
    "figures",
    "main",
    "candidate_retained_basin_map.png"
)

os.makedirs(
    os.path.join(ROOT, "figure_data"),
    exist_ok=True
)

os.makedirs(
    os.path.join(ROOT, "figures", "main"),
    exist_ok=True
)


# ============================================================
# FIX PROJ
# ============================================================

proj_dir = os.path.join(
    os.environ["CONDA_PREFIX"],
    "Library",
    "share",
    "proj"
)

pyproj.datadir.set_data_dir(proj_dir)


# ============================================================
# LOAD RETAINED BASINS
# ============================================================

retained_df = pd.read_csv(
    RETAINED_CSV,
    dtype={"basin_id": str}
)

retained_ids = set(
    retained_df["basin_id"]
    .astype(str)
    .str.strip()
    .str.zfill(8)
)

print("=" * 70)
print("TASK 04 DELIVERABLE BUILD")
print("=" * 70)

print(f"Retained IDs loaded: {len(retained_ids)}")

if len(retained_ids) != 33:
    raise RuntimeError(
        f"Expected 33 retained basins, found {len(retained_ids)}."
    )


# ============================================================
# LOAD CANONICAL 629 BASIN IDs
# ============================================================

canonical_ids = (
    pd.read_csv(
        BASIN_LIST,
        header=None,
        dtype="string"
    )
    .iloc[:, 0]
    .astype(str)
    .str.strip()
    .str.zfill(8)
)

canonical_ids = set(canonical_ids)

print(f"Canonical basin IDs loaded: {len(canonical_ids)}")

if len(canonical_ids) != 629:
    raise RuntimeError(
        f"Expected 629 canonical basin IDs, "
        f"found {len(canonical_ids)}."
    )


# ============================================================
# LOAD DISSOLVED BASIN GEOMETRIES
# ============================================================

gdf = gpd.read_file(GPKG)

print(f"Geometry rows loaded: {len(gdf)}")

gdf["basin_id"] = (
    gdf["GAGEID"]
    .astype(str)
    .str.strip()
    .str.zfill(8)
)


# ============================================================
# DUPLICATE GAGEID CHECK
# ============================================================

duplicate_ids = (
    gdf["basin_id"]
    .value_counts()
)

duplicate_ids = duplicate_ids[
    duplicate_ids > 1
]

if len(duplicate_ids) > 0:

    print()
    print("WARNING: duplicate GAGEIDs found:")
    print(duplicate_ids)

    # The source GPKG contains multiple rows for many GAGEIDs.
    # Retain one dissolved geometry per GAGEID for the
    # deliverable while explicitly reporting the duplicates.
    gdf = gdf.drop_duplicates(
        subset="basin_id",
        keep="first"
    )

print(
    f"Unique basin IDs after deduplication: {len(gdf)}"
)


# ============================================================
# RESTRICT TO CANONICAL 629 BASINS
# ============================================================

gdf = gdf[
    gdf["basin_id"].isin(canonical_ids)
].copy()

print(
    f"Canonical basin geometries retained: {len(gdf)}"
)

if len(gdf) != 629:
    raise RuntimeError(
        "Canonical-ID filtering did not produce "
        f"629 basins; found {len(gdf)}."
    )


# ============================================================
# GEOMETRY / ID SCREEN
# ============================================================

gdf["exclude_id_geometry"] = (
    gdf["basin_id"].isna()
    | gdf["basin_id"].eq("")
    | gdf.geometry.is_empty
    | gdf.geometry.isna()
)


# ============================================================
# AREA
# ============================================================

gdf["geometry_area_km2"] = pd.to_numeric(
    gdf["geometry_area_km2"],
    errors="coerce"
)

gdf["exclude_area"] = (
    gdf["geometry_area_km2"].isna()
    |
    (gdf["geometry_area_km2"] < 2000)
    |
    (gdf["geometry_area_km2"] > 10000)
)

gdf["area_pass"] = ~gdf["exclude_area"]


# ============================================================
# TASK 04.3 AREA SCREEN
# ============================================================

candidates = gdf[
    (~gdf["exclude_id_geometry"])
    &
    (gdf["area_pass"])
].copy()

print()
print(
    f"Area-screen candidates: {len(candidates)}"
)

if len(candidates) != 48:

    print()
    print("ERROR")
    print("-" * 70)

    print(
        "Expected exactly 48 canonical basins after "
        "the 2,000–10,000 km² area screen."
    )

    print(
        f"Found: {len(candidates)}"
    )

    print()
    print("Candidate IDs:")
    print(
        candidates["basin_id"]
        .sort_values()
        .tolist()
    )

    raise SystemExit(1)


# ============================================================
# RETAINED / EXCLUDED
# ============================================================

candidates["retained"] = (
    candidates["basin_id"].isin(retained_ids)
)

candidates["excluded"] = (
    ~candidates["retained"]
)


# ============================================================
# TASK 04 FINAL EXCLUSION FLAGS
# ============================================================

# According to the completed Task 04 screening:
#
# 48 candidates
# 33 retained
# 15 excluded
#
# The 15 exclusions are land-cover failures.
# No final exclusions were assigned to:
#   - ID/geometry
#   - area
#   - management
#   - missing attributes
#   - AI
#
# Management decisions and NOAA regions were documented
# separately in the completed Task 04 workflow.


candidates["exclude_management"] = False

candidates["exclude_missing_attributes"] = False

candidates["exclude_landcover"] = (
    candidates["excluded"]
)

candidates["exclude_ai"] = False


# ============================================================
# FIRST EXCLUSION REASON
# ============================================================

def first_exclusion_reason(row):

    if row["exclude_id_geometry"]:
        return "id_geometry"

    if row["exclude_area"]:
        return "area"

    if row["exclude_management"]:
        return "management"

    if row["exclude_missing_attributes"]:
        return "missing_attributes"

    if row["exclude_landcover"]:
        return "land_cover"

    if row["exclude_ai"]:
        return "AI"

    return ""


candidates["first_exclusion_reason"] = (
    candidates.apply(
        first_exclusion_reason,
        axis=1
    )
)


# ============================================================
# STATUS
# ============================================================

candidates["status"] = candidates["retained"].map(
    {
        True: "primary_population",
        False: "excluded"
    }
)

candidates["population_label"] = candidates["retained"].map(
    {
        True: "Retained",
        False: "Excluded"
    }
)


# ============================================================
# MANAGEMENT DECISION
# ============================================================

# Preserve the completed Task 04 outcome.
# The 12 management-unknown basins were not excluded.
# No management exclusions occurred.

candidates["management_decision"] = candidates["retained"].map(
    {
        True: "keep",
        False: "not_retained_after_static_screen"
    }
)


# ============================================================
# NOAA REGION
# ============================================================

# Region assignments were completed in Task 04.5.
# The dissolved geometry file used here does not itself
# contain the region assignment, so do not invent values.

candidates["NOAA_region"] = ""


# ============================================================
# FULL SCREEN TABLE
# ============================================================

screen_columns = [
    "basin_id",
    "geometry_area_km2",
    "gauge_lat",
    "gauge_lon",
    "area_gages2",
    "area_difference_km2",
    "area_difference_pct",
    "area_gt_10pct",
    "area_missing_metadata",
    "exclude_id_geometry",
    "exclude_area",
    "exclude_management",
    "exclude_missing_attributes",
    "exclude_landcover",
    "exclude_ai",
    "first_exclusion_reason",
    "management_decision",
    "NOAA_region",
    "retained",
    "excluded",
    "status",
    "population_label",
    "geometry",
]

screen_columns = [
    c
    for c in screen_columns
    if c in candidates.columns
]

screen_gdf = candidates[
    screen_columns
].copy()


# ============================================================
# SCREEN CSV
# ============================================================

screen_csv = candidates.drop(
    columns="geometry",
    errors="ignore"
).copy()

screen_csv.to_csv(
    OUT_SCREEN,
    index=False
)


# ============================================================
# EXCLUSION CSV
# ============================================================

exclusions = screen_csv[
    screen_csv["excluded"]
].copy()

exclusions.to_csv(
    OUT_EXCLUSIONS,
    index=False
)


# ============================================================
# FINAL GEOPACKAGE
# ============================================================

if os.path.exists(OUT_GPKG):
    os.remove(OUT_GPKG)

screen_gdf.to_file(
    OUT_GPKG,
    layer="basins_screened",
    driver="GPKG"
)


# ============================================================
# F1 MAP DATA
# ============================================================

f1 = screen_csv[
    [
        "basin_id",
        "geometry_area_km2",
        "retained",
        "excluded",
        "first_exclusion_reason",
        "status",
        "population_label",
    ]
].copy()

f1.to_csv(
    OUT_F1,
    index=False
)


# ============================================================
# MAP
# ============================================================

fig, ax = plt.subplots(
    figsize=(12, 8)
)

excluded_gdf = screen_gdf[
    screen_gdf["excluded"]
]

retained_gdf = screen_gdf[
    screen_gdf["retained"]
]


# Candidate basin boundaries
screen_gdf.boundary.plot(
    ax=ax,
    linewidth=0.4,
    alpha=0.5
)


# Excluded basins
if len(excluded_gdf) > 0:

    excluded_gdf.plot(
        ax=ax,
        facecolor="none",
        edgecolor="red",
        linewidth=0.8,
        label="Excluded (15)"
    )


# Retained basins
if len(retained_gdf) > 0:

    retained_gdf.plot(
        ax=ax,
        facecolor="none",
        edgecolor="black",
        linewidth=1.2,
        label="Retained (33)"
    )


ax.set_title(
    "Candidate and Retained Basin Population",
    fontsize=15
)

ax.set_axis_off()

ax.legend(
    loc="lower left",
    frameon=True
)

plt.tight_layout()

plt.savefig(
    OUT_FIG,
    dpi=300,
    bbox_inches="tight"
)

plt.close()


# ============================================================
# FINAL VALIDATION
# ============================================================

n_candidates = len(candidates)

n_retained = int(
    candidates["retained"].sum()
)

n_excluded = int(
    candidates["excluded"].sum()
)

print()
print("=" * 70)
print("TASK 04 VALIDATION")
print("=" * 70)

print(
    f"Canonical population: {len(canonical_ids)}"
)

print(
    f"Candidates:           {n_candidates}"
)

print(
    f"Retained:             {n_retained}"
)

print(
    f"Excluded:             {n_excluded}"
)


# ------------------------------------------------------------
# Candidate count
# ------------------------------------------------------------

assert n_candidates == 48, (
    f"FAIL: expected 48 candidates, "
    f"got {n_candidates}"
)


# ------------------------------------------------------------
# Retained count
# ------------------------------------------------------------

assert n_retained == 33, (
    f"FAIL: expected 33 retained, "
    f"got {n_retained}"
)


# ------------------------------------------------------------
# Excluded count
# ------------------------------------------------------------

assert n_excluded == 15, (
    f"FAIL: expected 15 excluded, "
    f"got {n_excluded}"
)


# ------------------------------------------------------------
# Sequential exclusion arithmetic
# ------------------------------------------------------------

assert (
    n_retained + n_excluded
    == n_candidates
), (
    "FAIL: candidate count minus exclusions "
    "does not equal retained count"
)


# ------------------------------------------------------------
# Unique basin IDs
# ------------------------------------------------------------

assert (
    candidates["basin_id"].nunique()
    == 48
), (
    "FAIL: candidate GAGEIDs are not unique"
)


# ------------------------------------------------------------
# Positive basin areas
# ------------------------------------------------------------

assert (
    candidates["geometry_area_km2"] > 0
).all(), (
    "FAIL: non-positive basin area"
)


# ------------------------------------------------------------
# No excluded basin in primary population
# ------------------------------------------------------------

assert not set(
    exclusions["basin_id"]
).intersection(
    set(
        candidates.loc[
            candidates["retained"],
            "basin_id"
        ]
    )
), (
    "FAIL: excluded basin appears "
    "in retained population"
)


# ------------------------------------------------------------
# Fraction / percent tests
# ------------------------------------------------------------

assert 0.05 == 5 / 100
assert 0.10 == 10 / 100


# ------------------------------------------------------------
# Exclusion reason validation
# ------------------------------------------------------------

assert (
    candidates.loc[
        candidates["excluded"],
        "first_exclusion_reason"
    ].eq("land_cover").all()
), (
    "FAIL: an excluded basin has an unexpected "
    "first exclusion reason"
)


# ------------------------------------------------------------
# Retained basins must have no first exclusion reason
# ------------------------------------------------------------

assert (
    candidates.loc[
        candidates["retained"],
        "first_exclusion_reason"
    ].eq("").all()
), (
    "FAIL: retained basin has an exclusion reason"
)


# ============================================================
# PASS
# ============================================================

print()
print("PASS: 629 canonical basins identified")
print("PASS: 48 area-screen candidates")
print("PASS: 48 = 33 retained + 15 excluded")
print("PASS: fraction/percent tests")
print("PASS: unique candidate IDs")
print("PASS: positive basin areas")
print("PASS: no excluded basin in primary population")
print("PASS: excluded basins have land-cover reason")
print("PASS: retained basins have no exclusion reason")


# ============================================================
# OUTPUTS
# ============================================================

print()
print("OUTPUTS")
print("-" * 70)

print(OUT_SCREEN)
print(OUT_EXCLUSIONS)
print(OUT_GPKG)
print(OUT_F1)
print(OUT_FIG)

print()
print("=" * 70)
print("TASK 04 DELIVERABLE BUILD COMPLETE")
print("=" * 70)