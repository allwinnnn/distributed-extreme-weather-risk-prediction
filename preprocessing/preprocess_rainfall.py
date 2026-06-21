import pandas as pd

print("STARTING SCRIPT")

# Load file
df = pd.read_csv("rainfall.csv", sep=';')

#  Clean column names properly
df.columns = df.columns.str.strip().str.lower().str.replace('\ufeff', '')

print("Cleaned Columns:", list(df.columns))

# Verify required columns exist
required_cols = ["state", "district", "month"]
for col in required_cols:
    if col not in df.columns:
        print(f"Missing column: {col}")
        exit()

# Identify day columns
day_cols = [col for col in df.columns if col not in required_cols]

print("Day columns detected:", day_cols[:5], "...")

# Melt
df_long = df.melt(
    id_vars=required_cols,
    value_vars=day_cols,
    var_name="day",
    value_name="rainfall"
)

# Extract numeric day
df_long["day"] = df_long["day"].str.extract(r'(\d+)').astype(int)

# Clean rainfall
df_long["rainfall"] = pd.to_numeric(df_long["rainfall"], errors="coerce")
df_long = df_long.dropna()
df_long = df_long[df_long["rainfall"] >= 0]

#  year
df_long["year"] = 2022

#  Create date
df_long["date"] = pd.to_datetime(
    df_long["year"].astype(str) + "-" +
    df_long["month"].astype(str) + "-" +
    df_long["day"].astype(str),
    errors="coerce"
)

# Final dataset
final_df = df_long[["state", "district", "date", "rainfall"]]

print("Final shape:", final_df.shape)

# Save
final_df.to_csv("processed_rainfall.csv", index=False)

print("✅ FILE SAVED SUCCESSFULLY")