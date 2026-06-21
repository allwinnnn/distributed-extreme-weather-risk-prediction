import xarray as xr
import pandas as pd

print("START ERA5 TP PREPROCESSING")

# Load dataset
file_path = "era5_tp_2022.nc"   
ds = xr.open_dataset(file_path)

print("Dataset loaded")
print("Variables:", list(ds.data_vars))
print("Dimensions:", ds.dims)

# Ensure 'tp' exists
if "tp" not in ds:
    raise Exception(f"tp variable not found. Available: {list(ds.data_vars)}")

# Extract rainfall
tp = ds["tp"]

# Convert to dataframe
df = tp.to_dataframe().reset_index()

print("Converted to dataframe")
print(df.head())

# Rename columns (handle both possible time names)
if "valid_time" in df.columns:
    df.rename(columns={"valid_time": "Date"}, inplace=True)
elif "time" in df.columns:
    df.rename(columns={"time": "Date"}, inplace=True)

df.rename(columns={
    "latitude": "Latitude",
    "longitude": "Longitude",
    "tp": "Rainfall_ERA5"
}, inplace=True)

# Convert rainfall from meters → mm
df["Rainfall_ERA5"] = df["Rainfall_ERA5"] * 1000

# REMOVE unwanted columns 
df = df[["Date", "Latitude", "Longitude", "Rainfall_ERA5"]]

# Drop missing values
df.dropna(inplace=True)

print("Final shape:", df.shape)


df.to_csv("era5_processed.csv", index=False)

print("✅ CLEAN ERA5 DATA SAVED as era5_processed.csv")