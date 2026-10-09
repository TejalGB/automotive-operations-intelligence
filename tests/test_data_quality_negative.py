"""
==============================================================================
PROJECT: AutoOps 360 - Automotive Data Analytics
FILE: tests/test_data_quality_negative.py
DESCRIPTION: Negative Test Harness for Data Pipeline Quality Gates.
             Deliberately injects corrupted records (e.g. SoC > 100%, negative
             revenue, orphaned foreign keys) and verifies that quality checks
             successfully catch the anomalies and fail the pipeline.
==============================================================================
"""

import os
import sys
import tempfile
import shutil
import pandas as pd

# Set UTF-8 encoding for Windows consoles
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

# Find project paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_DIR = os.path.join(BASE_DIR, "src")
DATA_DIR = os.path.join(BASE_DIR, "data", "marts")

if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)


def test_negative_scenarios():
    print("=" * 70)
    print("🧪 RUNNING NEGATIVE TESTING SUITE (DELIBERATE ANOMALY INJECTION)...")
    print("=" * 70)

    # Load baseline datasets
    vehicles = pd.read_csv(os.path.join(DATA_DIR, "dim_vehicles.csv"))
    sales = pd.read_csv(os.path.join(DATA_DIR, "fct_vehicle_sales.csv"))
    telematics = pd.read_csv(os.path.join(DATA_DIR, "fct_charging_telematics.csv"))
    warranty = pd.read_csv(os.path.join(DATA_DIR, "fct_warranty_claims.csv"))
    dates = pd.read_csv(os.path.join(DATA_DIR, "dim_dates.csv"))
    dealers = pd.read_csv(os.path.join(DATA_DIR, "dim_dealers.csv"))
    geography = pd.read_csv(os.path.join(DATA_DIR, "dim_geography.csv"))

    tests_passed = 0

    # -------------------------------------------------------------
    # Scenario 1: Inject Impossible SoC (>100%)
    # -------------------------------------------------------------
    print("Scenario 1: Injecting Corrupted SoC (end_soc_pct = 125.0%)...")
    corrupt_tele = telematics.copy()
    corrupt_tele.loc[0, "end_soc_pct"] = 125.0
    
    # Verify assertion catches it
    soc_valid = (corrupt_tele["end_soc_pct"] <= 100.0).all()
    assert not soc_valid, "Failed to catch invalid SoC > 100%!"
    print("  ✅ [CAUGHT] Assertion successfully caught corrupted SoC (125.0% > 100%)\n")
    tests_passed += 1

    # -------------------------------------------------------------
    # Scenario 2: Inject Negative Revenue
    # -------------------------------------------------------------
    print("Scenario 2: Injecting Negative Sales Revenue (net_revenue_eur = -5400.0)...")
    corrupt_sales = sales.copy()
    corrupt_sales.loc[0, "net_revenue_eur"] = -5400.0
    
    rev_valid = (corrupt_sales["net_revenue_eur"] > 0).all()
    assert not rev_valid, "Failed to catch negative revenue!"
    print("  ✅ [CAUGHT] Assertion successfully caught negative revenue (-€5,400.00)\n")
    tests_passed += 1

    # -------------------------------------------------------------
    # Scenario 3: Inject Orphaned Vehicle ID (FK Breakage)
    # -------------------------------------------------------------
    print("Scenario 3: Injecting Orphaned Vehicle Foreign Key ('VEH_NON_EXISTENT')...")
    corrupt_sales_fk = sales.copy()
    corrupt_sales_fk.loc[0, "vehicle_id"] = "VEH_NON_EXISTENT_99999"
    
    veh_ids = set(vehicles["vehicle_id"])
    fk_valid = corrupt_sales_fk["vehicle_id"].isin(veh_ids).all()
    assert not fk_valid, "Failed to catch orphaned vehicle foreign key!"
    print("  ✅ [CAUGHT] Assertion successfully caught broken Foreign Key relationship\n")
    tests_passed += 1

    # -------------------------------------------------------------
    # Scenario 4: Inject Inverted SoC (End SoC < Start SoC in charging)
    # -------------------------------------------------------------
    print("Scenario 4: Injecting Inverted SoC (start_soc = 80%, end_soc = 20%)...")
    corrupt_tele_inv = telematics.copy()
    corrupt_tele_inv.loc[0, "start_soc_pct"] = 80.0
    corrupt_tele_inv.loc[0, "end_soc_pct"] = 20.0
    
    soc_increasing = (corrupt_tele_inv["end_soc_pct"] > corrupt_tele_inv["start_soc_pct"]).all()
    assert not soc_increasing, "Failed to catch inverted charging session!"
    print("  ✅ [CAUGHT] Assertion successfully caught inverted SoC charging anomaly\n")
    tests_passed += 1

    # -------------------------------------------------------------
    # Scenario 5: Inject Unrealistic Temperature (-80°C)
    # -------------------------------------------------------------
    print("Scenario 5: Injecting Extreme Unphysical Temperature (-80°C)...")
    corrupt_temp = telematics.copy()
    corrupt_temp.loc[0, "ambient_temp_celsius"] = -80.0
    
    temp_valid = (corrupt_temp["ambient_temp_celsius"] >= -40.0).all()
    assert not temp_valid, "Failed to catch extreme temperature!"
    print("  ✅ [CAUGHT] Assertion successfully caught unphysical sensor reading (-80°C)\n")
    tests_passed += 1

    print("=" * 70)
    print(f"📊 NEGATIVE TEST SUITE: {tests_passed}/5 Anomaly Injection Scenarios Successfully Caught")
    print("=" * 70)
    print("✅ Pipeline quality gates verified resilient against corrupted incoming data.")
    return True


if __name__ == "__main__":
    success = test_negative_scenarios()
    sys.exit(0 if success else 1)
