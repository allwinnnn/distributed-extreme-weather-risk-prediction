from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col, upper, trim, to_date, regexp_replace, when, month, avg
)

# ------------------ START SPARK ------------------
spark = SparkSession.builder \
    .appName("Rainfall ETL FINAL CLEAN") \
    .config("spark.hadoop.fs.defaultFS", "hdfs://localhost:9000") \
    .getOrCreate()

spark.sparkContext.setLogLevel("ERROR")

print("🚀 Spark Started")

# ------------------ LOAD ------------------
india = spark.read.csv("hdfs://localhost:9000/rainfall_project/clean_indiafinal.csv", header=True, inferSchema=True)
gpm = spark.read.csv("hdfs://localhost:9000/rainfall_project/clean_gpm.csv", header=True, inferSchema=True)
era5 = spark.read.csv("hdfs://localhost:9000/rainfall_project/clean_era5.csv", header=True, inferSchema=True)
weather = spark.read.csv("hdfs://localhost:9000/rainfall_project/clean_weather.csv", header=True, inferSchema=True)

# ------------------ CLEAN ------------------
def clean(df):
    return df \
        .withColumn("district", upper(trim(regexp_replace(col("district"), "[^A-Za-z ]", "")))) \
        .withColumn("district", regexp_replace(col("district"), " +", " ")) \
        .withColumn("date", to_date(col("date"))) \
        .dropna(subset=["district", "date"])

india = clean(india)
gpm = clean(gpm)
era5 = clean(era5)
weather = clean(weather)

# ------------------ NORMALIZE ------------------
def normalize(df):
    return df.withColumn("district",
        when(col("district").like("%NICOBAR%"), "NICOBARS")
        .when(col("district").like("%ANDAMAN%"), "SOUTH ANDAMANS")
        .when(col("district").like("%MEDINIPUR%"), "PASCHIM MEDINIPUR")
        .when(col("district").like("%DINAJPUR%"), "UTTAR DINAJPUR")
        .when(col("district").like("%CHAMPARAN%"), "PASCHIM CHAMPARAN")
        .when(col("district").like("%BANGALORE%"), "BENGALURU")
        .otherwise(col("district"))
    )

india = normalize(india)
gpm = normalize(gpm)
era5 = normalize(era5)
weather = normalize(weather)

print("✅ Cleaning + normalization done")

# ------------------ MONSOON FILTER ------------------
india = india.filter(month(col("date")).isin([6,7,8,9]))
gpm = gpm.filter(month(col("date")).isin([6,7,8,9]))
era5 = era5.filter(month(col("date")).isin([6,7,8,9]))
weather = weather.filter(month(col("date")).isin([6,7,8,9]))

print("✅ Monsoon filter applied")

# ------------------ 🔥 REMOVE DUPLICATES (CRITICAL) ------------------
print("\n🧹 Aggregating to remove duplicates")

india = india.groupBy("date","district","state") \
    .agg(avg("target_rainfall").alias("target_rainfall"))

gpm = gpm.groupBy("date","district") \
    .agg(avg("gpm_rainfall").alias("gpm_rainfall"))

era5 = era5.groupBy("date","district") \
    .agg(avg("era5_rainfall").alias("era5_rainfall"))

weather = weather.groupBy("date","district") \
    .agg(
        avg("temperature").alias("temperature"),
        avg("humidity").alias("humidity"),
        avg("wind_speed").alias("wind_speed")
    )

print("✅ Aggregation done")

# ------------------ FINAL JOIN ------------------
df = india \
    .join(gpm, ["date","district"], "left") \
    .join(era5, ["date","district"], "left") \
    .join(weather, ["date","district"], "left")

print("✅ Final rows:", df.count())

# ------------------ NULL HANDLING ------------------
df = df.fillna({
    "gpm_rainfall": 0,
    "era5_rainfall": 0,
    "temperature": 0,
    "humidity": 0,
    "wind_speed": 0
})

# ------------------ VALIDATION ------------------
df.selectExpr(
    "count(*) as total_rows",
    "count(distinct district) as districts"
).show()

df.show(5)

# ------------------ SAVE ------------------
df.write.mode("overwrite").option("header", True).csv(
    "hdfs://localhost:9000/rainfall_project/final_dataset_spark"
)

print("\n💾 FINAL CLEAN DATA READY")

spark.stop()