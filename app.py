import streamlit as st
import pandas as pd
import altair as alt
import seaborn as sns
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import plotly.express as px
import plotly.graph_objects as go

# Set page configuration
st.set_page_config(page_title="Flight Analytics Dashboard", layout="wide")

# Custom CSS for better styling
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stPlotlyChart {
        background-color: white;
        border-radius: 5px;
        padding: 1rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .st-emotion-cache-1y4p8pa {
        padding: 2rem;
    }
    .metric-card {
        background-color: white;
        padding: 1rem;
        border-radius: 5px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .chart-container {
        margin: 1rem 0;
        padding: 1rem;
        background-color: white;
        border-radius: 5px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    </style>
""", unsafe_allow_html=True)

# Load and cache the dataset
@st.cache_data
def load_data():
    try:
        return pd.read_csv("FF_flights_data.csv")
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return None

# Load the data at the start
flight = load_data()

# Check if data is loaded successfully
if flight is None:
    st.error("Failed to load the flight data. Please check if the CSV file exists and is accessible.")
    st.stop()

# Sidebar controls with improved styling
st.sidebar.title("📊 Flight Analytics")
st.sidebar.markdown("---")

page = st.sidebar.radio("Navigation", [
    "🏠 Dashboard Overview",
    "📈 Performance Analytics",
    "🕒 Time Analysis",
    "🎯 Delay Patterns",
    "🌍 Route Analysis",
    "📊 Statistical Insights"
])

# Set slider range dynamically based on dataset size
max_sample_size = min(len(flight), 1000)  # cap at 1000 for performance
min_sample_size = min(100, max_sample_size - 1)  # ensure min is less than max
default_size = min(500, max_sample_size)

# Only show slider if we have enough data for a range
if max_sample_size > min_sample_size:
    sample_size = st.sidebar.slider("Sample size", min_sample_size, max_sample_size, default_size)
else:
    sample_size = max_sample_size
    st.sidebar.info(f"Using all available data points: {max_sample_size}")

# Sample the data
sampled_data = flight.sample(n=sample_size, random_state=42)

if page == "🏠 Dashboard Overview":
    st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("✈️ Total Flights", f"{len(flight):,}", 
                 delta=f"{len(flight)/1000000:.1f}M flights",
                 delta_color="normal")
    with col2:
        avg_dep_delay = flight['DEPARTURE_DELAY'].mean()
        st.metric("🕒 Avg Departure Delay", 
                 f"{avg_dep_delay:.1f} min",
                 delta=f"{avg_dep_delay:.1f} min",
                 delta_color="inverse")
    with col3:
        avg_arr_delay = flight['ARRIVAL_DELAY'].mean()
        st.metric("🛬 Avg Arrival Delay", 
                 f"{avg_arr_delay:.1f} min",
                 delta=f"{avg_arr_delay:.1f} min",
                 delta_color="inverse")
    st.markdown("</div>", unsafe_allow_html=True)

    # Enhanced Airline Distribution
    st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
    st.subheader("🏢 Airline Distribution")
    airline_data = flight['AIRLINE'].value_counts().reset_index()
    airline_data.columns = ['AIRLINE', 'COUNT']
    fig = px.pie(airline_data, 
                 values='COUNT', 
                 names='AIRLINE',
                 hole=0.4,
                 color_discrete_sequence=px.colors.qualitative.Set3)
    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # Enhanced Monthly Trends
    st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
    st.subheader("📈 Monthly Flight Trends")
    monthly_data = flight.groupby('MONTH').agg({
        'FLIGHT_NUMBER': 'count',
        'DEPARTURE_DELAY': 'mean',
        'ARRIVAL_DELAY': 'mean'
    }).reset_index()
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=monthly_data['MONTH'],
        y=monthly_data['FLIGHT_NUMBER'],
        name='Number of Flights',
        mode='lines+markers'
    ))
    fig.update_layout(
        xaxis_title="Month",
        yaxis_title="Number of Flights",
        hovermode='x unified'
    )
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

elif page == "📈 Performance Analytics":
    st.header("Airline Performance Metrics")
    
    # Performance Overview
    metrics = sampled_data.groupby('AIRLINE').agg({
        'DEPARTURE_DELAY': ['mean', 'std'],
        'ARRIVAL_DELAY': ['mean', 'std'],
        'DISTANCE': 'mean'
    }).round(2)
    
    # Interactive Scatter Plot
    fig = px.scatter(sampled_data, 
                    x='DEPARTURE_DELAY', 
                    y='ARRIVAL_DELAY',
                    color='AIRLINE',
                    hover_data=['DISTANCE'],
                    title='Delay Correlation by Airline')
    st.plotly_chart(fig, use_container_width=True)
    
    # Performance Table
    st.dataframe(metrics, use_container_width=True)

elif page == "🕒 Time Analysis":
    st.header("Temporal Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Hourly Delays
        hourly = sampled_data.groupby('SCHEDULED_DEPARTURE')[
            ['DEPARTURE_DELAY']].mean().reset_index()
        fig = px.line(hourly, 
                     x='SCHEDULED_DEPARTURE', 
                     y='DEPARTURE_DELAY',
                     title='Hourly Delay Pattern')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Day of Week Analysis
        fig = px.box(sampled_data, 
                    x='DAY_OF_WEEK', 
                    y='ARRIVAL_DELAY',
                    title='Delays by Day of Week')
        st.plotly_chart(fig, use_container_width=True)

elif page == "🎯 Delay Patterns":
    st.header("Delay Pattern Analysis")
    
    # Delay Distribution
    fig = px.histogram(sampled_data,
                      x='DEPARTURE_DELAY',
                      nbins=50,
                      title='Departure Delay Distribution')
    st.plotly_chart(fig, use_container_width=True)
    
    # Delay Heatmap
    delay_corr = sampled_data[[
        'DEPARTURE_DELAY', 'ARRIVAL_DELAY', 'DISTANCE']].corr()
    fig = px.imshow(delay_corr,
                    title='Delay Correlation Matrix')
    st.plotly_chart(fig, use_container_width=True)

elif page == "🌍 Route Analysis":
    st.header("Route Analytics")
    
    # Distance vs Delay (removed trendline parameter)
    fig = px.scatter(sampled_data,
                    x='DISTANCE',
                    y='ARRIVAL_DELAY',
                    color='AIRLINE',
                    title='Distance vs Delay Relationship')
    st.plotly_chart(fig, use_container_width=True)
    
    # Route Performance
    route_stats = sampled_data.groupby(['ORIGIN_AIRPORT', 'DESTINATION_AIRPORT']).agg({
        'ARRIVAL_DELAY': 'mean',
        'DEPARTURE_DELAY': 'mean',
        'DISTANCE': 'first'
    }).reset_index()
    
    st.dataframe(route_stats.sort_values('ARRIVAL_DELAY', ascending=False).head(10))

elif page == "📊 Statistical Insights":
    st.header("Statistical Analysis")
    
    # Correlation Analysis
    corr = sampled_data.select_dtypes(include=['float64', 'int64']).corr()
    fig = px.imshow(corr,
                    title='Feature Correlation Matrix')
    st.plotly_chart(fig, use_container_width=True)
    
    # Statistical Summary
    st.subheader("Summary Statistics")
    st.dataframe(sampled_data.describe())

st.sidebar.markdown("---")
st.sidebar.info("💡 Dashboard updated with interactive visualizations")