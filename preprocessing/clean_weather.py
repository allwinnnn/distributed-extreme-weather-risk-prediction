import pandas as pd
import re

print("🚀 CLEANING WEATHER DATA")

# Load
df = pd.read_csv("weather_district.csv")

print("Original shape:", df.shape)


def clean_district(x):
    if pd.isna(x):
        return x
    x = str(x).upper()
    x = re.sub(r"[^A-Z ]", "", x)   # remove symbols
    x = re.sub(r"\s+", " ", x).strip()
    return x

df["district"] = df["district"].apply(clean_district)


DISTRICT_MAP = {
    "BANGALORE URBAN": "BENGALURU URBAN",
    "BANGALORE RURAL": "BENGALURU RURAL",
    "TRIVANDRUM": "THIRUVANANTHAPURAM",
    "ALLEPPEY": "ALAPPUZHA",
    "COCHIN": "ERNAKULAM",
    "CALCUTTA": "KOLKATA",
    "BOMBAY": "MUMBAI",
    "DELHI": "NEW DELHI",
}

df["district"] = df["district"].replace(DISTRICT_MAP)


df["Date"] = pd.to_datetime(df["Date"], errors="coerce")


df = df.dropna(subset=["Date", "district"])

# remove very short garbage names
df = df[df["district"].str.len() > 3]


print("Checking duplicates...")

dup_check = df.groupby(["Date", "district"]).size().max()
print("Max duplicates per group:", dup_check)

# aggregate if duplicates exist
df = df.groupby(["Date", "district"], as_index=False).mean()


df = df.sort_values(["Date", "district"])

print("Final shape:", df.shape)


df.to_csv("weather_district_clean.csv", index=False)

print("✅ CLEAN FILE SAVED")