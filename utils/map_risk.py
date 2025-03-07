import pandas as pd
import geopandas as gpd
import folium
import branca
from streamlit_folium import folium_static

from utils.helpers import map_english_regions

def find_high_increase_regions(df, kpi_column):
    """Finds regions where predictions in 2025 are higher than actuals in 2024 and sorts them by increase."""
    actuals_2024 = df[(df['year'].dt.year == 2023) & (df['type'] == 'Actual')].set_index('region')[kpi_column]
    predictions_2025 = df[(df['year'].dt.year == 2025) & (df['type'] == 'Prediction')].set_index('region')[kpi_column]

    increase_df = (predictions_2025 - actuals_2024).dropna()
    high_regions = increase_df[increase_df > 0].sort_values(ascending=False).reset_index()

    return high_regions


def create_highrisk_map():
    # Load GeoJSON data
    geo_data = gpd.read_file("data/map/fi.json")
    geo_data['name'] = geo_data['name'].apply(map_english_regions)

    arrests_df = pd.read_csv("data/clean/arrests_forecast.csv", parse_dates=['year'])
    high_arrests_regions = find_high_increase_regions(arrests_df, 'arrests')

    merged = geo_data.merge(high_arrests_regions, left_on="name", right_on="region", how="left")

    # Creating a choropleth map
    m = folium.Map(location=[64.0, 26.0], zoom_start=5.4)
    
    colormap = branca.colormap.LinearColormap(
        vmin=merged["arrests"].min(),  # Minimum arrests in the data
        vmax=merged["arrests"].max(),  # Maximum arrests in the data
        colors=["#ffcccc", "#ff6666", "#ff3333", "#cc0000", "#990000"],  # Light to dark red
        caption="High risk regions",
    )

    popup = folium.GeoJsonPopup(
        fields=["name", "arrests"],
        aliases=["Region:", "Predicted arrests:"],
        localize=True,
        labels=True,
        style="""
            background-color: #FFFACD;
            border: 1px solid #FFD700;
            border-radius: 5px;
            font-family: Arial, sans-serif;
            font-size: 12px;
            padding: 5px;
        """,
    )

    tooltip = folium.GeoJsonTooltip(
        fields=["name", "arrests"],
        aliases=["Region:", "Predicted arrests:"],
        localize=True,
        sticky=False,
        labels=True,
        style="""
            background-color: #F0EFEF;
            border: 1px solid black;
            border-radius: 3px;
            font-family: Arial, sans-serif;
            font-size: 12px;
            padding: 5px;
        """,
        max_width=800,
    )

    folium.GeoJson(
        merged,
        style_function=lambda x: {
            "fillColor": colormap(x["properties"]["arrests"])
            if x["properties"]["arrests"] is not None
            else "transparent",
            "color": "black",
            "fillOpacity": 0.4,
        },
        tooltip=tooltip,
        popup=popup,
    ).add_to(m)

    colormap.add_to(m)

    return m
