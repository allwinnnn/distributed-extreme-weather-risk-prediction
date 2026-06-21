from pyspark.sql import SparkSession
from pyspark.sql.window import Window
from pyspark.sql.functions import lag, col

spark = SparkSession.builder \
    .appName("Feature Engineering FINAL FIX") \
    .config("spark.hadoop.fs.defaultFS", "hdfs://localhost:9000") \
    .getOrCreate()

print("🚀 Spark Started")

# -----------------------------
# LOAD DATA
# -----------------------------
df = spark.read.csv(
    "hdfs://localhost:9000/rainfall_project/final_dataset_spark",
    header=True,
    inferSchema=True
)

print("✅ Data Loaded")

# -----------------------------
# REMOVE FAKE DATA (VERY IMPORTANT)
# -----------------------------
df = df.filter(
    (col("gpm_rainfall") > 0) |
    (col("era5_rainfall") > 0)
)

print("✅ Removed rows with no rainfall signal")

# -----------------------------
# REMOVE INVALID WEATHER ROWS
# -----------------------------
df = df.filter(
    (col("temperature") > 0) &
    (col("humidity") > 0)
)

print("✅ Removed invalid weather rows")

# -----------------------------
# CREATE LAG FEATURE
# -----------------------------
window = Window.partitionBy("district").orderBy("date")

df = df.withColumn(
    "rainfall_lag1",
    lag("target_rainfall", 1).over(window)
)

# -----------------------------
# HANDLE LAG NULL
# -----------------------------
df = df.fillna({
    "rainfall_lag1": 0
})

print("✅ Lag feature created")

# -----------------------------
# FINAL CHECK
# -----------------------------
df.select(
    "gpm_rainfall",
    "era5_rainfall",
    "temperature",
    "humidity"
).describe().show()

df.show(5)

print("📊 Final rows:", df.count())

# -----------------------------
# SAVE FEATURE DATASET
# -----------------------------
df.write.mode("overwrite") \
    .option("header", True) \
    .csv("hdfs://localhost:9000/rainfall_project/feature_dataset")

print("💾 Feature dataset saved")

spark.stop()