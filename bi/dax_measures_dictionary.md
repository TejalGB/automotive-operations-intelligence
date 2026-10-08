# 📊 Power BI DAX Measures Dictionary & Data Model Specification

## 1. Data Model Relationships (Star Schema)

Ensure the following **1-to-many ($1 \to *)$ single-direction** relationships are established in Power BI:

| From Table (Dimension) | Primary Key | To Table (Fact) | Foreign Key | Cardinality |
| :--- | :--- | :--- | :--- | :--- |
| `dim_dates` | `date_id` | `fct_vehicle_sales` | `date_id` | $1 \to *$ |
| `dim_dates` | `date_id` | `fct_charging_telematics` | `date_id` | $1 \to *$ |
| `dim_dates` | `date_id` | `fct_warranty_claims` | `date_id` | $1 \to *$ |
| `dim_vehicles` | `vehicle_id` | `fct_vehicle_sales` | `vehicle_id` | $1 \to *$ |
| `dim_vehicles` | `vehicle_id` | `fct_charging_telematics` | `vehicle_id` | $1 \to *$ |
| `dim_vehicles` | `vehicle_id` | `fct_warranty_claims` | `vehicle_id` | $1 \to *$ |
| `dim_geography` | `geo_id` | `fct_vehicle_sales` | `geo_id` | $1 \to *$ |
| `dim_geography` | `geo_id` | `fct_warranty_claims` | `geo_id` | $1 \to *$ |
| `dim_dealers` | `dealer_id` | `fct_vehicle_sales` | `dealer_id` | $1 \to *$ |
| `dim_dealers` | `dealer_id` | `fct_warranty_claims` | `dealer_id` | $1 \to *$ |

---

## 2. Core DAX Measures by Dashboard Page

### 📄 Page 1: Executive KPI Cockpit (C-Suite Macro View)

```dax
// 1. Total Net Revenue (EUR Millions)
Total Revenue EUR = 
SUM(fct_vehicle_sales[net_revenue_eur]) / 1000000

// 2. Total Delivered Volume (Units)
Total Volume Delivered = 
COUNTROWS(fct_vehicle_sales)

// 3. Total Gross Profit (EUR Millions)
Total Gross Profit EUR = 
SUM(fct_vehicle_sales[gross_profit_eur]) / 1000000

// 4. Weighted Gross Margin %
Weighted Gross Margin % = 
DIVIDE(
    SUM(fct_vehicle_sales[gross_profit_eur]),
    SUM(fct_vehicle_sales[net_revenue_eur]),
    0
)

// 5. EV Sales Mix Share %
EV Sales Mix % = 
DIVIDE(
    CALCULATE(COUNTROWS(fct_vehicle_sales), dim_vehicles[powertrain_type] = "Pure_EV"),
    COUNTROWS(fct_vehicle_sales),
    0
)

// 6. Year-over-Year (YoY) Volume Growth %
YoY Volume Growth % = 
VAR CurrentVolume = [Total Volume Delivered]
VAR PriorYearVolume = CALCULATE([Total Volume Delivered], SAMEPERIODLASTYEAR(dim_dates[full_date]))
RETURN
DIVIDE(CurrentVolume - PriorYearVolume, PriorYearVolume, 0)
```

---

### 📄 Page 2: Commercial Performance & Dealership Margin Health

```dax
// 7. Discount Leakage % (Excluding Subscriptions - INC0841203)
Discount Leakage % = 
DIVIDE(
    CALCULATE(
        SUM(fct_vehicle_sales[dealer_discount_local]) * SELECTEDVALUE(dim_exchange_rates[exchange_rate_to_eur], 1.0),
        fct_vehicle_sales[sale_channel] IN {"Dealer_Wholesale", "Online_D2C"}
    ),
    CALCULATE(
        SUM(dim_vehicles[base_msrp_eur]),
        fct_vehicle_sales[sale_channel] IN {"Dealer_Wholesale", "Online_D2C"}
    ),
    0
)

// 8. Direct-to-Consumer (D2C) Share %
D2C Share % = 
DIVIDE(
    CALCULATE(COUNTROWS(fct_vehicle_sales), fct_vehicle_sales[sale_channel] = "Online_D2C"),
    COUNTROWS(fct_vehicle_sales),
    0
)

// 9. Average Order-to-Delivery Lead Days
Avg Delivery Lead Days = 
AVERAGE(fct_vehicle_sales[delivery_lead_days])
```

---

### 📄 Page 3: Connected EV Telematics & Battery Health Lab

```dax
// 10. Total Energy Delivered (MWh)
Total Energy Delivered MWh = 
SUM(fct_charging_telematics[energy_delivered_kwh]) / 1000

// 11. Average Fast-Charging Speed (kW)
Avg Fast Charging Speed kW = 
CALCULATE(
    AVERAGE(fct_charging_telematics[avg_charging_speed_kw]),
    fct_charging_telematics[charger_protocol] IN {"DC_Fast_150kW", "DC_UltraFast_250kW"}
)

// 12. Sub-Zero Charging Degradation Index
// Ratio of average charging speed in sub-zero temps vs. optimal conditions
Cold Weather Speed Degradation Index = 
VAR SubZeroSpeed = CALCULATE(AVERAGE(fct_charging_telematics[avg_charging_speed_kw]), fct_charging_telematics[ambient_temp_celsius] < 0)
VAR OptimalSpeed = CALCULATE(AVERAGE(fct_charging_telematics[avg_charging_speed_kw]), fct_charging_telematics[ambient_temp_celsius] >= 15)
RETURN
DIVIDE(SubZeroSpeed, OptimalSpeed, 1.0)
```

---

### 📄 Page 4: Quality Engineering & Warranty Early Warning

```dax
// 13. Total Warranty Expense (EUR)
Total Warranty Expense EUR = 
SUM(fct_warranty_claims[total_claim_cost_eur])

// 14. Warranty Cost per Unit (CPU)
Warranty Cost per Unit = 
DIVIDE(
    [Total Warranty Expense EUR],
    [Total Volume Delivered],
    0
)

// 15. Early-Life Claims per 1,000 Vehicles (CPTV at 6 MIS)
Early Life CPTV at 6MIS = 
VAR EarlyClaims = CALCULATE(COUNTROWS(fct_warranty_claims), fct_warranty_claims[months_in_service] <= 6)
VAR TotalUnits = [Total Volume Delivered]
RETURN
DIVIDE(EarlyClaims, TotalUnits, 0) * 1000

// 16. Safety-Critical Claim Share %
Safety Critical Claim % = 
DIVIDE(
    CALCULATE(COUNTROWS(fct_warranty_claims), fct_warranty_claims[is_safety_critical] = TRUE()),
    COUNTROWS(fct_warranty_claims),
    0
)
```
