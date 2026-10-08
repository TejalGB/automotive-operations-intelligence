# 🚀 Power BI Setup & Dashboard Layout Guide

This guide walks you through connecting **Power BI Desktop** to your MySQL database (or local CSV marts) and building the 4-page executive report.

---

## 🔌 Step 1: Connecting Power BI to Data

You have two easy ways to connect in Power BI Desktop:

### Option A: Connect via MySQL Database (Recommended)
1. Open **Power BI Desktop** $\to$ Click **Get Data** $\to$ Select **MySQL database**.
2. **Server:** `localhost:3306` (or your MySQL host).
3. **Database:** `auto_ops_dw`.
4. **Data Connectivity mode:** Select **Import** (or DirectQuery).
5. Select the 3 Analytical Views (`vw_commercial_ev_transition`, `vw_ev_telematics_performance`, `vw_warranty_quality_early_warning`) OR the 7 raw Star Schema tables (`dim_*` and `fct_*`).
6. Click **Load**.

### Option B: Connect via Local CSV Folder (Zero-Setup)
1. In Power BI Desktop $\to$ Click **Get Data** $\to$ Select **Folder**.
2. Browse to your repository directory: `.../automotive-operations-intelligence/data/marts/`.
3. Select and load all 7 CSV files.

---

## 🎨 Step 2: Dashboard Visual Layout by Page

### Page 1: 🏛️ Executive KPI Cockpit (C-Suite View)
* **Top KPI Cards (Row 1):**
  * Card 1: `Total Revenue EUR` (Formatted as `€###.## M`)
  * Card 2: `Total Volume Delivered` (Formatted as `#,### Units`)
  * Card 3: `Weighted Gross Margin %` (Formatted as `##.#%`)
  * Card 4: `EV Sales Mix %` (Target gauge: Goal 50%)
  * Card 5: `YoY Volume Growth %` (Green/Red conditional formatting)
* **Main Visuals (Row 2):**
  * **Line & Clustered Column Chart:** X-axis = `dim_dates[month_name]`, Column = `Total Revenue EUR`, Line = `EV Sales Mix %`.
  * **Donut Chart:** Powertrain Mix (`Pure_EV`, `PHEV`, `MHEV`).
* **Bottom Visuals (Row 3):**
  * **Clustered Bar Chart:** Regional Revenue Contribution (`Nordics`, `Central_Europe`, `Americas`, `Western_Europe`).
  * **Decomposition Tree:** Total Gross Profit $\to$ Sales Region $\to$ Model Family $\to$ Trim Level.

---

### Page 2: 💰 Commercial Performance & Dealership Margins
* **Top KPI Cards:**
  * Card 1: `Discount Leakage %` (Benchmark: $< 5\%$)
  * Card 2: `D2C Share %` (Direct Studio sales proportion)
  * Card 3: `Avg Delivery Lead Days` (Benchmark: $< 21$ days)
* **Visuals:**
  * **Scatter Plot:** X-axis = `Discount Leakage %`, Y-axis = `Total Volume Delivered`, Size = `Total Revenue EUR`, Legend = `Dealer Name` (Identifies rogue discounting dealers).
  * **Matrix Table:** Rows = `Country Name` $\to$ `Dealer Name`, Values = `Volume Sold`, `Revenue`, `Gross Margin %`, `Discount Leakage %`.

---

### Page 3: ⚡ Connected EV Telematics & Battery Health Lab
* **Top KPI Cards:**
  * Card 1: `Total Energy Delivered MWh`
  * Card 2: `Avg Fast Charging Speed kW`
  * Card 3: `Cold Weather Speed Degradation Index`
* **Visuals:**
  * **Line Chart (Fast Charge Curve):** X-axis = `start_soc_pct` (binned by 10%), Y-axis = `Avg Fast Charging Speed kW`, Legend = `Ambient Temp Bracket`.
  * **Box / Scatter Plot:** `Ambient Temperature (°C)` vs `Battery Temp Delta (°C)`.
  * **Stacked Bar Chart:** Charging Sessions by `Charger Protocol` (`AC 11kW`, `DC 150kW`, `DC 250kW`).

---

### Page 4: 🔧 Quality Engineering & Warranty Early Warning
* **Top KPI Cards:**
  * Card 1: `Total Warranty Expense EUR`
  * Card 2: `Warranty Cost per Unit (CPU)`
  * Card 3: `Early Life CPTV at 6MIS` (Claims per 1,000 vehicles)
  * Card 4: `Safety Critical Claim %`
* **Visuals:**
  * **Pareto Chart:** Bars = `Total Warranty Spend by Component Category`, Line = `Cumulative Spend %`.
  * **Heatmap Matrix:** Rows = `Manufacturing Plant`, Columns = `Model Family`, Values = `Early Life CPTV at 6MIS` (Color scale Red = High failure spike).
  * **Table with Detail Drill-through:** `VIN`, `Failure Symptom Code`, `Months in Service`, `Mileage`, `Total Claim Cost EUR`.

---

## 🔄 Step 3: Refreshing Data
Whenever you run `python src/run_daily_pipeline.py --days 1`, simply click **Refresh** in the Power BI ribbon. All KPIs, DAX measures, and charts will recalculate instantly!
