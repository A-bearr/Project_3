import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(layout="wide")
st.title("🌍 Global Financial Olympics")

# Load and clean data
medal_df = pd.read_csv("country_metrics_medals.csv")
medal_df.columns = medal_df.columns.str.strip()

# Select metric
metric = st.selectbox("Select Medal Type", ["Total", "Gold", "Silver", "Bronze"])
medal_df[metric] = pd.to_numeric(medal_df[metric], errors='coerce')

# Filters UI
with st.sidebar:
    st.header("🔍 Filter Options")

    # Alphabetical filter
    name_filter = st.text_input("Search by country name:")

    # Amount filter (min threshold)
    min_amount = st.number_input(f"Minimum {metric} count", min_value=0, value=0)

# Apply filters
filtered_df = medal_df.copy()
if name_filter:
    filtered_df = filtered_df[filtered_df["Country"].str.contains(name_filter, case=False)]

filtered_df = filtered_df[filtered_df[metric] >= min_amount]

# Add ranking
filtered_df["Rank"] = filtered_df[metric].rank(method="min", ascending=False).astype("Int64")
filtered_df = filtered_df.sort_values(by=metric, ascending=False)

# Choropleth
st.subheader(f"{metric} Medals by Country")
fig = px.choropleth(
    filtered_df,
    locations="Country",
    locationmode="country names",
    color=metric,
    hover_name="Country",
    color_continuous_scale="YlOrRd"
)
st.plotly_chart(fig, use_container_width=True)

# Leaderboard with dynamic heading
icons = {"Gold": "🥇", "Silver": "🥈", "Bronze": "🥉", "Total": "🏅"}
st.subheader(f"{icons.get(metric, '')} {metric} Ranking")

# Display leaderboard table
st.dataframe(
    filtered_df[["Rank", "Country", "Gold", "Silver", "Bronze", "Total"]],
    use_container_width=True
)
