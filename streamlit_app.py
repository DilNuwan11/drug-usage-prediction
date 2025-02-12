import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns

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

tab1, tab2 = st.tabs(["Monitoring", "Prediction"])

with tab1:

    # Title of the dashboard
    st.title("Monitoring Drug Usage in Finland")

    # Creating a grid with three columns for the top section
    col1, col2, col3 = st.columns([1, 1.5, 1])

    # Chart 1: Number of deaths
    with col1:
        st.subheader("Number of deaths")
        fig1, ax1 = plt.subplots()
        x = [2018, 2019, 2020, 2021, 2022]
        y = [10, 20, 30, 35, 40]
        ax1.plot(x, y)
        st.pyplot(fig1)

        st.subheader("Price of drugs")
        fig2, ax2 = plt.subplots()
        prices1 = [10, 20, 30, 35, 40]
        prices2 = [5, 15, 25, 30, 35]
        ax2.plot(x, prices1, label="Drug A")
        ax2.plot(x, prices2, label="Drug B")
        ax2.legend()
        st.pyplot(fig2)

    # Center column with map
    with col2:
        st.subheader("Drug-related arrests by regions")
        st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/0/0e/Regions_of_Finland_labelled_EN.svg/532px-Regions_of_Finland_labelled_EN.svg.png")  # Replace with real map data

    # Metrics
    with col3:
        year = st.selectbox("Select Year", options=["2023", "2024", "2025"])
        category = st.selectbox("Select Category", options=["All", "Category 1", "Category 2"])

        st.metric("Arrests", value = "3xxx", delta = "5%")
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
