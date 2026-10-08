-- ==============================================================================
-- PROJECT: Global Connected Automotive & Commercial Intelligence (AutoOps 360)
-- CLIENT PROFILE: Global Premium Nordic Automotive OEM (Anonymized)
-- DATABASE: MySQL 8.0+
-- FILE: 02_analytical_views.sql
-- DESCRIPTION: High-performance Analytical Views with CTEs and Window Functions
-- ==============================================================================

USE auto_ops_dw;

-- ==============================================================================
-- VIEW 1: Commercial EV Transition & Regional Margin Intelligence
-- Purpose: Feeds Power BI Page 1 & 2 (Sales Mix, Margin Health, Channel Mix)
-- ==============================================================================
CREATE OR REPLACE VIEW vw_commercial_ev_transition AS
WITH sales_enhanced AS (
    SELECT 
        s.sale_id,
        s.date_id,
        d.full_date,
        d.calendar_year,
        d.calendar_quarter,
        d.month_name,
        d.fiscal_quarter,
        v.vehicle_id,
        v.model_family,
        v.model_code,
        v.powertrain_type,
        v.trim_level,
        v.battery_chemistry,
        v.battery_nominal_kwh,
        g.country_name,
        g.sales_region,
        g.climate_zone,
        dlr.dealer_name,
        dlr.channel_type,
        s.financing_type,
        s.net_revenue_eur,
        s.factory_cost_eur,
        s.gross_profit_eur,
        s.gross_margin_pct,
        s.dealer_discount_local * s.fx_rate_to_eur AS discount_amount_eur,
        s.gross_list_price_local * s.fx_rate_to_eur AS list_price_eur,
        s.delivery_lead_days,
        CASE WHEN v.powertrain_type = 'Pure_EV' THEN 1 ELSE 0 END AS is_pure_ev,
        CASE WHEN v.powertrain_type = 'PHEV' THEN 1 ELSE 0 END AS is_phev,
        CASE WHEN v.powertrain_type = 'MHEV' THEN 1 ELSE 0 END AS is_mhev
    FROM fct_vehicle_sales s
    JOIN dim_vehicles v ON s.vehicle_id = v.vehicle_id
    JOIN dim_dates d ON s.date_id = d.date_id
    JOIN dim_geography g ON s.geo_id = g.geo_id
    JOIN dim_dealers dlr ON s.dealer_id = dlr.dealer_id
)
SELECT 
    *,
    -- Rolling 30-day average gross margin by model family
    AVG(gross_margin_pct) OVER (
        PARTITION BY model_family 
        ORDER BY full_date 
        ROWS BETWEEN 29 PRECEDING AND CURRENT ROW
    ) AS rolling_30d_avg_margin_pct,
    
    -- Discount Leakage Rate (% of MSRP surrendered as discounts)
    CASE 
        WHEN list_price_eur > 0 AND channel_type != 'Care_Subscription_Hub' 
        THEN ROUND((discount_amount_eur / list_price_eur) * 100, 2)
        ELSE 0.00 
    END AS discount_leakage_pct
FROM sales_enhanced;


-- ==============================================================================
-- VIEW 2: Connected EV Charging & Thermal Kinetics
-- Purpose: Feeds Power BI Page 3 (Battery Degradation, Fast Charge Stress, Temperature)
-- ==============================================================================
CREATE OR REPLACE VIEW vw_ev_telematics_performance AS
SELECT 
    t.session_id,
    t.vehicle_id,
    t.date_id,
    d.full_date,
    d.calendar_year,
    d.calendar_quarter,
    d.month_name,
    v.model_family,
    v.battery_chemistry,
    v.battery_nominal_kwh,
    v.wltp_range_km,
    t.charger_protocol,
    t.ambient_temp_celsius,
    -- Temperature bracket for cold-weather clustering
    CASE 
        WHEN t.ambient_temp_celsius < -10.0 THEN '1. Severe Cold (< -10°C)'
        WHEN t.ambient_temp_celsius BETWEEN -10.0 AND 0.0 THEN '2. Freezing (-10°C to 0°C)'
        WHEN t.ambient_temp_celsius BETWEEN 0.1 AND 15.0 THEN '3. Moderate (0°C to 15°C)'
        WHEN t.ambient_temp_celsius BETWEEN 15.1 AND 25.0 THEN '4. Optimal (15°C to 25°C)'
        ELSE '5. High Heat (> 25°C)'
    END AS ambient_temp_bracket,
    t.start_soc_pct,
    t.end_soc_pct,
    (t.end_soc_pct - t.start_soc_pct) AS soc_delta_pct,
    t.energy_delivered_kwh,
    t.avg_charging_speed_kw,
    t.session_duration_minutes,
    t.battery_temp_start_celsius,
    t.battery_temp_end_celsius,
    t.battery_temp_delta_celsius,
    t.battery_preconditioned,
    t.estimated_range_gained_km,
    -- Real-world charging efficiency: kWh per 10 minutes
    ROUND(t.energy_delivered_kwh / (t.session_duration_minutes / 10.0), 2) AS kwh_per_10min_throughput
FROM fct_charging_telematics t
JOIN dim_vehicles v ON t.vehicle_id = v.vehicle_id
JOIN dim_dates d ON t.date_id = d.date_id;


-- ==============================================================================
-- VIEW 3: Aftersales Quality & Warranty Early Warning
-- Purpose: Feeds Power BI Page 4 (Component Failure Rates, Batch Spikes, CPTV)
-- ==============================================================================
CREATE OR REPLACE VIEW vw_warranty_quality_early_warning AS
WITH claims_enhanced AS (
    SELECT 
        c.claim_id,
        c.vehicle_id,
        c.dealer_id,
        c.date_id,
        d.full_date AS claim_date,
        d.calendar_year,
        d.calendar_quarter,
        v.model_family,
        v.model_code,
        v.powertrain_type,
        v.battery_chemistry,
        v.manufacturing_plant,
        v.production_date,
        g.country_name,
        g.sales_region,
        g.climate_zone,
        c.component_category,
        c.failure_symptom_code,
        c.months_in_service,
        c.mileage_at_failure_km,
        c.labor_hours,
        c.labor_cost_eur,
        c.parts_cost_eur,
        c.total_claim_cost_eur,
        c.is_safety_critical,
        c.claim_status
    FROM fct_warranty_claims c
    JOIN dim_vehicles v ON c.vehicle_id = v.vehicle_id
    JOIN dim_dates d ON c.date_id = d.date_id
    JOIN dim_geography g ON c.geo_id = g.geo_id
)
SELECT 
    *,
    -- Flag early field failures (< 6 months in service) indicating factory/supplier quality escape
    CASE WHEN months_in_service <= 6 THEN 1 ELSE 0 END AS is_early_life_failure,
    
    -- Cumulative warranty cost per vehicle model family over time
    SUM(total_claim_cost_eur) OVER (
        PARTITION BY model_family 
        ORDER BY claim_date
    ) AS cumulative_warranty_spend_eur
FROM claims_enhanced;
