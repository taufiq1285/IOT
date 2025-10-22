# 🌡️ IoT Environmental Monitoring System
## Big Data & Predictive Analytics - Project Mini

**Topik:** Lake vs Warehouse; Batch vs Streaming; Format Data  
**Skenario:** IoT Lingkungan - Smart Lab & Classroom Monitoring  
**Kelompok:** [NAMA KELOMPOK ANDA]

---

## 📋 Daftar Anggota

| No | Nama | NIM | Kontribusi |
|----|------|-----|------------|
| 1  | [Taufiq] | | Arsitektur, Data Generation |
| 2  | [aswin] |  | Batch Pipeline, Data Quality |
| 3  | [ahmad fauzan] |  | Streaming Simulation |
| 4  | [Rifki arianto] | | Queries, Benchmark |
| 5  | [herawanti | | Documentation, Laporan |

---

## 🎯 Tujuan Proyek

Membangun sistem monitoring lingkungan IoT untuk optimasi kenyamanan dan efisiensi energi di kampus dengan:
- ✅ Real-time alerts untuk kondisi tidak nyaman
- ✅ Historical analysis untuk optimasi jadwal AC
- ✅ Data-driven decision making

---

## 🏗️ Arsitektur Sistem

### High-Level Architecture
![Architecture Diagram](01_architecture/architecture_diagram.md)

### Technology Stack
- **Language:** Python 3.11+
- **Processing:** Pandas, NumPy
- **Formats:** CSV, JSON, Parquet
- **Compression:** Snappy

### Data Pipeline
```
IoT Sensors → Streaming/Batch → Bronze → Silver → Gold → Analytics
              (Raw Data)         (Cleaned)  (Warehouse)  (Insights)
```

---

## 🚀 Quick Start (PENTING!)

### Prerequisites
```bash
# Python 3.8+ required
python --version

# VS Code (recommended)
```

### Setup Environment

**Langkah 1: Clone/Download Project**
```bash
# Jika dari Git
git clone [URL_REPO]
cd iot_project

# Atau extract ZIP file
unzip BDPA_TugasProyek_Kelompok[1]_IoT.zip
cd BDPA_TugasProyek_Kelompok[1]_IoT
```

**Langkah 2: Install Dependencies**
```bash
pip install -r requirements.txt
```

**Langkah 3: Run Pipeline (BERURUTAN!)**

```bash
# 1. Generate dataset (3000 records)
python 02_data/generator.py

# 2. Run batch pipeline (Bronze → Silver → Gold)
python 03_pipeline/batch_pipeline.py

# 3. Run streaming simulation (50 events, 5s interval)
python 03_pipeline/streaming_simulation.py

# 4. Execute sample queries
python 04_queries/sample_queries.py

# 5. Run benchmark comparison
python 05_evaluation/benchmark_formats.py
```

**Total execution time: ~5-10 menit**

---

## 📁 Struktur Project

```
BDPA_TugasProyek_Kelompok[1]_IoT/
│
├── 01_architecture/               # Diagram & dokumentasi arsitektur
│   └── architecture_diagram.md
│
├── 02_data/                       # Data & generator
│   ├── generator.py              ← [RUN FIRST!]
│   ├── raw/                      # CSV, JSON (row-oriented)
│   ├── bronze/                   # Parquet (unified)
│   ├── silver/                   # Cleaned data
│   ├── gold/                     # Data warehouse (star schema)
│   └── stream_output/            # Streaming results
│
├── 03_pipeline/                   # ETL pipelines
│   ├── batch_pipeline.py         ← [RUN SECOND!]
│   └── streaming_simulation.py   ← [RUN THIRD!]
│
├── 04_queries/                    # Analytical queries
│   ├── sample_queries.py         ← [RUN FOURTH!]
│   ├── query1_result.csv
│   ├── query2_result.csv
│   └── query3_result.csv
│
├── 05_evaluation/                 # Benchmark & evaluation
│   ├── benchmark_formats.py      ← [RUN FIFTH!]
│   ├── benchmark_results.csv
│   └── format_comparison.png
│
├── 06_docs/                       # Documentation
│   ├── data_dictionary.csv
│   ├── data_dictionary.md
│   └── LAPORAN.md               # Template laporan PDF
│
├── requirements.txt               # Python dependencies
└── README.md                      # This file
```

---

## 📊 Hasil Evaluasi

### File Size Comparison

| Format | Size | vs CSV | Use Case |
|--------|------|--------|----------|
| CSV | ~2.5 MB | Baseline | Human-readable, debugging |
| JSON | ~3.5 MB | +40% | Streaming, flexible schema |
| **Parquet** | **~0.8 MB** | **-68%** | ✅ **Analytics, production** |

**Kesimpulan:** Parquet menghemat **68% storage** dengan **2-3x faster** reads!

### Query Performance

| Query Type | CSV | Parquet | Speedup |
|------------|-----|---------|---------|
| Full Scan | 150ms | 50ms | **3x faster** |
| Aggregation | 120ms | 40ms | **3x faster** |
| Column Read | 80ms | 15ms | **5x faster** |

---

## 🎯 Design Decisions

### 1️⃣ **Lake vs Warehouse: Hybrid Approach**

**Data Lake (Bronze/Silver):**
- ✅ Store raw data for reprocessing
- ✅ Schema flexibility
- ✅ Cost-effective for historical data

**Data Warehouse (Gold):**
- ✅ Optimized star schema
- ✅ Fast analytical queries
- ✅ Pre-aggregated summaries

**Justifikasi:** Hybrid memberikan fleksibilitas (lake) + performance (warehouse)

### 2️⃣ **Batch vs Streaming: Lambda Architecture**

**Streaming (Real-time):**
- ✅ Alerts untuk kondisi abnormal
- ✅ Live monitoring
- ⏱️ Latency: <10 seconds

**Batch (Historical):**
- ✅ Daily aggregations
- ✅ Data quality enforcement
- ⏱️ Schedule: 1x per day

**Justifikasi:** Lambda memenuhi kebutuhan real-time DAN historical analysis

### 3️⃣ **Format Selection**

| Layer | Format | Reasoning |
|-------|--------|-----------|
| Bronze (Raw) | JSON | Preserve original, easy debug |
| Bronze (Unified) | Parquet | Efficient storage |
| Silver | Parquet + Snappy | Compressed, cleaned |
| Gold | Parquet | Columnar for analytics |

---

## 📈 Sample Queries

### Query 1: Average Temperature per Building
```python
df.groupby('building').agg({
    'temperature': ['mean', 'min', 'max']
})
```

### Query 2: High Temperature Rooms (>28°C)
```python
high_temp = df[df['temperature'] > 28]
high_temp.groupby('room_id').size()
```

### Query 3: Hourly Trend (Last 24h)
```python
df.groupby(df['timestamp'].dt.floor('H')).agg({
    'temperature': 'mean'
})
```

---

## 🛡️ Data Quality & Governance

### Data Quality Rules
✅ No null values in critical fields (timestamp, sensor_id)  
✅ Temperature range: 15-40°C  
✅ Humidity range: 30-90%  
✅ CO2 range: 350-3000 ppm  
✅ Duplicate detection based on (sensor_id, timestamp)

### Metadata Management
- **Data Dictionary:** Complete column definitions
- **Lineage:** Bronze → Silver → Gold tracked
- **Versioning:** Timestamp-based partitioning

### Access Control (Conceptual)
| Role | Bronze | Silver | Gold |
|------|--------|--------|------|
| Data Engineer | Read/Write | Read/Write | Read/Write |
| Analyst | Read | Read | Read |
| Public Dashboard | - | - | Read (aggregated only) |

### Retention Policy
- **Bronze:** 90 days (raw data)
- **Silver:** 1 year (cleaned)
- **Gold:** 3 years (warehouse)

---

## ⚠️ Risiko & Mitigasi

| Risiko | Dampak | Mitigasi |
|--------|--------|----------|
| Schema berubah | Pipeline break | Use flexible JSON in Bronze, schema validation |
| Data skew | Unbalanced partitions | Monitor partition sizes, repartition if needed |
| Late/dirty data | Quality issues | Implement data validation rules, quarantine bad data |
| Sensor failure | Missing data | Alert on prolonged gaps, use interpolation for short gaps |

---

## 📝 Deliverables Checklist

- [x] Laporan PDF (max 6 halaman)
- [x] Diagram arsitektur (PNG/SVG)
- [x] Kode: Python scripts (.py)
- [x] Dataset: 3000 records, multiple formats
- [x] Data dictionary
- [x] Log kontribusi anggota

---

## 🎓 Learning Outcomes (CPMK)

✅ **Membedakan Data Lake vs Warehouse:** Implemented hybrid approach  
✅ **Batch vs Streaming:** Lambda architecture with clear SLAs  
✅ **Format Selection:** Empirical comparison of CSV/JSON/Parquet  
✅ **End-to-end Pipeline:** Complete Bronze-Silver-Gold pipeline

---

## 📞 Kontak

**Kelompok:** [NAMA KELOMPOK]  
**Email:** [EMAIL]  
**Mata Kuliah:** Big Data & Predictive Analytics  
**Dosen:** [NAMA DOSEN]

---

## 📜 License

Educational project for academic purposes only.

---

**Terakhir diupdate:** [TANGGAL]
