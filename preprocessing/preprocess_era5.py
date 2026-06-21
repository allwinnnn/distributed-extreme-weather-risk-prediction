import xarray as xr
import pandas as pd

print("START ERA5 PREPROCESSING")

file = "/Users/allwinsuresh/rainfall_project/project/data_stream-oper_stepType-instant.nc"

# Load dataset
ds = xr.open_dataset(file)

print("\nDataset loaded")
print("Variables:", list(ds.data_vars))
print("Dimensions:", ds.dims)

# Check variables
print("\nVariables:", list(ds.data_vars))

# Extract precipitation
if "tp" not in ds:
    raise Exception("tp variable not found. Available: " + str(list(ds.data_vars)))

data = ds["tp"]

# Convert to dataframe
df = data.to_dataframe().reset_index()

print("\nRaw data shape:", df.shape)

# Convert meters → mm
df["rainfall_mm"] = df["tp"] * 1000

# Detect column names (ERA5 sometimes differs)
lat_col = "latitude" if "latitude" in df.columns else "lat"
lon_col = "longitude" if "longitude" in df.columns else "lon"

# Filter India region
df_india = df[
    (df[lat_col] >= 6) & (df[lat_col] <= 38) &
    (df[lon_col] >= 68) & (df[lon_col] <= 98)
]

print("India filtered shape:", df_india.shape)

# Convert time → date
df_india["date"] = pd.to_datetime(df_india["time"]).dt.date

# Final dataset
final_df = df_india[["date", lat_col, lon_col, "rainfall_mm"]]

print("\nFinal shape:", final_df.shape)
print(final_df.head())

# Save
final_df.to_csv("processed_era5.csv", index=False)

print("\n✅ ERA5 preprocessing DONE")