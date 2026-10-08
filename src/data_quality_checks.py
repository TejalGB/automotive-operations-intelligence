"""
==============================================================================
PROJECT: AutoOps 360 - Automotive Data Analytics
FILE: src/data_quality_checks.py
DESCRIPTION: Easy-to-read data inspector.
             Checks that our CSV data is clean, complete, and error-free.
==============================================================================
"""

import os
import sys
import pandas as pd

# Set UTF-8 so Windows prints nicely
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# Find the path to the 'data/marts' folder
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data", "marts")


def run_all_checks():
    print("=" * 60)
    print("🔍 INSPECTING AUTOMOTIVE DATASETS FOR ERRORS...")
    print("=" * 60)

    # -------------------------------------------------------------
    # 1. Load the CSV Files
    # -------------------------------------------------------------
    print("Step 1: Reading CSV files...")
    vehicles = pd.read_csv(os.path.join(DATA_DIR, "dim_vehicles.csv"))
    sales = pd.read_csv(os.path.join(DATA_DIR, "fct_vehicle_sales.csv"))
    telematics = pd.read_csv(os.path.join(DATA_DIR, "fct_charging_telematics.csv"))
    warranty = pd.read_csv(os.path.join(DATA_DIR, "fct_warranty_claims.csv"))
    print("✓ All files loaded successfully.\n")

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
    # 2. Check for Duplicate or Missing ID Numbers
    # -------------------------------------------------------------
    print("Step 2: Checking ID numbers...")
    # Vehicle IDs must be unique (no duplicates)
    check(vehicles["vehicle_id"].is_unique, "Vehicle IDs have no duplicates")
    check(vehicles["vehicle_id"].notnull().all(), "Vehicle IDs have no empty values")

    # Sales IDs must be unique
    check(sales["sale_id"].is_unique, "Sales IDs have no duplicates")
    check(sales["sale_id"].notnull().all(), "Sales IDs have no empty values")

    # Telematics Charging Session IDs must be unique
    check(telematics["session_id"].is_unique, "Charging Session IDs have no duplicates")

    # Warranty Claim IDs must be unique
    check(warranty["claim_id"].is_unique, "Warranty Claim IDs have no duplicates")
    print()

    # -------------------------------------------------------------
    # 3. Check Real-World Physical Limits (EV Battery & Temperature)
    # -------------------------------------------------------------
    print("Step 3: Checking physical sensor bounds...")
    
    # Battery State of Charge (SoC) must be between 0% and 100%
    soc_is_valid = (telematics["start_soc_pct"] >= 0).all() and (telematics["end_soc_pct"] <= 100).all()
    check(soc_is_valid, "Battery Charge % is between 0% and 100%")

    # Ambient temperatures should be realistic (between -40°C and +50°C)
    temp_is_valid = (telematics["ambient_temp_celsius"] >= -40).all() and (telematics["ambient_temp_celsius"] <= 50).all()
    check(temp_is_valid, "Sensor temperatures are in realistic range (-40°C to +50°C)")

    # Charging speed must be greater than 0 (no divide-by-zero errors)
    speed_is_valid = (telematics["avg_charging_speed_kw"] > 0).all()
    check(speed_is_valid, "Charging speeds are greater than 0 kW (No zero-division)")
    print()

    # -------------------------------------------------------------
    # 4. Check Financial & Business Rules
    # -------------------------------------------------------------
    print("Step 4: Checking financial sanity...")
    
    # Net sales revenue must always be positive
    revenue_is_positive = (sales["net_revenue_eur"] > 0).all()
    check(revenue_is_positive, "All vehicle sales have positive revenue (€ > 0)")

    # Gross Margin should not be abnormally negative (Currency Conversion check)
    margin_is_healthy = (sales["gross_margin_pct"] >= -5.0).all()
    check(margin_is_healthy, "Currencies converted correctly (No negative FX margins)")

    # Subscription vehicles should not have dealer discounts
    subscription_cars = sales[sales["sale_channel"] == "Care_Subscription"]
    subs_no_discount = (subscription_cars["dealer_discount_local"] == 0).all()
    check(subs_no_discount, "Nordic Car Subscriptions have 0 upfront dealer discount")
    print()

    # -------------------------------------------------------------
    # 5. Final Summary
    # -------------------------------------------------------------
    print("=" * 60)
    print(f"📊 RESULT: {passed_count} Passed | {failed_count} Failed")
    print("=" * 60)

    if failed_count > 0:
        sys.exit(1)


if __name__ == "__main__":
    run_all_checks()
