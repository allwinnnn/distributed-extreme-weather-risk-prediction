import pandas as pd

print("🔹 Cleaning Weather Dataset")

df = pd.read_csv("weather_district_final.csv")

# standardize columns
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

# FIX DATE (NO dayfirst)
df['date'] = pd.to_datetime(df['date'], errors='coerce')

# drop bad rows
df = df.dropna(subset=['date', 'district'])

print("Shape:", df.shape)
print(df.head())

df.to_csv("clean_weather.csv", index=False)

print("✅ WEATHER CLEANED")