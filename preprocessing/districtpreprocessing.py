import pandas as pd
import geopandas as gpd

print("🚀 STARTING DISTRICT PREPROCESSING")

# =========================
# 1. LOAD DATA
# =========================
print("Loading GPM data...")
df = pd.read_csv("gpm_final.csv")

# Convert date
df["Date"] = pd.to_datetime(df["Date"])

# =========================
# 2. FILTER INDIA
# =========================
df = df[
    (df["Latitude"] >= 5) & (df["Latitude"] <= 35) &
    (df["Longitude"] >= 65) & (df["Longitude"] <= 98)
]

print("After India filter:", df.shape)

# =========================
# 3. CONVERT TO GEO
# =========================
gdf = gpd.GeoDataFrame(
    df,
    geometry=gpd.points_from_xy(df["Longitude"], df["Latitude"]),
    crs="EPSG:4326"
)

# =========================
# 4. LOAD DISTRICTS
# =========================
print("Loading district boundaries...")
districts = gpd.read_file("india_district.geojson")

districts = districts.to_crs("EPSG:4326")

print("District columns:")
print(districts.columns)

# =========================
# 5. SPATIAL JOIN
# =========================
print("Performing spatial join...")
gdf = gpd.sjoin(gdf, districts, how="inner", predicate="within")

print("After join:", gdf.shape)

# =========================
# 6. AUTO DETECT DISTRICT COLUMN
# =========================
print("Columns after join:")
print(gdf.columns)

possible_cols = [col for col in gdf.columns if "district" in col.lower()]

if not possible_cols:
    raise Exception("❌ No district column found!")

district_col = possible_cols[0]

print("✅ Using district column:", district_col)

# =========================
# 7. AGGREGATE
# =========================
df_final = (
    gdf.groupby(["Date", district_col])["Rainfall_GPM"]
    .mean()
    .reset_index()
)

print("Final shape:", df_final.shape)

# =========================
# 8. SAVE
# =========================
df_final.to_csv("gpm_district.csv", index=False)

print("✅ DONE: gpm_district.csv saved")