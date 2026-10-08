-- ==============================================================================
-- PROJECT: Global Connected Automotive & Commercial Intelligence (AutoOps 360)
-- CLIENT PROFILE: Global Premium Nordic Automotive OEM (Anonymized)
-- DATABASE: MySQL 8.0+
-- FILE: 03_business_queries.sql
-- DESCRIPTION: 10 Enterprise Analytical Queries Answering Strategic C-Suite Questions
-- ==============================================================================

USE auto_ops_dw;

-- ==============================================================================
-- QUERY 1: EV Transition Pace & Pure EV Sales Share by Market (YoY Analysis)
-- Business Impact: Tracks regional progress toward the corporate 100% EV target.
-- ==============================================================================
WITH regional_ev_stats AS (
    SELECT 
        g.sales_region,
        d.calendar_year,
        COUNT(s.sale_id) AS total_units_sold,
        SUM(CASE WHEN v.powertrain_type = 'Pure_EV' THEN 1 ELSE 0 END) AS ev_units_sold,
        SUM(s.net_revenue_eur) AS total_revenue_eur,
        SUM(CASE WHEN v.powertrain_type = 'Pure_EV' THEN s.net_revenue_eur ELSE 0 END) AS ev_revenue_eur
    FROM fct_vehicle_sales s
    JOIN dim_vehicles v ON s.vehicle_id = v.vehicle_id
    JOIN dim_geography g ON s.geo_id = g.geo_id
    JOIN dim_dates d ON s.date_id = d.date_id
    GROUP BY g.sales_region, d.calendar_year
)
SELECT 
    sales_region,
    calendar_year,
    total_units_sold,
    ev_units_sold,
    ROUND((ev_units_sold / total_units_sold) * 100, 2) AS ev_unit_share_pct,
    ROUND(total_revenue_eur / 1000000.0, 2) AS total_rev_eur_millions,
    ROUND((ev_revenue_eur / total_revenue_eur) * 100, 2) AS ev_revenue_share_pct,
    -- YoY Growth in EV Units
    LAG(ev_units_sold, 1) OVER (PARTITION BY sales_region ORDER BY calendar_year) AS prev_year_ev_units,
    ROUND(
        ((ev_units_sold - LAG(ev_units_sold, 1) OVER (PARTITION BY sales_region ORDER BY calendar_year)) / 
         NULLIF(LAG(ev_units_sold, 1) OVER (PARTITION BY sales_region ORDER BY calendar_year), 0)) * 100, 2
    ) AS yoy_ev_unit_growth_pct
FROM regional_ev_stats
ORDER BY sales_region, calendar_year;


-- ==============================================================================
-- QUERY 2: Channel Profitability & Discount Leakage (Dealer vs. Direct Studio vs. Subscription)
-- Business Impact: Evaluates if Direct-to-Consumer preserves margin vs. dealer discounting.
-- ==============================================================================
SELECT 
    s.sale_channel,
    COUNT(s.sale_id) AS total_volume_delivered,
    ROUND(SUM(s.net_revenue_eur) / 1000000.0, 2) AS total_revenue_eur_millions,
    ROUND(SUM(s.gross_profit_eur) / 1000000.0, 2) AS gross_profit_eur_millions,
    ROUND((SUM(s.gross_profit_eur) / SUM(s.net_revenue_eur)) * 100, 2) AS weighted_gross_margin_pct,
    ROUND(AVG(s.gross_margin_pct), 2) AS avg_unit_margin_pct,
    -- Discount leakage % of total MSRP value
    ROUND(
        (SUM(s.dealer_discount_local * s.fx_rate_to_eur) / 
         SUM(s.gross_list_price_local * s.fx_rate_to_eur)) * 100, 2
    ) AS discount_leakage_pct,
    ROUND(AVG(s.delivery_lead_days), 1) AS avg_delivery_lead_days
FROM fct_vehicle_sales s
GROUP BY s.sale_channel
ORDER BY weighted_gross_margin_pct DESC;


-- ==============================================================================
-- QUERY 3: Cold-Weather EV Charging Throughput & Battery Pre-Conditioning Efficacy
-- Business Impact: Quantifies real-world DC fast-charge degradation in Subarctic winters.
-- ==============================================================================
SELECT 
    CASE 
        WHEN ambient_temp_celsius < 0.0 THEN 'Sub-Zero (< 0°C)'
        WHEN ambient_temp_celsius BETWEEN 0.0 AND 15.0 THEN 'Moderate (0°C to 15°C)'
        ELSE 'Optimal (> 15°C)'
    END AS temp_category,
    charger_protocol,
    battery_preconditioned,
    COUNT(session_id) AS total_sessions,
    ROUND(AVG(session_duration_minutes), 1) AS avg_duration_mins,
    ROUND(AVG(energy_delivered_kwh), 2) AS avg_kwh_delivered,
    ROUND(AVG(avg_charging_speed_kw), 2) AS avg_charging_speed_kw,
    ROUND(AVG(battery_temp_delta_celsius), 2) AS avg_battery_temp_rise_c
FROM fct_charging_telematics
WHERE charger_protocol IN ('DC_Fast_150kW', 'DC_UltraFast_250kW')
GROUP BY 
    CASE 
        WHEN ambient_temp_celsius < 0.0 THEN 'Sub-Zero (< 0°C)'
        WHEN ambient_temp_celsius BETWEEN 0.0 AND 15.0 THEN 'Moderate (0°C to 15°C)'
        ELSE 'Optimal (> 15°C)'
    END,
    charger_protocol,
    battery_preconditioned
ORDER BY charger_protocol, temp_category, battery_preconditioned DESC;


-- ==============================================================================
-- QUERY 4: Warranty Defect Pareto Analysis (Top Cost Components)
-- Business Impact: Directs Quality Engineering resources to the highest warranty cost drivers.
-- ==============================================================================
WITH component_costs AS (
    SELECT 
        component_category,
        COUNT(claim_id) AS total_claims,
        SUM(parts_cost_eur) AS total_parts_cost_eur,
        SUM(labor_cost_eur) AS total_labor_cost_eur,
        SUM(total_claim_cost_eur) AS total_claim_cost_eur,
        ROUND(AVG(total_claim_cost_eur), 2) AS avg_cost_per_claim_eur,
        SUM(CASE WHEN is_safety_critical = 1 THEN 1 ELSE 0 END) AS safety_critical_claims
    FROM fct_warranty_claims
    GROUP BY component_category
)
SELECT 
    component_category,
    total_claims,
    safety_critical_claims,
    ROUND(total_claim_cost_eur, 2) AS total_claim_cost_eur,
    avg_cost_per_claim_eur,
    -- Percentage of total warranty spend
    ROUND((total_claim_cost_eur / SUM(total_claim_cost_eur) OVER ()) * 100, 2) AS share_of_total_warranty_cost_pct,
    -- Cumulative percentage (Pareto)
    ROUND(
        (SUM(total_claim_cost_eur) OVER (ORDER BY total_claim_cost_eur DESC) / 
         SUM(total_claim_cost_eur) OVER ()) * 100, 2
    ) AS pareto_cumulative_spend_pct
FROM component_costs
ORDER BY total_claim_cost_eur DESC;


-- ==============================================================================
-- QUERY 5: Early-Life Quality Escapes (Claims per 1,000 Vehicles at 6 Months in Service)
-- Business Impact: Detects early batch manufacturing defects before massive recall expenses.
-- ==============================================================================
WITH vehicle_sales_base AS (
    SELECT 
        v.model_family,
        v.manufacturing_plant,
        COUNT(s.sale_id) AS vehicles_delivered
    FROM fct_vehicle_sales s
    JOIN dim_vehicles v ON s.vehicle_id = v.vehicle_id
    GROUP BY v.model_family, v.manufacturing_plant
),
early_claims AS (
    SELECT 
        v.model_family,
        v.manufacturing_plant,
        COUNT(c.claim_id) AS early_life_claims_6mis,
        SUM(c.total_claim_cost_eur) AS early_claims_cost_eur
    FROM fct_warranty_claims c
    JOIN dim_vehicles v ON c.vehicle_id = v.vehicle_id
    WHERE c.months_in_service <= 6
    GROUP BY v.model_family, v.manufacturing_plant
)
SELECT 
    b.model_family,
    b.manufacturing_plant,
    b.vehicles_delivered,
    COALESCE(e.early_life_claims_6mis, 0) AS early_life_claims_6mis,
    -- CPTV Formula: (Claims / Deliveries) * 1000
    ROUND((COALESCE(e.early_life_claims_6mis, 0) / CAST(b.vehicles_delivered AS DECIMAL(10,2))) * 1000, 2) AS early_cptv_at_6mis,
    ROUND(COALESCE(e.early_claims_cost_eur, 0), 2) AS early_claims_cost_eur
FROM vehicle_sales_base b
LEFT JOIN early_claims e ON b.model_family = e.model_family AND b.manufacturing_plant = e.manufacturing_plant
ORDER BY early_cptv_at_6mis DESC;


-- ==============================================================================
-- QUERY 6: Battery Chemistry Resilience Across Climate Zones (NMC vs. LFP)
-- Business Impact: Guides battery procurement strategy for Nordic vs. Southern markets.
-- ==============================================================================
SELECT 
    v.battery_chemistry,
    g.climate_zone,
    COUNT(DISTINCT v.vehicle_id) AS active_ev_population,
    COUNT(c.claim_id) AS battery_warranty_claims,
    ROUND((COUNT(c.claim_id) / CAST(COUNT(DISTINCT v.vehicle_id) AS DECIMAL(10,2))) * 100, 2) AS battery_claim_rate_pct,
    ROUND(SUM(c.total_claim_cost_eur), 2) AS total_battery_warranty_spend_eur
FROM dim_vehicles v
JOIN fct_vehicle_sales s ON v.vehicle_id = s.vehicle_id
JOIN dim_geography g ON s.geo_id = g.geo_id
LEFT JOIN fct_warranty_claims c ON v.vehicle_id = c.vehicle_id AND c.component_category = 'HV_Battery_Pack'
WHERE v.powertrain_type = 'Pure_EV' AND v.battery_chemistry IS NOT NULL
GROUP BY v.battery_chemistry, g.climate_zone
ORDER BY v.battery_chemistry, battery_claim_rate_pct DESC;


-- ==============================================================================
-- QUERY 7: Top 10 Dealerships by Sales Volume & Discount Discipline
-- Business Impact: Identifies high-volume retail partners leaking excessive margin.
-- ==============================================================================
SELECT 
    dlr.dealer_name,
    g.country_name,
    dlr.channel_type,
    COUNT(s.sale_id) AS units_sold,
    ROUND(SUM(s.net_revenue_eur) / 1000000.0, 2) AS revenue_eur_millions,
    ROUND(AVG(s.gross_margin_pct), 2) AS avg_gross_margin_pct,
    ROUND(
        (SUM(s.dealer_discount_local * s.fx_rate_to_eur) / 
         SUM(s.gross_list_price_local * s.fx_rate_to_eur)) * 100, 2
    ) AS discount_leakage_pct
FROM fct_vehicle_sales s
JOIN dim_dealers dlr ON s.dealer_id = dlr.dealer_id
JOIN dim_geography g ON s.geo_id = g.geo_id
GROUP BY dlr.dealer_name, g.country_name, dlr.channel_type
HAVING units_sold >= 200
ORDER BY units_sold DESC
LIMIT 10;


-- ==============================================================================
-- QUERY 8: Order-to-Delivery Lead Time by Manufacturing Plant & Geography
-- Business Impact: Highlights logistics bottlenecks across global factories and hubs.
-- ==============================================================================
SELECT 
    v.manufacturing_plant,
    g.sales_region,
    COUNT(s.sale_id) AS units_delivered,
    ROUND(AVG(s.delivery_lead_days), 1) AS avg_lead_days,
    MIN(s.delivery_lead_days) AS min_lead_days,
    MAX(s.delivery_lead_days) AS max_lead_days,
    -- Rank regions by speed from each factory
    RANK() OVER (PARTITION BY v.manufacturing_plant ORDER BY AVG(s.delivery_lead_days) ASC) AS logistics_speed_rank
FROM fct_vehicle_sales s
JOIN dim_vehicles v ON s.vehicle_id = v.vehicle_id
JOIN dim_geography g ON s.geo_id = g.geo_id
GROUP BY v.manufacturing_plant, g.sales_region
ORDER BY v.manufacturing_plant, avg_lead_days ASC;


-- ==============================================================================
-- QUERY 9: Software Release Quality Tracking (Post-OTA Defect Rates)
-- Business Impact: Monitors if specific software builds trigger infotainment or sensor bugs.
-- ==============================================================================
SELECT 
    v.software_release_version,
    COUNT(DISTINCT v.vehicle_id) AS total_fleet_vehicles,
    COUNT(c.claim_id) AS total_software_claims,
    ROUND((COUNT(c.claim_id) / CAST(COUNT(DISTINCT v.vehicle_id) AS DECIMAL(10,2))) * 100, 2) AS defect_rate_pct,
    ROUND(SUM(c.total_claim_cost_eur), 2) AS total_repair_cost_eur
FROM dim_vehicles v
LEFT JOIN fct_warranty_claims c ON v.vehicle_id = c.vehicle_id AND c.component_category IN ('Infotainment_OTA', 'ADAS_Vision_Sensor')
GROUP BY v.software_release_version
ORDER BY defect_rate_pct DESC;


-- ==============================================================================
-- QUERY 10: Executive Commercial Summary Matrix (By Model Family & Trim)
-- Business Impact: Core table feeding the executive financial overview in Power BI.
-- ==============================================================================
SELECT 
    v.model_family,
    v.trim_level,
    v.powertrain_type,
    COUNT(s.sale_id) AS volume_sold,
    ROUND(SUM(s.net_revenue_eur) / 1000000.0, 2) AS total_revenue_eur_millions,
    ROUND(SUM(s.gross_profit_eur) / 1000000.0, 2) AS total_gross_profit_eur_millions,
    ROUND((SUM(s.gross_profit_eur) / SUM(s.net_revenue_eur)) * 100, 2) AS gross_margin_pct,
    ROUND(AVG(s.net_revenue_eur), 2) AS avg_unit_selling_price_eur
FROM fct_vehicle_sales s
JOIN dim_vehicles v ON s.vehicle_id = v.vehicle_id
GROUP BY v.model_family, v.trim_level, v.powertrain_type
ORDER BY total_revenue_eur_millions DESC;
