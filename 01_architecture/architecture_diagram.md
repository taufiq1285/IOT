# Architecture Diagram - IoT Environmental Monitoring

# Lab Kebidanan Mega

## System Architecture (Lambda Architecture)

```mermaid
flowchart TB
    subgraph Sources["📡 DATA SOURCES"]
        S1[DHT22 Sensors<br/>Lab KTD]
        S2[DHT22 Sensors<br/>Lab ANC]
        S3[DHT22 Sensors<br/>Lab PNC]
        S4[DHT22 Sensors<br/>Lab INC]
        S5[DHT22 Sensors<br/>Lab BBL]
        S6[DHT22 Sensors<br/>Lab KB]
        S7[DHT22 Sensors<br/>Lab Konseling]
        S8[DHT22 Sensors<br/>Lab Komunitas]
        S9[DHT22 Sensors<br/>Lab Anak]
        S10[DHT22 Sensors<br/>Depo Alat]
    end

    subgraph Ingestion["🔄 DATA INGESTION"]
        direction LR
        B1[Batch Ingestion<br/>CSV/JSON<br/>Hourly]
        S1_Stream[Stream Ingestion<br/>Real-time Events<br/>5-10s interval]
    end

    subgraph Storage["💾 DATA LAKE (Bronze Layer)"]
        direction TB
        RAW_CSV[Raw CSV Files<br/>02_data/raw/csv/]
        RAW_JSON[Raw JSON Files<br/>02_data/raw/json/]
        BRONZE_PARQUET[Bronze Parquet<br/>02_data/bronze/<br/>Partitioned by date]
    end

    subgraph Processing["⚙️ DATA PROCESSING"]
        direction TB
        BATCH[Batch Pipeline<br/>Pandas/PySpark<br/>Cleaning & Validation]
        STREAM[Streaming Pipeline<br/>Micro-batch<br/>Window: 10 min]
    end

    subgraph Warehouse["🏛️ DATA WAREHOUSE"]
        direction TB
        subgraph Silver["Silver Layer - Cleaned"]
            SILVER_DATA[sensor_data_cleaned<br/>Validated & Enriched<br/>Parquet format]
        end
        
        subgraph Gold["Gold Layer - Star Schema"]
            DIM_ROOM[dim_room<br/>10 rooms]
            DIM_TIME[dim_time<br/>Hourly periods]
            DIM_ALERT[dim_alert<br/>Alert types]
            FACT[fact_sensor_readings<br/>Main metrics]
            AGG[summary_hourly<br/>Aggregations]
        end
    end

    subgraph Analytics["📈 ANALYTICS & SERVING"]
        direction LR
        QUERIES[SQL Queries<br/>Pandas Analysis]
        DASHBOARD[Streamlit Dashboard<br/>Real-time Monitoring]
        REPORTS[PDF Reports<br/>Daily/Weekly]
    end

    subgraph Governance["🔒 DATA GOVERNANCE"]
        QUALITY[Data Quality Rules<br/>Range checks, Duplicates]
        METADATA[Data Dictionary<br/>Schema documentation]
        SECURITY[Access Control<br/>Role-based]
    end

    %% Data Flow - Batch Path
    S1 & S2 & S3 & S4 & S5 --> B1
    S6 & S7 & S8 & S9 & S10 --> B1
    B1 --> RAW_CSV
    B1 --> RAW_JSON
    RAW_CSV --> BRONZE_PARQUET
    RAW_JSON --> BRONZE_PARQUET
    
    %% Data Flow - Stream Path
    S1 & S2 & S3 & S4 & S5 --> S1_Stream
    S6 & S7 & S8 & S9 & S10 --> S1_Stream
    S1_Stream --> STREAM
    
    %% Processing
    BRONZE_PARQUET --> BATCH
    STREAM --> BATCH
    BATCH --> SILVER_DATA
    
    %% Warehouse
    SILVER_DATA --> DIM_ROOM
    SILVER_DATA --> DIM_TIME
    SILVER_DATA --> DIM_ALERT
    SILVER_DATA --> FACT
    FACT --> AGG
    
    %% Analytics
    DIM_ROOM & DIM_TIME & DIM_ALERT & FACT & AGG --> QUERIES
    QUERIES --> DASHBOARD
    QUERIES --> REPORTS
    
    %% Governance
    QUALITY -.-> BATCH
    METADATA -.-> Storage
    SECURITY -.-> Warehouse

    style Sources fill:#e1f5ff
    style Ingestion fill:#fff4e1
    style Storage fill:#e8f5e9
    style Processing fill:#fff9e1
    style Warehouse fill:#f3e5f5
    style Analytics fill:#ffe1e1
    style Governance fill:#fafafa
```

## Architecture Decisions

### 1. **Hybrid Architecture (Lambda)**

- **Batch Path**: Hourly ingestion untuk historical analysis
- **Stream Path**: Real-time monitoring untuk immediate alerts
- **Reason**: Balance between latency & cost

### 2. **Data Lake + Warehouse Combination**

- **Lake (Bronze)**: Raw data preservation, schema flexibility
- **Warehouse (Gold)**: Star schema untuk efficient queries
- **Reason**: Best of both worlds

### 3. **Storage Format Strategy**

| Layer | Format | Reason |
|-------|--------|--------|
| Raw | CSV, JSON | Human-readable, debugging |
| Bronze | Parquet | Compression, partitioning |
| Silver | Parquet | Fast queries |
| Gold | Parquet | Optimized analytics |

### 4. **SLA & Latency Targets**

- **Batch**: 1-hour latency, 99.9% reliability
- **Stream**: <30s latency, 99.5% reliability
- **Queries**: <2s response time
- **Retention**: Raw (30 days), Processed (1 year)
