import pandas as pd

print("🔹 Cleaning ERA5 Rainfall Dataset")

df = pd.read_csv("era5_district_final.csv")

# standardize
df.columns = df.columns.str.lower()

# clean district
df['district'] = (
    df['district']
    .astype(str)
    .str.upper()
    .str.replace(r'[^A-Z ]', '', regex=True)
    .str.replace(r'\s+', ' ', regex=True)
    .str.strip()
)

# FIX DATE (NO dayfirst here)
df['date'] = pd.to_datetime(df['date'], errors='coerce')

# rename
df.rename(columns={'rainfall_era5': 'era5_rainfall'}, inplace=True)

# drop bad rows
df = df.dropna(subset=['date', 'district'])

print("Shape:", df.shape)
print(df.head())

df.to_csv("clean_era5.csv", index=False)

print("✅ ERA5 CLEANED")