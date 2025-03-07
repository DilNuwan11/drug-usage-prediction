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
from utils.map_risk import create_highrisk_map
from streamlit_folium import folium_static

import plotly.graph_objects as go

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

# Sidebar for navigation
st.sidebar.title("")
page = st.sidebar.radio("Go to", ["Monitoring", "Prediction", "Impact"])


if page == "Monitoring":
    # Title of the dashboard
    st.title("Monitoring Drug Usage in Finland")

    # Creating a grid with three columns for the top section
    col1, col2 = st.columns([1, 1])

    # Chart 1: Number of deaths
    with col1:
        st.subheader("Number of deaths by Age Group")
        df_1 = pd.read_csv("data/clean/Drug_related_deaths.csv")
        years = [int(col) for col in df_1.columns if col != "Age_group"]

        fig1 = go.Figure()
        for index, row in df_1.iterrows():
            age_group = row["Age_group"]
            death_counts = row[1:].values.astype(int)
            fig1.add_trace(go.Scatter(x=years, y=death_counts, mode='lines+markers', name=age_group))

        fig1.update_layout(# title="Number of Deaths by Age Group Over the Years",
                           xaxis_title="Year", yaxis_title="Number of deaths",
                           template="plotly_white", showlegend=True)
        st.plotly_chart(fig1, use_container_width=True)

    with col2:
        st.subheader("Drug Price Trends")
        data = pd.read_csv("data/clean/Retail_drug_prices.csv")
        data["Year"] = data["Year"].astype(int)

        df = data.sort_values(by="Year")
        drug_options = list(df.columns[1:])

        plot_option = st.selectbox("Select plot option:", ["All types of drugs", "Commonly used drugs"], index=1)

        fig2 = go.Figure()

        if plot_option == "All types of drugs":
            for drug in drug_options:
                fig2.add_trace(go.Scatter(x=df["Year"], y=df[drug], mode='lines+markers', name=drug))
        elif plot_option == "Commonly used drugs":
            mostly_used = ["ATS_MDMA (tablet)", "ATS_Amphetamine (gram)", "Cannabis_Resin (gram)", "Cannabis_Herbal (gram)"]
            for drug in mostly_used:
                if drug in df.columns:
                    fig2.add_trace(go.Scatter(x=df["Year"], y=df[drug], mode='lines+markers', name=drug))

        fig2.update_layout(# title="Drug Price Trends Over Time",
                           xaxis_title="Year", yaxis_title="Price (€)",
                           template="plotly_white", showlegend=True)
        st.plotly_chart(fig2, use_container_width=True)


    with st.container():
        st.subheader("Trends by regions")
        
        kpi_options = ["arrests", "offences", "rehab", "clinic"]
        selected_kpis = st.multiselect("Select KPI(s):", options=kpi_options, default=["arrests"])

        # # Mode selection
        # mode = st.radio("Select Mode", options=["View in dynamic mode", "Examine in static mode"])

        # if mode == "View in dynamic mode":
        cont_col1, cont_col2 = st.columns(2)

        with cont_col1:
            # Load the GIF
            gif_path = "data/drug_usage_maps_2000_2023.gif"
            with open(gif_path, 'rb') as file:
                contents = file.read()
            data_url = base64.b64encode(contents).decode('utf-8-sig')
            st.markdown(f'<img src="data:image/gif;base64,{data_url}">', unsafe_allow_html=True)

        with cont_col2:
            ## line plots 

            df = pd.read_csv("data/merged_TSA.csv")
            
            # Create a selectbox for region filtering.
            unique_regions = sorted(df["region"].unique())
            region_selected = st.selectbox("Select Region:", unique_regions)

            # Filter the DataFrame based on the selected region.
            filtered_df = df[df["region"] == region_selected]

            # Create a Plotly line chart.
            fig = go.Figure()

            # Optional: Define colors for each KPI for consistency.
            kpi_colors = {"arrests": "blue", "offences": "red", "rehab": "green", "clinic": "orange"}

            # Add a trace for each selected KPI.
            for kpi in selected_kpis:
                fig.add_trace(go.Scatter(
                    x=filtered_df['year'],
                    y=filtered_df[kpi],
                    mode='lines+markers',
                    name=kpi.capitalize(),
                    line=dict(color=kpi_colors.get(kpi, "black"))
                ))

            # Update layout for clarity.
            fig.update_layout(
                title=f"KPI Trends for {region_selected}",
                xaxis_title="Year",
                yaxis_title="Count",
                template="plotly_white"
            )

            st.plotly_chart(fig, use_container_width=True)
            

        # elif mode == "Examine in static mode":
        #     df = pd.read_csv("./data/clean/Reported_drug_usage_by_regions.csv")

        #     # Select year
        #     year = st.selectbox("Select Year", options=df["year"].unique(), index=43)

        #     # Create and display the map
        #     m = create_folium_map(year)
        #     folium_static(m, width=800, height=900)


elif page == "Prediction":
    # Load datasets
    offences_df = pd.read_csv("data/clean/offences_forecast.csv", parse_dates=['year'])
    arrests_df = pd.read_csv("data/clean/arrests_forecast.csv", parse_dates=['year'])
    deaths_forecast_df = pd.read_csv("data/clean/deaths_forecast.csv", parse_dates=['year'])
    deaths_history_df = pd.read_csv("data/clean/death_df.csv", parse_dates=['year'])

    # Streamlit UI
    st.title("Future Trends in Illegal Drug-Related KPIs in Finland")

    # Create layout with three columns: Left (2), Spacer (0.05), Right (2)
    col1, col2 = st.columns([2, 2])

    ### ---- LEFT SIDE: Offences & Arrests ---- ###
    with col1:
        st.header("Offences and Arrests Forecast")

        kpi_selected = st.selectbox("Select Forecast KPI:", ["Offences", "Arrests"])
        
        # Ensure unique region names and keep "Uusimaa" only once
        unique_regions = sorted(set(offences_df["region"].unique()) - {"Uusimaa"})
        region_selected = st.selectbox("Select a Region:", ["Uusimaa"] + unique_regions)

        # Select dataset
        df = offences_df if kpi_selected == "Offences" else arrests_df
        kpi_column = "offences" if kpi_selected == "Offences" else "arrests"
        lower_col, upper_col = f"{kpi_column}_lower", f"{kpi_column}_upper"

        # Filter data
        filtered_df = df[(df["region"] == region_selected) & (df['type'].isin(['Prediction', 'Actual']))]

        # Create line chart
        fig1 = go.Figure()

        # Plot actual values
        actuals = filtered_df[filtered_df['type'] == 'Actual']
        fig1.add_trace(go.Scatter(x=actuals['year'], y=actuals[kpi_column], mode='lines+markers', name='Actual', line=dict(color='blue')))

        # Plot predictions
        predictions = filtered_df[filtered_df['type'] == 'Prediction']
        fig1.add_trace(go.Scatter(x=predictions['year'], y=predictions[kpi_column], mode='lines+markers', name='Prediction', line=dict(color='red', dash='dash')))

        # Plot confidence intervals
        if lower_col in filtered_df.columns and upper_col in filtered_df.columns:
            fig1.add_trace(go.Scatter(
                x=predictions['year'], y=predictions[lower_col],
                mode='lines', name='Lower Bound', line=dict(color='red', dash='dot'), showlegend=False))
            fig1.add_trace(go.Scatter(
                x=predictions['year'], y=predictions[upper_col],
                mode='lines', name='Upper Bound', line=dict(color='red', dash='dot'),
                fill='tonexty', fillcolor='rgba(255, 0, 0, 0.2)', showlegend=False))

        fig1.update_layout(title=f"{kpi_selected} Forecast - {region_selected}",
                        xaxis_title="Year", yaxis_title=f"{kpi_selected} Count",
                        template="plotly_white", showlegend=True)

        st.plotly_chart(fig1, use_container_width=True)

        # Data table
        st.subheader("Forecast Data Table")
        displayed_df = filtered_df[['year', 'region', 'type', kpi_column, lower_col, upper_col]].sort_values(by='year')
        st.dataframe(displayed_df.style.format({"offences": "{:.2f}", "offences_lower":"{:.2f}", "offences_upper":"{:.2f}",
                                                "arrests": "{:.2f}", "arrests_lower":"{:.2f}", "arrests_upper":"{:.2f}"}), height=200)

    ### ---- RIGHT SIDE: Deaths Forecast ---- ###
    with col2:
        st.header("Drug-Related Deaths Forecast")

        age_groups = deaths_forecast_df["age_group"].unique()
        age_selected = st.selectbox("Select Age Group:", age_groups)

        # Filter data
        deaths_forecast_filtered = deaths_forecast_df[deaths_forecast_df["age_group"] == age_selected]
        deaths_history_filtered = deaths_history_df[deaths_history_df["age_group"] == age_selected]

        # Create line chart
        fig2 = go.Figure()

        # Plot actual deaths
        fig2.add_trace(go.Scatter(x=deaths_history_filtered['year'], y=deaths_history_filtered['deaths'],
                                mode='lines+markers', name='Actual Deaths', line=dict(color='blue')))

        # Plot predicted deaths
        fig2.add_trace(go.Scatter(x=deaths_forecast_filtered['year'], y=deaths_forecast_filtered['forecast'],
                                mode='lines+markers', name='Predicted Deaths', line=dict(color='red', dash='dash')))

        # Plot confidence intervals
        if 'lower' in deaths_forecast_filtered.columns and 'upper' in deaths_forecast_filtered.columns:
            fig2.add_trace(go.Scatter(
                x=deaths_forecast_filtered['year'], y=deaths_forecast_filtered['lower'],
                mode='lines', name='Lower Bound', line=dict(color='red', dash='dot'), showlegend=False))
            fig2.add_trace(go.Scatter(
                x=deaths_forecast_filtered['year'], y=deaths_forecast_filtered['upper'],
                mode='lines', name='Upper Bound', line=dict(color='red', dash='dot'),
                fill='tonexty', fillcolor='rgba(255, 0, 0, 0.2)', showlegend=False))

        fig2.update_layout(title=f"Drug-Related Deaths Forecast - {age_selected}",
                        xaxis_title="Year", yaxis_title="Deaths Count",
                        template="plotly_white", showlegend=True)

        st.plotly_chart(fig2, use_container_width=True)

        # --- Pie Chart for Deaths Forecast in 2025 by Age Group ---
        st.subheader("Deaths Forecast Distribution by Age Group (2025)")

        # Filter deaths forecast for 2025
        deaths_2025 = deaths_forecast_df[deaths_forecast_df["year"].dt.year == 2025]

        # Create Pie Chart
        fig_pie = go.Figure(data=[go.Pie(labels=deaths_2025["age_group"], 
                                        values=deaths_2025["forecast"], 
                                        hole=0.4)])

        fig_pie.update_layout(title="Proportion of Predicted Drug-Related Deaths by Age Group (2025)")

        st.plotly_chart(fig_pie, use_container_width=True)

    with st.container():
        cont_col1, cont_col2 = st.columns(2)

        with cont_col1:
            # Identify Regions with High Increase in 2025
            def find_high_increase_regions(df, kpi_column):
                """Finds regions where predictions in 2025 are higher than actuals in 2024 and sorts them by increase."""
                actuals_2024 = df[(df['year'].dt.year == 2023) & (df['type'] == 'Actual')].set_index('region')[kpi_column]
                predictions_2025 = df[(df['year'].dt.year == 2025) & (df['type'] == 'Prediction')].set_index('region')[kpi_column]

                increase_df = (predictions_2025 - actuals_2024).dropna()
                high_regions = increase_df[increase_df > 0].sort_values(ascending=False).reset_index()
            
                return high_regions

            # Get high increase regions for offences and arrests
            high_offences_regions = find_high_increase_regions(offences_df, 'offences')
            high_arrests_regions = find_high_increase_regions(arrests_df, 'arrests')

            # Display high increase regions
            st.subheader("Regions with High Increase in Offences (2025 vs 2024)")
            st.write(high_offences_regions.style.format({"offences": "{:.2f}"}))

            st.subheader("Regions with High Increase in Arrests (2025 vs 2024)")
            st.write(high_arrests_regions.style.format({"arrests": "{:.2f}"}))

        with cont_col2:
            st.subheader("High risk regions (2025)")

            m = create_highrisk_map()
            folium_static(m, width=800, height=900)

elif page == "Impact":
    # review the content
    st.title("Our Initiative of Monitoring and Prediction of drug usage in Finland")

    st.header("Who is it for?")
    st.write("""
    This dashboard is designed for key stakeholders responsible for addressing and mitigating drug usage in Finland.\n
    It provides critical insights into drug-related deaths, offenses, price trends, regional usage patterns, and rehabilitation needs.
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