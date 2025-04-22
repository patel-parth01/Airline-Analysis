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
    </style>
""", unsafe_allow_html=True)

# ... existing code ...

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

# ... existing code for sample size slider ...

if page == "🏠 Dashboard Overview":
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Flights", f"{len(flight):,}", 
                 delta=f"{len(flight)/1000000:.1f}M flights")
    with col2:
        avg_dep_delay = flight['DEPARTURE_DELAY'].mean()
        st.metric("Avg Departure Delay", 
                 f"{avg_dep_delay:.1f} min",
                 delta=f"{avg_dep_delay:.1f} min")
    with col3:
        avg_arr_delay = flight['ARRIVAL_DELAY'].mean()
        st.metric("Avg Arrival Delay", 
                 f"{avg_arr_delay:.1f} min",
                 delta=f"{avg_arr_delay:.1f} min")

    # Airline Distribution
    st.subheader("Airline Distribution")
    fig = px.pie(flight['AIRLINE'].value_counts().reset_index(), 
                 values='count', names='AIRLINE', 
                 hole=0.4)
    st.plotly_chart(fig, use_container_width=True)

    # Monthly Trends
    st.subheader("Monthly Flight Trends")
    monthly_data = flight.groupby('MONTH').size().reset_index(name='count')
    fig = px.line(monthly_data, x='MONTH', y='count',
                  markers=True)
    st.plotly_chart(fig, use_container_width=True)

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
    
    # Distance vs Delay
    fig = px.scatter(sampled_data,
                    x='DISTANCE',
                    y='ARRIVAL_DELAY',
                    color='AIRLINE',
                    trendline="ols",
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