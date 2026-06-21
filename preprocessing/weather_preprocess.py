import xarray as xr
import pandas as pd
import geopandas as gpd
import numpy as np

print("🚀 STARTING WEATHER DISTRICT MAPPING")

# =========================
# 1. LOAD NETCDF
# =========================
ds = xr.open_dataset("era5_weather.nc")

print("Variables:", list(ds.data_vars))

# Convert to dataframe
df = ds.to_dataframe().reset_index()

# =========================
# 2. CLEAN + RENAME
# =========================
df.rename(columns={
    "valid_time": "Date",
    "latitude": "Latitude",
    "longitude": "Longitude",
    "t2m": "Temperature",
    "d2m": "DewPoint",
    "u10": "Wind_U",
    "v10": "Wind_V"
}, inplace=True)

# Convert units
df["Temperature"] = df["Temperature"] - 273.15
df["DewPoint"] = df["DewPoint"] - 273.15

# =========================
# 3. CALCULATE FEATURES
# =========================
# Humidity
df["Humidity"] = 100 * (
    np.exp((17.625 * df["DewPoint"]) / (243.04 + df["DewPoint"])) /
    np.exp((17.625 * df["Temperature"]) / (243.04 + df["Temperature"]))
)

# Wind speed
df["Wind_Speed"] = np.sqrt(df["Wind_U"]**2 + df["Wind_V"]**2)

# Keep needed columns
df = df[[
    "Date", "Latitude", "Longitude",
    "Temperature", "Humidity", "Wind_Speed"
]]

df.dropna(inplace=True)

print("After cleaning:", df.shape)

# =========================
# 4. CONVERT TO GEO
# =========================
gdf = gpd.GeoDataFrame(
    df,
    geometry=gpd.points_from_xy(df["Longitude"], df["Latitude"]),
    crs="EPSG:4326"
)

# =========================
# 5. LOAD DISTRICT SHAPE
# =========================
districts = gpd.read_file("INDIA_DISTRICTS.geojson")
districts = districts.to_crs("EPSG:4326")

# =========================
# 6. SPATIAL JOIN
# =========================
print("Mapping to districts...")
gdf = gpd.sjoin(gdf, districts, how="inner", predicate="within")

print("After join:", gdf.shape)

# =========================
# 7. FIND DISTRICT COLUMN
# =========================
possible_cols = [col for col in gdf.columns if "district" in col.lower()]
district_col = possible_cols[0]

print("Using district column:", district_col)

# =========================
# 8. AGGREGATE
# =========================
df_final = (
    gdf.groupby(["Date", district_col])[
        ["Temperature", "Humidity", "Wind_Speed"]
    ]
    .mean()
    .reset_index()
)

# Rename
df_final.columns = [
    "Date", "district",
    "Temperature", "Humidity", "Wind_Speed"
]

print("Final shape:", df_final.shape)

# =========================
# 9. SAVE
# =========================
df_final.to_csv("weather_district.csv", index=False)

print("✅ DONE: weather_district.csv saved")