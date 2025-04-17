import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ✅ Set layout FIRST before any other Streamlit command
st.set_page_config(layout="wide")

# Sidebar Config
with st.sidebar:
    st.title("⚙️ Settings")

    
    selected_charts = st.multiselect(
        "Select Visualizations to Display:",
        [
            "Medal Choropleth",
            "Medal Leaderboard",
            "Stacked Medal Bar Chart",
            "Avg Revenue vs Avg Earnings Scatter",
            "Financial Power Score Map"
        ],
        default=[
            "Medal Choropleth",
            "Medal Leaderboard",
            "Avg Revenue vs Avg Earnings Scatter"
        ]
    )



st.title("🌍 Global Financial Olympics Dashboard")

# Load data and clean
@st.cache_data
def load_and_clean_data():
    df = pd.read_csv("country_metrics_medals.csv")
    df.columns = df.columns.str.strip()

    country_replacements = {
        "USA": "United States",
        "UK": "United Kingdom",
        "UAE": "United Arab Emirates",
        "Korea, South": "South Korea",
        "Russian Federation": "Russia",
        "Iran (Islamic Republic of)": "Iran"
    }

    num_cols = [
        "Gold", "Silver", "Bronze", "Total",
        "Avg_Revenue", "Avg_Earnings", "Avg_MarketCap", "Financial_Power_Score", "Companies"
    ]

    df["Country"] = df["Country"].replace(country_replacements).str.strip().str.title()
    df.fillna(0, inplace=True)

    for col in num_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    # Group by Country and aggregate
    df = df.groupby("Country", as_index=False).agg({
        col: "sum" if col in ["Gold", "Silver", "Bronze", "Total", "Companies"] else "mean"
        for col in num_cols
    })

    return df

summary_df = load_and_clean_data()
medal_df = summary_df.copy()

# Metric selector for medal choropleth
metric = st.selectbox("Select Medal Type", ["Total", "Gold", "Silver", "Bronze"])
medal_df[metric] = pd.to_numeric(medal_df[metric], errors='coerce')

# Filter UI
with st.sidebar:
    st.header("🔍 Medal Filters")
    name_filter = st.text_input("Search by country name:")
    min_amount = st.number_input(f"Minimum {metric} count", min_value=0, value=0)

# Apply filters
filtered_df = medal_df.copy()
if name_filter:
    filtered_df = filtered_df[filtered_df["Country"].str.contains(name_filter, case=False)]
filtered_df = filtered_df[filtered_df[metric] >= min_amount]
filtered_df["Rank"] = filtered_df[metric].rank(method="min", ascending=False).astype("Int64")
filtered_df = filtered_df.sort_values(by=metric, ascending=False)

if "Medal Choropleth" in selected_charts:
    st.subheader(f"🗺️ {metric} Medals by Country")
    map_fig = px.choropleth(
        filtered_df,  # ✅ Use filtered data so zeroes don't flatten the scale
        locations="Country",
        locationmode="country names",
        color=metric,
        hover_name="Country",
        title=f"{metric} Medals by Country",
        color_continuous_scale="YlOrRd",
        hover_data={
            "Gold": ":,.0f",
            "Silver": ":,.0f",
            "Bronze": ":,.0f",
            "Total": ":,.0f",
            "Companies": True,
            "Avg_Revenue": ":,.0f",
            "Avg_Earnings": ":,.0f",
            "Avg_MarketCap": ":,.0f"
        }
    )
    st.plotly_chart(map_fig, use_container_width=True)


if "Medal Leaderboard" in selected_charts:
    st.subheader(f"🏅 {metric} Ranking")
    st.dataframe(
        filtered_df[["Rank", "Country", "Gold", "Silver", "Bronze", "Total"]],
        use_container_width=True
    )

if "Avg Revenue vs Avg Earnings Scatter" in selected_charts:
    st.subheader("📈 Avg Revenue vs Avg Earnings per Country")
    scatter_fig = px.scatter(
        summary_df,
        x="Avg_Revenue",
        y="Avg_Earnings",
        size="Companies",
        color="Country",
        hover_name="Country",
        title="Avg Revenue vs Avg Earnings (Bubble = Company Count)",
        labels={
            "Avg_Revenue": "Avg Revenue (USD)",
            "Avg_Earnings": "Avg Earnings (USD)"
        },
        hover_data={
            "Avg_Revenue": ":,.0f",
            "Avg_Earnings": ":,.0f",
            "Avg_MarketCap": ":,.0f",
            "Companies": True,
            "Gold": True,
            "Silver": True,
            "Bronze": True,
            "Total": True
        }
    )
    st.plotly_chart(scatter_fig, use_container_width=True)

if "Financial Power Score Map" in selected_charts:
    st.subheader("🌍 Financial Power Score by Country")
    map_fig = px.choropleth(
        summary_df,
        locations="Country",
        locationmode="country names",
        color="Financial_Power_Score",
        hover_name="Country",
        title="Financial Power Score by Country",
        color_continuous_scale="Viridis",
        hover_data={
            "Financial_Power_Score": True,
            "Companies": True,
            "Avg_Revenue": ":,.0f",
            "Avg_Earnings": ":,.0f",
            "Avg_MarketCap": ":,.0f",
            "Gold": True,
            "Silver": True,
            "Bronze": True,
            "Total": True
        }
    )
    st.plotly_chart(map_fig, use_container_width=True)

if "Stacked Medal Bar Chart" in selected_charts:
    st.subheader("🎖️ Gold, Silver, Bronze Breakdown by Country")
    stacked_fig = go.Figure(data=[
        go.Bar(name='Gold', x=medal_df['Country'], y=medal_df['Gold']),
        go.Bar(name='Silver', x=medal_df['Country'], y=medal_df['Silver']),
        go.Bar(name='Bronze', x=medal_df['Country'], y=medal_df['Bronze'])
    ])
    stacked_fig.update_layout(
        barmode='stack',
        title="Medal Breakdown by Country",
        xaxis_title="Country",
        yaxis_title="Medal Count",
        xaxis_tickangle=-45
    )
    st.plotly_chart(stacked_fig, use_container_width=True)