# 🚀 Power BI Setup & Dashboard Layout Guide

This guide walks you through connecting **Power BI Desktop** to your data marts (via cloud GitHub URLs, local CSVs, or MySQL), configuring the 4-page executive report, and enabling **automated cloud scheduled refreshes**.

---

## 🔌 Step 1: Connecting Power BI to Data

You have three connectivity options:

### 🌟 Option A: Connect via GitHub Cloud Web URLs (Recommended for Automated Refresh)
> **Zero Gateway Required!** Because your GitHub Actions bot commits fresh data daily to GitHub, connecting directly to GitHub Raw URLs allows **Power BI Service (`app.powerbi.com`)** to refresh automatically in the cloud.

1. In **Power BI Desktop**, go to **Transform Data** (Power Query Editor).
2. For each query, open the **Advanced Editor** and paste the respective M script from [`bi/power_query_m_scripts.md`](power_query_m_scripts.md).
3. Base URLs for direct web connection:
   * `dim_dates`: `https://raw.githubusercontent.com/TejalGB/automotive-operations-intelligence/main/data/marts/dim_dates.csv`
   * `dim_dealers`: `https://raw.githubusercontent.com/TejalGB/automotive-operations-intelligence/main/data/marts/dim_dealers.csv`
   * `dim_exchange_rates`: `https://raw.githubusercontent.com/TejalGB/automotive-operations-intelligence/main/data/marts/dim_exchange_rates.csv`
   * `dim_geography`: `https://raw.githubusercontent.com/TejalGB/automotive-operations-intelligence/main/data/marts/dim_geography.csv`
   * `dim_vehicles`: `https://raw.githubusercontent.com/TejalGB/automotive-operations-intelligence/main/data/marts/dim_vehicles.csv`
   * `fct_charging_telematics`: `https://raw.githubusercontent.com/TejalGB/automotive-operations-intelligence/main/data/marts/fct_charging_telematics.csv`
   * `fct_vehicle_sales`: `https://raw.githubusercontent.com/TejalGB/automotive-operations-intelligence/main/data/marts/fct_vehicle_sales.csv`
   * `fct_warranty_claims`: `https://raw.githubusercontent.com/TejalGB/automotive-operations-intelligence/main/data/marts/fct_warranty_claims.csv`
4. Set privacy level to **Anonymous** (public repo).
5. Click **Close & Apply**.

---

### Option B: Connect via Local CSV Folder (Zero-Setup Offline)
1. In Power BI Desktop $\to$ Click **Get Data** $\to$ Select **Folder**.
2. Browse to your repository directory: `.../automotive-operations-intelligence/data/marts/`.
3. Select and load the CSV files.

---

### Option C: Connect via MySQL Database (Enterprise DW)
1. Open **Power BI Desktop** $\to$ Click **Get Data** $\to$ Select **MySQL database**.
2. **Server:** `localhost:3306` (or cloud host) $\to$ **Database:** `auto_ops_dw`.
3. **Connectivity mode:** Select **Import** (or DirectQuery).
4. Select the analytical views (`vw_*`) or star schema tables (`dim_*` and `fct_*`).

---

## ⏰ Step 2: Enabling Cloud Scheduled Refresh in Power BI Service

Once your report is connected using **Option A (GitHub Web URLs)**:

1. In Power BI Desktop, click **Publish** (Home ribbon) $\to$ Select your workspace (e.g., **My Workspace**).
2. Log in to [app.powerbi.com](https://app.powerbi.com).
3. Navigate to your workspace $\to$ find the **Automotive_Operations_Dashboard** dataset $\to$ click the **three dots (...)** $\to$ **Settings**.
4. Under **Data source credentials**:
   * Click **Edit credentials** for each web URL.
   * Authentication method: **Anonymous** $\to$ Privacy level: **Organizational** (or Public) $\to$ Click **Sign in**.
5. Under **Scheduled refresh**:
   * Toggle **Keep your data up to date** to **On**.
   * Refresh frequency: **Daily**.
   * Time zone: Select your local time zone (e.g., **(UTC+05:30) Chennai, Kolkata, Mumbai, New Delhi**).
   * Time: Set to **08:00 AM** (30 minutes after GitHub Actions runs at 07:30 AM IST).
6. Click **Apply**.
7. **Result:** Your dashboard will automatically update every single morning without touching your computer!

---

## 🎨 Step 3: Dashboard Visual Layout by Page

### Page 1: 🏛️ Executive KPI Cockpit (C-Suite View)
* **Top KPI Cards (Row 1):**
  * Card 1: `Total Revenue EUR` (Formatted as `€###.## M`)
  * Card 2: `Total Volume Delivered` (Formatted as `#,### Units`)
  * Card 3: `Weighted Gross Margin %` (Formatted as `##.#%`)
  * Card 4: `Pure EV (BEV) Mix %` (Target gauge: Goal 60%)
  * Card 5: `YoY Volume Growth %` (Green/Red conditional formatting)
* **Main Visuals (Row 2):**
  * **Line & Clustered Column Chart:** X-axis = `dim_dates[month_name]`, Column = `Total Revenue EUR`, Line = `Pure EV Mix %`.
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

## 🔄 Step 4: Summary of Refresh Options

| Refresh Method | Frequency | Prerequisite | Gateway Needed? |
| :--- | :--- | :--- | :--- |
| **Power BI Service Scheduled Refresh (Web URLs)** | **Daily (Automated)** | Connect via GitHub Raw URLs | **No (Zero Gateway)** |
| **Power BI Desktop Manual Refresh** | On demand | Open `.pbix` and click "Refresh" | No |
| **On-Premises Data Gateway** | Daily (Scheduled) | Local PC must be powered on | Yes |
