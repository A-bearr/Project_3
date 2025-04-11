import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(layout="wide")
st.title("🌍 Global Financial Olympics")

# Load the medal tally data
medal_df = pd.read_csv("country_metrics_medals.csv")
medal_df.columns = medal_df.columns.str.strip()

# Metric selector
metric = st.selectbox("Select Medal Type", ["Total", "Gold", "Silver", "Bronze"])

# Ensure column is numeric
medal_df[metric] = pd.to_numeric(medal_df[metric], errors='coerce')

# Choropleth map
st.subheader(f"{metric} Medals by Country")
fig = px.choropleth(
    medal_df,
    locations="Country",
    locationmode="country names",
    color=metric,
    hover_name="Country",
    color_continuous_scale="YlOrRd"
)
st.plotly_chart(fig, use_container_width=True)

# Medal leaderboard
st.subheader("🏅 Medal Table")
st.dataframe(medal_df.sort_values(metric, ascending=False), use_container_width=True)
