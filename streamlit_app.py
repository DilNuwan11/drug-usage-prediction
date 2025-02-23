import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import geopandas as gpd
import folium
import branca

from utils.map_utils import create_folium_map
from streamlit_folium import folium_static

# Custom style for prettier plots
sns.set_style("whitegrid")  # Add gridlines with a clean style
plt.rcParams.update({
    "axes.facecolor": "#f9f9f9",  # Light background for contrast
    "axes.edgecolor": "#cccccc",
    "axes.linewidth": 1.2,
    "grid.color": "#dddddd",
    "font.size": 12,              # Larger font for readability
    "xtick.color": "#333333",
    "ytick.color": "#333333",
    "axes.titlesize": 14,
    "axes.labelsize": 12
})

st.set_page_config(
    page_title="Finland Drug Usage Dashboard",
    page_icon="💊",
    layout="wide",
    initial_sidebar_state="expanded")

make_map_responsive= """
 <style>
 [title~="st.iframe"] { width: 100%}
 </style>
"""
st.markdown(make_map_responsive, unsafe_allow_html=True)

tab1, tab2 = st.tabs(["Monitoring", "Prediction"])

with tab1:

    # Title of the dashboard
    st.title("Monitoring Drug Usage in Finland")

    # Creating a grid with three columns for the top section
    col1, col2, col3 = st.columns([1.5, 1.5, 1])

    # Chart 1: Number of deaths
    with col1:
        st.subheader("Number of deaths")
        fig1, ax1 = plt.subplots()
        x = [2018, 2019, 2020, 2021, 2022]
        y = [10, 20, 30, 35, 40]
        ax1.plot(x, y)
        st.pyplot(fig1)

        st.subheader("Drug Price Trends Over the Years")
        data = pd.read_csv("data/clean/Retail_drug_prices.csv")
        data["Year"] = data["Year"].astype(int)

        df = data.sort_values(by="Year")
        # List all drug columns (excluding 'Year')
        drug_options = list(df.columns[1:])  

        # Dropdown with two options: plot all drugs or mostly used drugs
        plot_option = st.selectbox("Select plot option:", ["All types of drugs", "Mostly used drugs"])

        fig2, ax2 = plt.subplots(figsize=(10, 5))

        if plot_option == "All types of drugs":
            # Plot every drug column available in the data
            for drug in drug_options:
                ax2.plot(df["Year"], df[drug], marker='o', linestyle='-', label=drug)
        elif plot_option == "Mostly used drugs":
            # Define the mostly used drugs: MDMA, Amphetamines, and both types of Cannabis
            mostly_used = ["ATS_MDMA (tablet)", "ATS_Amphetamine (gram)", "Cannabis_Resin (gram)", "Cannabis_Herbal (gram)"]
            for drug in mostly_used:
                if drug in df.columns:
                    ax2.plot(df["Year"], df[drug], marker='o', linestyle='-', label=drug)

        ax2.set_xticks(df["Year"])
        ax2.set_xticklabels(df["Year"], rotation=45)
        ax2.set_xlabel("Year")
        ax2.set_ylabel("Price (€)")
        ax2.set_title("Drug Price Trends Over Time")
        ax2.legend()
        ax2.grid(True)

        st.pyplot(fig2)

    # Center column with map
    with col2:
        st.subheader("Drug-related arrests by regions")

        df = pd.read_csv("./data/clean/Reported_drug_usage_by_regions.csv")

        # Select year
        year = st.selectbox("Select Year", options=df["year"].unique(), index=43)

        # Create and display the map
        m = create_folium_map(year)
        folium_static(m, width=800, height=900)

    # Metrics
    with col3:
        year = st.selectbox("Select Year", options=["2023", "2024", "2025"])
        category = st.selectbox("Select Category", options=["All", "Category 1", "Category 2"])

        # # Calculate the increased rate using pct_change
        # df['KOKO MAA'] = df['KOKO MAA'].astype(float)
        # df['increase_rate'] = df['KOKO MAA'].pct_change() * 100

        # current_year_value = df[df["year"] == year]['KOKO MAA'].values[0]
        # increase_rate = df[df["year"] == year]['increase_rate'].values[0]

        # st.metric("Arrests", value=current_year_value, delta=f"{increase_rate:.2f}%")
        st.metric("Some metric", "xxx", "-8%")

with tab2:
    # Third section: Prediction of drug usage
    st.title("Prediction of Drug Usage in Finland")

    # Prediction row with area filter and chart
    col6, col7 = st.columns([1, 3])

    with col6:
        area = st.selectbox("Select Area", options=["All", "Area 1", "Area 2", "Area 3"])

    with col7:
        st.subheader("Number of deaths")
        fig3, ax3 = plt.subplots()
        ax3.plot(x, y)
        st.pyplot(fig3)