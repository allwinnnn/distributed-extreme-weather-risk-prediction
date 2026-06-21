# Distributed Multimodal Extreme Weather Risk Prediction Using Hadoop and Apache Spark

## Overview

Extreme rainfall events during the Indian monsoon season frequently lead to floods, infrastructure damage, agricultural losses, and disruptions to daily life. Traditional weather analytics systems often struggle to process the large volumes of heterogeneous climate data generated from satellites, reanalysis datasets, and meteorological observations.

This project presents a distributed multimodal climate analytics framework that combines Hadoop, Apache Spark, Machine Learning, MongoDB, and Streamlit to build a scalable extreme rainfall risk prediction system.

The framework integrates multiple environmental datasets including Indian rainfall observations, NASA GPM satellite precipitation measurements, ERA5 rainfall reanalysis data, and atmospheric weather variables such as temperature, humidity, and wind speed. Apache Spark is used for large-scale ETL operations, feature engineering, distributed machine learning, and prediction generation, while MongoDB and Streamlit provide scalable storage and interactive visualization capabilities.

---

# Problem Statement

Accurate prediction of extreme rainfall events is essential for:

- Flood preparedness
- Disaster management
- Agricultural planning
- Infrastructure protection
- Climate risk monitoring

Most existing systems focus on individual climate datasets and lack scalable distributed architectures capable of processing multimodal weather information.

This project addresses these limitations by developing a distributed end-to-end rainfall prediction pipeline that integrates multiple environmental data sources and machine learning models within a big data ecosystem.

---

# Project Objectives

- Build a distributed climate analytics framework using Hadoop and Apache Spark.
- Integrate multimodal environmental datasets from multiple sources.
- Perform large-scale ETL and preprocessing operations.
- Engineer meaningful climate features for rainfall prediction.
- Train and evaluate machine learning models using Spark MLlib.
- Store prediction outputs in MongoDB.
- Develop an interactive Streamlit dashboard for climate analytics and monitoring.
- Enable district-level rainfall risk assessment across India.

---

# Technology Stack

## Big Data Technologies

- Hadoop HDFS
- Apache Spark
- Spark SQL
- Spark MLlib

## Machine Learning

- Logistic Regression
- Decision Tree
- Random Forest
- Gradient Boosted Trees (GBT)

## Data Processing

- Pandas
- NumPy
- PySpark
- GeoPandas

## Databases

- MongoDB

## Visualization

- Streamlit
- Plotly
- Plotly Mapbox

## Programming Language

- Python

---

# Data Sources

The framework integrates four major climate datasets.

## 1. IMD Rainfall Dataset

Source:
Indian Meteorological Department Rainfall Dataset (Kaggle)

Contains:

- District-wise rainfall observations
- Daily rainfall measurements
- Historical monsoon data

---

## 2. NASA GPM Satellite Data

Source:
Global Precipitation Measurement (GPM)

Contains:

- Satellite-derived rainfall estimates
- Spatial precipitation observations
- High-resolution rainfall measurements

Format:

- NetCDF (.nc4)

---

## 3. ERA5 Reanalysis Rainfall Dataset

Source:
ECMWF ERA5 Reanalysis

Contains:

- Total precipitation measurements
- Historical climate observations
- Atmospheric reanalysis variables

Format:

- NetCDF (.nc)

---

## 4. ERA5 Weather Dataset

Contains:

- Temperature
- Humidity
- Wind Speed

Format:

- NetCDF (.nc)

---

# System Architecture

The system consists of six major layers:

1. Data Collection Layer
2. Data Preprocessing Layer
3. Distributed Storage Layer
4. Spark ETL and Machine Learning Layer
5. Prediction Storage Layer
6. Interactive Dashboard Layer

---

# Complete Data Processing Pipeline

## Stage 1 — IMD Rainfall Processing

### Input

IMD Rainfall Dataset

### Files

- preprocess_rainfall.py
- cleanindia_processing.py

### Workflow

IMD Rainfall CSV

↓

preprocess_rainfall.py

↓

processed_rainfall_final.csv

↓

cleanindia_processing.py

↓

clean_indiafinal.csv

### Processing Performed

- District normalization
- Date standardization
- Missing value handling
- Invalid row removal
- Rainfall column standardization
- Target rainfall generation

---

## Stage 2 — NASA GPM Satellite Processing

### Input

NASA GPM NetCDF Files (.nc4)

### Files

- preprocess_gpm.py
- districtpreprocessing.py
- gpmfinalpreprocessing.py

### Workflow

GPM .nc4 Files

↓

preprocess_gpm.py

↓

gpm_processed.csv

↓

districtpreprocessing.py

↓

gpm_district_final.csv

↓

gpmfinalpreprocessing.py

↓

clean_gpm.csv

### Processing Performed

- NetCDF rainfall extraction
- Latitude-longitude conversion
- Geospatial district mapping
- District aggregation
- Rainfall normalization
- Satellite data cleaning

---

## Stage 3 — ERA5 Rainfall Processing

### Input

ERA5 Precipitation Dataset

### Files

- preprocess_era5_tp.py
- era5district_preprocess.py
- era5districtpreprocessing.py

### Workflow

ERA5 Rainfall Data

↓

preprocess_era5_tp.py

↓

era5_processed.csv

↓

era5district_preprocess.py

↓

era5_district_final.csv

↓

era5districtpreprocessing.py

↓

clean_era5.csv

### Processing Performed

- Precipitation extraction
- Grid-to-district mapping
- Spatial aggregation
- Duplicate removal
- Climate data normalization

---

## Stage 4 — Weather Parameter Processing

### Input

ERA5 Weather Dataset

### Files

- weather_preprocess.py
- clean_weather.py
- cleanweather.py

### Workflow

ERA5 Weather Data

↓

weather_preprocess.py

↓

weather_district.csv

↓

clean_weather.py

↓

weather_district_clean.csv

↓

cleanweather.py

↓

clean_weather.csv

### Processing Performed

- Temperature extraction
- Humidity extraction
- Wind speed extraction
- District-level mapping
- Missing value handling
- Duplicate removal

---

# Hadoop Distributed Storage

After preprocessing, all cleaned datasets are stored in Hadoop Distributed File System (HDFS).

Stored Datasets:

- clean_indiafinal.csv
- clean_gpm.csv
- clean_era5.csv
- clean_weather.csv

Benefits:

- Distributed storage
- Fault tolerance
- Scalability
- High-volume climate data processing

---

# Apache Spark ETL Pipeline

## File

spark_etl.py

Spark performs:

- Distributed CSV loading from HDFS
- District normalization
- Date standardization
- Monsoon filtering
- Duplicate aggregation
- Dataset joins
- Missing value handling

### Monsoon Filtering

Only records from:

- June
- July
- August
- September

were retained to improve prediction relevance and reduce seasonal noise.

---

# Feature Engineering

## File

feature_engineering.py

### Spark Operations

- Distributed filtering
- Window functions
- Lag feature generation
- Feature preparation

### Generated Feature

rainfall_lag1

(previous day's rainfall)

### Final Feature Set

- gpm_rainfall
- era5_rainfall
- temperature
- humidity
- wind_speed
- rainfall_lag1

These features capture both spatial and temporal rainfall patterns.

---

# Label Creation

## File

label_creation.py

To perform supervised learning, binary labels were generated using a percentile-based thresholding strategy.

### Method

95th Percentile Threshold

Label:

- 1 → Extreme Rainfall Event
- 0 → Normal Rainfall Event

This allows the system to identify high-risk rainfall events automatically.

---

# Distributed Machine Learning Pipeline

## File

train_multiple_models.py

### Models Evaluated

1. Logistic Regression
2. Decision Tree
3. Random Forest
4. Gradient Boosted Trees (GBT)

### Spark ML Operations

- VectorAssembler
- StandardScaler
- Weighted Classification
- Distributed Training
- Distributed Evaluation

### Train-Test Split

80 : 20

### Evaluation Metric

AUC-ROC

---

# Model Performance

| Model | AUC |
|---------|---------|
| Logistic Regression | 0.7368 |
| Decision Tree | 0.3158 |
| GBT | 0.7748 |
| Random Forest | 0.7753 |

### Best Model

Random Forest

The Random Forest classifier achieved the highest predictive performance and was selected as the final deployment model.

---

# Prediction Generation

## File

predict_final.py

The trained Random Forest model generates:

- Rainfall risk probability
- Extreme rainfall classification
- District-level predictions

Prediction outputs include:

- District
- State
- Date
- Extreme Rainfall Probability
- Risk Label

---

# MongoDB Integration

Prediction results are stored in MongoDB.

Collection:

predictions

Benefits:

- Flexible schema
- Fast querying
- Real-time analytics support
- Dashboard integration

---

# Interactive Streamlit Dashboard

## File

dashboard.py

The dashboard provides:

### Monitoring

- Real-time prediction visualization
- State-wise rainfall analysis
- District-wise rainfall analysis

### Analytics

- Rainfall probability distribution
- Temporal trend analysis
- Risk comparison across states
- High-risk district ranking

### Geospatial Intelligence

- Interactive hotspot maps
- Rainfall severity visualization
- District-level risk monitoring

### AI Insights

- Extreme rainfall statistics
- Risk summaries
- Monsoon trend analysis
- High-risk state identification

---

# Key Contributions

- Distributed multimodal climate data integration
- Hadoop-based scalable storage
- Spark-based ETL and machine learning pipeline
- Satellite and weather data fusion
- District-level rainfall risk prediction
- MongoDB-powered prediction storage
- Interactive climate analytics dashboard
- Geospatial hotspot visualization

---

# Future Enhancements

- Deep Learning Integration
- Real-Time Streaming Analytics
- Apache Kafka Integration
- IoT Weather Sensor Support
- Cloud Deployment
- Flood Prediction System
- GIS-Based Advanced Analytics

---

# Repository Structure

text distributed-extreme-weather-risk-prediction/ │ ├── data/ ├── preprocessing/ ├── spark_pipeline/ ├── dashboard/ ├── results/ ├── report/ ├── geojson/ ├── README.md └── requirements.txt 

---

# Authors

Akhil Sebastian  
M.Tech Data Science  
Amrita Vishwa Vidyapeetham

Allwin Suresh  
M.Tech Data Science  
Amrita Vishwa Vidyapeetham
