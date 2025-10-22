# ⚡ EXECUTION CHECKLIST - URGENT MODE
## Deadline: Jam 1 Siang - Step-by-Step Guide

**WAKTU TOTAL: ~30-40 MENIT** (termasuk dokumentasi)

---

## 📋 PRE-FLIGHT CHECK (5 menit)

### ✅ Step 0: Verifikasi Environment
```bash
# Check Python version (need 3.8+)
python --version

# Install dependencies
pip install pandas numpy pyarrow matplotlib seaborn

# Navigate to project folder
cd iot_project
```

**Status:** [ ] DONE

---

## 🚀 EXECUTION SEQUENCE (25 menit)

### ✅ Step 1: Generate Dataset (2 menit)
```bash
python 02_data/generator.py
```

**Expected Output:**
- ✅ 3000 records generated
- ✅ Files created in `02_data/raw/` (CSV, JSON)
- ✅ Files created in `02_data/bronze/` (Parquet)
- ✅ Data dictionary created in `06_docs/`

**Checkpoint Questions:**
- [ ] File `02_data/raw/csv/sensor_data.csv` exists? (should be ~2.5 MB)
- [ ] File `02_data/bronze/sensor_data.parquet` exists? (should be ~0.8 MB)
- [ ] File `06_docs/data_dictionary.md` exists?

**If Error:** Check Python version, install missing packages

**Status:** [ ] DONE (___:___ AM/PM)

---

### ✅ Step 2: Run Batch Pipeline (3 menit)
```bash
python 03_pipeline/batch_pipeline.py
```

**Expected Output:**
- ✅ Bronze → Silver → Gold transformation
- ✅ Files in `02_data/silver/sensor_data_cleaned.parquet`
- ✅ Files in `02_data/gold/` (dim_room, dim_time, fact_sensor_readings)

**Checkpoint Questions:**
- [ ] Silver layer created? (`02_data/silver/sensor_data_cleaned.parquet`)
- [ ] Gold dimension tables created? (dim_room, dim_time, dim_alert)
- [ ] Fact table created with partitions? (`02_data/gold/fact_sensor_readings.parquet/`)

**If Error:** Check if Step 1 completed, verify file paths

**Status:** [ ] DONE (___:___ AM/PM)

---

### ✅ Step 3: Run Streaming Simulation (4 menit)
```bash
python 03_pipeline/streaming_simulation.py
```

**Expected Output:**
- ✅ 50 events generated (5 seconds interval)
- ✅ Real-time console output with alerts
- ✅ File `02_data/stream_output/streaming_events.jsonl`
- ✅ Micro-batch files created

**Checkpoint Questions:**
- [ ] See console output with temperature readings?
- [ ] File `02_data/stream_output/streaming_events.jsonl` exists?
- [ ] Any WARNING alerts shown? (should see some if temp >29°C)

**Notes:** 
- Will run for ~4 minutes (50 events × 5 seconds)
- Can press Ctrl+C to stop early if needed
- If running short on time, modify MAX_EVENTS to 20 (will finish in 2 min)

**Status:** [ ] DONE (___:___ AM/PM)

---

### ✅ Step 4: Execute Sample Queries (2 menit)
```bash
python 04_queries/sample_queries.py
```

**Expected Output:**
- ✅ Query 1: Average temp per building
- ✅ Query 2: High temp rooms (>28°C)
- ✅ Query 3: Hourly trend (24h)
- ✅ Execution times displayed (should be <100ms)
- ✅ CSV results in `04_queries/`

**Checkpoint Questions:**
- [ ] All 4 queries executed successfully?
- [ ] Execution times < 200ms?
- [ ] Result files created? (query1_result.csv, query2_result.csv, query3_result.csv)

**Status:** [ ] DONE (___:___ AM/PM)

---

### ✅ Step 5: Run Format Benchmark (3 menit)
```bash
python 05_evaluation/benchmark_formats.py
```

**Expected Output:**
- ✅ Size comparison (CSV, JSON, Parquet)
- ✅ Performance benchmarks (read, write, query)
- ✅ Visualization: `05_evaluation/format_comparison.png`
- ✅ CSV summary: `05_evaluation/benchmark_results.csv`

**Checkpoint Questions:**
- [ ] Parquet shows ~68% size reduction vs CSV?
- [ ] Parquet shows 2-5x faster query performance?
- [ ] PNG chart created successfully?

**SCREENSHOT THIS:** The console output showing size comparison!

**Status:** [ ] DONE (___:___ AM/PM)

---

## 📄 DOCUMENTATION (10 menit)

### ✅ Step 6: Customize Report Template
```bash
# Open in VS Code or any editor
code 06_docs/LAPORAN_TEMPLATE.md
```

**TODO:**
1. [ ] Replace all [PLACEHOLDER] with your group info
2. [ ] Add member names and contributions
3. [ ] Copy benchmark results from console
4. [ ] Take screenshots of:
   - Architecture diagram (from 01_architecture/)
   - Format comparison chart (from 05_evaluation/)
   - Console output dari query execution

**Status:** [ ] DONE (___:___ AM/PM)

---

### ✅ Step 7: Update README
```bash
code README.md
```

**TODO:**
1. [ ] Fill in group member table
2. [ ] Update contact info
3. [ ] Add date completed

**Status:** [ ] DONE (___:___ AM/PM)

---

## 📦 PACKAGING & SUBMISSION (5 menit)

### ✅ Step 8: Verify All Files
**Checklist:**
```
├── 01_architecture/
│   └── [x] architecture_diagram.md
├── 02_data/
│   ├── [x] generator.py
│   ├── raw/
│   │   ├── csv/ [x] sensor_data.csv
│   │   └── json/ [x] sensor_data.json
│   ├── bronze/ [x] sensor_data.parquet
│   ├── silver/ [x] sensor_data_cleaned.parquet
│   ├── gold/
│   │   ├── [x] dim_room.parquet
│   │   ├── [x] dim_time.parquet
│   │   ├── [x] dim_alert.parquet
│   │   ├── [x] fact_sensor_readings.parquet/
│   │   └── [x] summary_hourly.parquet
│   └── stream_output/ [x] streaming_events.jsonl
├── 03_pipeline/
│   ├── [x] batch_pipeline.py
│   └── [x] streaming_simulation.py
├── 04_queries/
│   ├── [x] sample_queries.py
│   └── [x] query*_result.csv (3 files)
├── 05_evaluation/
│   ├── [x] benchmark_formats.py
│   ├── [x] benchmark_results.csv
│   └── [x] format_comparison.png
├── 06_docs/
│   ├── [x] data_dictionary.md
│   └── [x] LAPORAN.pdf (export from template!)
├── [x] README.md
└── [x] requirements.txt
```

### ✅ Step 9: Create ZIP File
```bash
# Option 1: Command line
zip -r BDPA_TugasProyek_KelompokX_IoT.zip iot_project/

# Option 2: Manual
# Right-click folder → Compress/Send to ZIP
```

**Verify ZIP:**
- [ ] Size < 20 MB? (should be ~5-10 MB)
- [ ] Extract test: can unzip successfully?

**Status:** [ ] DONE (___:___ AM/PM)

---

### ✅ Step 10: Upload to Drive & Submit
1. [ ] Upload ZIP to Google Drive
2. [ ] Set sharing to "Anyone with link can view"
3. [ ] Copy share link
4. [ ] Submit link to LMS Edlink

**Google Drive Link:** ________________________________

**LMS Submission:** [ ] DONE (___:___ AM/PM)

---

## 🎯 QUICK TROUBLESHOOTING

### Problem: "ModuleNotFoundError: pandas"
**Solution:** `pip install pandas numpy pyarrow`

### Problem: "FileNotFoundError" in pipeline scripts
**Solution:** Make sure you run scripts IN ORDER (Step 1 → 2 → 3)

### Problem: Scripts running too slow
**Solution:** Reduce NUM_RECORDS in generator.py to 1000

### Problem: Streaming simulation stuck
**Solution:** Press Ctrl+C to stop, or reduce MAX_EVENTS to 20

### Problem: Can't create ZIP (file too large)
**Solution:** Delete `02_data/test_data/` folder (from benchmark)

---

## ⏰ TIME ALLOCATION GUIDE

**If you have LIMITED time, PRIORITIZE this sequence:**

### 30 Minutes Available:
1. Generate data (2 min) ✅ CRITICAL
2. Batch pipeline (3 min) ✅ CRITICAL
3. Skip streaming (or run with MAX_EVENTS=10)
4. Queries (2 min) ✅ CRITICAL
5. Benchmark (3 min) ✅ CRITICAL
6. Quick doc fill (5 min)
7. ZIP & upload (5 min)

### 45 Minutes Available:
- Do ALL steps as listed above

### 60 Minutes Available:
- Do all steps + POLISH documentation + add extra screenshots

---

## 📊 EXPECTED DELIVERABLES CHECKLIST

### Required Files:
- [x] Laporan PDF (6 pages max) - **EXPORT from LAPORAN_TEMPLATE.md**
- [x] Architecture diagram (PNG/SVG) - **Screenshot from Mermaid**
- [x] Python code (.py files) - **All in 02_data/, 03_pipeline/, 04_queries/, 05_evaluation/**
- [x] Dataset (CSV, JSON, Parquet) - **In 02_data/raw/ and bronze/**
- [x] Data dictionary - **In 06_docs/data_dictionary.md**
- [x] Contribution log - **In LAPORAN.pdf Lampiran**

### Naming:
File name: `BDPA_TugasProyek_Kelompok[X]_IoT.zip`

Example: `BDPA_TugasProyek_Kelompok5_IoT.zip`

---

## 🎓 PRESENTATION PREP (For next week)

**Recommended Slides (10-15 minutes):**
1. Cover (group, topic)
2. Problem & Scenario
3. Architecture Overview (THE DIAGRAM!)
4. Demo: Show running code (optional)
5. Results: Benchmark comparison chart
6. Lessons Learned
7. Q&A

**Practice Tips:**
- Each member speaks 2-3 minutes
- Emphasize WHY you made decisions (Lake+Warehouse, Lambda, Parquet)
- Show the format_comparison.png chart - very visual!

---

## ✅ FINAL CHECKLIST

Before submitting, verify:
- [ ] All scripts run without errors
- [ ] ZIP file < 20 MB
- [ ] README.md has group info filled
- [ ] LAPORAN.pdf exported (6 pages max)
- [ ] Data dictionary included
- [ ] Architecture diagram included
- [ ] Google Drive link works (test in incognito)
- [ ] LMS submission confirmed

---

## 🎉 SUCCESS CRITERIA

You'll know you're DONE when:
✅ All 10 steps completed
✅ ZIP file uploaded to Drive
✅ Link submitted to LMS
✅ Can re-download and extract ZIP successfully
✅ Laporan PDF is readable and complete

---

**GOOD LUCK! 🚀**

**Current Time:** ________
**Target Completion:** 1:00 PM
**Time Remaining:** ________ minutes

---

## 💡 PRO TIPS

1. **Work in parallel:** 
   - Person 1-3: Run scripts
   - Person 4-5: Work on documentation simultaneously

2. **Screenshot everything:** 
   - Console outputs
   - Successful script runs
   - Benchmark results

3. **Test early:**
   - Run generator.py FIRST to catch dependency issues

4. **Backup strategy:**
   - Keep original files
   - Make a copy before ZIP

5. **If behind schedule:**
   - Skip streaming simulation (nice-to-have)
   - Focus on: data generation, batch, queries, benchmark
   - Minimal documentation

---

**Remember:** 
- DONE is better than PERFECT
- Follow the sequence IN ORDER
- Don't skip Step 1 (generator) - everything depends on it!
- Keep this checklist open and mark progress ✅

**Let's GO! 💪**
