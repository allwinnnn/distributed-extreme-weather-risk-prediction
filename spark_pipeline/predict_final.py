from pyspark.sql import SparkSession
from pyspark.sql.functions import col, isnan
from pyspark.sql.types import DoubleType
from pyspark.ml.functions import vector_to_array
from pyspark.ml import PipelineModel

# -----------------------------
# START SPARK (FIXED CONFIG)
# -----------------------------
spark = SparkSession.builder \
    .appName("Rainfall Prediction FINAL") \
    .config("spark.jars.packages",
        "org.mongodb.spark:mongo-spark-connector_2.12:10.3.0") \
    .config("spark.mongodb.write.connection.uri",
            "mongodb://127.0.0.1:27017") \
    .getOrCreate()

spark.sparkContext.setLogLevel("ERROR")

print("🚀 Spark Started")

# -----------------------------
# LOAD DATA
# -----------------------------
df = spark.read.csv(
    "hdfs://localhost:9000/rainfall_project/feature_dataset",
    header=True,
    inferSchema=True
)

print("✅ Feature Dataset Loaded")

# -----------------------------
# FEATURES 
# -----------------------------
cols = [
    "gpm_rainfall",
    "era5_rainfall",
    "temperature",
    "humidity",
    "wind_speed",
    "rainfall_lag1"
]

# -----------------------------
# CLEAN DATA
# -----------------------------
for c in cols:
    df = df.withColumn(c, col(c).cast(DoubleType()))

df = df.dropna(subset=cols)

for c in cols:
    df = df.filter(~isnan(col(c)))

print("✅ Data Cleaned")

# -----------------------------
# LOAD MODEL
# -----------------------------
model = PipelineModel.load(
    "hdfs://localhost:9000/rainfall_project/best_model"
)

print("✅ Model Loaded")

# -----------------------------
# PREDICTIONS
# -----------------------------
predictions = model.transform(df)

print("⚡ Predictions Generated:", predictions.count())

# -----------------------------
# DEBUG SAMPLE
# -----------------------------
predictions.select(
    "gpm_rainfall",
    "era5_rainfall",
    "rainfall_lag1",
    "prediction"
).show(10, False)

# -----------------------------
# EXTRACT PROBABILITY
# -----------------------------
predictions = predictions \
    .withColumn("probability_array", vector_to_array("probability")) \
    .withColumn("extreme_rain_probability", col("probability_array")[1])

# -----------------------------
# FINAL OUTPUT
# -----------------------------
final_df = predictions.select(
    "date",
    "district",
    "state",
    "extreme_rain_probability",
    col("prediction").alias("risk_label")
)

final_df.show(10)

# -----------------------------
# WRITE TO MONGODB 
# -----------------------------
final_df.write \
.format("mongodb") \
.mode("overwrite") \
.option("spark.mongodb.write.connection.uri", "mongodb://127.0.0.1:27017") \
.option("spark.mongodb.write.database", "rainfall") \
.option("spark.mongodb.write.collection", "predictions") \
.save()

print("✅ Written to MongoDB")

# -----------------------------
# SAVE TO HDFS
# -----------------------------
final_df.write.mode("overwrite") \
    .option("header", True) \
    .csv("hdfs://localhost:9000/rainfall_project/predictions_output")

print("💾 Predictions saved to HDFS")

spark.stop()