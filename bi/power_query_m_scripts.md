# 🌐 Power Query (M) Scripts: Cloud Web Connector for Power BI

Use these exact Power Query (M) scripts to connect **Power BI Desktop** directly to your live GitHub-hosted CSV data marts. 

> **Why this matters for your project:**  
> Connecting via GitHub Raw URLs allows **Power BI Service (`app.powerbi.com`)** to perform **automated daily scheduled refreshes in the cloud with ZERO on-premises data gateway or local computer required**.

---

## 📋 Table of Contents
1. [`dim_dates`](#1-dim_dates)
2. [`dim_dealers`](#2-dim_dealers)
3. [`dim_exchange_rates`](#3-dim_exchange_rates)
4. [`dim_geography`](#4-dim_geography)
5. [`dim_vehicles`](#5-dim_vehicles)
6. [`fct_charging_telematics`](#6-fct_charging_telematics)
7. [`fct_vehicle_sales`](#7-fct_vehicle_sales)
8. [`fct_warranty_claims`](#8-fct_warranty_claims)

---

## How to Apply in Power BI Desktop
1. Open your `.pbix` in **Power BI Desktop**.
2. Click **Transform Data** in the Home ribbon to launch **Power Query Editor**.
3. For each existing query (or click **New Source $\to$ Blank Query**):
   * Click **Advanced Editor** in the Home ribbon.
   * Replace the entire content with the respective snippet below.
   * Click **Done**.
4. Set privacy level to **Organizational** or **Anonymous** if prompted.
5. Click **Close & Apply**.

---

### 1. `dim_dates`
```powerquery
let
    Source = Csv.Document(Web.Contents("https://raw.githubusercontent.com/TejalGB/automotive-operations-intelligence/main/data/marts/dim_dates.csv"),[Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.None]),
    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    #"Changed Type" = Table.TransformColumnTypes(#"Promoted Headers",{
        {"date_id", Int64.Type}, 
        {"full_date", type date}, 
        {"month_name", type text}, 
        {"month_num", Int64.Type}, 
        {"calendar_quarter", type text}, 
        {"calendar_year", Int64.Type}, 
        {"fiscal_quarter", type text}
    })
in
    #"Changed Type"
```

---

### 2. `dim_dealers`
```powerquery
let
    Source = Csv.Document(Web.Contents("https://raw.githubusercontent.com/TejalGB/automotive-operations-intelligence/main/data/marts/dim_dealers.csv"),[Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.None]),
    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    #"Changed Type" = Table.TransformColumnTypes(#"Promoted Headers",{
        {"dealer_id", type text}, 
        {"name", type text}, 
        {"geo_id", type text}, 
        {"channel", type text}
    })
in
    #"Changed Type"
```

---

### 3. `dim_exchange_rates`
```powerquery
let
    Source = Csv.Document(Web.Contents("https://raw.githubusercontent.com/TejalGB/automotive-operations-intelligence/main/data/marts/dim_exchange_rates.csv"),[Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.None]),
    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    #"Changed Type" = Table.TransformColumnTypes(#"Promoted Headers",{
        {"currency_code", type text}, 
        {"fx_rate_to_eur", type number}, 
        {"effective_year", Int64.Type}
    })
in
    #"Changed Type"
```

---

### 4. `dim_geography`
```powerquery
let
    Source = Csv.Document(Web.Contents("https://raw.githubusercontent.com/TejalGB/automotive-operations-intelligence/main/data/marts/dim_geography.csv"),[Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.None]),
    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    #"Changed Type" = Table.TransformColumnTypes(#"Promoted Headers",{
        {"geo_id", type text}, 
        {"country", type text}, 
        {"region", type text}, 
        {"currency", type text}, 
        {"fx_to_eur", type number}
    })
in
    #"Changed Type"
```

---

### 5. `dim_vehicles`
```powerquery
let
    Source = Csv.Document(Web.Contents("https://raw.githubusercontent.com/TejalGB/automotive-operations-intelligence/main/data/marts/dim_vehicles.csv"),[Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.None]),
    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    #"Changed Type" = Table.TransformColumnTypes(#"Promoted Headers",{
        {"vehicle_id", type text}, 
        {"vin", type text}, 
        {"model_family", type text}, 
        {"powertrain_type", type text}, 
        {"trim_level", type text}, 
        {"battery_nominal_kwh", type number}, 
        {"base_msrp_eur", type number}, 
        {"factory_unit_cost_eur", type number}
    })
in
    #"Changed Type"
```

---

### 6. `fct_charging_telematics`
```powerquery
let
    Source = Csv.Document(Web.Contents("https://raw.githubusercontent.com/TejalGB/automotive-operations-intelligence/main/data/marts/fct_charging_telematics.csv"),[Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.None]),
    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    #"Changed Type" = Table.TransformColumnTypes(#"Promoted Headers",{
        {"session_id", type text}, 
        {"vehicle_id", type text}, 
        {"date_id", Int64.Type}, 
        {"session_start_time", type datetime}, 
        {"session_end_time", type datetime}, 
        {"session_duration_minutes", type number}, 
        {"charger_protocol", type text}, 
        {"ambient_temp_celsius", type number}, 
        {"start_soc_pct", type number}, 
        {"end_soc_pct", type number}, 
        {"energy_delivered_kwh", type number}, 
        {"avg_charging_speed_kw", type number}, 
        {"battery_temp_start_celsius", type number}, 
        {"battery_temp_end_celsius", type number}, 
        {"battery_temp_delta_celsius", type number}, 
        {"battery_preconditioned", type logical}, 
        {"estimated_range_gained_km", type number}
    })
in
    #"Changed Type"
```

---

### 7. `fct_vehicle_sales`
```powerquery
let
    Source = Csv.Document(Web.Contents("https://raw.githubusercontent.com/TejalGB/automotive-operations-intelligence/main/data/marts/fct_vehicle_sales.csv"),[Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.None]),
    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    #"Changed Type" = Table.TransformColumnTypes(#"Promoted Headers",{
        {"sale_id", type text}, 
        {"vehicle_id", type text}, 
        {"dealer_id", type text}, 
        {"geo_id", type text}, 
        {"date_id", Int64.Type}, 
        {"order_date", type date}, 
        {"delivery_date", type date}, 
        {"delivery_lead_days", Int64.Type}, 
        {"sale_channel", type text}, 
        {"financing_type", type text}, 
        {"currency_code", type text}, 
        {"gross_list_price_local", type number}, 
        {"dealer_discount_local", type number}, 
        {"net_sale_price_local", type number}, 
        {"fx_rate_to_eur", type number}, 
        {"net_revenue_eur", type number}, 
        {"factory_cost_eur", type number}, 
        {"gross_profit_eur", type number}, 
        {"gross_margin_pct", type number}
    })
in
    #"Changed Type"
```

---

### 8. `fct_warranty_claims`
```powerquery
let
    Source = Csv.Document(Web.Contents("https://raw.githubusercontent.com/TejalGB/automotive-operations-intelligence/main/data/marts/fct_warranty_claims.csv"),[Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.None]),
    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    #"Changed Type" = Table.TransformColumnTypes(#"Promoted Headers",{
        {"claim_id", type text}, 
        {"vehicle_id", type text}, 
        {"dealer_id", type text}, 
        {"geo_id", type text}, 
        {"date_id", Int64.Type}, 
        {"repair_date", type date}, 
        {"component_category", type text}, 
        {"failure_symptom_code", type text}, 
        {"months_in_service", Int64.Type}, 
        {"mileage_at_failure_km", type number}, 
        {"labor_hours", type number}, 
        {"labor_cost_eur", type number}, 
        {"parts_cost_eur", type number}, 
        {"total_claim_cost_eur", type number}, 
        {"is_safety_critical", type logical}, 
        {"claim_status", type text}
    })
in
    #"Changed Type"
```
