import pandas as pd

print("🔹 Cleaning GPM Dataset")

# LOAD
df = pd.read_csv("gpm_district_final.csv")

# STANDARDIZE COLUMNS
df.columns = df.columns.str.lower()

# CLEAN DISTRICT
df['district'] = (
    df['district']
    .astype(str)
    .str.upper()
    .str.replace(r'[^A-Z ]', '', regex=True)
    .str.replace(r'\s+', ' ', regex=True)
    .str.strip()
)

# FIX DATE (ROBUST)
df['date'] = pd.to_datetime(df['date'], errors='coerce', dayfirst=True)

# RENAME
df.rename(columns={'rainfall_gpm': 'gpm_rainfall'}, inplace=True)

# DROP BAD ROWS
df = df.dropna(subset=['date', 'district'])

print("Shape:", df.shape)
print(df.head())

# SAVE
df.to_csv("clean_gpm.csv", index=False)

print("✅ GPM CLEANED")