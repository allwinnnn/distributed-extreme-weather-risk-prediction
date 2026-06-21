from pyspark.sql import SparkSession
from pyspark.sql.functions import when, col, isnan
from pyspark.sql.types import DoubleType

from pyspark.ml.feature import VectorAssembler, StandardScaler
from pyspark.ml.classification import (
    LogisticRegression,
    RandomForestClassifier,
    GBTClassifier,
    DecisionTreeClassifier
)
from pyspark.ml.evaluation import BinaryClassificationEvaluator
from pyspark.ml import Pipeline


spark = SparkSession.builder \
    .appName("Rainfall ML Training FINAL") \
    .config("spark.hadoop.fs.defaultFS", "hdfs://localhost:9000") \
    .getOrCreate()

spark.sparkContext.setLogLevel("ERROR")
print("🚀 Spark Started")

df = spark.read.csv(
    "hdfs://localhost:9000/rainfall_project/labeled_dataset",
    header=True,
    inferSchema=True
)

print("📊 Data Loaded")


features = [
    "gpm_rainfall",
    "era5_rainfall",
    "temperature",
    "humidity",
    "wind_speed",
    "rainfall_lag1"  
]

label = "extreme_rain"


for c in features:
    df = df.withColumn(c, col(c).cast(DoubleType()))


for c in features:
    df = df.filter(col(c).isNotNull())
    df = df.filter(~isnan(col(c)))

print("✅ Data Cleaned")


total = df.count()

class_counts = df.groupBy(label).count().collect()

count_0 = [r['count'] for r in class_counts if r[label] == 0][0]
count_1 = [r['count'] for r in class_counts if r[label] == 1][0]

weight_0 = total / (2 * count_0)
weight_1 = total / (2 * count_1)

df = df.withColumn(
    "classWeight",
    when(col(label) == 1, weight_1).otherwise(weight_0)
)

print("⚖️ Class weights added")


assembler = VectorAssembler(
    inputCols=features,
    outputCol="features"
)

scaler = StandardScaler(
    inputCol="features",
    outputCol="scaled_features" #(x − mean)/std
)


train, test = df.randomSplit([0.8, 0.2], seed=42)

print(f"Train: {train.count()} | Test: {test.count()}")


models = {
    "Logistic Regression": LogisticRegression(
        featuresCol="scaled_features",
        labelCol=label,
        weightCol="classWeight",
        maxIter=50
    ),
    "Random Forest": RandomForestClassifier(
        featuresCol="features",
        labelCol=label,
        weightCol="classWeight",   #  FIXED
        numTrees=120,
        maxDepth=10
    ),
    "Decision Tree": DecisionTreeClassifier(
        featuresCol="features",
        labelCol=label,
        weightCol="classWeight"    #  FIXED
    ),
    "GBT": GBTClassifier(
        featuresCol="features",
        labelCol=label,
        maxIter=40,
        maxDepth=5
    )
}


evaluator = BinaryClassificationEvaluator(
    labelCol=label,
    metricName="areaUnderROC"
)

results = {}
trained_models = {}


for name, model in models.items():
    print(f"\n🔹 Training {name}")

    if name == "Logistic Regression":
        pipeline = Pipeline(stages=[assembler, scaler, model])
    else:
        pipeline = Pipeline(stages=[assembler, model])

    fitted = pipeline.fit(train)
    predictions = fitted.transform(test)

    auc = evaluator.evaluate(predictions)

    results[name] = auc
    trained_models[name] = fitted

    print(f"✅ {name} AUC = {auc:.4f}")


best_model_name = max(results, key=results.get)
best_model = trained_models[best_model_name]

print("\n🏆 BEST MODEL:", best_model_name)
print("📈 BEST AUC:", results[best_model_name])

best_model.write().overwrite().save(
    "hdfs://localhost:9000/rainfall_project/best_model"
)

print("💾 Model Saved")

spark.stop()