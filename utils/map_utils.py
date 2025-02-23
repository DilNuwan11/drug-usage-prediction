import pandas as pd
import geopandas as gpd
import folium
import branca
from streamlit_folium import folium_static

from utils.helpers import map_finnish_regions

def create_folium_map(year):
    # Load GeoJSON data
    geo_data = gpd.read_file("./data/map/fi.json")

    # Load the CSV data
    df = pd.read_csv("./data/clean/Reported_drug_usage_by_regions.csv")
    df.drop(columns=['Unnamed: 0', 'KOKO MAA'], inplace=True)

    # Unpivot the dataframe
    df_melted = pd.melt(df, id_vars=['year'], 
                        value_vars=[
                            "Uusimaa",
                            "Varsinais-Suomi",
                            "Satakunta",
                            "Kanta-Häme",
                            "Pirkanmaa",
                            "Päijät-Häme",
                            "Kymenlaakso",
                            "Etelä-Karjala",
                            "Etelä-Savo",
                            "Pohjois-Savo",
                            "Pohjois-Karjala",
                            "Keski-Suomi",
                            "Etelä-Pohjanmaa",
                            "Pohjanmaa",
                            "Keski-Pohjanmaa",
                            "Pohjois-Pohjanmaa",
                            "Kainuu",
                            "Lappi",
                            "Ahvenanmaa"
                        ],
                        var_name='region', value_name='value')

    df_melted['region_en'] = df_melted['region'].apply(map_finnish_regions)

    merged = geo_data.merge(df_melted, left_on="name", right_on="region_en", how="left")

    year_data = merged[merged['year'] == year]

    # Creating a choropleth map
    m = folium.Map(location=[64.0, 26.0], zoom_start=5.4)
    
    colormap = branca.colormap.LinearColormap(
        vmin=year_data["value"].min(),  # Minimum value in the data
        vmax=year_data["value"].max(),  # Maximum value in the data
        colors=["#ffcccc", "#ff6666", "#ff3333", "#cc0000", "#990000"],  # Light to dark red
        caption="Reported Drug Usage for Finnish Regions",
    )

    popup = folium.GeoJsonPopup(
        fields=["name", "value"],
        aliases=["Region:", "Reported drug usage:"],
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
        fields=["name", "value"],
        aliases=["Region:", "Reported drug usage:"],
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
        year_data,
        style_function=lambda x: {
            "fillColor": colormap(x["properties"]["value"])
            if x["properties"]["value"] is not None
            else "transparent",
            "color": "black",
            "fillOpacity": 0.4,
        },
        tooltip=tooltip,
        popup=popup,
    ).add_to(m)

    colormap.add_to(m)

    return m