from pyspark.sql import SparkSession
from pyspark.sql.functions import col

# -------------------------------
# START SPARK
# -------------------------------
spark = SparkSession.builder \
    .appName("Label Creation FINAL") \
    .config("spark.hadoop.fs.defaultFS", "hdfs://localhost:9000") \
    .getOrCreate()

spark.sparkContext.setLogLevel("ERROR")

print("🚀 Spark Started")

# -------------------------------
# LOAD FEATURE DATA
# -------------------------------
df = spark.read.csv(
    "hdfs://localhost:9000/rainfall_project/feature_dataset",
    header=True,
    inferSchema=True
)

print("📊 Feature data loaded")

# -------------------------------
# CHECK TARGET DISTRIBUTION
# -------------------------------
df.select("target_rainfall").describe().show()

# -------------------------------
# CALCULATE THRESHOLD (90th percentile)
# -------------------------------
threshold = df.approxQuantile("target_rainfall", [0.95], 0.01)[0]

print(f"🔥 Threshold (90th percentile): {threshold}")

# -------------------------------
# CREATE LABEL (FIXED)
# -------------------------------
df = df.withColumn(
    "extreme_rain",
    (col("target_rainfall") >= threshold).cast("int")
)

# -------------------------------
# CHECK CLASS DISTRIBUTION
# -------------------------------
print("📊 Label Distribution")
df.groupBy("extreme_rain").count().show()

# -------------------------------
# DEBUG: SEE EXTREME CASES
# -------------------------------
print("🌧️ Sample Extreme Rain Rows")
df.filter(col("extreme_rain") == 1) \
  .select("target_rainfall", "gpm_rainfall", "era5_rainfall") \
  .show(10)

# -------------------------------
# SAVE LABELED DATA
# -------------------------------
df.write.mode("overwrite") \
    .option("header", True) \
    .csv("hdfs://localhost:9000/rainfall_project/labeled_dataset")

print("💾 Labeled dataset saved")

# -------------------------------
# STOP
# -------------------------------
spark.stop()