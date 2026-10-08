"""
==============================================================================
PROJECT: AutoOps 360 - Automotive Data Analytics
FILE: src/run_daily_pipeline.py
DESCRIPTION: Simple Daily Simulator.
             Adds a few new car sales, EV charges, and warranty claims for today.
==============================================================================
"""

import os
import sys
import random
from datetime import datetime, timedelta
import pandas as pd

# Set UTF-8 so Windows prints nicely
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# Find the 'data/marts' folder
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data", "marts")

from data_quality_checks import run_all_checks


def simulate_today():
    print("=" * 60)
    print("⏰ SIMULATING TODAY'S NEW AUTOMOTIVE DATA...")
    print("=" * 60)

    # -------------------------------------------------------------
    # Step 1: Read existing CSV files
    # -------------------------------------------------------------
    sales_file = os.path.join(DATA_DIR, "fct_vehicle_sales.csv")
    chg_file = os.path.join(DATA_DIR, "fct_charging_telematics.csv")
    claims_file = os.path.join(DATA_DIR, "fct_warranty_claims.csv")

    sales_df = pd.read_csv(sales_file)
    chg_df = pd.read_csv(chg_file)
    claims_df = pd.read_csv(claims_file)

    today = datetime.now().date()
    today_id = int(today.strftime("%Y%m%d"))

    # -------------------------------------------------------------
    # Step 2: Add 10 New Car Sales
    # -------------------------------------------------------------
    print("--> 1/3 Adding 10 new vehicle sales for today...")
    last_sale_num = max([int(x.split('_')[1]) for x in sales_df["sale_id"]])
    
    new_sales = []
    for i in range(1, 11):
        sale_id = f"SAL_{(last_sale_num + i):07d}"
        random_old_sale = sales_df.sample(1).iloc[0].to_dict()
        
        # Update dates to today
        random_old_sale["sale_id"] = sale_id
        random_old_sale["date_id"] = today_id
        random_old_sale["delivery_date"] = str(today)
        new_sales.append(random_old_sale)

    updated_sales = pd.concat([sales_df, pd.DataFrame(new_sales)], ignore_index=True)
    updated_sales.to_csv(sales_file, index=False)
    print("   ✓ 10 new sales saved to fct_vehicle_sales.csv")

    # -------------------------------------------------------------
    # Step 3: Add 20 New EV Charging Sessions
    # -------------------------------------------------------------
    print("--> 2/3 Adding 20 new EV charging sessions...")
    last_chg_num = max([int(x.split('_')[1]) for x in chg_df["session_id"]])
    
    new_charges = []
    for i in range(1, 21):
        chg_id = f"CHG_{(last_chg_num + i):08d}"
        random_old_chg = chg_df.sample(1).iloc[0].to_dict()
        
        random_old_chg["session_id"] = chg_id
        random_old_chg["date_id"] = today_id
        new_charges.append(random_old_chg)

    updated_chg = pd.concat([chg_df, pd.DataFrame(new_charges)], ignore_index=True)
    updated_chg.to_csv(chg_file, index=False)
    print("   ✓ 20 new charges saved to fct_charging_telematics.csv")

    # -------------------------------------------------------------
    # Step 4: Add 2 New Warranty Claims
    # -------------------------------------------------------------
    print("--> 3/3 Adding 2 new warranty claims from service centers...")
    last_claim_num = max([int(x.split('_')[1]) for x in claims_df["claim_id"]])
    
    new_claims = []
    for i in range(1, 3):
        claim_id = f"CLM_{(last_claim_num + i):07d}"
        random_old_claim = claims_df.sample(1).iloc[0].to_dict()
        
        random_old_claim["claim_id"] = claim_id
        random_old_claim["date_id"] = today_id
        random_old_claim["repair_date"] = str(today)
        new_claims.append(random_old_claim)

    updated_claims = pd.concat([claims_df, pd.DataFrame(new_claims)], ignore_index=True)
    updated_claims.to_csv(claims_file, index=False)
    print("   ✓ 2 new claims saved to fct_warranty_claims.csv\n")

    # -------------------------------------------------------------
    # Step 5: Automatically check data quality
    # -------------------------------------------------------------
    print("--> Running data inspection on updated data...")
    run_all_checks()
    print("✅ Today's data updated successfully! Ready for Power BI.")


if __name__ == "__main__":
    simulate_today()
