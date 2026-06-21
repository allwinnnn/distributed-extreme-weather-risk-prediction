from pyspark.sql import SparkSession
from pyspark.sql.functions import round, avg

print("🚀 STARTING SPARK PREPROCESSING")

# 1️⃣ Start Spark
spark = SparkSession.builder \
    .appName("Rainfall Preprocessing") \
    .getOrCreate()

# Reduce shuffle
spark.conf.set("spark.sql.shuffle.partitions", "8")


df = spark.read.csv(
    "gpm_processed.csv",   
    header=True,
    inferSchema=True
)

print("✅ Data Loaded")


df = df.select("Date", "Latitude", "Longitude", "Rainfall_GPM")

#  FILTER INDIA 
df = df.filter(
    (df.Latitude >= 6) & (df.Latitude <= 38) &
    (df.Longitude >= 68) & (df.Longitude <= 98)
)

#  Remove zero rainfall
df = df.filter(df.Rainfall_GPM > 0)

#  Reduce precision
df = df.withColumn("Latitude", round(df.Latitude, 1))
df = df.withColumn("Longitude", round(df.Longitude, 1))

#  Aggregate
df = df.groupBy("Date", "Latitude", "Longitude") \
       .agg(avg("Rainfall_GPM").alias("Rainfall_GPM"))

print("✅ Aggregation done")

#  FORCE SINGLE FILE OUTPUT
df = df.coalesce(1)

#  Save as CSV
output_folder = "gpm_final_output"

df.write.mode("overwrite") \
    .option("header", True) \
    .csv(output_folder)

print("✅ Saved as single-part CSV folder")

spark.stop()