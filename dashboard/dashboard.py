import streamlit as st
import pandas as pd
from pymongo import MongoClient
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# =========================================================
# PAGE CONFIG
# =========================================================
st.set_page_config(
    page_title="Rainfall Risk Dashboard",
    layout="wide"
)

st.title("🌧️ Extreme Rainfall Prediction Dashboard")
st.markdown(
    """
    Real-time analytical dashboard for monitoring
    extreme rainfall risks across Indian districts
    using Machine Learning + Big Data Analytics.
    """
)

# =========================================================
# LOAD DATA
# =========================================================
@st.cache_data
def load_data():

    client = MongoClient("mongodb://127.0.0.1:27017")

    db = client["rainfall"]

    collection = db["predictions"]

    data = list(collection.find())

    df = pd.DataFrame(data)

    # FIX OBJECT ID ISSUE
    df["_id"] = df["_id"].astype(str)

    # DATE
    df["date"] = pd.to_datetime(df["date"])

    return df


df = load_data()

# =========================================================
# DISTRICT COORDINATES
# =========================================================
district_coords = {

    "ADILABAD": [19.67, 78.53],
    "AGRA": [27.18, 78.01],
    "AHMADABAD": [23.03, 72.58],
    "AHMEDNAGAR": [19.09, 74.74],
    "AIZAWL": [23.72, 92.72],
    "AJMER": [26.45, 74.64],
    "AKOLA": [20.70, 77.02],
    "ALIGARH": [27.89, 78.08],
    "ALIRAJPUR": [22.30, 74.35],
    "BENGALURU": [12.97, 77.59],
    "BHOPAL": [23.25, 77.41],
    "CHENNAI": [13.08, 80.27],
    "ERNAKULAM": [9.98, 76.28],
    "HYDERABAD": [17.38, 78.48],
    "JAIPUR": [26.91, 75.78],
    "KOZHIKODE": [11.25, 75.78],
    "KOLKATA": [22.57, 88.36],
    "LUCKNOW": [26.84, 80.94],
    "MADURAI": [9.92, 78.11],
    "MUMBAI": [19.07, 72.87],
    "PATNA": [25.59, 85.13],
    "PUNE": [18.52, 73.85],
    "SURAT": [21.17, 72.83],
    "THIRUVANANTHAPURAM": [8.52, 76.93],
    "VIJAYAWADA": [16.50, 80.64],
    "VISAKHAPATNAM": [17.68, 83.21]
}

# =========================================================
# MAP LATITUDE LONGITUDE
# =========================================================
df["latitude"] = df["district"].map(
    lambda x: district_coords.get(
        str(x).upper(),
        [np.nan, np.nan]
    )[0]
)

df["longitude"] = df["district"].map(
    lambda x: district_coords.get(
        str(x).upper(),
        [np.nan, np.nan]
    )[1]
)

# =========================================================
# SIDEBAR FILTERS
# =========================================================
st.sidebar.header("🔎 Dashboard Filters")

states = st.sidebar.multiselect(
    "Select State",
    sorted(df["state"].dropna().unique()),
    default=sorted(df["state"].dropna().unique())
)

districts = st.sidebar.multiselect(
    "Select District",
    sorted(df["district"].dropna().unique()),
    default=sorted(df["district"].dropna().unique())
)

date_range = st.sidebar.date_input(
    "Select Date Range",
    [
        df["date"].min(),
        df["date"].max()
    ]
)

# =========================================================
# FILTER DATA
# =========================================================
filtered_df = df[
    (df["state"].isin(states)) &
    (df["district"].isin(districts)) &
    (df["date"] >= pd.to_datetime(date_range[0])) &
    (df["date"] <= pd.to_datetime(date_range[1]))
]

# =========================================================
# KPI METRICS
# =========================================================
st.subheader("📊 Key Metrics")

col1, col2, col3, col4, col5 = st.columns(5)

col1.metric(
    "Total Records",
    len(filtered_df)
)

col2.metric(
    "Extreme Events",
    int((filtered_df["risk_label"] == 1).sum())
)

col3.metric(
    "Average Risk",
    round(
        filtered_df["extreme_rain_probability"].mean(),
        3
    )
)

col4.metric(
    "Maximum Risk",
    round(
        filtered_df["extreme_rain_probability"].max(),
        3
    )
)

col5.metric(
    "States Covered",
    filtered_df["state"].nunique()
)

# =========================================================
# TIME SERIES
# =========================================================
st.subheader("📈 Rainfall Risk Trend Over Time")

ts = filtered_df.groupby("date")[
    "extreme_rain_probability"
].mean().reset_index()

fig_ts = px.line(
    ts,
    x="date",
    y="extreme_rain_probability",
    title="Average Rainfall Risk Trend",
    markers=True
)

st.plotly_chart(fig_ts, use_container_width=True)

# =========================================================
# RISK DISTRIBUTION
# =========================================================
st.subheader("📊 Probability Distribution")

fig_hist = px.histogram(
    filtered_df,
    x="extreme_rain_probability",
    nbins=40,
    color="risk_label",
    title="Extreme Rainfall Probability Distribution"
)

st.plotly_chart(fig_hist, use_container_width=True)

# =========================================================
# STATE RISK
# =========================================================
st.subheader("🌍 State Wise Rainfall Risk")

state_risk = (
    filtered_df.groupby("state")
    ["extreme_rain_probability"]
    .mean()
    .reset_index()
    .sort_values(
        by="extreme_rain_probability",
        ascending=False
    )
)

fig_state = px.bar(
    state_risk,
    x="state",
    y="extreme_rain_probability",
    color="extreme_rain_probability",
    title="Average Risk By State"
)

st.plotly_chart(fig_state, use_container_width=True)

# =========================================================
# TOP DISTRICTS
# =========================================================
st.subheader("🔥 Top High Risk Districts")

top_districts = (
    filtered_df.groupby("district")
    ["extreme_rain_probability"]
    .mean()
    .reset_index()
    .sort_values(
        by="extreme_rain_probability",
        ascending=False
    )
    .head(15)
)

fig_top = px.bar(
    top_districts,
    x="district",
    y="extreme_rain_probability",
    color="extreme_rain_probability",
    title="Top 15 High Risk Districts"
)

st.plotly_chart(fig_top, use_container_width=True)

# =========================================================
# EXTREME EVENT FILTER
# =========================================================
extreme_df = filtered_df[
    filtered_df["risk_label"] == 1
]

# =========================================================
# EXTREME MAP
# =========================================================
st.subheader("🗺️ Extreme Rainfall Hotspots")

map_df = extreme_df.dropna(
    subset=["latitude", "longitude"]
)

fig_map = px.scatter_mapbox(
    map_df,
    lat="latitude",
    lon="longitude",
    color="extreme_rain_probability",
    size="extreme_rain_probability",
    hover_name="district",
    hover_data=[
        "state",
        "extreme_rain_probability"
    ],
    zoom=3.5,
    height=700,
    color_continuous_scale="Turbo"
)

fig_map.update_layout(
    mapbox_style="carto-darkmatter",
    margin={"r":0, "t":0, "l":0, "b":0}
)

st.plotly_chart(fig_map, use_container_width=True)

# =========================================================
# EXTREME EVENTS TABLE
# =========================================================
st.subheader("🚨 Extreme Rainfall Alerts")

alerts = filtered_df[
    filtered_df["extreme_rain_probability"] > 0.7
]

if len(alerts) > 0:

    st.error(
        f"{len(alerts)} High Risk Events Detected"
    )

    st.dataframe(
        alerts.sort_values(
            "extreme_rain_probability",
            ascending=False
        )[
            [
                "date",
                "district",
                "state",
                "extreme_rain_probability",
                "risk_label"
            ]
        ].head(20)
    )

else:

    st.success("No High Risk Events Detected")

# =========================================================
# HEATMAP
# =========================================================
st.subheader("🌡️ State vs Risk Heatmap")

heatmap_df = (
    filtered_df.groupby(["state", "risk_label"])
    .size()
    .reset_index(name="count")
)

fig_heat = px.density_heatmap(
    heatmap_df,
    x="state",
    y="risk_label",
    z="count",
    title="State vs Extreme Risk Density"
)

st.plotly_chart(fig_heat, use_container_width=True)

# =========================================================
# PIE CHART
# =========================================================
st.subheader("🥧 Extreme vs Normal Rainfall")

pie_df = filtered_df["risk_label"] \
    .value_counts() \
    .reset_index()

pie_df.columns = [
    "Risk",
    "Count"
]

pie_df["Risk"] = pie_df["Risk"].replace({
    0: "Normal",
    1: "Extreme"
})

fig_pie = px.pie(
    pie_df,
    names="Risk",
    values="Count",
    title="Rainfall Event Distribution"
)

st.plotly_chart(fig_pie, use_container_width=True)

# =========================================================
# AI INSIGHTS
# =========================================================
st.subheader("🧠 Insights")

total_extreme = len(extreme_df)

top_state = (
    state_risk.iloc[0]["state"]
    if len(state_risk) > 0
    else "N/A"
)

top_district = (
    top_districts.iloc[0]["district"]
    if len(top_districts) > 0
    else "N/A"
)

max_prob = round(
    filtered_df["extreme_rain_probability"].max(),
    3
)

avg_prob = round(
    filtered_df["extreme_rain_probability"].mean(),
    3
)

st.info(f"""
• Total Extreme Rainfall Events Predicted: {total_extreme}

• Highest Risk State: {top_state}

• Highest Risk District: {top_district}

• Maximum Predicted Probability: {max_prob}

• Average Predicted Probability: {avg_prob}

• Random Forest model achieved best performance
with AUC score ≈ 0.775.

• Monsoon months (June–September) dominate
extreme rainfall occurrence patterns.

• Previous day rainfall (lag feature) significantly
improved prediction quality.

• Weather + satellite rainfall fusion improved
prediction robustness.
""")

# =========================================================
# RAW DATA
# =========================================================
st.subheader("📄 Prediction Data")

st.dataframe(
    filtered_df.head(100)
)