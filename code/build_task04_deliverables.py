import os
import shutil
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import pyproj
import requests
from io import BytesIO
import zipfile


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
    "candidate_retained_basin_map_final.png"
)
OUT_MANAGEMENT = os.path.join(
    ROOT,
    "manifests",
    "task04_4_management_review_reconstructed.csv"
)

OUT_REGIONS = os.path.join(
    ROOT,
    "manifests",
    "task04_5_basin_regions_reconstructed.csv"
)

OUT_REGION_FRACTIONS = os.path.join(
    ROOT,
    "manifests",
    "task04_5_noaa_region_overlap_fractions_reconstructed.csv"
)


os.makedirs(
    os.path.join(ROOT, "figure_data"),
    exist_ok=True
)

os.makedirs(
    os.path.join(ROOT, "figures", "main"),
    exist_ok=True
)

os.makedirs(
    os.path.join(ROOT, "manifests"),
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
# START
# ============================================================

print("=" * 70)
print("TASK 04 DELIVERABLE BUILD")
print("=" * 70)


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
    .str.replace(r"\.0$", "", regex=True)
    .str.zfill(8)
)

print(f"Retained IDs loaded: {len(retained_ids)}")

if len(retained_ids) != 33:
    raise RuntimeError(
        f"Expected 33 retained basins, found {len(retained_ids)}."
    )


# ============================================================
# LOAD CANONICAL 629 IDs
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
    .str.replace(r"\.0$", "", regex=True)
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
# LOAD GEOMETRIES
# ============================================================

gdf = gpd.read_file(GPKG)

print(f"Geometry rows loaded: {len(gdf)}")

gdf["basin_id"] = (
    gdf["GAGEID"]
    .astype(str)
    .str.strip()
    .str.replace(r"\.0$", "", regex=True)
    .str.zfill(8)
)


# ============================================================
# DUPLICATE CHECK
# ============================================================

duplicate_ids = gdf["basin_id"].value_counts()
duplicate_ids = duplicate_ids[duplicate_ids > 1]

if len(duplicate_ids) > 0:

    print()
    print("WARNING: duplicate GAGEIDs found.")
    print(
        f"Duplicate IDs: {len(duplicate_ids)}"
    )

    gdf = gdf.drop_duplicates(
        subset="basin_id",
        keep="first"
    )

print(
    f"Unique basin IDs after deduplication: {len(gdf)}"
)


# ============================================================
# CANONICAL FILTER
# ============================================================

gdf = gdf[
    gdf["basin_id"].isin(canonical_ids)
].copy()

print(
    f"Canonical basin geometries retained: {len(gdf)}"
)

if len(gdf) != 629:
    raise RuntimeError(
        f"Expected 629 canonical geometries; "
        f"found {len(gdf)}."
    )


# ============================================================
# ID / GEOMETRY SCREEN
# ============================================================

gdf["exclude_id_geometry"] = (
    gdf["basin_id"].isna()
    |
    gdf["basin_id"].eq("")
    |
    gdf.geometry.isna()
    |
    gdf.geometry.is_empty
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
# 48 AREA-SCREEN CANDIDATES
# ============================================================

candidates = gdf[
    (~gdf["exclude_id_geometry"])
    &
    (gdf["area_pass"])
].copy()

print()
print(f"Area-screen candidates: {len(candidates)}")

if len(candidates) != 48:
    raise RuntimeError(
        f"Expected 48 area-screen candidates; "
        f"found {len(candidates)}."
    )


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
# TASK 04.3 STATIC FLAGS
# ============================================================

candidates["exclude_management"] = False
candidates["exclude_missing_attributes"] = False
candidates["exclude_landcover"] = candidates["excluded"]
candidates["exclude_ai"] = False


# ============================================================
# MANAGEMENT REVIEW
#
# Reconstructed from the recorded Task 04.4 execution.
#
# Notebook result:
#   keep    = 21
#   unknown = 12
#   exclude = 0
#
# The 12 unknown IDs and documented reasons below are taken
# from the notebook's recorded Task 04.4 output.
# ============================================================

UNKNOWN_MANAGEMENT = {

    "05585000":
        "GAGES-II screening comments document an upstream city "
        "and reservoirs on two small tributaries; timing/status "
        "relative to reference classification is not established.",

    "06043500":
        "GAGES-II WR report documents irrigation diversions "
        "of about 1,400 acres upstream from station; timing "
        "relative to reference classification is not established.",

    "06339500":
        "GAGES-II screening comments document small reservoirs "
        "on some tributaries; timing/status relative to reference "
        "classification is not established.",

    "06353000":
        "GAGES-II screening comments document small reservoirs "
        "on some tributaries; timing/status relative to reference "
        "classification is not established.",

    "06441500":
        "GAGES-II screening comments document small reservoirs "
        "on some tributaries; timing/status relative to reference "
        "classification is not established.",

    "06450500":
        "GAGES-II WR report documents diurnal fluctuations caused "
        "by a small powerplant and several irrigation diversions "
        "upstream; timing relative to reference classification "
        "is not established.",

    "06453600":
        "GAGES-II WR report documents minor irrigation diversions "
        "above station; timing relative to reference classification "
        "is not established.",

    "06464500":
        "GAGES-II screening comments document small reservoirs "
        "on several tributaries; timing/status relative to reference "
        "classification is not established.",

    "07014500":
        "GAGES-II screening comments document small impoundments "
        "on tributaries; timing/status relative to reference "
        "classification is not established.",

    "07226500":
        "GAGES-II WR report documents irrigation diversions for "
        "a few hundred acres upstream from station; timing relative "
        "to reference classification is not established.",

    "08164000":
        "GAGES-II WR report documents small irrigation diversions "
        "above station; although it states no known regulation, "
        "the timing/status of the diversions relative to the "
        "reference classification is not established.",

    "09430500":
        "GAGES-II WR report documents irrigation diversions for "
        "about 500 acres upstream; timing relative to reference "
        "classification is not established.",
}


candidates["management_decision"] = pd.NA
candidates["management_exclusion_reason"] = pd.NA
candidates["management_review_note"] = pd.NA

# Only the 33 retained basins entered the actual management review.
for basin_id in candidates["basin_id"]:

    if basin_id in UNKNOWN_MANAGEMENT:

        candidates.loc[
            candidates["basin_id"] == basin_id,
            "management_decision"
        ] = "unknown"

        candidates.loc[
            candidates["basin_id"] == basin_id,
            "management_exclusion_reason"
        ] = UNKNOWN_MANAGEMENT[basin_id]

        candidates.loc[
            candidates["basin_id"] == basin_id,
            "management_review_note"
        ] = (
            "Management evidence exists, but available metadata "
            "does not establish whether the infrastructure represents "
            "a post-classification change."
        )

    elif basin_id in retained_ids:

        candidates.loc[
            candidates["basin_id"] == basin_id,
            "management_decision"
        ] = "keep"

        candidates.loc[
            candidates["basin_id"] == basin_id,
            "management_review_note"
        ] = (
            "No management change requiring exclusion was identified "
            "in the completed Task 04.4 review."
        )


# ============================================================
# MANAGEMENT VALIDATION
# ============================================================

management_keep = int(
    (candidates["management_decision"] == "keep").sum()
)

management_unknown = int(
    (candidates["management_decision"] == "unknown").sum()
)

management_exclude = int(
    (candidates["management_decision"] == "exclude").sum()
)

print()
print("Task 04.4 management:")
print(f"  keep:    {management_keep}")
print(f"  unknown: {management_unknown}")
print(f"  exclude: {management_exclude}")

assert management_keep == 21
assert management_unknown == 12
assert management_exclude == 0


# ============================================================
# SAVE RECONSTRUCTED MANAGEMENT TABLE
# ============================================================

management_output = candidates[
    [
        "basin_id",
        "management_decision",
        "management_exclusion_reason",
        "management_review_note",
    ]
].copy()

management_output = management_output[
    management_output["management_decision"].notna()
].copy()

management_output.to_csv(
    OUT_MANAGEMENT,
    index=False
)

print()
print("Saved reconstructed management table:")
print(OUT_MANAGEMENT)


# ============================================================
# NOAA REGION ASSIGNMENT
#
# This follows the Task 04.5 notebook method:
#
# 1. Download CONUS state boundaries
# 2. Assign each state to one NOAA region
# 3. Dissolve states by NOAA region
# 4. Intersect basin polygons with NOAA regions
# 5. Calculate overlap fractions
# 6. Select largest overlap
# 7. Alphabetical region name breaks exact ties
# ============================================================

print()
print("Loading CONUS geographic state boundaries...")


# ------------------------------------------------------------
# Census TIGER/Line states
# ------------------------------------------------------------

STATE_URL = (
    "https://www2.census.gov/geo/tiger/TIGER2023/STATE/"
    "tl_2023_us_state.zip"
)

response = requests.get(
    STATE_URL,
    timeout=60
)

response.raise_for_status()

with zipfile.ZipFile(
    BytesIO(response.content)
) as z:

    shp_files = [
        n for n in z.namelist()
        if n.endswith(".shp")
    ]

    if not shp_files:
        raise RuntimeError(
            "Could not find state shapefile in Census ZIP."
        )

    extract_dir = os.path.join(
        ROOT,
        "manifests",
        "_tmp_states"
    )

    os.makedirs(
        extract_dir,
        exist_ok=True
    )

    z.extractall(extract_dir)


state_shp = os.path.join(
    extract_dir,
    "tl_2023_us_state.shp"
)

states = gpd.read_file(state_shp)

print(f"States loaded: {len(states)}")


# ============================================================
# EXACT STATE → NOAA REGION MAPPING
# FROM TASK 04.5 NOTEBOOK
# ============================================================

STATE_TO_REGION = {

    # Northeast
    "09": "Northeast",       # CT
    "23": "Northeast",       # ME
    "25": "Northeast",       # MA
    "33": "Northeast",       # NH
    "34": "Northeast",       # NJ
    "36": "Northeast",       # NY
    "42": "Northeast",       # PA
    "44": "Northeast",       # RI
    "50": "Northeast",       # VT

    # Upper Midwest
    "17": "Upper Midwest",   # IL
    "18": "Upper Midwest",   # IN
    "26": "Upper Midwest",   # MI
    "27": "Upper Midwest",   # MN
    "39": "Upper Midwest",   # OH
    "55": "Upper Midwest",   # WI
    "19": "Upper Midwest",   # IA

    # Ohio Valley
    "21": "Ohio Valley",     # KY
    "47": "Ohio Valley",     # TN
    "54": "Ohio Valley",     # WV

    # Southeast
    "01": "Southeast",       # AL
    "10": "Southeast",       # DE
    "12": "Southeast",       # FL
    "13": "Southeast",       # GA
    "24": "Southeast",       # MD
    "28": "Southeast",       # MS
    "37": "Southeast",       # NC
    "45": "Southeast",       # SC
    "51": "Southeast",       # VA
    "11": "Southeast",       # DC

    # Northern Rockies and Plains
    "08": "Northern Rockies and Plains",  # CO
    "20": "Northern Rockies and Plains",  # KS
    "29": "Northern Rockies and Plains",  # MO
    "30": "Northern Rockies and Plains",  # MT
    "31": "Northern Rockies and Plains",  # NE
    "38": "Northern Rockies and Plains",  # ND
    "46": "Northern Rockies and Plains",  # SD
    "56": "Northern Rockies and Plains",  # WY

    # South
    "05": "South",           # AR
    "22": "South",           # LA
    "40": "South",           # OK
    "48": "South",           # TX

    # Southwest
    "04": "Southwest",       # AZ
    "32": "Southwest",       # NV
    "35": "Southwest",       # NM
    "49": "Southwest",       # UT

    # Northwest
    "16": "Northwest",       # ID
    "41": "Northwest",       # OR
    "53": "Northwest",       # WA

    # West
    "06": "West",            # CA
}


states["STATEFP"] = (
    states["STATEFP"]
    .astype(str)
    .str.zfill(2)
)

states["NOAA_REGION"] = states["STATEFP"].map(
    STATE_TO_REGION
)

# CONUS only.
# Exclude AK, HI, PR, territories.
states = states[
    states["STATEFP"].isin(
        STATE_TO_REGION.keys()
    )
].copy()

if states["NOAA_REGION"].isna().any():
    missing_states = states.loc[
        states["NOAA_REGION"].isna(),
        ["STATEFP", "STUSPS", "NAME"]
    ]

    raise RuntimeError(
        "States without NOAA region assignment:\n"
        + missing_states.to_string(index=False)
    )


# ============================================================
# USE EQUAL-AREA CRS
# ============================================================

AREA_CRS = "EPSG:5070"

basins_area = candidates[
    ["basin_id", "geometry"]
].copy()

basins_area = gpd.GeoDataFrame(
    basins_area,
    geometry="geometry",
    crs=gdf.crs
)

basins_area = basins_area.to_crs(
    AREA_CRS
)

states_area = states.to_crs(
    AREA_CRS
)


# ============================================================
# DISSOLVE STATES INTO NOAA REGIONS
# ============================================================

regions = (
    states_area
    .dissolve(
        by="NOAA_REGION",
        as_index=False
    )
)

print(
    f"NOAA regions created: {len(regions)}"
)

assert len(regions) == 9


# ============================================================
# BASIN × NOAA REGION INTERSECTION
# ============================================================

print("Calculating basin-region intersections...")

intersection = gpd.overlay(
    basins_area,
    regions[
        ["NOAA_REGION", "geometry"]
    ],
    how="intersection"
)


# ============================================================
# OVERLAP FRACTIONS
# ============================================================

intersection["intersection_area_m2"] = (
    intersection.geometry.area
)

basin_areas = (
    basins_area
    .set_index("basin_id")
    .geometry
    .area
)

intersection["basin_area_m2"] = (
    intersection["basin_id"]
    .map(basin_areas)
)

intersection["overlap_fraction"] = (
    intersection["intersection_area_m2"]
    /
    intersection["basin_area_m2"]
)

intersection["overlap_percent"] = (
    intersection["overlap_fraction"] * 100
)


# ============================================================
# KEEP ONLY ACTUAL RETAINED POPULATION FOR REGION ASSIGNMENT
# ============================================================

intersection_retained = intersection[
    intersection["basin_id"].isin(retained_ids)
].copy()


# ============================================================
# FRACTION SUM TEST
# ============================================================

fraction_sums = (
    intersection_retained
    .groupby("basin_id")["overlap_fraction"]
    .sum()
)

print()
print("NOAA fraction-sum test:")
print(
    f"Basins checked: {len(fraction_sums)}"
)

if len(fraction_sums) != 33:
    raise RuntimeError(
        f"Expected 33 basins in NOAA assignment; "
        f"found {len(fraction_sums)}."
    )

max_error = float(
    (fraction_sums - 1.0)
    .abs()
    .max()
)

print(
    f"Maximum absolute difference: {max_error}"
)

assert max_error < 1e-6


# ============================================================
# ASSIGN LARGEST OVERLAP
# ============================================================

intersection_sorted = intersection_retained.sort_values(
    [
        "basin_id",
        "overlap_fraction",
        "NOAA_REGION"
    ],
    ascending=[
        True,
        False,
        True
    ]
)

assignments = (
    intersection_sorted
    .drop_duplicates(
        subset="basin_id",
        keep="first"
    )
    [
        [
            "basin_id",
            "NOAA_REGION",
            "overlap_fraction",
            "overlap_percent"
        ]
    ]
    .copy()
)

assignments = assignments.rename(
    columns={
        "overlap_fraction":
            "assigned_region_fraction",

        "overlap_percent":
            "assigned_region_percent"
    }
)


# ============================================================
# EXACT TIE CHECK
# ============================================================

tie_rows = []

for basin_id, group in (
    intersection_retained
    .groupby("basin_id")
):

    max_fraction = group[
        "overlap_fraction"
    ].max()

    tied = group[
        group["overlap_fraction"]
        .sub(max_fraction)
        .abs()
        .lt(1e-12)
    ]

    if len(tied) > 1:

        chosen = sorted(
            tied["NOAA_REGION"].tolist()
        )[0]

        tie_rows.append(
            {
                "basin_id": basin_id,
                "tied_regions":
                    "; ".join(
                        sorted(
                            tied["NOAA_REGION"].tolist()
                        )
                    ),
                "tie_fraction":
                    max_fraction,
                "tie_rule":
                    "Alphabetical NOAA region name",
                "assigned_region":
                    chosen
            }
        )

print(
    f"Exact largest-overlap ties: {len(tie_rows)}"
)

# The notebook recorded zero ties.
assert len(tie_rows) == 0


# ============================================================
# SAVE REGION ASSIGNMENTS
# ============================================================

assignments = assignments.sort_values(
    "basin_id"
)

assignments.to_csv(
    OUT_REGIONS,
    index=False
)

intersection_retained[
    [
        "basin_id",
        "NOAA_REGION",
        "overlap_fraction",
        "overlap_percent"
    ]
].sort_values(
    ["basin_id", "NOAA_REGION"]
).to_csv(
    OUT_REGION_FRACTIONS,
    index=False
)

print()
print("Saved reconstructed NOAA assignments:")
print(OUT_REGIONS)

print()
print("Saved reconstructed overlap fractions:")
print(OUT_REGION_FRACTIONS)


# ============================================================
# MERGE NOAA REGION INTO CANDIDATES
# ============================================================

candidates = candidates.merge(
    assignments[
        [
            "basin_id",
            "NOAA_REGION",
            "assigned_region_fraction",
            "assigned_region_percent"
        ]
    ],
    on="basin_id",
    how="left"
)


# ============================================================
# FINAL FIRST-EXCLUSION REASON
# ============================================================

def first_exclusion_reason(row):

    if row["exclude_id_geometry"]:
        return "ID/geometry"

    if row["exclude_area"]:
        return "area"

    if row["exclude_management"]:
        return "management"

    if row["exclude_missing_attributes"]:
        return "missing attributes"

    if row["exclude_landcover"]:
        return "land-cover screens"

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
# FINAL STATUS
# ============================================================

candidates["excluded"] = (
    candidates["first_exclusion_reason"] != ""
)

candidates["primary_population"] = (
    ~candidates["excluded"]
)

candidates["population_label"] = (
    candidates["primary_population"]
    .map(
        {
            True: "retained",
            False: "excluded"
        }
    )
)


# ============================================================
# MANAGEMENT UNKNOWN FLAG
# ============================================================

candidates["management_unknown"] = (
    candidates["management_decision"]
    .fillna("")
    .astype(str)
    .str.lower()
    .eq("unknown")
)

candidates["management_feasibility_flag_final"] = (
    candidates["management_unknown"]
)


# ============================================================
# FINAL COUNTS
# ============================================================

n_candidates = len(candidates)

n_retained = int(
    candidates["primary_population"].sum()
)

n_excluded = int(
    candidates["excluded"].sum()
)

print()
print("=" * 70)
print("TASK 04 FINAL VALIDATION")
print("=" * 70)

print(f"Canonical basins: {len(canonical_ids)}")
print(f"Candidates:       {n_candidates}")
print(f"Retained:         {n_retained}")
print(f"Excluded:         {n_excluded}")

assert len(canonical_ids) == 629
assert n_candidates == 48
assert n_retained == 33
assert n_excluded == 15

assert (
    n_candidates - n_excluded
    == n_retained
)

assert (
    candidates["basin_id"].nunique()
    == 48
)

assert (
    candidates["geometry_area_km2"] > 0
).all()

assert (
    candidates.loc[
        candidates["excluded"],
        "first_exclusion_reason"
    ].eq("land-cover screens").all()
)

assert (
    candidates.loc[
        candidates["retained"],
        "first_exclusion_reason"
    ].eq("").all()
)

assert (
    candidates.loc[
        candidates["retained"],
        "NOAA_REGION"
    ].notna().all()
)

assert (
    candidates.loc[
        candidates["retained"],
        "management_decision"
    ].isin(
        ["keep", "unknown"]
    ).all()
)

assert management_keep == 21
assert management_unknown == 12
assert management_exclude == 0


# ============================================================
# SCREEN CSV
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
    "management_unknown",
    "management_feasibility_flag_final",
    "management_exclusion_reason",
    "management_review_note",

    "NOAA_REGION",
    "assigned_region_fraction",
    "assigned_region_percent",

    "retained",
    "excluded",
    "primary_population",
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
# SAVE SCREEN CSV
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
# SAVE EXCLUSIONS
# ============================================================

exclusions = screen_csv[
    screen_csv["excluded"]
].copy()

exclusions.to_csv(
    OUT_EXCLUSIONS,
    index=False
)


# ============================================================
# SAVE GEOPACKAGE
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

f1_columns = [
    "basin_id",
    "NOAA_REGION",
    "assigned_region_fraction",
    "assigned_region_percent",
    "geometry_area_km2",
    "management_decision",
    "management_unknown",
    "primary_population",
    "population_label",
    "first_exclusion_reason",
    "exclude_landcover",
]

f1 = screen_csv[
    f1_columns
].copy()

f1.to_csv(
    OUT_F1,
    index=False
)


# ============================================================
# CONUS OUTLINE
# ============================================================

print()
print("Loading CONUS geographic outline...")

# Use the Census states already downloaded above.
# Dissolve all CONUS states into a single outline.

conus = states[
    ["geometry"]
].dissolve()

print("CONUS outline loaded successfully.")


# ============================================================
# MAP
# ============================================================

fig, ax = plt.subplots(
    figsize=(12, 8)
)


# ------------------------------------------------------------
# CONUS outline
# ------------------------------------------------------------

conus.boundary.plot(
    ax=ax,
    linewidth=0.9,
    edgecolor="0.35",
    zorder=1
)


# ------------------------------------------------------------
# Candidate basin boundaries
# ------------------------------------------------------------

screen_gdf.boundary.plot(
    ax=ax,
    linewidth=0.35,
    color="0.75",
    alpha=0.65,
    zorder=2
)


# ------------------------------------------------------------
# Excluded
# ------------------------------------------------------------

excluded_gdf = screen_gdf[
    screen_gdf["excluded"]
]

if len(excluded_gdf) > 0:

    excluded_gdf.plot(
        ax=ax,
        facecolor="none",
        edgecolor="red",
        linewidth=1.0,
        label=f"Excluded ({len(excluded_gdf)})",
        zorder=3
    )


# ------------------------------------------------------------
# Retained
# ------------------------------------------------------------

retained_gdf = screen_gdf[
    screen_gdf["retained"]
]

if len(retained_gdf) > 0:

    retained_gdf.plot(
        ax=ax,
        facecolor="none",
        edgecolor="black",
        linewidth=1.35,
        label=f"Retained ({len(retained_gdf)})",
        zorder=4
    )


# ============================================================
# TITLE
# ============================================================

ax.set_title(
    "Candidate and Retained Basin Population",
    fontsize=15
)


# ============================================================
# SCALE BAR
# ============================================================

# Work in Web Mercator only for scale-bar placement.
# 500 km = 500,000 m.

map_bounds = conus.to_crs(
    "EPSG:3857"
)

minx, miny, maxx, maxy = (
    map_bounds.total_bounds
)

# Place scale bar in lower-left area.
bar_x = minx + (
    maxx - minx
) * 0.08

bar_y = miny + (
    maxy - miny
) * 0.055

bar_length = 500_000


# Plot scale bar using a second axis transformation.
# Convert the two endpoints back to geographic CRS.
from shapely.geometry import LineString

scale_line = gpd.GeoSeries(
    [
        LineString(
            [
                (bar_x, bar_y),
                (
                    bar_x + bar_length,
                    bar_y
                )
            ]
        )
    ],
    crs="EPSG:3857"
).to_crs(
    screen_gdf.crs
)

scale_line.plot(
    ax=ax,
    color="black",
    linewidth=3.0,
    zorder=10
)


# Tick marks
tick_height = (
    maxy - miny
) * 0.012

ticks = []

for x in [
    bar_x,
    bar_x + bar_length
]:

    ticks.append(
        LineString(
            [
                (x, bar_y - tick_height),
                (x, bar_y + tick_height)
            ]
        )
    )

tick_lines = gpd.GeoSeries(
    ticks,
    crs="EPSG:3857"
).to_crs(
    screen_gdf.crs
)

tick_lines.plot(
    ax=ax,
    color="black",
    linewidth=2.0,
    zorder=10
)


# Label
label_point = gpd.GeoSeries(
    [
        gpd.points_from_xy(
            [
                bar_x + bar_length / 2
            ],
            [
                bar_y + tick_height * 3
            ]
        )[0]
    ],
    crs="EPSG:3857"
).to_crs(
    screen_gdf.crs
)

x_label = label_point.iloc[0].x
y_label = label_point.iloc[0].y

ax.text(
    x_label,
    y_label,
    "500 km",
    ha="center",
    va="bottom",
    fontsize=12,
    fontweight="bold",
    zorder=11
)


# ============================================================
# LEGEND
# ============================================================

ax.legend(
    loc="lower left",
    frameon=True
)

ax.set_axis_off()

plt.tight_layout()

# Save to a fresh filename to avoid Windows/PIL file-lock issues
fig.savefig(
    OUT_FIG,
    dpi=300,
    bbox_inches="tight",
    format="png"
)
plt.close(fig)


# ============================================================
# CLEAN TEMP STATES
# ============================================================

try:
    shutil.rmtree(
        extract_dir
    )
except Exception:
    pass


# ============================================================
# FINAL OUTPUT REPORT
# ============================================================

print()
print("=" * 70)
print("TASK 04 COMPLETE")
print("=" * 70)

print()
print("PASS: 629 canonical basins")
print("PASS: 48 area-screen candidates")
print("PASS: 33 retained")
print("PASS: 15 excluded")
print("PASS: 21 management keep")
print("PASS: 12 management unknown")
print("PASS: 0 management exclusions")
print("PASS: 33 NOAA region assignments")
print("PASS: NOAA fraction sums")
print("PASS: no exact NOAA overlap ties")
print("PASS: sequential exclusion arithmetic")
print("PASS: positive basin areas")
print("PASS: CONUS outline")
print("PASS: 500 km scale bar")

print()
print("OUTPUTS")
print("-" * 70)

print(OUT_SCREEN)
print(OUT_EXCLUSIONS)
print(OUT_GPKG)
print(OUT_F1)
print(OUT_FIG)
print(OUT_MANAGEMENT)
print(OUT_REGIONS)
print(OUT_REGION_FRACTIONS)

print()
print("=" * 70)
print("TASK 04 DELIVERABLE BUILD COMPLETE")
print("=" * 70)