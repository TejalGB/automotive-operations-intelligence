-- ==============================================================================
-- PROJECT: Global Connected Automotive & Commercial Intelligence (AutoOps 360)
-- CLIENT PROFILE: Global Premium Nordic Automotive OEM (Anonymized)
-- DATABASE: MySQL 8.0+
-- FILE: 01_schema_ddl.sql
-- DESCRIPTION: Kimball Star Schema DDL for Dimensions and Multi-Domain Fact Tables
-- ==============================================================================

CREATE DATABASE IF NOT EXISTS auto_ops_dw
  DEFAULT CHARACTER SET utf8mb4
  DEFAULT COLLATE utf8mb4_unicode_ci;

USE auto_ops_dw;

-- Drop tables in reverse order of foreign key dependencies (if re-running)
SET FOREIGN_KEY_CHECKS = 0;
DROP TABLE IF EXISTS fct_warranty_claims;
DROP TABLE IF EXISTS fct_charging_telematics;
DROP TABLE IF EXISTS fct_vehicle_sales;
DROP TABLE IF EXISTS dim_exchange_rates;
DROP TABLE IF EXISTS dim_dates;
DROP TABLE IF EXISTS dim_dealers;
DROP TABLE IF EXISTS dim_geography;
DROP TABLE IF EXISTS dim_vehicles;
SET FOREIGN_KEY_CHECKS = 1;

-- ==============================================================================
-- 1. CONFORMED DIMENSIONS
-- ==============================================================================

-- 1.1 Vehicle Dimension (Master vehicle specifications & battery properties)
CREATE TABLE dim_vehicles (
    vehicle_id VARCHAR(36) PRIMARY KEY,
    vin VARCHAR(17) NOT NULL UNIQUE,
    model_code VARCHAR(30) NOT NULL,            -- e.g., 'EX30_COMPACT_EV', 'EX90_FLAGSHIP_EV', 'XC60_PHEV'
    model_family VARCHAR(20) NOT NULL,          -- e.g., 'EX30', 'EX90', 'XC60', 'XC40', 'V60'
    body_style VARCHAR(20) NOT NULL,            -- 'SUV', 'Sedan', 'Estate'
    powertrain_type VARCHAR(20) NOT NULL,       -- 'Pure_EV', 'PHEV', 'MHEV'
    trim_level VARCHAR(20) NOT NULL,            -- 'Core', 'Plus', 'Ultimate'
    battery_chemistry VARCHAR(15),              -- 'NMC', 'LFP', NULL (for non-EV)
    battery_nominal_kwh DECIMAL(5,2),           -- e.g., 69.00, 82.00, 111.00
    wltp_range_km INT,                          -- Certified lab range
    software_release_version VARCHAR(20) NOT NULL, -- e.g., 'v2.11.4', 'v3.0.2'
    manufacturing_plant VARCHAR(50) NOT NULL,   -- 'Torslanda_Plant', 'Ghent_Plant', 'Daqing_Plant'
    production_date DATE NOT NULL,
    base_msrp_eur DECIMAL(10,2) NOT NULL,
    factory_unit_cost_eur DECIMAL(10,2) NOT NULL,
    INDEX idx_model_family (model_family),
    INDEX idx_powertrain (powertrain_type)
) ENGINE=InnoDB;

-- 1.2 Geography Dimension (Market tiers, regional climate profiles)
CREATE TABLE dim_geography (
    geo_id VARCHAR(10) PRIMARY KEY,             -- e.g., 'GEO_SE', 'GEO_DE', 'GEO_US'
    country_code VARCHAR(2) NOT NULL,           -- 'SE', 'NO', 'DE', 'UK', 'US', 'NL', 'FR'
    country_name VARCHAR(50) NOT NULL,
    sales_region VARCHAR(20) NOT NULL,          -- 'Nordics', 'Central_Europe', 'Western_Europe', 'Americas', 'APAC'
    climate_zone VARCHAR(20) NOT NULL,          -- 'Subarctic', 'Temperate', 'Continental', 'Mediterranean'
    currency_code VARCHAR(3) NOT NULL,          -- 'EUR', 'SEK', 'NOK', 'GBP', 'USD'
    ev_subsidy_tier VARCHAR(20) NOT NULL        -- 'High', 'Moderate', 'None'
) ENGINE=InnoDB;

-- 1.3 Dealer & Retail Hub Dimension (Omnichannel network)
CREATE TABLE dim_dealers (
    dealer_id VARCHAR(20) PRIMARY KEY,          -- e.g., 'DLR_SE_001', 'STU_DE_002'
    dealer_name VARCHAR(100) NOT NULL,
    geo_id VARCHAR(10) NOT NULL,
    city VARCHAR(50) NOT NULL,
    channel_type VARCHAR(30) NOT NULL,          -- 'Franchised_Retailer', 'Direct_Brand_Studio', 'Care_Subscription_Hub'
    is_certified_ev_center BOOLEAN NOT NULL DEFAULT TRUE,
    annual_sales_target INT NOT NULL,
    FOREIGN KEY (geo_id) REFERENCES dim_geography(geo_id)
) ENGINE=InnoDB;

-- 1.4 Date Dimension (Master calendar & fiscal hierarchy 2024 - 2026)
CREATE TABLE dim_dates (
    date_id INT PRIMARY KEY,                    -- Format: YYYYMMDD
    full_date DATE NOT NULL UNIQUE,
    day_of_week_name VARCHAR(10) NOT NULL,
    day_of_month INT NOT NULL,
    month_number INT NOT NULL,
    month_name VARCHAR(10) NOT NULL,
    calendar_quarter VARCHAR(2) NOT NULL,       -- 'Q1', 'Q2', 'Q3', 'Q4'
    calendar_year INT NOT NULL,
    fiscal_quarter VARCHAR(5) NOT NULL,         -- 'FY24-Q1', etc.
    is_weekend BOOLEAN NOT NULL,
    is_quarter_end BOOLEAN NOT NULL,
    INDEX idx_full_date (full_date)
) ENGINE=InnoDB;

-- 1.5 Currency Exchange Rates (Used to normalize global sales into EUR)
CREATE TABLE dim_exchange_rates (
    rate_id VARCHAR(20) PRIMARY KEY,            -- e.g., '20240101_USD'
    date_id INT NOT NULL,
    from_currency VARCHAR(3) NOT NULL,
    to_currency VARCHAR(3) NOT NULL DEFAULT 'EUR',
    exchange_rate_to_eur DECIMAL(10,6) NOT NULL,
    FOREIGN KEY (date_id) REFERENCES dim_dates(date_id)
) ENGINE=InnoDB;

-- ==============================================================================
-- 2. CORE FACT TABLES
-- ==============================================================================

-- 2.1 Fact Vehicle Sales (Commercial performance, omnichannel margins)
CREATE TABLE fct_vehicle_sales (
    sale_id VARCHAR(36) PRIMARY KEY,
    vehicle_id VARCHAR(36) NOT NULL,
    dealer_id VARCHAR(20) NOT NULL,
    geo_id VARCHAR(10) NOT NULL,
    date_id INT NOT NULL,                       -- Delivery date key
    order_date DATE NOT NULL,
    delivery_date DATE NOT NULL,
    delivery_lead_days INT NOT NULL,
    sale_channel VARCHAR(30) NOT NULL,          -- 'Dealer_Wholesale', 'Online_D2C', 'Care_Subscription'
    financing_type VARCHAR(20) NOT NULL,        -- 'Cash', 'Bank_Loan', 'Operating_Lease', 'Subscription'
    currency_code VARCHAR(3) NOT NULL,
    gross_list_price_local DECIMAL(12,2) NOT NULL,
    dealer_discount_local DECIMAL(12,2) NOT NULL DEFAULT 0.00,
    net_sale_price_local DECIMAL(12,2) NOT NULL,
    
    -- Normalized to EUR base currency (Addressing INC0948102)
    fx_rate_to_eur DECIMAL(10,6) NOT NULL,
    net_revenue_eur DECIMAL(12,2) NOT NULL,
    factory_cost_eur DECIMAL(12,2) NOT NULL,
    gross_profit_eur DECIMAL(12,2) NOT NULL,
    gross_margin_pct DECIMAL(5,2) NOT NULL,     -- ((net_revenue - factory_cost) / net_revenue) * 100
    
    FOREIGN KEY (vehicle_id) REFERENCES dim_vehicles(vehicle_id),
    FOREIGN KEY (dealer_id) REFERENCES dim_dealers(dealer_id),
    FOREIGN KEY (geo_id) REFERENCES dim_geography(geo_id),
    FOREIGN KEY (date_id) REFERENCES dim_dates(date_id),
    INDEX idx_sales_date (date_id),
    INDEX idx_sales_channel (sale_channel)
) ENGINE=InnoDB;

-- 2.2 Fact Charging Telematics (Connected EV energy & battery performance)
CREATE TABLE fct_charging_telematics (
    session_id VARCHAR(36) PRIMARY KEY,
    vehicle_id VARCHAR(36) NOT NULL,
    date_id INT NOT NULL,
    session_start_time DATETIME NOT NULL,
    session_end_time DATETIME NOT NULL,
    session_duration_minutes DECIMAL(6,2) NOT NULL,
    charger_protocol VARCHAR(20) NOT NULL,       -- 'AC_Wallbox_11kW', 'DC_Fast_150kW', 'DC_UltraFast_250kW'
    ambient_temp_celsius DECIMAL(4,1) NOT NULL,  -- e.g., -15.5 to 35.0
    start_soc_pct DECIMAL(5,2) NOT NULL,         -- State of Charge at start (0.00 - 100.00)
    end_soc_pct DECIMAL(5,2) NOT NULL,           -- State of Charge at end (0.00 - 100.00)
    energy_delivered_kwh DECIMAL(6,2) NOT NULL,
    avg_charging_speed_kw DECIMAL(6,2) NOT NULL, -- Safeguarded against 0-duration division (INC0719402)
    battery_temp_start_celsius DECIMAL(4,1) NOT NULL,
    battery_temp_end_celsius DECIMAL(4,1) NOT NULL,
    battery_temp_delta_celsius DECIMAL(4,1) NOT NULL,
    battery_preconditioned BOOLEAN NOT NULL DEFAULT FALSE,
    estimated_range_gained_km DECIMAL(6,2) NOT NULL,
    
    FOREIGN KEY (vehicle_id) REFERENCES dim_vehicles(vehicle_id),
    FOREIGN KEY (date_id) REFERENCES dim_dates(date_id),
    INDEX idx_telematics_date (date_id),
    INDEX idx_charger_protocol (charger_protocol),
    INDEX idx_ambient_temp (ambient_temp_celsius)
) ENGINE=InnoDB;

-- 2.3 Fact Warranty Claims (Aftersales service, defect early warning)
CREATE TABLE fct_warranty_claims (
    claim_id VARCHAR(36) PRIMARY KEY,
    vehicle_id VARCHAR(36) NOT NULL,
    dealer_id VARCHAR(20) NOT NULL,
    geo_id VARCHAR(10) NOT NULL,
    date_id INT NOT NULL,                       -- Claim submission date key
    repair_date DATE NOT NULL,
    component_category VARCHAR(40) NOT NULL,    -- 'HV_Battery_Pack', 'Electric_Drive_Inverter', 'Infotainment_OTA', 'ADAS_Vision_Sensor', 'Air_Suspension'
    failure_symptom_code VARCHAR(30) NOT NULL,  -- e.g., 'ERR_BMS_CELL_DELTA', 'ERR_INVERTER_OVERHEAT'
    months_in_service INT NOT NULL,             -- Mileage / age at failure
    mileage_at_failure_km INT NOT NULL,
    labor_hours DECIMAL(5,2) NOT NULL,
    labor_cost_eur DECIMAL(10,2) NOT NULL,
    parts_cost_eur DECIMAL(10,2) NOT NULL,
    total_claim_cost_eur DECIMAL(10,2) NOT NULL,
    is_safety_critical BOOLEAN NOT NULL DEFAULT FALSE,
    claim_status VARCHAR(20) NOT NULL,          -- 'Approved', 'Reimbursed', 'Under_Investigation'
    
    FOREIGN KEY (vehicle_id) REFERENCES dim_vehicles(vehicle_id),
    FOREIGN KEY (dealer_id) REFERENCES dim_dealers(dealer_id),
    FOREIGN KEY (geo_id) REFERENCES dim_geography(geo_id),
    FOREIGN KEY (date_id) REFERENCES dim_dates(date_id),
    INDEX idx_claim_component (component_category),
    INDEX idx_months_in_service (months_in_service)
) ENGINE=InnoDB;
