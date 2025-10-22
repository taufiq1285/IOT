"""
IoT Environmental Data Generator - Lab Kebidanan Mega
Generates sensor data for 9 midwifery labs + 1 equipment depot
"""

import pandas as pd
import numpy as np
import random
import os
from datetime import datetime, timedelta

# Set random seed
np.random.seed(42)
random.seed(42)

# Configuration
NUM_RECORDS = 3000
START_DATE = datetime(2025, 10, 1, 6, 0, 0)

# Lab Kebidanan Mega - 10 Rooms Configuration
ROOMS = {
    'LAB_KTD': {
        'name': 'Lab Keterampilan Dasar Praktik Kebidanan',
        'floor': 1,
        'capacity': 30,
        'type': 'Lab Praktik'
    },
    'LAB_ANC': {
        'name': 'Lab ANC (Antenatal Care)',
        'floor': 1,
        'capacity': 25,
        'type': 'Lab Praktik'
    },
    'LAB_PNC': {
        'name': 'Lab PNC (Postnatal Care)',
        'floor': 1,
        'capacity': 25,
        'type': 'Lab Praktik'
    },
    'LAB_INC': {
        'name': 'Lab INC (Intranatal Care)',
        'floor': 1,
        'capacity': 20,
        'type': 'Lab Praktik'
    },
    'LAB_BBL': {
        'name': 'Lab BBL (Bayi Baru Lahir)',
        'floor': 1,
        'capacity': 22,
        'type': 'Lab Praktik'
    },
    'LAB_KB': {
        'name': 'Lab Pelayanan KB',
        'floor': 1,
        'capacity': 20,
        'type': 'Lab Praktik'
    },
    'LAB_KONSELING': {
        'name': 'Lab Konseling & Pendidikan Kesehatan',
        'floor': 1,
        'capacity': 28,
        'type': 'Lab Konseling'
    },
    'LAB_KOMUNITAS': {
        'name': 'Lab Kebidanan Komunitas',
        'floor': 1,
        'capacity': 30,
        'type': 'Lab Praktik'
    },
    'LAB_ANAK': {
        'name': 'Lab Bayi, Balita, Anak Prasekolah',
        'floor': 1,
        'capacity': 25,
        'type': 'Lab Praktik'
    },
    'DEPO_ALAT': {
        'name': 'Ruangan Depo Alat',
        'floor': 1,
        'capacity': 5,
        'type': 'Storage'
    }
}

# Single sensor type: DHT22
SENSOR_TYPE = 'DHT22'

def generate_sensor_id(room_id):
    """Generate sensor ID with consistent naming"""
    return f"SENS_{room_id}_{SENSOR_TYPE}"

def generate_environmental_data(timestamp, room_id, room_info):
    """
    Generate realistic environmental sensor readings for midwifery labs
    """
    hour = timestamp.hour
    day_of_week = timestamp.strftime('%A')
    is_weekend = day_of_week in ['Saturday', 'Sunday']

    # Base environmental parameters (clinical environment)
    base_temp = 23.0  # Clinical labs need cooler temp
    base_humidity = 55.0  # Lower humidity for equipment preservation
    base_co2 = 420

    # Time-based variations
    if 6 <= hour < 9:  # Early morning
        temp_adj = -1.0
        occupancy_factor = 0.1
    elif 9 <= hour < 12:  # Morning practicum
        temp_adj = 1.5
        occupancy_factor = 0.7
    elif 12 <= hour < 14:  # Lunch break
        temp_adj = 2.0
        occupancy_factor = 0.2
    elif 14 <= hour < 17:  # Afternoon practicum
        temp_adj = 2.5
        occupancy_factor = 0.8
    elif 17 <= hour < 20:  # Evening
        temp_adj = 1.0
        occupancy_factor = 0.3
    else:  # Night
        temp_adj = -0.5
        occupancy_factor = 0.0

    # Weekend adjustment
    if is_weekend:
        occupancy_factor *= 0.1  # Minimal activity on weekends

    # Room type specific adjustments
    if room_info['type'] == 'Storage':  # Depo Alat
        base_temp = 20.0  # Cooler for equipment storage
        base_humidity = 45.0  # Drier to prevent rust/damage
        occupancy_factor = 0.05  # Minimal human activity
        base_co2 = 410
    elif room_info['type'] == 'Lab Konseling':
        base_temp = 24.0  # Slightly warmer for comfort
        base_humidity = 60.0
    elif 'BBL' in room_id or 'ANAK' in room_id:
        base_temp = 24.5  # Warmer for baby care
        base_humidity = 58.0

    # Calculate occupancy
    max_occupancy = room_info['capacity']
    occupancy = int(max_occupancy * occupancy_factor * random.uniform(0.6, 1.2))
    occupancy = max(0, min(occupancy, max_occupancy))

    # Temperature (20-30°C) - clinical range
    temp_variation = np.random.normal(0, 1.0)
    occupancy_heat = occupancy * 0.04  # Body heat contribution
    temperature = base_temp + temp_adj + temp_variation + occupancy_heat
    temperature = round(np.clip(temperature, 20, 30), 2)

    # Humidity (40-75%) - clinical range
    humidity_variation = np.random.normal(0, 2.5)
    occupancy_humidity = occupancy * 0.06
    humidity = base_humidity + humidity_variation + occupancy_humidity
    humidity = round(np.clip(humidity, 40, 75), 2)

    # CO2 (400-1800 ppm) - lower than general labs
    co2_base = base_co2 + (occupancy * 25)
    co2_variation = np.random.normal(0, 40)
    co2 = int(co2_base + co2_variation)
    co2 = np.clip(co2, 400, 1800)

    # Light (0-700 lux)
    if room_info['type'] == 'Storage':
        if 6 <= hour < 18:
            light = int(random.uniform(100, 300))  # Lower light in storage
        else:
            light = int(random.uniform(0, 50))
    else:
        if 6 <= hour < 18:
            light = int(random.uniform(250, 700))  # Bright for clinical work
        else:
            light = int(random.uniform(0, 100))

    # Occupancy percentage
    occupancy_pct = round((occupancy / max_occupancy) * 100, 1) if max_occupancy > 0 else 0

    # AC Status (important for clinical environment)
    if room_info['type'] == 'Storage':
        ac_status = 'ON' if temperature > 22 else 'OFF'
    else:
        ac_status = 'ON' if (temperature > 25 and occupancy > max_occupancy * 0.2) else 'OFF'

    # Alert status (stricter for clinical environment)
    alert_status = 'NORMAL'
    alert_details = None

    # Clinical environment thresholds
    if room_info['type'] == 'Storage':
        # Stricter for equipment storage
        if temperature > 23 or humidity > 50 or co2 > 600:
            alert_status = 'WARNING'
            alerts = []
            if temperature > 23:
                alerts.append(f'Storage temp high: {temperature}°C')
            if humidity > 50:
                alerts.append(f'Humidity risk: {humidity}%')
            if co2 > 600:
                alerts.append(f'Ventilation needed: {co2}ppm')
            alert_details = '; '.join(alerts)
    else:
        # Lab praktik thresholds
        if temperature > 27 or humidity > 70 or co2 > 1200:
            alert_status = 'WARNING'
            alerts = []
            if temperature > 27:
                alerts.append(f'Temperature comfort: {temperature}°C')
            if humidity > 70:
                alerts.append(f'High humidity: {humidity}%')
            if co2 > 1200:
                alerts.append(f'CO2 elevated: {co2}ppm')
            alert_details = '; '.join(alerts)

    if temperature > 29 or temperature < 18 or co2 > 1500:
        alert_status = 'CRITICAL'

    # Thermal comfort (clinical PMV)
    if room_info['type'] == 'Storage':
        if 18 <= temperature <= 22 and humidity < 50:
            thermal_comfort = 'Optimal Storage'
        else:
            thermal_comfort = 'Suboptimal'
    else:
        if 22 <= temperature <= 25 and 45 <= humidity <= 65:
            thermal_comfort = 'Comfortable'
        elif 20 <= temperature <= 27 and 40 <= humidity <= 70:
            thermal_comfort = 'Acceptable'
        else:
            thermal_comfort = 'Uncomfortable'

    # Energy efficiency score (0-100)
    # Target: 23°C, 55% humidity, <800 CO2
    temp_efficiency = 100 - abs(temperature - 23) * 10
    humidity_efficiency = 100 - abs(humidity - 55) * 2
    co2_efficiency = 100 if co2 < 800 else (100 - (co2 - 800) / 10)
    energy_efficiency = round((temp_efficiency + humidity_efficiency + co2_efficiency) / 3, 1)
    energy_efficiency = max(0, min(100, energy_efficiency))

    return {
        'sensor_id': generate_sensor_id(room_id),
        'timestamp': timestamp,
        'room_id': room_id,
        'room_name': room_info['name'],
        'building': 'Lab Kebidanan Mega',
        'floor': room_info['floor'],
        'room_type': room_info['type'],
        'temperature': temperature,
        'humidity': humidity,
        'co2_ppm': co2,
        'light_lux': light,
        'occupancy_count': occupancy,
        'room_capacity': max_occupancy,
        'occupancy_pct': occupancy_pct,
        'ac_status': ac_status,
        'alert_status': alert_status,
        'alert_details': alert_details,
        'thermal_comfort': thermal_comfort,
        'energy_efficiency': energy_efficiency,
        'day_of_week': day_of_week,
        'is_weekend': 'Yes' if is_weekend else 'No',
        'date': timestamp.strftime('%Y-%m-%d'),
        'hour': hour
    }

def generate_dataset():
    """
    Generate complete IoT sensor dataset for midwifery labs
    """
    print("=" * 60)
    print("  IoT ENVIRONMENTAL MONITORING - LAB KEBIDANAN MEGA")
    print("=" * 60)
    print()
    print(f"🏥 Building: Lab Kebidanan Mega")
    print(f"🚪 Total Rooms: {len(ROOMS)}")
    print(f"   - Lab Praktik Kebidanan: 9 ruangan")
    print(f"   - Depo Alat: 1 ruangan")
    print(f"📡 Sensor Type: {SENSOR_TYPE}")
    print(f"📊 Target Records: {NUM_RECORDS:,}")
    print()

    # Print room details
    print("📋 ROOM CONFIGURATION:")
    for i, (room_id, room_info) in enumerate(ROOMS.items(), 1):
        print(f"  {i:2d}. {room_id:15s} - {room_info['name'][:40]:40s} (Lantai {room_info['floor']}, Kapasitas: {room_info['capacity']})")
    print()

    data = []
    current_time = START_DATE

    # Calculate time interval
    total_minutes = NUM_RECORDS // len(ROOMS)
    time_increment = timedelta(minutes=1)

    print(f"🔄 Generating {NUM_RECORDS} sensor records...")

    for i in range(total_minutes):
        for room_id, room_info in ROOMS.items():
            record = generate_environmental_data(current_time, room_id, room_info)
            data.append(record)

        current_time += time_increment

        # Progress indicator
        if (i + 1) % 50 == 0:
            records_so_far = (i + 1) * len(ROOMS)
            print(f"  ✓ Generated {records_so_far}/{NUM_RECORDS} records...")

    df = pd.DataFrame(data)
    df = df.head(NUM_RECORDS)  # Trim to exact count

    print(f"✅ Successfully generated {len(df):,} records!")
    print()

    return df

def save_multiple_formats(df):
    """
    Save data in multiple formats for comparison
    """
    print("💾 Saving data in multiple formats...")
    print()

    # Create directories
    os.makedirs('02_data/raw/csv', exist_ok=True)
    os.makedirs('02_data/raw/json', exist_ok=True)
    os.makedirs('02_data/bronze', exist_ok=True)

    # 1. CSV
    print("  📄 Saving as CSV...")
    csv_path = '02_data/raw/csv/sensor_data.csv'
    df.to_csv(csv_path, index=False)
    csv_size = os.path.getsize(csv_path) / (1024 * 1024)
    print(f"     ✓ CSV saved: {csv_size:.2f} MB")

    # 2. JSON
    print("  📄 Saving as JSON...")
    json_path = '02_data/raw/json/sensor_data.json'
    # Convert timestamp column to string before saving to JSON
    df_json_copy = df.copy()
    df_json_copy['timestamp'] = df_json_copy['timestamp'].astype(str)
    df_json_copy.to_json(json_path, orient='records', indent=2, date_format='iso')
    json_size = os.path.getsize(json_path) / (1024 * 1024)
    print(f"     ✓ JSON saved: {json_size:.2f} MB")

    # 3. Parquet
    print("  📦 Saving as Parquet...")
    try:
        parquet_path = '02_data/bronze/sensor_data.parquet'
        # Add 'date_str' column here BEFORE saving any parquet file
        df['date_str'] = pd.to_datetime(df['timestamp']).dt.strftime('%Y-%m-%d')
        df.to_parquet(parquet_path, engine='pyarrow', compression='snappy', index=False)
        parquet_size = os.path.getsize(parquet_path) / (1024 * 1024)
        print(f"     ✓ Parquet saved: {parquet_size:.2f} MB")

        # Partitioned Parquet
        print("  📦 Saving as Partitioned Parquet (by date)...")
        partition_path = '02_data/bronze/sensor_data_partitioned'
        # 'date_str' already exists
        df.to_parquet(partition_path, engine='pyarrow', compression='snappy',
                      partition_cols=['date_str'], index=False)
        print(f"     ✓ Partitioned Parquet saved")

        print()
        print(f"📊 SIZE COMPARISON:")
        print(f"  CSV:      {csv_size:.2f} MB (baseline)")
        print(f"  JSON:     {json_size:.2f} MB ({json_size/csv_size*100:.1f}% of CSV)")
        print(f"  Parquet:  {parquet_size:.2f} MB ({parquet_size/csv_size*100:.1f}% of CSV)")
        print(f"  Savings:  {csv_size - parquet_size:.2f} MB ({(1-parquet_size/csv_size)*100:.1f}% reduction)")
        print()

        return {'csv_mb': csv_size, 'json_mb': json_size, 'parquet_mb': parquet_size}

    except Exception as e:
        print(f"     ⚠️ Parquet failed: {e}")
        bronze_path = '02_data/bronze/sensor_data.csv'
        df.to_csv(bronze_path, index=False)
        print(f"     ✓ Bronze CSV saved (fallback)")
        return {'csv_mb': csv_size, 'json_mb': json_size}

def create_data_dictionary(df):
    """
    Create data dictionary documentation
    """
    print("📖 Creating data dictionary...")

    os.makedirs('06_docs', exist_ok=True)

    # Make sure 'date_str' column exists if it was added for parquet
    if 'date_str' not in df.columns:
         df['date_str'] = pd.to_datetime(df['timestamp']).dt.strftime('%Y-%m-%d')


    data_dict = {
        'Column': list(df.columns),
        'Data Type': [str(dtype) for dtype in df.dtypes],
        'Description': [
            'Unique sensor identifier (SENS_ROOMID_DHT22)',
            'Timestamp of reading (YYYY-MM-DD HH:MM:SS)',
            'Room ID code',
            'Full room name (Indonesian)',
            'Building name (Lab Kebidanan Mega)',
            'Floor number (1-3)', # Floor number should match ROOMS config (always 1?)
            'Room type (Lab Praktik/Storage)',
            'Temperature in Celsius (20-30°C)',
            'Relative humidity (40-75%)',
            'CO2 concentration in ppm (400-1800)',
            'Light intensity in lux (0-700)',
            'Number of occupants',
            'Maximum room capacity',
            'Occupancy percentage',
            'Air conditioning status (ON/OFF)',
            'Alert level (NORMAL/WARNING/CRITICAL)',
            'Detailed alert information',
            'Thermal comfort assessment',
            'Energy efficiency score (0-100)',
            'Day of the week',
            'Weekend indicator (Yes/No)',
            'Date (YYYY-MM-DD)',
            'Hour of day (0-23)',
            'Date string for partitioning (YYYY-MM-DD)' # <-- DESKRIPSI KE-24
        ],
        'Sample Values': [str(df[col].iloc[0]) for col in df.columns]
    }

    # Debugging print statements
    print(f"  Jumlah Kolom: {len(data_dict['Column'])}")
    print(f"  Jumlah Tipe Data: {len(data_dict['Data Type'])}")
    print(f"  Jumlah Deskripsi: {len(data_dict['Description'])}")
    print(f"  Jumlah Contoh Nilai: {len(data_dict['Sample Values'])}")

    # Check if lengths match before creating DataFrame
    lengths = {
        'Column': len(data_dict['Column']),
        'Data Type': len(data_dict['Data Type']),
        'Description': len(data_dict['Description']),
        'Sample Values': len(data_dict['Sample Values'])
    }
    if len(set(lengths.values())) != 1:
        print("   ⚠️ ERROR: Panjang list untuk Data Dictionary tidak sama!")
        print(f"      Panjang: {lengths}")
        # Optionally, raise an error or exit here
        # raise ValueError("Data dictionary array lengths do not match.")
        return # Stop function if lengths mismatch

    dict_df = pd.DataFrame(data_dict)
    dict_df.to_csv('06_docs/data_dictionary.csv', index=False)

    with open('06_docs/data_dictionary.md', 'w') as f:
        f.write("# Data Dictionary - Lab Kebidanan Mega\n\n")
        f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(f"**Building:** Lab Kebidanan Mega\n")
        f.write(f"**Total Records:** {len(df):,}\n")
        f.write(f"**Rooms:** {len(ROOMS)} (9 Lab Praktik + 1 Depo Alat)\n")
        f.write(f"**Sensor Type:** {SENSOR_TYPE}\n\n")
        f.write("## Room List\n\n")
        for room_id, info in ROOMS.items():
            f.write(f"- **{room_id}**: {info['name']} (Lantai {info['floor']}, Kapasitas {info['capacity']})\n")
        f.write("\n## Column Definitions\n\n")
        f.write(dict_df.to_markdown(index=False))

    print("  ✓ Data dictionary saved\n")

# Main execution
if __name__ == "__main__":
    df = generate_dataset()

    print("📋 DATA PREVIEW:")
    print(df.head(10).to_string())
    print()

    print("📊 ENVIRONMENTAL STATISTICS:")
    print(df[['temperature', 'humidity', 'co2_ppm', 'light_lux', 'occupancy_count']].describe())
    print()

    print("🏥 ROOM STATISTICS:")
    room_stats = df.groupby('room_id').agg({
        'temperature': 'mean',
        'humidity': 'mean',
        'occupancy_count': 'mean'
    }).round(2)
    print(room_stats)
    print()

    sizes = save_multiple_formats(df)
    # Ensure df passed to create_data_dictionary includes 'date_str'
    create_data_dictionary(df)

    print("=" * 60)
    print("✅ ALL DONE! Lab Kebidanan Mega Dataset Ready")
    print("=" * 60)
    print()
    print("📁 Generated files:")
    print("  - 02_data/raw/csv/sensor_data.csv")
    print("  - 02_data/raw/json/sensor_data.json")
    print("  - 02_data/bronze/sensor_data.parquet")
    print("  - 02_data/bronze/sensor_data_partitioned/") # Added partitioned folder
    print("  - 06_docs/data_dictionary.csv")
    print("  - 06_docs/data_dictionary.md")
    print()
    print("🚀 Next steps:")
    print("  1. python 03_pipeline/batch_pipeline.py")
    print("  2. python 04_queries/sample_queries.py")
    print("  3. python 05_evaluation/benchmark_formats.py")