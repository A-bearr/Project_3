from flask import Flask, render_template, jsonify
import pandas as pd
import json

app = Flask(__name__)

# Load the merged company data
df = pd.read_csv("Merged_Company_Financial.csv")

# Load the coordinates
with open("world_countries_coordinates.json") as f:
    country_coords = json.load(f)

# Column mapping for cleaner access
metric_columns = {
    "Revenue": ("Revenue", "Revenue_Rank"),
    "Earnings": ("Earnings", "Earnings_Rank"),
    "Market Cap": ("Market_Cap", "MarketCap_Rank")
}

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/metric/<metric>")
def metric_data(metric):
    df = pd.read_csv("Merged_Company_Financial.csv")
    with open("world_countries_coordinates.json", "r") as f:
        coordinates = json.load(f)

    # Rename to match coordinates key
    df["Country"] = df["Country"].replace({"Taiwan, Province of China": "Taiwan"})

    data = []
    
    for _, row in df.iterrows():
        country = row["Country"]
        coords = coordinates.get(country)
        if coords is None:
            continue

        if metric == "All":
            values = {
                "Revenue": row.get("Revenue"),
                "Earnings": row.get("Earnings"),
                "Market Cap": row.get("Market_Cap"),
            }
            ranks = {
                "Revenue": row.get("Revenue_Rank"),
                "Earnings": row.get("Earnings_Rank"),
                "Market Cap": row.get("MarketCap_Rank"),
            }

            if any(pd.isna(v) for v in values.values()):
                continue  # Skip if any are NaN

            data.append({
                "company": row["Name"],
                "ticker": row["Symbol"],
                "country": country,
               "lat": coords[0],
               "lon": coords[1],
                "values": values,
                "ranks": ranks
            })
        else:
            col_map = {
                "Revenue": ("Revenue", "Revenue_Rank"),
                "Earnings": ("Earnings", "Earnings_Rank"),
                "Market Cap": ("Market_Cap", "MarketCap_Rank")
            }

            if metric not in col_map:
                return jsonify({"error": "Invalid metric"}), 400

            val_col, rank_col = col_map[metric]
            value = row[val_col]
            rank = row[rank_col]

            if pd.isna(value) or pd.isna(rank):
                continue  # Skip bad data

            data.append({
                "company": row["Name"],
                "ticker": row["Symbol"],
                "country": country,
               "lat": coords[0],
               "lon": coords[1],
                "value": value,
                "rank": int(rank),
            })

    return jsonify(data)


if __name__ == "__main__":
    app.run(debug=True)
