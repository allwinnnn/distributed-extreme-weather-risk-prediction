

import xarray as xr
import pandas as pd
import os
from glob import glob
from sklearn.neighbors import BallTree
import numpy as np

print("🚀 STARTING FINAL GPM PREPROCESSING")

# 📁 Folder with nc4 files
DATA_FOLDER = "/Users/allwinsuresh/rainfall_project/project"   # change if needed

# 📄 Load files
files = sorted(glob(os.path.join(DATA_FOLDER, "*.nc4")))

all_data = []

# =========================
# 📍 LOAD GEO DATA (district lat/lon)


geo_df = pd.read_csv("district_geo.csv")

geo_df = geo_df.dropna(subset=["Latitude", "Longitude"])

# Convert to radians for BallTree
geo_coords = np.radians(geo_df[["Latitude", "Longitude"]].values)
tree = BallTree(geo_coords, metric='haversine')

print("✅ Geo data loaded:", geo_df.shape)

# =========================
# 📦 PROCESS FILES
# =========================
for i, file in enumerate(files):
    print(f"Processing {i+1}/{len(files)}")

    try:
        ds = xr.open_dataset(file)

        # Detect rainfall variable
        vars_available = list(ds.data_vars)

        if "precipitation" in vars_available:
            rain_var = "precipitation"
        elif "precipitationCal" in vars_available:
            rain_var = "precipitationCal"
        else:
            print(f"❌ Skipping file — no rainfall var: {vars_available}")
            continue

        data = ds[rain_var]

        df = data.to_dataframe().reset_index()

        df.rename(columns={
            "time": "Date",
            rain_var: "Rainfall_GPM",
            "lat": "Latitude",
            "lon": "Longitude"
        }, inplace=True)

        # 🗓 Convert date
        df["Date"] = pd.to_datetime(df["Date"])

        # 🌧 Monsoon only
        df = df[df["Date"].dt.month.isin([6, 7, 8, 9])]

        # 🧹 Drop missing
        df.dropna(inplace=True)

        # 🔥 Reduce spatial resolution FIRST (very important)
        df["Latitude"] = df["Latitude"].round(1)
        df["Longitude"] = df["Longitude"].round(1)

        df = df.groupby(
            ["Date", "Latitude", "Longitude"]
        )["Rainfall_GPM"].mean().reset_index()

        # =========================
        # 📍 MAP TO DISTRICT
        # =========================

        coords = np.radians(df[["Latitude", "Longitude"]].values)

        # Find nearest district
        dist, ind = tree.query(coords, k=1)

        df["District"] = geo_df.iloc[ind.flatten()]["District"].values

        # =========================
        # 📉 FINAL AGGREGATION
        # =========================

        df = df.groupby(
            ["Date", "District"]
        )["Rainfall_GPM"].mean().reset_index()

        all_data.append(df)

    except Exception as e:
        print(f"❌ Error: {e}")

# =========================
# 📦 COMBINE ALL FILES
# =========================

print("📦 Combining data...")
final_df = pd.concat(all_data, ignore_index=True)

# Final cleanup
final_df.dropna(inplace=True)

print("✅ FINAL SHAPE:", final_df.shape)

# =========================
# 💾 SAVE
# =========================

output_file = "gpm_district_processed.csv"
final_df.to_csv(output_file, index=False)

print(f"🎯 SAVED: {output_file}")