"""
Streaming Simulation - Real-time IoT Sensor Events
Simulates sensor data arriving every 5-10 seconds
"""

import pandas as pd
import numpy as np
from datetime import datetime
import time
import os
import json

class IoTStreamSimulator:
    def __init__(self, interval_seconds=5, max_events=100):
        self.interval = interval_seconds
        self.max_events = max_events
        self.event_count = 0
        self.stream_buffer = []
        
        # Setup output directory
        os.makedirs('02_data/stream_output', exist_ok=True)
        
        # Rooms configuration
        self.rooms = [
            {'room_id': 'LAB_A101', 'building': 'Gedung A', 'capacity': 40},
            {'room_id': 'LAB_A201', 'building': 'Gedung A', 'capacity': 35},
            {'room_id': 'KELAS_B101', 'building': 'Gedung B', 'capacity': 50},
        ]
    
    def generate_event(self):
        """Generate a single sensor event"""
        timestamp = datetime.now()
        hour = timestamp.hour
        
        # Select random room
        room = self.rooms[np.random.randint(0, len(self.rooms))]
        
        # Generate realistic values
        is_class_hour = 8 <= hour <= 16
        
        if is_class_hour:
            occupancy_pct = np.random.uniform(0.5, 0.9)
            base_temp = 27.0
        else:
            occupancy_pct = np.random.uniform(0, 0.2)
            base_temp = 24.0
        
        occupancy_count = int(room['capacity'] * occupancy_pct)
        temperature = base_temp + (occupancy_count * 0.1) + np.random.normal(0, 0.5)
        humidity = 70 - (temperature - 25) * 1.5 + np.random.normal(0, 2)
        co2 = 420 + (occupancy_count * 30) + np.random.normal(0, 40)
        
        # Alerts
        alerts = []
        if temperature > 29:
            alerts.append('HIGH_TEMP')
        if co2 > 1200:
            alerts.append('HIGH_CO2')
        
        event = {
            'event_id': f"EVT_{self.event_count:06d}",
            'timestamp': timestamp.isoformat(),
            'room_id': room['room_id'],
            'building': room['building'],
            'temperature': round(temperature, 2),
            'humidity': round(humidity, 2),
            'co2_ppm': int(co2),
            'occupancy_count': occupancy_count,
            'occupancy_pct': round(occupancy_pct * 100, 1),
            'alert_status': 'WARNING' if alerts else 'NORMAL',
            'alert_details': ','.join(alerts) if alerts else None
        }
        
        self.event_count += 1
        return event
    
    def process_event(self, event):
        """
        Process incoming event (mini transformation)
        Simulates real-time processing
        """
        # Add processing timestamp
        event['processed_at'] = datetime.now().isoformat()
        
        # Calculate thermal comfort
        temp = event['temperature']
        humid = event['humidity']
        
        if 22 <= temp <= 26 and 40 <= humid <= 60:
            event['thermal_comfort'] = 'Comfortable'
        elif temp > 28:
            event['thermal_comfort'] = 'Too Hot'
        else:
            event['thermal_comfort'] = 'Acceptable'
        
        # Air quality
        if event['co2_ppm'] < 800:
            event['air_quality'] = 'Excellent'
        elif event['co2_ppm'] < 1200:
            event['air_quality'] = 'Good'
        else:
            event['air_quality'] = 'Moderate'
        
        return event
    
    def write_to_sink(self, event):
        """Write processed event to output (simulates sink)"""
        # Append to JSON Lines file (common streaming format)
        output_file = '02_data/stream_output/streaming_events.jsonl'
        with open(output_file, 'a') as f:
            f.write(json.dumps(event) + '\n')
        
        # Also add to buffer for batch micro-aggregation
        self.stream_buffer.append(event)
        
        # Every 10 events, create a micro-batch
        if len(self.stream_buffer) >= 10:
            self.create_microbatch()
    
    def create_microbatch(self):
        """Create micro-batch from buffer (simulates mini aggregation)"""
        if not self.stream_buffer:
            return
        
        df = pd.DataFrame(self.stream_buffer)
        
        # Micro-aggregation by room
        agg = df.groupby('room_id').agg({
            'temperature': 'mean',
            'humidity': 'mean',
            'co2_ppm': 'mean',
            'occupancy_count': 'mean'
        }).round(2)
        
        agg['window_start'] = df['timestamp'].min()
        agg['window_end'] = df['timestamp'].max()
        agg['event_count'] = df.groupby('room_id').size()
        
        # Save micro-batch
        batch_id = datetime.now().strftime('%Y%m%d_%H%M%S')
        agg.to_csv(f'02_data/stream_output/microbatch_{batch_id}.csv')
        
        print(f"  📦 Micro-batch created: {len(self.stream_buffer)} events aggregated")
        
        # Clear buffer
        self.stream_buffer = []
    
    def run(self):
        """Run the streaming simulation"""
        print("=" * 60)
        print("  STREAMING SIMULATION - IoT Sensor Events")
        print("=" * 60)
        print(f"  Interval: {self.interval} seconds")
        print(f"  Max events: {self.max_events}")
        print(f"  Output: 02_data/stream_output/")
        print("=" * 60)
        print()
        print("🔴 STREAMING STARTED... (Press Ctrl+C to stop)")
        print()
        
        try:
            while self.event_count < self.max_events:
                # Generate event
                event = self.generate_event()
                
                # Process event
                processed_event = self.process_event(event)
                
                # Write to sink
                self.write_to_sink(processed_event)
                
                # Display event
                status_icon = "⚠️" if processed_event['alert_status'] == 'WARNING' else "✅"
                print(f"{status_icon} Event #{self.event_count:03d} | "
                      f"{processed_event['room_id']} | "
                      f"Temp: {processed_event['temperature']:.1f}°C | "
                      f"CO2: {processed_event['co2_ppm']} ppm | "
                      f"{processed_event['thermal_comfort']}")
                
                # Wait for next event
                time.sleep(self.interval)
            
            # Process remaining buffer
            if self.stream_buffer:
                self.create_microbatch()
            
            print()
            print("=" * 60)
            print(f"✅ Streaming simulation completed!")
            print(f"  Total events: {self.event_count}")
            print(f"  Output file: 02_data/stream_output/streaming_events.jsonl")
            print("=" * 60)
            
        except KeyboardInterrupt:
            print("\n\n⏸️  Streaming stopped by user")
            if self.stream_buffer:
                self.create_microbatch()
            print(f"  Total events processed: {self.event_count}")

if __name__ == "__main__":
    # Configuration
    INTERVAL = 5  # seconds between events
    MAX_EVENTS = 50  # total events to generate (set rendah untuk demo)
    
    # Run simulation
    simulator = IoTStreamSimulator(interval_seconds=INTERVAL, max_events=MAX_EVENTS)
    simulator.run()
    
    print()
    print("📊 STREAM ANALYSIS:")
    
    # Load and analyze all events
    df_stream = pd.read_json('02_data/stream_output/streaming_events.jsonl', lines=True)
    
    print(f"  Total events: {len(df_stream)}")
    print(f"  Rooms monitored: {df_stream['room_id'].nunique()}")
    print(f"  Alerts triggered: {(df_stream['alert_status'] == 'WARNING').sum()}")
    print()
    print("  Average metrics per room:")
    print(df_stream.groupby('room_id')[['temperature', 'humidity', 'co2_ppm']].mean().round(2))
    print()
    print("🎯 Streaming simulation results saved!")
