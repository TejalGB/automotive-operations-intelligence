"""
==============================================================================
PROJECT: AutoOps 360 - Automotive Data Analytics
FILE: src/data_quality_checks.py
DESCRIPTION: Automated Data Quality Assertion Suite & Schema Validator.
             Executes 16 rigorous tests covering Primary/Foreign Key integrity,
             physical EV battery sensor bounds, financial sanity, and warranty
             temporal consistency.
==============================================================================
"""

import os
import sys
import pandas as pd

# Set UTF-8 encoding for Windows
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data", "marts")


def run_all_checks():
    print("=" * 70)
    print("🔍 EXECUTING AUTOMATED DATA QUALITY & REFERENTIAL INTEGRITY SUITE...")
    print("=" * 70)

    # 1. Load Data Marts
    print("Step 1: Ingesting Star Schema CSV Data Marts...")
    try:
        vehicles = pd.read_csv(os.path.join(DATA_DIR, "dim_vehicles.csv"))
        dealers = pd.read_csv(os.path.join(DATA_DIR, "dim_dealers.csv"))
        geography = pd.read_csv(os.path.join(DATA_DIR, "dim_geography.csv"))
        dates = pd.read_csv(os.path.join(DATA_DIR, "dim_dates.csv"))
        sales = pd.read_csv(os.path.join(DATA_DIR, "fct_vehicle_sales.csv"))
        telematics = pd.read_csv(os.path.join(DATA_DIR, "fct_charging_telematics.csv"))
        warranty = pd.read_csv(os.path.join(DATA_DIR, "fct_warranty_claims.csv"))
        print("  ✓ All 7 dimensional and fact tables loaded successfully.\n")
    except Exception as e:
        print(f"  ❌ [ERROR] Failed to load data files: {e}")
        return False

    passed_count = 0
    failed_count = 0

    def check(condition, test_name):
        nonlocal passed_count, failed_count
        if condition:
            print(f"  ✅ [PASS] {test_name}")
            passed_count += 1
        else:
            print(f"  ❌ [FAIL] {test_name}")
            failed_count += 1

    # -------------------------------------------------------------
    # 2. Primary Key Uniqueness & Nullability
    # -------------------------------------------------------------
    print("Step 2: Validating Primary Keys & Uniqueness Constraints...")
    check(vehicles["vehicle_id"].is_unique and vehicles["vehicle_id"].notnull().all(),
          "dim_vehicles: vehicle_id is unique and non-null")
    check(sales["sale_id"].is_unique and sales["sale_id"].notnull().all(),
          "fct_vehicle_sales: sale_id is unique and non-null")
    check(telematics["session_id"].is_unique and telematics["session_id"].notnull().all(),
          "fct_charging_telematics: session_id is unique and non-null")
    check(warranty["claim_id"].is_unique and warranty["claim_id"].notnull().all(),
          "fct_warranty_claims: claim_id is unique and non-null")
    print()

    # -------------------------------------------------------------
    # 3. Cross-Table Referential Integrity (Foreign Keys)
    # -------------------------------------------------------------
    print("Step 3: Validating Cross-Table Foreign Key Integrity...")
    veh_ids = set(vehicles["vehicle_id"])
    dlr_ids = set(dealers["dealer_id"])
    geo_ids = set(geography["geo_id"])
    date_ids = set(dates["date_id"])

    # Sales FKs
    sales_veh_fk = sales["vehicle_id"].isin(veh_ids).all()
    sales_dlr_fk = sales["dealer_id"].isin(dlr_ids).all()
    sales_geo_fk = sales["geo_id"].isin(geo_ids).all()
    sales_date_fk = sales["date_id"].isin(date_ids).all()
    check(sales_veh_fk and sales_dlr_fk and sales_geo_fk and sales_date_fk,
          "fct_vehicle_sales: Foreign Keys valid (vehicles, dealers, geography, dates)")

    # Telematics FKs
    tele_veh_fk = telematics["vehicle_id"].isin(veh_ids).all()
    tele_date_fk = telematics["date_id"].isin(date_ids).all()
    check(tele_veh_fk and tele_date_fk,
          "fct_charging_telematics: Foreign Keys valid (vehicles, dates)")

    # Warranty FKs
    warr_veh_fk = warranty["vehicle_id"].isin(veh_ids).all()
    warr_dlr_fk = warranty["dealer_id"].isin(dlr_ids).all()
    warr_geo_fk = warranty["geo_id"].isin(geo_ids).all()
    warr_date_fk = warranty["date_id"].isin(date_ids).all()
    check(warr_veh_fk and warr_dlr_fk and warr_geo_fk and warr_date_fk,
          "fct_warranty_claims: Foreign Keys valid (vehicles, dealers, geography, dates)")
    print()

    # -------------------------------------------------------------
    # 4. EV Telematics Physical & Sensor Bounds
    # -------------------------------------------------------------
    print("Step 4: Validating EV Telematics & Physical Sensor Bounds...")
    # Both start and end SoC must be within [0%, 100%]
    start_soc_valid = (telematics["start_soc_pct"] >= 0).all() and (telematics["start_soc_pct"] <= 100).all()
    end_soc_valid = (telematics["end_soc_pct"] >= 0).all() and (telematics["end_soc_pct"] <= 100).all()
    check(start_soc_valid and end_soc_valid, "Battery SoC: start_soc and end_soc strictly within [0%, 100%]")

    # Charging session must strictly increase state of charge
    soc_increasing = (telematics["end_soc_pct"] > telematics["start_soc_pct"]).all()
    check(soc_increasing, "Battery SoC: end_soc strictly greater than start_soc (charging delta > 0)")

    # Temperature bounds
    temp_valid = (telematics["ambient_temp_celsius"] >= -40).all() and (telematics["ambient_temp_celsius"] <= 50).all()
    check(temp_valid, "Ambient Temperature: Realistic sensor range (-40°C to +50°C)")

    # Speed & Energy positivity
    speed_valid = (telematics["avg_charging_speed_kw"] > 0).all()
    energy_valid = (telematics["energy_delivered_kwh"] > 0).all()
    check(speed_valid and energy_valid, "Charging Speed & Energy: Strictly positive (kW > 0, kWh > 0)")
    print()

    # -------------------------------------------------------------
    # 5. Financial Sanity & Channel Economics
    # -------------------------------------------------------------
    print("Step 5: Validating Financial Calculations & Commercial Sanity...")
    rev_valid = (sales["net_revenue_eur"] > 0).all()
    check(rev_valid, "Commercial Revenue: All transactions have positive revenue (€ > 0)")

    margin_valid = (sales["gross_margin_pct"] >= 0.0).all() and (sales["gross_margin_pct"] <= 50.0).all()
    check(margin_valid, "Gross Margin: Realistic profitability bounds (0.0% to 50.0%)")

    # Subscription vehicles have 0 dealer discount
    subs = sales[sales["sale_channel"] == "Care_Subscription_Hub"]
    subs_valid = (subs["dealer_discount_local"] == 0.0).all()
    check(subs_valid, "Subscription Pricing: Care Subscription Hub discount is exactly 0.00")
    print()

    # -------------------------------------------------------------
    # 6. Warranty Quality & Temporal Consistency
    # -------------------------------------------------------------
    print("Step 6: Validating Warranty Lifecycles & Temporal Consistency...")
    mis_valid = (warranty["months_in_service"] >= 1).all() and (warranty["months_in_service"] <= 36).all()
    check(mis_valid, "Warranty Claims: Months in Service within valid lifespan (1 to 36 MIS)")

    cost_valid = (warranty["total_claim_cost_eur"] > 0).all()
    check(cost_valid, "Warranty Claims: Total claim expense strictly positive (€ > 0)")

    # Categories match reference list
    valid_cats = {"HV_Battery_Pack", "Electric_Drive_Inverter", "Air_Suspension", "ADAS_Vision_Sensor", "Infotainment_OTA"}
    cats_valid = warranty["component_category"].isin(valid_cats).all()
    check(cats_valid, "Warranty Claims: Component categories conform to master defect catalog")
    print()

    # -------------------------------------------------------------
    # Summary
    # -------------------------------------------------------------
    print("=" * 70)
    print(f"📊 QUALITY SUITE SUMMARY: {passed_count} Passed | {failed_count} Failed")
    print("=" * 70)

    if failed_count == 0:
        print("✅ ALL 16 DATA QUALITY ASSERTIONS PASSED! Pipeline data contracts verified.")
        return True
    else:
        print(f"❌ {failed_count} DATA QUALITY ASSERTIONS FAILED! Pipeline halted.")
        return False


if __name__ == "__main__":
    success = run_all_checks()
    sys.exit(0 if success else 1)
