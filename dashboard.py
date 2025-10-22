import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import os

st.set_page_config(page_title="IoT Monitoring Dashboard", layout="wide")

# Title
st.title("🌡️ IoT Environmental Monitoring Dashboard")
st.markdown("Real-time monitoring suhu, kelembapan, dan CO2 di kampus")

# Sidebar
st.sidebar.header("📊 Filters")

# Load data with fallback options
try:
    # Try loading from multiple sources (most robust approach)
    if os.path.exists('02_data/bronze/sensor_data.parquet'):
        df = pd.read_parquet('02_data/bronze/sensor_data.parquet')
        st.sidebar.success("📦 Loaded from Parquet (optimized)")
    elif os.path.exists('02_data/raw/csv/sensor_data.csv'):
        df = pd.read_csv('02_data/raw/csv/sensor_data.csv')
        st.sidebar.info("📄 Loaded from CSV")
    elif os.path.exists('02_data/bronze/sensor_data.csv'):
        df = pd.read_csv('02_data/bronze/sensor_data.csv')
        st.sidebar.info("📄 Loaded from Bronze CSV")
    else:
        st.error("❌ Data file not found! Run generator.py first.")
        st.info("Expected locations:\n- 02_data/bronze/sensor_data.parquet\n- 02_data/raw/csv/sensor_data.csv\n- 02_data/bronze/sensor_data.csv")
        st.stop()
    
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    # Filters
    buildings = st.sidebar.multiselect(
        "Pilih Gedung:",
        options=df['building'].unique(),
        default=df['building'].unique()
    )
    
    # Filter data
    filtered_df = df[df['building'].isin(buildings)]
    
    # Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "🌡️ Avg Temperature", 
            f"{filtered_df['temperature'].mean():.1f}°C",
            f"{filtered_df['temperature'].std():.1f}°C std"
        )
    
    with col2:
        st.metric(
            "💧 Avg Humidity", 
            f"{filtered_df['humidity'].mean():.1f}%",
            f"{filtered_df['humidity'].std():.1f}% std"
        )
    
    with col3:
        st.metric(
            "🫁 Avg CO2", 
            f"{filtered_df['co2_ppm'].mean():.0f} ppm",
            "Good" if filtered_df['co2_ppm'].mean() < 1000 else "High"
        )
    
    with col4:
        alerts = (filtered_df['alert_status'] == 'WARNING').sum()
        st.metric(
            "⚠️ Alerts", 
            f"{alerts}",
            "warnings"
        )
    
    st.markdown("---")
    
    # Temperature trend
    st.subheader("📈 Temperature Trend Over Time")
    fig_temp = px.line(
        filtered_df, 
        x='timestamp', 
        y='temperature',
        color='building',
        title='Temperature by Building'
    )
    fig_temp.update_layout(
        height=500,
        xaxis_title="Time",
        yaxis_title="Temperature (°C)",
        hovermode='x unified'
    )
    st.plotly_chart(fig_temp, key="temp_trend")
    
    # Room comparison
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🏢 Average Metrics by Room")
        room_avg = filtered_df.groupby('room_id').agg({
            'temperature': 'mean',
            'humidity': 'mean',
            'co2_ppm': 'mean'
        }).round(2)
        
        fig_room = go.Figure()
        fig_room.add_trace(go.Bar(
            x=room_avg.index,
            y=room_avg['temperature'],
            name='Temperature (°C)',
            marker_color='#1f77b4'
        ))
        fig_room.update_layout(
            height=400,
            xaxis_title="Room ID",
            yaxis_title="Temperature (°C)",
            showlegend=True
        )
        st.plotly_chart(fig_room, key="room_metrics")
    
    with col2:
        st.subheader("🎯 Thermal Comfort Distribution")
        comfort_counts = filtered_df['thermal_comfort'].value_counts()
        fig_comfort = px.pie(
            values=comfort_counts.values,
            names=comfort_counts.index,
            title='Thermal Comfort Status',
            hole=0.3
        )
        fig_comfort.update_layout(height=400)
        st.plotly_chart(fig_comfort, key="comfort_dist")
    
    # Heatmap
    st.subheader("🔥 Temperature Heatmap by Room and Hour")
    heatmap_data = filtered_df.pivot_table(
        values='temperature',
        index='room_id',
        columns='hour',
        aggfunc='mean'
    )
    fig_heatmap = px.imshow(
        heatmap_data,
        labels=dict(x="Hour", y="Room", color="Temperature"),
        aspect="auto",
        color_continuous_scale='RdYlBu_r'
    )
    fig_heatmap.update_layout(
        height=500,
        xaxis_title="Hour of Day",
        yaxis_title="Room ID"
    )
    st.plotly_chart(fig_heatmap, key="temp_heatmap")
    
    # Data table
    st.subheader("📋 Raw Data Preview")
    st.dataframe(
        filtered_df.head(100),
        height=400
    )
    
    # Download button
    csv = filtered_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Filtered Data",
        data=csv,
        file_name='filtered_sensor_data.csv',
        mime='text/csv',
    )
    
except Exception as e:
    st.error(f"❌ Error loading data: {e}")
    st.info("💡 Make sure you've run the generator script first!")
    st.code("""
# Run this command to generate data:
python 02_data/generator.py
    """, language="bash")