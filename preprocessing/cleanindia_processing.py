import pandas as pd

print("Cleaning Indian Rainfall Dataset")

df = pd.read_csv("processed_rainfall_final.csv")

# Standardize column names
df.columns = df.columns.str.lower()

# Clean district
df['district'] = (
    df['district']
    .str.upper()
    .str.replace(r'[^A-Z ]', '', regex=True)
    .str.replace(r'\s+', ' ', regex=True)
    .str.strip()
)

# Fix date
df['date'] = pd.to_datetime(df['date'], dayfirst=True, errors='coerce')

# Rename rainfall column
df.rename(columns={'rainfall': 'target_rainfall'}, inplace=True)

print(df.head())
print("Shape:", df.shape)

# Save
df.to_csv("clean_indiafinal.csv", index=False)

print("✅ Saved clean_indiafinal.csv")