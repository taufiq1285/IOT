"""
Batch Pipeline - Extract, Transform, Load
Bronze → Silver → Gold layers
"""

import pandas as pd
import numpy as np
from datetime import datetime
import os

print("=" * 60)
print("  BATCH PIPELINE - IoT Data Processing")
print("=" * 60)
print()

# ==================== EXTRACT ====================
print("📥 STEP 1: EXTRACT (Bronze Layer)")
print("-" * 60)

# Read from multiple formats
print("  Loading CSV data...")
df_csv = pd.read_csv('02_data/raw/csv/sensor_data.csv')
print(f"  ✓ Loaded {len(df_csv)} records from CSV")

print("  Loading JSON data...")
df_json = pd.read_json('02_data/raw/json/sensor_data.json')
print(f"  ✓ Loaded {len(df_json)} records from JSON")

print("  Loading Parquet data...")
df_parquet = pd.read_parquet('02_data/bronze/sensor_data.parquet')
print(f"  ✓ Loaded {len(df_parquet)} records from Parquet")

# Use Parquet as source (most efficient)
df_bronze = df_parquet.copy()
print(f"\n  ✅ Bronze layer: {len(df_bronze)} records loaded\n")

# ==================== TRANSFORM ====================
print("🔧 STEP 2: TRANSFORM (Silver Layer)")
print("-" * 60)

df_silver = df_bronze.copy()

# 1. Data Type Conversion
print("  1. Converting data types...")
df_silver['timestamp'] = pd.to_datetime(df_silver['timestamp'])
df_silver['date'] = pd.to_datetime(df_silver['date'])

# 2. Data Quality Checks
print("  2. Applying data quality rules...")
initial_count = len(df_silver)

# Remove duplicates
df_silver = df_silver.drop_duplicates(subset=['sensor_id', 'timestamp'])
print(f"     - Removed {initial_count - len(df_silver)} duplicate records")

# Remove invalid values
df_silver = df_silver[
    (df_silver['temperature'] >= 15) & (df_silver['temperature'] <= 40)
]
print(f"     - Filtered temperature range: 15-40°C")

df_silver = df_silver[
    (df_silver['humidity'] >= 30) & (df_silver['humidity'] <= 90)
]
print(f"     - Filtered humidity range: 30-90%")

df_silver = df_silver[
    (df_silver['co2_ppm'] >= 350) & (df_silver['co2_ppm'] <= 3000)
]
print(f"     - Filtered CO2 range: 350-3000 ppm")

# 3. Feature Engineering
print("  3. Creating derived features...")

# Thermal comfort index (simplified)
df_silver['thermal_comfort'] = df_silver.apply(
    lambda row: 'Comfortable' if (22 <= row['temperature'] <= 26 and 40 <= row['humidity'] <= 60)
    else 'Too Hot' if row['temperature'] > 26
    else 'Too Cold' if row['temperature'] < 22
    else 'Too Humid' if row['humidity'] > 60
    else 'Too Dry',
    axis=1
)

# Air quality category based on CO2
df_silver['air_quality'] = pd.cut(
    df_silver['co2_ppm'],
    bins=[0, 800, 1200, 2000, 5000],
    labels=['Excellent', 'Good', 'Moderate', 'Poor']
)

# Energy efficiency score (0-100)
# Lower when AC is ON but occupancy is low
df_silver['energy_efficiency'] = df_silver.apply(
    lambda row: 100 if row['ac_status'] == 'OFF'
    else max(0, 100 - (30 if row['occupancy_pct'] < 30 else 0)),
    axis=1
)

# 4. Add processing metadata
df_silver['processed_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
df_silver['data_quality_score'] = 95.0  # Simplified score

print(f"\n  ✅ Silver layer: {len(df_silver)} records cleaned and enriched\n")

# Save Silver layer
os.makedirs('02_data/silver', exist_ok=True)
df_silver.to_parquet('02_data/silver/sensor_data_cleaned.parquet', 
                     compression='snappy', index=False)
print("  💾 Saved to: 02_data/silver/sensor_data_cleaned.parquet\n")

# ==================== LOAD (Gold Layer - Warehouse) ====================
print("🏆 STEP 3: LOAD (Gold Layer - Data Warehouse)")
print("-" * 60)

# Create dimension tables
print("  Creating dimension tables...")

# DIM_ROOM
dim_room = df_silver[['room_id', 'building', 'floor', 'room_type', 'room_capacity']].drop_duplicates()
dim_room['room_key'] = range(1, len(dim_room) + 1)
dim_room.to_parquet('02_data/gold/dim_room.parquet', index=False)
print(f"  ✓ dim_room: {len(dim_room)} rooms")

# DIM_TIME
df_silver['time_key'] = df_silver['timestamp'].dt.strftime('%Y%m%d%H')
dim_time = pd.DataFrame({
    'time_key': df_silver['time_key'].unique()
})
dim_time['time_key'] = dim_time['time_key'].astype(int)
dim_time = dim_time.sort_values('time_key')
dim_time['date'] = pd.to_datetime(dim_time['time_key'].astype(str).str[:8], format='%Y%m%d')
dim_time['hour'] = dim_time['time_key'].astype(str).str[8:10].astype(int)
dim_time['day_of_week'] = dim_time['date'].dt.day_name()
dim_time['is_weekend'] = dim_time['date'].dt.dayofweek.isin([5, 6])
dim_time.to_parquet('02_data/gold/dim_time.parquet', index=False)
print(f"  ✓ dim_time: {len(dim_time)} time periods")

# DIM_ALERT
dim_alert = pd.DataFrame({
    'alert_key': [1, 2, 3],
    'alert_status': ['NORMAL', 'WARNING', 'CRITICAL'],
    'alert_description': [
        'All parameters within normal range',
        'One or more parameters exceed threshold',
        'Critical condition requiring immediate action'
    ]
})
dim_alert.to_parquet('02_data/gold/dim_alert.parquet', index=False)
print(f"  ✓ dim_alert: {len(dim_alert)} alert types")

# FACT_SENSOR_READINGS (Fact table)
print("\n  Creating fact table...")

# Merge with dimension keys
fact_table = df_silver.copy()
fact_table['time_key'] = fact_table['timestamp'].dt.strftime('%Y%m%d%H').astype(int)
fact_table = fact_table.merge(dim_room[['room_id', 'room_key']], on='room_id', how='left')
fact_table['alert_key'] = fact_table['alert_status'].map({
    'NORMAL': 1, 'WARNING': 2, 'CRITICAL': 3
})

# Select only necessary columns for fact table
fact_columns = [
    'sensor_id', 'timestamp', 'time_key', 'room_key', 'alert_key',
    'temperature', 'humidity', 'co2_ppm', 'light_lux',
    'occupancy_count', 'occupancy_pct', 'ac_status',
    'thermal_comfort', 'air_quality', 'energy_efficiency'
]
fact_sensor_readings = fact_table[fact_columns]

# Save fact table (partitioned by date for better query performance)
fact_sensor_readings['partition_date'] = fact_sensor_readings['timestamp'].dt.strftime('%Y-%m-%d')
fact_sensor_readings.to_parquet(
    '02_data/gold/fact_sensor_readings.parquet',
    partition_cols=['partition_date'],
    compression='snappy',
    index=False
)
print(f"  ✓ fact_sensor_readings: {len(fact_sensor_readings)} readings")

# Create aggregated summary table
print("\n  Creating aggregated summary...")
summary_hourly = fact_table.groupby(['room_id', 'time_key']).agg({
    'temperature': ['mean', 'min', 'max', 'std'],
    'humidity': ['mean', 'min', 'max'],
    'co2_ppm': ['mean', 'max'],
    'occupancy_count': ['mean', 'max'],
    'energy_efficiency': 'mean'
}).round(2)

summary_hourly.columns = ['_'.join(col).strip() for col in summary_hourly.columns.values]
summary_hourly = summary_hourly.reset_index()
summary_hourly.to_parquet('02_data/gold/summary_hourly.parquet', index=False)
print(f"  ✓ summary_hourly: {len(summary_hourly)} aggregated records")

print(f"\n  ✅ Gold layer: Star schema created successfully!\n")

# ==================== PIPELINE SUMMARY ====================
print("=" * 60)
print("  PIPELINE EXECUTION SUMMARY")
print("=" * 60)
print(f"  Bronze (Raw):     {len(df_bronze):,} records")
print(f"  Silver (Cleaned): {len(df_silver):,} records")
print(f"  Gold (Warehouse): ")
print(f"    - dim_room:              {len(dim_room):,} records")
print(f"    - dim_time:              {len(dim_time):,} records")
print(f"    - dim_alert:             {len(dim_alert):,} records")
print(f"    - fact_sensor_readings:  {len(fact_sensor_readings):,} records")
print(f"    - summary_hourly:        {len(summary_hourly):,} records")
print()
print("✅ Batch pipeline completed successfully!")
print("=" * 60)
print()
print("📁 Output files:")
print("  - 02_data/silver/sensor_data_cleaned.parquet")
print("  - 02_data/gold/dim_room.parquet")
print("  - 02_data/gold/dim_time.parquet")
print("  - 02_data/gold/dim_alert.parquet")
print("  - 02_data/gold/fact_sensor_readings.parquet/")
print("  - 02_data/gold/summary_hourly.parquet")
