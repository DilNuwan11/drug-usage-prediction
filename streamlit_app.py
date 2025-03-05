import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
import geopandas as gpd
import folium
import branca
import base64

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

tab1, tab2, tab3 = st.tabs(["Monitoring", "Prediction", "Impact"])

with tab1:

    # Title of the dashboard
    st.title("Monitoring Drug Usage in Finland")

    # Creating a grid with three columns for the top section
    col1, col2, col3 = st.columns([1.5, 1.5, 1])

    # Chart 1: Number of deaths
    with col1:
        st.subheader("Number of deaths by Age Group")
        df_1 = pd.read_csv("data/clean/Drug_related_deaths.csv")
        years = [int(col) for col in df_1.columns if col != "Age_group"]
        fig1, ax1 = plt.subplots()
        for index, row in df_1.iterrows():
            age_group = row["Age_group"]
            # Convert the row values for the years to integers
            death_counts = row[1:].values.astype(int)
            ax1.plot(years, death_counts, marker='o', linestyle='-', label=age_group)
        ax1.set_xlabel("Year")
        ax1.set_ylabel("Number of deaths")
        ax1.set_title("Number of Deaths by Age Group Over the Years")
        ax1.legend(title="Age Group")
        ax1.set_xticks(years)
        ax1.set_xticklabels(years, rotation=45)
        ax1.grid(True)
        st.pyplot(fig1)

        st.subheader("Drug Price Trends")
        data = pd.read_csv("data/clean/Retail_drug_prices.csv")
        data["Year"] = data["Year"].astype(int)

        df = data.sort_values(by="Year")
        drug_options = list(df.columns[1:])  

        plot_option = st.selectbox("Select plot option:", ["All types of drugs", "Mostly used drugs"])

        fig2, ax2 = plt.subplots(figsize=(10, 5))

        if plot_option == "All types of drugs":
            for drug in drug_options:
                ax2.plot(df["Year"], df[drug], marker='o', linestyle='-', label=drug)
        elif plot_option == "Mostly used drugs":
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
        # # Mode selection
        # mode = st.radio("Select Mode", options=["View in Time Series", "View in Static"])

        # if mode == "View in Time Series":
        #     st.subheader("Drug-related arrests by regions")

        #     df = pd.read_csv("./data/clean/Reported_drug_usage_by_regions.csv")

        #     # Select year
        #     year = st.selectbox("Select Year", options=df["year"].unique(), index=43)

        #     # Create and display the map
        #     m = create_folium_map(year)
        #     folium_static(m, width=800, height=900)
            
        # elif mode == "View in Static":
        st.subheader("Drug-related arrests by regions")

        # Load the GIF
        gif_path = "data/drug_usage_maps_2000_2023.gif"
        with open(gif_path, 'rb') as file:
            contents = file.read()
        data_url = base64.b64encode(contents).decode('utf-8-sig')
        st.markdown(f'<img src="data:image/gif;base64,{data_url}">', unsafe_allow_html=True)


    # Metrics
    with col3:
        # arrests
        df = pd.read_csv("./data/clean/Reported_drug_usage_by_regions.csv")
        df_death = pd.read_csv("./data/clean/Drug_related_deaths.csv")

        year_list = list(range(2007, 2024))
        year = st.selectbox("Select Year", options=year_list, index=16)

        current_year_value = df[df["year"] == year]['KOKO MAA'].values[0]
        year_before_value = df[df["year"] == year-1]['KOKO MAA'].values[0]

        increase_rate = ((current_year_value - year_before_value) / year_before_value) * 100

        st.metric(f"Drug related **arrests** change (%) in {year}", value=np.round(increase_rate, decimals=2), border=True)

        # deaths
        df_death.loc['Total'] = df_death.sum(numeric_only=True)

        current_year_value = df_death.loc['Total', str(year)]
        year_before_value = df_death.loc['Total', str(year-1)]

        increase_rate = ((current_year_value - year_before_value) / year_before_value) * 100

        st.metric(f"Drug related **deaths** change (%) in {year}", value=np.round(increase_rate, decimals=2), border=True)

        # regions
        max_arrests_region = df[df["year"] == year].drop(columns=["year", "KOKO MAA"]).idxmax(axis=1).values[0]
        max_arrests_value = df[df["year"] == year][max_arrests_region].values[0]

        st.metric(f"Region with most arrests in {year}", value=max_arrests_region, help=str(max_arrests_value), border=True)

with tab2:
    # Third section: Prediction of drug usage
    st.title("Prediction of Drug Usage in Finland")

    # Prediction row with area filter and chart
    col6, col7 = st.columns([1, 3])

    with col6:
        area = st.selectbox("Select Area", options=["All", "Area 1", "Area 2", "Area 3"])

    with col7:
        st.subheader("Number of deaths")
        # fig3, ax3 = plt.subplots()
        # ax3.plot(x, y)
        # st.pyplot(fig3)

with tab3:

    # review the content
    st.title("Our Initiative of Monitoring and Prediction of drug usage in Finland")

    st.header("Who is it for?")
    st.write("""
    This dashboard is designed for policymakers, healthcare professionals, and researchers who are involved in monitoring and addressing drug usage trends in Finland.\n
    It provides valuable insights into drug-related deaths, price trends, and regional usage patterns.
    """)

    st.header("Who benefits from the dashboard?")
    st.write("""
    The primary beneficiaries of this dashboard are:
    - **Policymakers**: To make informed decisions and create effective policies to combat drug usage.
    - **Healthcare Professionals**: To understand the trends and allocate resources efficiently.
    - **Researchers**: To analyze data and identify patterns for further studies.
    - **General Public**: To stay informed about the drug usage trends and their impact on society.
    """)

    st.header("Recommendations")
    st.write("""
    Based on the data presented in this dashboard, the following recommendations can be made:
    - **Increase Awareness Programs**: Implement educational campaigns to raise awareness about the dangers of drug usage.
    - **Enhance Support Services**: Provide better support and rehabilitation services for individuals struggling with drug addiction.
    - **Strengthen Law Enforcement**: Increase efforts to curb the illegal drug trade and reduce drug-related crimes.
    - **Policy Reforms**: Develop and implement policies that address the root causes of drug usage and provide long-term solutions.
    """)