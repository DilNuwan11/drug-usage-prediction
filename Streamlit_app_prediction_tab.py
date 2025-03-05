import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# Set Streamlit page layout
st.set_page_config(page_title="Drug-Related KPIs Forecast", layout="wide")

# Load datasets
offences_df = pd.read_csv("data/clean/offences_forecast.csv", parse_dates=['year'])
arrests_df = pd.read_csv("data/clean/arrests_forecast.csv", parse_dates=['year'])
deaths_forecast_df = pd.read_csv("data/clean/deaths_forecast.csv", parse_dates=['year'])
deaths_history_df = pd.read_csv("data/clean/death_df.csv", parse_dates=['year'])

# Streamlit UI
st.title("Future Trends in Illegal Drug-Related KPIs in Finland")

# Create layout with three columns: Left (2), Spacer (0.05), Right (2)
col1, col_space, col2 = st.columns([2, 0.05, 2])

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
    st.dataframe(filtered_df[['year', 'region', 'type', kpi_column, lower_col, upper_col]].sort_values(by='year'))

    # Divider for better spacing
    st.divider()

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
    st.write(high_offences_regions)

    st.subheader("Regions with High Increase in Arrests (2025 vs 2024)")
    st.write(high_arrests_regions)


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

