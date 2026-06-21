import pandas as pd
import geopandas as gpd

print("🚀 STARTING ERA5 DISTRICT PROCESSING")

# =========================
# Load ERA5 data
# =========================
print("Loading ERA5 data...")
df = pd.read_csv("era5_processed.csv")

# Convert to GeoDataFrame
gdf = gpd.GeoDataFrame(
    df,
    geometry=gpd.points_from_xy(df["Longitude"], df["Latitude"]),
    crs="EPSG:4326"
)

# =========================
# Load district shapefile
# =========================
print("Loading district boundaries...")
districts = gpd.read_file("INDIA_DISTRICTS.geojson")

# Match CRS
districts = districts.to_crs(gdf.crs)

print("Available district columns:", districts.columns)

# =========================
# Spatial join
# =========================
print("Performing spatial join...")
joined = gpd.sjoin(gdf, districts, how="inner", predicate="within")

print("Columns after join:", joined.columns)

# =========================
# Identify district column
# =========================
district_col = None
for col in ["district", "DISTRICT", "dtname", "name"]:
    if col in joined.columns:
        district_col = col
        break

if district_col is None:
    raise Exception("District column not found!")

print("Using district column:", district_col)

# =========================
# Aggregate to district level
# =========================
print("Aggregating...")
final = (
    joined.groupby(["Date", district_col])["Rainfall_ERA5"]
    .mean()
    .reset_index()
)

# Rename
final.columns = ["Date", "district", "Rainfall_ERA5"]

print("Final shape:", final.shape)

# =========================
# Save
# =========================
final.to_csv("era5_district.csv", index=False)

print("✅ DONE: era5_district.csv saved")