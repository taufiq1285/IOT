"""
Sample Queries - Analytical Examples
Demonstrates filtering, aggregation, and joins
"""

import pandas as pd
import time

print("=" * 60)
print("  SAMPLE ANALYTICAL QUERIES")
print("=" * 60)
print()

# Load data from Gold layer
print("📥 Loading data from Gold layer...")
dim_room = pd.read_parquet('02_data/gold/dim_room.parquet')
fact_readings = pd.read_parquet('02_data/gold/fact_sensor_readings.parquet')
summary_hourly = pd.read_parquet('02_data/gold/summary_hourly.parquet')

print(f"  ✓ Loaded {len(fact_readings):,} fact records")
print(f"  ✓ Loaded {len(dim_room)} rooms")
print()

# ==================== QUERY 1: Aggregation ====================
print("🔍 QUERY 1: Average Temperature per Building")
print("-" * 60)

start_time = time.time()

# Merge fact with dimension
df = fact_readings.merge(dim_room[['room_key', 'building']], on='room_key', how='left')

# Aggregate
result_q1 = df.groupby('building').agg({
    'temperature': ['mean', 'min', 'max'],
    'humidity': 'mean',
    'co2_ppm': 'mean'
}).round(2)

result_q1.columns = ['avg_temp', 'min_temp', 'max_temp', 'avg_humidity', 'avg_co2']
result_q1 = result_q1.reset_index()

execution_time_q1 = time.time() - start_time

print(result_q1.to_string(index=False))
print(f"\n⏱️  Execution time: {execution_time_q1*1000:.2f} ms")
print()

# Save result
result_q1.to_csv('04_queries/query1_result.csv', index=False)

# ==================== QUERY 2: Filter + Aggregation ====================
print("🔍 QUERY 2: Rooms with High Temperature (>28°C)")
print("-" * 60)

start_time = time.time()

# Filter high temperature
high_temp = fact_readings[fact_readings['temperature'] > 28].copy()

# Join with room details
high_temp = high_temp.merge(
    dim_room[['room_key', 'room_id', 'building', 'room_type']], 
    on='room_key', 
    how='left'
)

# Aggregate
result_q2 = high_temp.groupby(['building', 'room_id', 'room_type']).agg({
    'temperature': ['count', 'mean', 'max'],
    'occupancy_count': 'mean'
}).round(2)

result_q2.columns = ['high_temp_count', 'avg_temp', 'max_temp', 'avg_occupancy']
result_q2 = result_q2.reset_index()
result_q2 = result_q2.sort_values('high_temp_count', ascending=False)

execution_time_q2 = time.time() - start_time

print(result_q2.head(10).to_string(index=False))
print(f"\n⏱️  Execution time: {execution_time_q2*1000:.2f} ms")
print()

# Save result
result_q2.to_csv('04_queries/query2_result.csv', index=False)

# ==================== QUERY 3: Time-Series Analysis ====================
print("🔍 QUERY 3: Hourly Temperature Trend (Last 24 hours)")
print("-" * 60)

start_time = time.time()

# Convert timestamp
fact_readings['timestamp'] = pd.to_datetime(fact_readings['timestamp'])

# Get latest 24 hours
max_time = fact_readings['timestamp'].max()
min_time = max_time - pd.Timedelta(hours=24)

recent_data = fact_readings[
    (fact_readings['timestamp'] >= min_time) & 
    (fact_readings['timestamp'] <= max_time)
].copy()

# Create hourly bins
recent_data['hour'] = recent_data['timestamp'].dt.floor('H')

# Aggregate by hour
result_q3 = recent_data.groupby('hour').agg({
    'temperature': ['mean', 'min', 'max'],
    'humidity': 'mean',
    'co2_ppm': 'mean',
    'sensor_id': 'count'
}).round(2)

result_q3.columns = ['avg_temp', 'min_temp', 'max_temp', 'avg_humidity', 'avg_co2', 'reading_count']
result_q3 = result_q3.reset_index()

execution_time_q3 = time.time() - start_time

print(result_q3.to_string(index=False))
print(f"\n⏱️  Execution time: {execution_time_q3*1000:.2f} ms")
print()

# Save result
result_q3.to_csv('04_queries/query3_result.csv', index=False)

# ==================== BONUS QUERY 4: Energy Efficiency ====================
print("🔍 BONUS QUERY 4: Energy Efficiency by Room Type")
print("-" * 60)

start_time = time.time()

# Merge with room details
df_efficiency = fact_readings.merge(
    dim_room[['room_key', 'room_type', 'building']], 
    on='room_key', 
    how='left'
)

# Calculate metrics
result_q4 = df_efficiency.groupby('room_type').agg({
    'energy_efficiency': 'mean',
    'ac_status': lambda x: (x == 'ON').sum(),
    'occupancy_pct': 'mean',
    'sensor_id': 'count'
}).round(2)

result_q4.columns = ['avg_efficiency_score', 'ac_on_count', 'avg_occupancy_pct', 'total_readings']
result_q4 = result_q4.reset_index()
result_q4 = result_q4.sort_values('avg_efficiency_score', ascending=False)

execution_time_q4 = time.time() - start_time

print(result_q4.to_string(index=False))
print(f"\n⏱️  Execution time: {execution_time_q4*1000:.2f} ms")
print()

# ==================== SUMMARY ====================
print("=" * 60)
print("  QUERY PERFORMANCE SUMMARY")
print("=" * 60)

summary = pd.DataFrame({
    'Query': [
        'Q1: Avg Temp per Building',
        'Q2: High Temp Rooms',
        'Q3: Hourly Trend (24h)',
        'Q4: Energy Efficiency'
    ],
    'Execution Time (ms)': [
        f"{execution_time_q1*1000:.2f}",
        f"{execution_time_q2*1000:.2f}",
        f"{execution_time_q3*1000:.2f}",
        f"{execution_time_q4*1000:.2f}"
    ],
    'Result Rows': [
        len(result_q1),
        len(result_q2),
        len(result_q3),
        len(result_q4)
    ]
})

print(summary.to_string(index=False))
print()
print("✅ All queries executed successfully!")
print()
print("📁 Results saved to 04_queries/")
print("  - query1_result.csv")
print("  - query2_result.csv")
print("  - query3_result.csv")
print("=" * 60)
