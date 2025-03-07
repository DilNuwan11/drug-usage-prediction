   ## line plots 

    # Load the dataset
    df = pd.read_csv("merged_TSA.csv")

    st.header("KPI Trends Over Time")

    # Create a selectbox for region filtering.
    unique_regions = sorted(df["region"].unique())
    region_selected = st.selectbox("Select Region:", unique_regions)

    # Create a multiselect for KPIs
    kpi_options = ["arrests", "offences", "rehab", "clinic"]
    selected_kpis = st.multiselect("Select KPI(s):", options=kpi_options, default=["arrests"])

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
 