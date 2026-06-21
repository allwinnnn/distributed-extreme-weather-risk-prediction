# Dataset Information

## Overview

This project integrates multiple climate and environmental datasets to build a distributed machine learning framework for extreme rainfall risk prediction across India.

The datasets contain rainfall observations, satellite-derived precipitation measurements, weather variables, and climate reanalysis data. These heterogeneous data sources are combined through a multimodal ETL pipeline using Hadoop and Apache Spark.

---

# Datasets Used

## 1. IMD Rainfall Dataset

### Source
Indian Meteorological Department (IMD) Rainfall Dataset

### Description
Provides district-level rainfall observations used as the primary rainfall reference dataset.

### Features

- District Name
- State Name
- Date
- Rainfall Measurements

### Usage

Used for:

- Rainfall target generation
- Historical rainfall analysis
- Extreme rainfall event identification

---

## 2. NASA GPM Satellite Dataset

### Source

NASA Global Precipitation Measurement (GPM)

### Format

NetCDF (.nc4)

### Description

Provides satellite-derived precipitation estimates with high spatial coverage.

### Usage

Used for:

- Satellite rainfall extraction
- District-level precipitation estimation
- Multimodal rainfall feature generation

---

## 3. ERA5 Reanalysis Rainfall Dataset

### Source

ECMWF ERA5 Reanalysis

### Format

NetCDF (.nc)

### Description

Provides atmospheric reanalysis rainfall measurements derived from weather forecasting models and observational data.

### Usage

Used for:

- Rainfall feature extraction
- Climate trend analysis
- District-level rainfall aggregation

---

## 4. ERA5 Weather Dataset

### Source

ECMWF ERA5 Reanalysis

### Format

NetCDF (.nc)

### Weather Variables

- Temperature
- Relative Humidity
- Wind Speed

### Usage

Used for:

- Weather feature extraction
- Climate condition analysis
- Machine learning feature generation

---

# Data Processing Workflow

The raw datasets undergo multiple preprocessing stages before being used for machine learning.

### IMD Processing

IMD Dataset

↓

Rainfall Cleaning

↓

District Normalization

↓

Date Standardization

↓

clean_indiafinal.csv

### NASA GPM Processing

GPM NetCDF Files

↓

Rainfall Extraction

↓

Geospatial Mapping

↓

District Aggregation

↓

clean_gpm.csv

### ERA5 Rainfall Processing

ERA5 Precipitation Data

↓

Rainfall Extraction

↓

District Mapping

↓

Aggregation

↓

clean_era5.csv

### ERA5 Weather Processing

ERA5 Weather Data

↓

Temperature Extraction

↓

Humidity Extraction

↓

Wind Speed Extraction

↓

clean_weather.csv

---

# Final Multimodal Dataset

The processed datasets are integrated using Apache Spark.

Final Features:

- gpm_rainfall
- era5_rainfall
- temperature
- humidity
- wind_speed
- rainfall_lag1

Target Variable:

- extreme_rain

Where:

- 1 = Extreme Rainfall Event
- 0 = Normal Rainfall Event

---

# Storage

Raw and processed datasets are stored and processed using:

- Hadoop HDFS
- Apache Spark

Prediction outputs are stored in:

- MongoDB

---

# Notes

The original datasets are not included in this repository due to their large size and licensing restrictions.

Users can download the datasets from their respective official sources and execute the preprocessing pipeline provided in this repository.

---

# Research Objective

To develop a scalable multimodal climate analytics framework capable of predicting extreme rainfall events using distributed data processing, machine learning, and geospatial analysis.
