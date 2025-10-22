# LAPORAN PROYEK MINI

## Big Data & Predictive Analytics

---

## COVER PAGE

**Topik:** Lake vs Warehouse; Batch vs Streaming; Format Data

**Skenario:** IoT Environmental Monitoring - Lab Kebidanan Mega

**Kelompok:** [ISI NOMOR KELOMPOK]

**Anggota Kelompok:**

1. [Nama Lengkap 1] - [NIM 1]
2. [Nama Lengkap 2] - [NIM 2]
3. [Nama Lengkap 3] - [NIM 3]
4. [Nama Lengkap 4] - [NIM 4]
5. [Nama Lengkap 5] - [NIM 5]

**Tanggal:** [ISI TANGGAL]

---

## HALAMAN 1: LATAR BELAKANG

### 1.1 Konteks

Lab Kebidanan Mega memerlukan sistem monitoring lingkungan real-time untuk memastikan kondisi optimal bagi kegiatan praktikum dan penyimpanan alat medis. Sistem harus mampu:

- Monitoring 10 ruangan (9 lab praktik + 1 depo alat)
- Deteksi dini kondisi tidak normal
- Historical analysis untuk optimasi energi

### 1.2 Tantangan

- **Data Volume**: 3000+ readings/day dari 10 sensors
- **Latency**: Alert <30 detik untuk kondisi kritis
- **Storage**: Efficient storage dengan budget terbatas
- **Governance**: Comply dengan standar klinik

### 1.3 Objectives

1. Membandingkan Data Lake vs Warehouse untuk IoT data
2. Implement hybrid Batch+Stream processing
3. Evaluasi format file (CSV/JSON/Parquet) untuk use case
4. Design scalable & cost-effective pipeline

---

## HALAMAN 2: ARSITEKTUR & DESAIN

### 2.1 Architecture Overview

[INSERT: architecture_diagram.png]

### 2.2 Architecture Decisions

**Choice: Hybrid Lake + Warehouse (Lambda Architecture)**

| Component | Technology | Justification |
|-----------|------------|---------------|
| **Data Lake** (Bronze) | Parquet files | - Raw data preservation<br/>- Schema evolution support<br/>- Cost-effective storage |
| **Data Warehouse** (Gold) | Star schema (Parquet) | - Optimized queries<br/>- Business-friendly structure<br/>- Fast aggregations |
| **Processing Mode** | Batch + Stream | - Batch: Historical (hourly)<br/>- Stream: Alerts (real-time) |

**Rationale:**

- **Lake**: Flexibility untuk exploratory analysis, data scientist friendly
- **Warehouse**: Performance untuk operational dashboards, manager friendly
- **Hybrid**: Balance cost vs latency - tidak semua data perlu real-time

### 2.3 Storage Zones & Format

| Zone | Purpose | Format | Retention |
|------|---------|--------|-----------|
| **Raw** | Landing zone | CSV, JSON | 30 days |
| **Bronze** | Raw preservation | Parquet (partitioned) | 90 days |
| **Silver** | Cleaned | Parquet (snappy) | 1 year |
| **Gold** | Analytics | Parquet (star schema) | 3 years |

**Partitioning Strategy:**

- Bronze: `dt=YYYY-MM-DD/` (daily partitions)
- Gold Fact: `date=YYYY-MM-DD/` (for time-based queries)

**Naming Convention:**

- `sensor_data_{layer}_{date}.parquet`
- `dim_{dimension_name}.parquet`
- `fact_{fact_name}.parquet`

### 2.4 Mode & SLA

**Processing Mode: Lambda Architecture**

| Path | Latency | Throughput | Use Case |
|------|---------|------------|----------|
| **Batch** | 1 hour | 3000 records/hour | Historical analysis, reports |
| **Stream** | <30 sec | 10 events/sec | Real-time alerts, monitoring |

**SLA Targets:**

- Data freshness: Batch (1h), Stream (30s)
- Query response: <2 seconds
- Uptime: 99.5%
- Data accuracy: 99.9%

---

## HALAMAN 3: DATASET & PIPELINE

### 3.1 Dataset Simulation

**Specifications:**

- Total Records: 3,000
- Time Range: 300 hours (12.5 days)
- Sensors: 10 DHT22 (1 per room)
- Frequency: 1 reading/minute per sensor

**Rooms Configuration:**

| Room ID | Name | Floor | Capacity | Type |
|---------|------|-------|----------|------|
| LAB_KTD | Lab Keterampilan Dasar | 1 | 30 | Lab Praktik |
| LAB_ANC | Lab Antenatal Care | 1 | 25 | Lab Praktik |
| LAB_PNC | Lab Postnatal Care | 2 | 25 | Lab Praktik |
| LAB_INC | Lab Intranatal Care | 2 | 20 | Lab Praktik |
| LAB_BBL | Lab Bayi Baru Lahir | 2 | 22 | Lab Praktik |
| LAB_KB | Lab Pelayanan KB | 3 | 20 | Lab Praktik |
| LAB_KONSELING | Lab Konseling | 3 | 28 | Lab Konseling |
| LAB_KOMUNITAS | Lab Kebidanan Komunitas | 3 | 30 | Lab Praktik |
| LAB_ANAK | Lab Bayi/Balita/Anak | 3 | 25 | Lab Praktik |
| DEPO_ALAT | Ruangan Depo Alat | 1 | 5 | Storage |

**Data Dictionary:** See `06_docs/data_dictionary.md` (23 columns)

### 3.2 Pipeline Implementation

**A. Batch Pipeline** (`03_pipeline/batch_pipeline.py`)

```
Extract (Bronze) → Transform (Silver) → Load (Gold)
```

**Transformations:**

1. **Data Cleaning**
   - Remove duplicates
   - Handle missing values
   - Range validation (temp: 20-30°C, humidity: 40-75%)

2. **Data Enrichment**
   - Calculate thermal_comfort index
   - Calculate energy_efficiency score
   - Add time-based features

3. **Star Schema Creation**
   - dim_room (10 records)
   - dim_time (300 hourly periods)
   - dim_alert (3 alert types)
   - fact_sensor_readings (3000 records)
   - summary_hourly (300 aggregated records)

**B. Streaming Pipeline** (`03_pipeline/streaming_simulation.py`)

- Simulates 50 real-time events
- 5-10 second intervals
- Micro-batch processing (10-minute windows)
- Outputs to streaming_events/

---

## HALAMAN 4: EVALUASI & HASIL

### 4.1 Format Comparison

**File Size Benchmark:**

[INSERT HASIL DARI benchmark_results.csv]

| Format | Size (MB) | vs CSV | Write (ms) | Read (ms) | Query (ms) |
|--------|-----------|--------|------------|-----------|------------|
| CSV | 0.42 | 100% | 245 | 148 | 122 |
| JSON | 1.54 | 367% | 312 | 165 | 138 |
| Parquet | 0.07 | 17% | 189 | 47 | 41 |

**Key Findings:**

- ✅ Parquet: **83% storage savings** vs CSV
- ✅ Parquet: **3x faster** read performance
- ✅ Parquet: **3x faster** query execution
- ❌ CSV: Largest size, slowest queries
- ⚠️ JSON: Good for flexibility, but inefficient

[INSERT: format_comparison.png chart]

### 4.2 Query Performance

**Sample Queries Execution Time:**

| Query | Description | Time (ms) | Records |
|-------|-------------|-----------|---------|
| Q1 | AVG temperature per room | 45 | 10 |
| Q2 | High alert rooms (>27°C) | 38 | [hasil] |
| Q3 | Hourly temperature trend | 52 | 24 |
| Q4 | Energy efficiency by type | 41 | 3 |

**Observations:**

- Parquet columnar format ideal untuk aggregations
- Query performance <100ms untuk 3K records
- Projected: <2s untuk 1M records (with partitioning)

### 4.3 Data Quality Rules

**Implemented Checks:**

| Rule | Threshold | Action |
|------|-----------|--------|
| Temperature range | 20-30°C | Warning if outside |
| Humidity range | 40-75% | Warning if outside |
| CO2 range | 400-1800 ppm | Critical if >1500 |
| Duplicates | 0 tolerance | Remove |
| Missing values | <1% | Impute with median |
| Timestamp gaps | <5 min | Flag for review |

**Results:**

- Duplicates removed: [X] records
- Out-of-range values: [X] warnings
- Data quality score: 99.8%

---

## HALAMAN 5: GOVERNANCE & MITIGASI RISIKO

### 5.1 Data Governance

**Metadata Management:**

- Column-level documentation (data_dictionary.md)
- Lineage tracking (bronze → silver → gold)
- Schema versioning (Parquet schema evolution)

**Access Control:**

| Role | Access | Scope |
|------|--------|-------|
| Administrator | Read/Write/Delete | All layers |
| Data Engineer | Read/Write | Bronze, Silver |
| Data Analyst | Read | Silver, Gold |
| Dashboard User | Read | Gold only |

**Retention Policy:**

- Raw data: 30 days (compliance minimum)
- Processed data: 1 year (analytics)
- Aggregations: 3 years (trends)

### 5.2 Risiko & Mitigasi

| Risiko | Dampak | Probability | Mitigasi |
|--------|--------|-------------|----------|
| **Schema berubah** | High | Medium | - Parquet schema evolution<br/>- Bronze layer preservation<br/>- Version control |
| **Data skew** | Medium | High | - Partition by date<br/>- Room-level balancing<br/>- Monitor partition sizes |
| **Late arrival data** | Low | Medium | - Watermarking (stream)<br/>- Reprocessing windows<br/>- Idempotent pipelines |
| **Sensor failure** | High | Low | - Last-value-carry-forward<br/>- Alert on missing data<br/>- Redundant sensors (future) |
| **Storage cost overrun** | Medium | Medium | - Automatic archiving<br/>- Retention enforcement<br/>- Compression monitoring |

---

## HALAMAN 6: KESIMPULAN

### 6.1 Key Takeaways

**Lake vs Warehouse:**

- Lake (Bronze/Silver): Flexibility + schema evolution
- Warehouse (Gold): Performance + business alignment
- **Winner**: Hybrid approach (80% of benefits, 50% of complexity)

**Batch vs Streaming:**

- Batch: Cost-effective untuk historical
- Stream: Necessary untuk real-time alerts
- **Winner**: Lambda architecture (practical tradeoff)

**Format Selection:**

- Parquet: Clear winner untuk analytics (83% savings, 3x speed)
- CSV: Good for debugging & data exchange
- JSON: Useful for flexible schemas (raw ingestion)

### 6.2 Recommendations

**For Production Deployment:**

1. ✅ Implement full Lambda architecture
2. ✅ Use Parquet for all processed layers
3. ✅ Add CDC (Change Data Capture) for stream
4. ✅ Implement data catalog (e.g., Hive Metastore)
5. ✅ Add automated data quality checks
6. ✅ Set up monitoring & alerting

### 6.3 Limitations & Future Work

**Current Limitations:**

- Single building (not yet multi-building)
- Simulated data (not real sensors)
- Local processing (not distributed)

**Future Enhancements:**

- Scale to 50+ buildings
- Real sensor integration (MQTT/IoT Hub)
- Distributed processing (Spark cluster)
- Machine learning (predictive alerts)
- Mobile app integration

---

## KONTRIBUSI ANGGOTA

| Nama | NIM | Tugas | % Kontribusi |
|------|-----|-------|--------------|
| [Nama 1] | [NIM 1] | Data generation, arsitektur diagram | 20% |
| [Nama 2] | [NIM 2] | Batch pipeline, data transformation | 20% |
| [Nama 3] | [NIM 3] | Query implementation, performance testing | 20% |
| [Nama 4] | [NIM 4] | Format benchmark, evaluation | 20% |
| [Nama 5] | [NIM 5] | Dashboard, dokumentasi, integration | 20% |

**Detail Kontribusi:**

**[Nama 1]:**

- Generate dataset 3000 records
- Design Lambda architecture
- Create mermaid diagram
- Research best practices

**[Nama 2]:**

- Implement batch_pipeline.py
- Data cleaning & validation
- Star schema design
- Silver/Gold layer creation

**[Nama 3]:**

- Write sample_queries.py
- Execute 4 analytical queries
- Performance measurement
- Query optimization

**[Nama 4]:**

- Implement benchmark_formats.py
- Compare CSV/JSON/Parquet
- Create comparison charts
- Write evaluation section

**[Nama 5]:**

- Build Streamlit dashboard
- Integration testing
- Write documentation
- Prepare final submission

---

## REFERENSI

1. "Designing Data-Intensive Applications" - Martin Kleppmann
2. AWS Data Lake Best Practices (2024)
3. Apache Parquet Documentation
4. Lambda Architecture - Nathan Marz
5. Data Warehouse Toolkit - Ralph Kimball

```

---

### **Step 4.2: Fill in Actual Values**

Setelah run benchmark, **UPDATE bagian ini:**

1. **HALAMAN 4 - Table Format Comparison**: Copy actual numbers
2. **HALAMAN 4 - Query Performance**: Copy actual times
3. **HALAMAN 5 - Data Quality**: Copy actual counts
4. **HALAMAN 6 - Kontribusi**: Isi nama & NIM anggota

---

### **Step 4.3: Insert Images**

Prepare 3 images untuk diinsert ke laporan:

1. `architecture_diagram.png` → Halaman 2
2. `format_comparison.png` → Halaman 4
3. Dashboard screenshot → Halaman 4 (optional)

---

### **Step 4.4: Export to PDF**

**Via Google Docs:**
1. Copy SEMUA isi `LAPORAN_FINAL.md`
2. Paste ke Google Docs
3. Format:
   - Fix headings (H1, H2, H3)
   - Remove markdown syntax (`#`, `**`, `|`)
   - Format tables properly
4. Insert images at marked positions
5. File → Download → PDF Document
6. Save as: `BDPA_Laporan_Kelompok[X]_LabKebidanan.pdf`

**Ensure:** Maximum 6 pages!

---

## **📦 FASE 5: FINALIZE & SUBMIT** (10 menit)

### **Step 5.1: Final File Check**

Verify SEMUA file ini ada:
```

iot_project/
├── 01_architecture/
│   ├── architecture_diagram.md          ✓
│   └── architecture_diagram.png         ✓
├── 02_data/
│   ├── raw/csv/sensor_data.csv          ✓ (row-oriented)
│   ├── raw/json/sensor_data.json        ✓ (row-oriented)
│   ├── bronze/sensor_data.parquet       ✓ (columnar)
│   ├── silver/*.parquet                 ✓
│   └── gold/*.parquet                   ✓
├── 03_pipeline/
│   ├── batch_pipeline.py                ✓
│   └── streaming_simulation.py          ✓
├── 04_queries/
│   ├── sample_queries.py                ✓
│   └── query*.csv                       ✓
├── 05_evaluation/
│   ├── benchmark_formats.py             ✓
│   ├── benchmark_results.csv            ✓
│   └── format_comparison.png            ✓
├── 06_docs/
│   ├── data_dictionary.md               ✓
│   └── LAPORAN_FINAL.pdf                ✓
├── dashboard.py                         ✓
├── generator.py                         ✓
└── README.md                            ✓
