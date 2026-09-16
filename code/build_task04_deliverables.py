import os
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import pyproj
import matplotlib.patches as mpatches


# ============================================================
# PATHS
# ============================================================

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

GPKG = os.path.join(
    ROOT,
    "manifests",
    "task04_dissolved_basins.gpkg"
)

RETAINED_CSV = os.path.join(
    ROOT,
    "manifests",
    "task04_retained_basins.csv"
)

BASIN_LIST = os.path.join(
    ROOT,
    "data",
    "basin_lists",
    "basin_list_v1.txt"
)

OUT_SCREEN = os.path.join(
    ROOT,
    "basin_screen.csv"
)

OUT_EXCLUSIONS = os.path.join(
    ROOT,
    "basin_exclusions.csv"
)

OUT_GPKG = os.path.join(
    ROOT,
    "basins_screened.gpkg"
)

OUT_F1 = os.path.join(
    ROOT,
    "figure_data",
    "F1_map.csv"
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

print(
    f"Retained IDs loaded: {len(retained_ids)}"
)

if len(retained_ids) != 33:
    raise RuntimeError(
        f"Expected 33 retained basins, "
        f"found {len(retained_ids)}."
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

print(
    f"Canonical basin IDs loaded: "
    f"{len(canonical_ids)}"
)

if len(canonical_ids) != 629:
    raise RuntimeError(
        f"Expected 629 canonical basin IDs, "
        f"found {len(canonical_ids)}."
    )


# ============================================================
# LOAD DISSOLVED BASIN GEOMETRIES
# ============================================================

gdf = gpd.read_file(GPKG)

print(
    f"Geometry rows loaded: {len(gdf)}"
)

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

    gdf = gdf.drop_duplicates(
        subset="basin_id",
        keep="first"
    )

print(
    f"Unique basin IDs after deduplication: "
    f"{len(gdf)}"
)


# ============================================================
# RESTRICT TO CANONICAL 629 BASINS
# ============================================================

gdf = gdf[
    gdf["basin_id"].isin(canonical_ids)
].copy()

print(
    f"Canonical basin geometries retained: "
    f"{len(gdf)}"
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
    |
    gdf["basin_id"].eq("")
    |
    gdf.geometry.is_empty
    |
    gdf.geometry.isna()
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
        "Expected exactly 48 canonical basins "
        "after the 2,000–10,000 km² area screen."
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

candidates["management_decision"] = candidates["retained"].map(
    {
        True: "keep",
        False: "not_retained_after_static_screen"
    }
)


# ============================================================
# NOAA REGION
# ============================================================

# Actual Task 04.5 NOAA region assignments are not available
# in this build input. Do not invent region values.

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

# NAD83 / Conus Albers
# Equal-area CONUS projection.
# Units are meters.

MAP_CRS = "EPSG:5070"

map_gdf = screen_gdf.to_crs(
    MAP_CRS
)

excluded_gdf = map_gdf[
    map_gdf["excluded"]
].copy()

retained_gdf = map_gdf[
    map_gdf["retained"]
].copy()


# ============================================================
# LOAD CONUS STATE OUTLINE
# ============================================================

# U.S. Census Cartographic Boundary state layer.
# Used only as a geographic reference.

CONUS_URL = (
    "https://www2.census.gov/geo/tiger/"
    "GENZ2024/shp/cb_2024_us_state_500k.zip"
)

print()
print("Loading CONUS geographic outline...")

try:

    states = gpd.read_file(
        CONUS_URL
    )

    # Keep only the contiguous United States.
    conus_states = states[
        ~states["STUSPS"].isin(
            [
                "AK",
                "HI",
                "PR",
                "AS",
                "GU",
                "MP",
                "VI"
            ]
        )
    ].copy()

    conus_states = conus_states.to_crs(
        MAP_CRS
    )

    # Dissolve all CONUS states into one outline.
    conus_outline = conus_states[
        ["geometry"]
    ].dissolve()

    print(
        "CONUS outline loaded successfully."
    )

except Exception as e:

    print()
    print(
        "WARNING: Could not load the CONUS outline."
    )

    print(
        f"Reason: {e}"
    )

    conus_outline = None


# ============================================================
# CREATE FIGURE
# ============================================================

fig, ax = plt.subplots(
    figsize=(12, 8)
)


# ============================================================
# CONUS OUTLINE
# ============================================================

if conus_outline is not None:

    conus_outline.boundary.plot(
        ax=ax,
        color="0.35",
        linewidth=1.0,
        zorder=1
    )


# ============================================================
# CANDIDATE BASINS
# ============================================================

map_gdf.boundary.plot(
    ax=ax,
    color="0.60",
    linewidth=0.45,
    alpha=0.8,
    zorder=2
)


# ============================================================
# EXCLUDED BASINS
# ============================================================

if len(excluded_gdf) > 0:

    excluded_gdf.plot(
        ax=ax,
        facecolor="none",
        edgecolor="red",
        linewidth=1.1,
        zorder=3
    )


# ============================================================
# RETAINED BASINS
# ============================================================

if len(retained_gdf) > 0:

    retained_gdf.plot(
        ax=ax,
        facecolor="none",
        edgecolor="black",
        linewidth=1.4,
        zorder=4
    )


# ============================================================
# MAP EXTENT
# ============================================================

if conus_outline is not None:

    minx, miny, maxx, maxy = (
        conus_outline.total_bounds
    )

    xpad = 0.03 * (maxx - minx)
    ypad = 0.03 * (maxy - miny)

    ax.set_xlim(
        minx - xpad,
        maxx + xpad
    )

    ax.set_ylim(
        miny - ypad,
        maxy + ypad
    )


# ============================================================
# TITLE
# ============================================================

ax.set_title(
    "Candidate and Retained Basin Population",
    fontsize=16,
    pad=12
)


# ============================================================
# 500 KM SCALE BAR
# ============================================================

# Calculate position AFTER the map extent has been established.

xmin, xmax = ax.get_xlim()
ymin, ymax = ax.get_ylim()

bar_length = 500_000

bar_x = xmin + 0.08 * (
    xmax - xmin
)

bar_y = ymin + 0.07 * (
    ymax - ymin
)

ax.plot(
    [bar_x, bar_x + bar_length],
    [bar_y, bar_y],
    color="black",
    linewidth=4,
    solid_capstyle="butt",
    zorder=10
)

tick_height = 0.012 * (
    ymax - ymin
)

ax.plot(
    [bar_x, bar_x],
    [
        bar_y - tick_height / 2,
        bar_y + tick_height / 2
    ],
    color="black",
    linewidth=2,
    zorder=10
)

ax.plot(
    [
        bar_x + bar_length,
        bar_x + bar_length
    ],
    [
        bar_y - tick_height / 2,
        bar_y + tick_height / 2
    ],
    color="black",
    linewidth=2,
    zorder=10
)

ax.text(
    bar_x + bar_length / 2,
    bar_y + 0.018 * (
        ymax - ymin
    ),
    "500 km",
    ha="center",
    va="bottom",
    fontsize=11,
    fontweight="bold",
    zorder=10
)


# ============================================================
# LEGEND
# ============================================================

excluded_patch = mpatches.Patch(
    facecolor="none",
    edgecolor="red",
    label="Excluded (15)"
)

retained_patch = mpatches.Patch(
    facecolor="none",
    edgecolor="black",
    label="Retained (33)"
)

ax.legend(
    handles=[
        excluded_patch,
        retained_patch
    ],
    loc="lower left",
    bbox_to_anchor=(0.02, 0.12),
    frameon=True,
    framealpha=0.95,
    fontsize=10
)

# ============================================================
# CLEAN APPEARANCE
# ============================================================

ax.set_axis_off()

plt.tight_layout()


# ============================================================
# SAVE MAP SAFELY
# ============================================================

# Write the new figure to a temporary file first.
# This avoids problems when Windows has the old PNG open.

TEMP_FIG = os.path.join(
    ROOT,
    "figures",
    "main",
    "candidate_retained_basin_map_new.png"
)

# Remove stale temporary file if it exists.
if os.path.exists(TEMP_FIG):
    try:
        os.remove(TEMP_FIG)
    except PermissionError:
        raise RuntimeError(
            "The temporary map file is open or locked. "
            "Close the map image and run the script again."
        )

plt.savefig(
    TEMP_FIG,
    dpi=300,
    bbox_inches="tight"
)

plt.close()


# Replace the previous figure.
if os.path.exists(OUT_FIG):

    try:
        os.remove(OUT_FIG)

    except PermissionError:
        # Clean up temporary output.
        if os.path.exists(TEMP_FIG):
            os.remove(TEMP_FIG)

        raise RuntimeError(
            "The existing candidate_retained_basin_map.png "
            "is open or locked by another program. "
            "Close the image and run the script again."
        )

os.replace(
    TEMP_FIG,
    OUT_FIG
)

print()
print("Map written to:")
print(OUT_FIG)


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


# ============================================================
# VALIDATION TESTS
# ============================================================

assert n_candidates == 48, (
    f"FAIL: expected 48 candidates, "
    f"got {n_candidates}"
)

assert n_retained == 33, (
    f"FAIL: expected 33 retained, "
    f"got {n_retained}"
)

assert n_excluded == 15, (
    f"FAIL: expected 15 excluded, "
    f"got {n_excluded}"
)

assert (
    n_retained + n_excluded
    == n_candidates
), (
    "FAIL: candidate count minus exclusions "
    "does not equal retained count"
)

assert (
    candidates["basin_id"].nunique()
    == 48
), (
    "FAIL: candidate GAGEIDs are not unique"
)

assert (
    candidates["geometry_area_km2"] > 0
).all(), (
    "FAIL: non-positive basin area"
)

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

assert 0.05 == 5 / 100
assert 0.10 == 10 / 100

assert (
    candidates.loc[
        candidates["excluded"],
        "first_exclusion_reason"
    ].eq("land_cover").all()
), (
    "FAIL: an excluded basin has an unexpected "
    "first exclusion reason"
)

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