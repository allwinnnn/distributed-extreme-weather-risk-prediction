import xarray as xr
import pandas as pd
import geopandas as gpd
import numpy as np

print("🚀 PROCESSING ERA5 WEATHER")

# Load ERA5 file
ds = xr.open_dataset("/Users/allwinsuresh/rainfall_project/project/data_stream-oper_stepType-instant-3.nc")

# Extract variables
t2m = ds['t2m']
d2m = ds['d2m']
u10 = ds['u10']
v10 = ds['u10'] if 'v10' not in ds else ds['v10']  # safe fallback

# Convert to dataframe (faster way)
df = ds[['t2m', 'd2m', 'u10', 'v10']].to_dataframe().reset_index()

# Convert units
df['Temperature'] = df['t2m'] - 273.15
df['Wind_Speed'] = np.sqrt(df['u10']**2 + df['v10']**2)

# Humidity calculation
df['Humidity'] = 100 * (
    np.exp((17.625*(df['d2m']-273.15))/(243.04+(df['d2m']-273.15))) /
    np.exp((17.625*(df['t2m']-273.15))/(243.04+(df['t2m']-273.15)))
)

print("Columns available:", df.columns)

# Auto-detect time column
time_col = None
for col in ['time', 'valid_time', 'date']:
    if col in df.columns:
        time_col = col
        break

if time_col is None:
    raise Exception("No time column found!")

print("Using time column:", time_col)

df = df[[time_col, 'latitude', 'longitude', 'Temperature', 'Humidity', 'Wind_Speed']]
df.rename(columns={time_col: 'Date'}, inplace=True)
df.rename(columns={'time': 'Date'}, inplace=True)
df['Date'] = pd.to_datetime(df['Date']).dt.date

print("Shape:", df.shape)

# =========================
# DISTRICT MAPPING
# =========================
districts = gpd.read_file("INDIA_DISTRICTS.geojson")

gdf = gpd.GeoDataFrame(
    df,
    geometry=gpd.points_from_xy(df.longitude, df.latitude),
    crs="EPSG:4326"
)

joined = gpd.sjoin(gdf, districts, how='inner', predicate='within')

# Auto detect district column
district_col = None
for col in ['district', 'DISTRICT', 'dtname']:
    if col in joined.columns:
        district_col = col
        break

print("Using:", district_col)

# Aggregate
weather = joined.groupby(['Date', district_col]).agg({
    'Temperature': 'mean',
    'Humidity': 'mean',
    'Wind_Speed': 'mean'
}).reset_index()

weather.rename(columns={district_col: 'district'}, inplace=True)

weather.to_csv("weather_district_final.csv", index=False)

print("✅ weather_district_final.csv saved")