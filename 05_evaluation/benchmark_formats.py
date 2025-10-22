"""
Format Benchmark - Compare CSV, JSON, Parquet performance
Evaluates: file size, write speed, read speed, query performance
"""

import pandas as pd
import numpy as np
import time
import os
import matplotlib.pyplot as plt
import seaborn as sns

print("=" * 60)
print("  FILE FORMAT BENCHMARK")
print("=" * 60)
print()

# Load original data
print("📥 Loading test dataset...")
df = pd.read_parquet('02_data/bronze/sensor_data.parquet')
print(f"  Dataset: {len(df):,} records, {len(df.columns)} columns")
print()

# Prepare test directory
test_dir = '05_evaluation/test_data'
os.makedirs(test_dir, exist_ok=True)

# ==================== FILE SIZE COMPARISON ====================
print("📦 BENCHMARK 1: File Size Comparison")
print("-" * 60)

formats = ['csv', 'json', 'parquet']
size_results = {}

for fmt in formats:
    filepath = f"{test_dir}/test_data.{fmt}"
    
    if fmt == 'csv':
        df.to_csv(filepath, index=False)
    elif fmt == 'json':
        df.to_json(filepath, orient='records', date_format='iso')
    elif fmt == 'parquet':
        df.to_parquet(filepath, engine='pyarrow', compression='snappy', index=False)
    
    size_mb = os.path.getsize(filepath) / (1024 * 1024)
    size_results[fmt] = size_mb
    print(f"  {fmt.upper():8s}: {size_mb:8.2f} MB")

# Calculate savings
csv_size = size_results['csv']
json_size = size_results['json']
parquet_size = size_results['parquet']

print()
print("  Compression Efficiency:")
print(f"    JSON vs CSV:    {(json_size/csv_size - 1)*100:+.1f}% ({json_size-csv_size:+.2f} MB)")
print(f"    Parquet vs CSV: {(parquet_size/csv_size - 1)*100:+.1f}% ({parquet_size-csv_size:+.2f} MB)")
print(f"    Savings:        {(1-parquet_size/csv_size)*100:.1f}% space reduction")
print()

# ==================== WRITE PERFORMANCE ====================
print("✍️  BENCHMARK 2: Write Performance")
print("-" * 60)

write_results = {}

for fmt in formats:
    filepath = f"{test_dir}/write_test.{fmt}"
    
    start = time.time()
    
    if fmt == 'csv':
        df.to_csv(filepath, index=False)
    elif fmt == 'json':
        df.to_json(filepath, orient='records')
    elif fmt == 'parquet':
        df.to_parquet(filepath, compression='snappy', index=False)
    
    elapsed = time.time() - start
    write_results[fmt] = elapsed
    print(f"  {fmt.upper():8s}: {elapsed*1000:8.2f} ms")

print()

# ==================== READ PERFORMANCE ====================
print("📖 BENCHMARK 3: Read Performance")
print("-" * 60)

read_results = {}

for fmt in formats:
    filepath = f"{test_dir}/test_data.{fmt}"
    
    start = time.time()
    
    if fmt == 'csv':
        _ = pd.read_csv(filepath)
    elif fmt == 'json':
        _ = pd.read_json(filepath)
    elif fmt == 'parquet':
        _ = pd.read_parquet(filepath)
    
    elapsed = time.time() - start
    read_results[fmt] = elapsed
    print(f"  {fmt.upper():8s}: {elapsed*1000:8.2f} ms")

print()

# ==================== QUERY PERFORMANCE ====================
print("🔍 BENCHMARK 4: Query Performance (Aggregation)")
print("-" * 60)

query_results = {}

# Test query: GROUP BY building, AVG temperature
for fmt in formats:
    filepath = f"{test_dir}/test_data.{fmt}"
    
    start = time.time()
    
    if fmt == 'csv':
        temp_df = pd.read_csv(filepath)
    elif fmt == 'json':
        temp_df = pd.read_json(filepath)
    elif fmt == 'parquet':
        temp_df = pd.read_parquet(filepath)
    
    # Execute query
    _ = temp_df.groupby('building')['temperature'].mean()
    
    elapsed = time.time() - start
    query_results[fmt] = elapsed
    print(f"  {fmt.upper():8s}: {elapsed*1000:8.2f} ms")

print()

# ==================== COLUMNAR ACCESS TEST ====================
print("📊 BENCHMARK 5: Columnar Access (Single Column Read)")
print("-" * 60)

columnar_results = {}

for fmt in formats:
    filepath = f"{test_dir}/test_data.{fmt}"
    
    start = time.time()
    
    if fmt == 'csv':
        temp_df = pd.read_csv(filepath, usecols=['temperature'])
    elif fmt == 'json':
        temp_df = pd.read_json(filepath)
        _ = temp_df['temperature']
    elif fmt == 'parquet':
        temp_df = pd.read_parquet(filepath, columns=['temperature'])
    
    elapsed = time.time() - start
    columnar_results[fmt] = elapsed
    print(f"  {fmt.upper():8s}: {elapsed*1000:8.2f} ms")

print()

# ==================== SUMMARY TABLE ====================
print("=" * 60)
print("  BENCHMARK SUMMARY")
print("=" * 60)

summary = pd.DataFrame({
    'Format': ['CSV', 'JSON', 'Parquet'],
    'Size (MB)': [size_results['csv'], size_results['json'], size_results['parquet']],
    'Write (ms)': [write_results['csv']*1000, write_results['json']*1000, write_results['parquet']*1000],
    'Read (ms)': [read_results['csv']*1000, read_results['json']*1000, read_results['parquet']*1000],
    'Query (ms)': [query_results['csv']*1000, query_results['json']*1000, query_results['parquet']*1000],
    'Column Read (ms)': [columnar_results['csv']*1000, columnar_results['json']*1000, columnar_results['parquet']*1000]
})

summary = summary.round(2)
print(summary.to_string(index=False))
print()

# Save results
summary.to_csv('05_evaluation/benchmark_results.csv', index=False)
print("💾 Results saved to: 05_evaluation/benchmark_results.csv")
print()

# ==================== VISUALIZATION ====================
print("📈 Creating visualization...")

fig, axes = plt.subplots(2, 2, figsize=(12, 10))
fig.suptitle('File Format Comparison - IoT Sensor Data', fontsize=16, fontweight='bold')

# 1. File Size
axes[0, 0].bar(summary['Format'], summary['Size (MB)'], color=['#3498db', '#e74c3c', '#2ecc71'])
axes[0, 0].set_title('Storage Size')
axes[0, 0].set_ylabel('Size (MB)')
axes[0, 0].grid(axis='y', alpha=0.3)

for i, v in enumerate(summary['Size (MB)']):
    axes[0, 0].text(i, v + 0.1, f'{v:.2f}', ha='center', va='bottom')

# 2. Read Performance
axes[0, 1].bar(summary['Format'], summary['Read (ms)'], color=['#3498db', '#e74c3c', '#2ecc71'])
axes[0, 1].set_title('Read Performance (Lower is Better)')
axes[0, 1].set_ylabel('Time (ms)')
axes[0, 1].grid(axis='y', alpha=0.3)

# 3. Query Performance
axes[1, 0].bar(summary['Format'], summary['Query (ms)'], color=['#3498db', '#e74c3c', '#2ecc71'])
axes[1, 0].set_title('Query Performance (Lower is Better)')
axes[1, 0].set_ylabel('Time (ms)')
axes[1, 0].grid(axis='y', alpha=0.3)

# 4. Overall Comparison (normalized)
metrics = ['Size', 'Read', 'Query', 'Column Read']
csv_baseline = [1.0, 1.0, 1.0, 1.0]
json_normalized = [
    size_results['json'] / size_results['csv'],
    read_results['json'] / read_results['csv'],
    query_results['json'] / query_results['csv'],
    columnar_results['json'] / columnar_results['csv']
]
parquet_normalized = [
    size_results['parquet'] / size_results['csv'],
    read_results['parquet'] / read_results['csv'],
    query_results['parquet'] / query_results['csv'],
    columnar_results['parquet'] / columnar_results['csv']
]

x = np.arange(len(metrics))
width = 0.25

axes[1, 1].bar(x - width, csv_baseline, width, label='CSV', color='#3498db')
axes[1, 1].bar(x, json_normalized, width, label='JSON', color='#e74c3c')
axes[1, 1].bar(x + width, parquet_normalized, width, label='Parquet', color='#2ecc71')
axes[1, 1].set_title('Normalized Performance (CSV = 1.0)')
axes[1, 1].set_ylabel('Relative Performance')
axes[1, 1].set_xticks(x)
axes[1, 1].set_xticklabels(metrics, rotation=15)
axes[1, 1].legend()
axes[1, 1].axhline(y=1.0, color='gray', linestyle='--', alpha=0.5)
axes[1, 1].grid(axis='y', alpha=0.3)

plt.tight_layout()
plt.savefig('05_evaluation/format_comparison.png', dpi=150, bbox_inches='tight')
print("✅ Visualization saved to: 05_evaluation/format_comparison.png")
print()

# ==================== RECOMMENDATIONS ====================
print("=" * 60)
print("  💡 RECOMMENDATIONS")
print("=" * 60)
print()
print("✅ For RAW/BRONZE Layer:")
print("   → Use JSON for streaming events (flexible schema)")
print("   → Human-readable, easy to debug")
print()
print("✅ For SILVER/GOLD Layer:")
print("   → Use PARQUET with Snappy compression")
print(f"   → {(1-parquet_size/csv_size)*100:.1f}% space savings vs CSV")
print(f"   → {(1-read_results['parquet']/read_results['csv'])*100:.1f}% faster reads")
print("   → Excellent for analytics (columnar)")
print()
print("❌ Avoid CSV/JSON for:")
print("   → Large datasets (>100MB)")
print("   → Analytics workloads")
print("   → Production data warehouses")
print()
print("=" * 60)
print("✅ Benchmark completed!")
print("=" * 60)
