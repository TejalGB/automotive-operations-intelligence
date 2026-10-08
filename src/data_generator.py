"""
==============================================================================
PROJECT: AutoOps 360 - Automotive Data Analytics
FILE: src/data_generator.py
DESCRIPTION: Simple Master Data Generator.
             Generates initial baseline CSV files for cars, sales, EV charging,
             and warranty claims in `data/marts/`.
==============================================================================
"""

import os
import sys
import random
from datetime import datetime, timedelta
import pandas as pd

# Set UTF-8 encoding for Windows
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data", "marts")
os.makedirs(DATA_DIR, exist_ok=True)

random.seed(42)

# -----------------------------------------------------------------------------
# 1. CAR MODELS & SPECIFICATIONS
# -----------------------------------------------------------------------------
CAR_MODELS = [
    {"model": "EX30", "body": "Compact_SUV", "powertrain": "Pure_EV", "battery_kwh": 69.0, "msrp": 42500.0, "cost": 31200.0},
    {"model": "EX90", "body": "7_Seater_SUV", "powertrain": "Pure_EV", "battery_kwh": 111.0, "msrp": 86000.0, "cost": 62500.0},
    {"model": "EC40", "body": "Crossover_SUV", "powertrain": "Pure_EV", "battery_kwh": 82.0, "msrp": 53500.0, "cost": 39800.0},
    {"model": "XC60", "body": "Midsize_SUV", "powertrain": "PHEV", "battery_kwh": 18.8, "msrp": 64500.0, "cost": 46200.0},
    {"model": "XC90", "body": "Large_SUV", "powertrain": "PHEV", "battery_kwh": 18.8, "msrp": 89000.0, "cost": 64100.0},
    {"model": "V60", "body": "Estate", "powertrain": "MHEV", "battery_kwh": 0.0, "msrp": 44800.0, "cost": 32900.0}
]

COUNTRIES = [
    {"geo_id": "GEO_SE", "country": "Sweden", "region": "Nordics", "currency": "SEK", "fx_to_eur": 0.088},
    {"geo_id": "GEO_NO", "country": "Norway", "region": "Nordics", "currency": "NOK", "fx_to_eur": 0.086},
    {"geo_id": "GEO_DE", "country": "Germany", "region": "Central_Europe", "currency": "EUR", "fx_to_eur": 1.000},
    {"geo_id": "GEO_UK", "country": "United Kingdom", "region": "Western_Europe", "currency": "GBP", "fx_to_eur": 1.185},
    {"geo_id": "GEO_US", "country": "United States", "region": "Americas", "currency": "USD", "fx_to_eur": 0.920}
]

DEALERS = [
    {"dealer_id": "DLR_SE_001", "name": "Stockholm Central Studio", "geo_id": "GEO_SE", "channel": "Direct_Brand_Studio"},
    {"dealer_id": "DLR_SE_002", "name": "Gothenburg Nordic Bilia", "geo_id": "GEO_SE", "channel": "Franchised_Retailer"},
    {"dealer_id": "DLR_NO_001", "name": "Oslo Fjord Mobility", "geo_id": "GEO_NO", "channel": "Direct_Brand_Studio"},
    {"dealer_id": "DLR_DE_001", "name": "Munich Premium Autohaus", "geo_id": "GEO_DE", "channel": "Franchised_Retailer"},
    {"dealer_id": "DLR_UK_001", "name": "London Mayfair Studio", "geo_id": "GEO_UK", "channel": "Direct_Brand_Studio"},
    {"dealer_id": "DLR_US_001", "name": "New York Manhattan Hub", "geo_id": "GEO_US", "channel": "Direct_Brand_Studio"}
]


def generate_baseline():
    print("=" * 60)
    print("🚗 GENERATING BASELINE AUTOMOTIVE DATASETS...")
    print("=" * 60)

    # 1. Master Dates (2024 - 2026)
    print("--> 1/5 Creating dim_dates.csv...")
    dates = []
    start = datetime(2024, 1, 1)
    for d in range(1000):
        curr = start + timedelta(days=d)
        q = (curr.month - 1) // 3 + 1
        dates.append({
            "date_id": int(curr.strftime("%Y%m%d")),
            "full_date": str(curr.date()),
            "month_name": curr.strftime("%B"),
            "calendar_quarter": f"Q{q}",
            "calendar_year": curr.year,
            "fiscal_quarter": f"FY{curr.strftime('%y')}-Q{q}"
        })
    pd.DataFrame(dates).to_csv(os.path.join(DATA_DIR, "dim_dates.csv"), index=False)

    # 2. Master Geography & Dealers
    print("--> 2/5 Creating dim_geography.csv & dim_dealers.csv...")
    pd.DataFrame(COUNTRIES).to_csv(os.path.join(DATA_DIR, "dim_geography.csv"), index=False)
    pd.DataFrame(DEALERS).to_csv(os.path.join(DATA_DIR, "dim_dealers.csv"), index=False)

    # 3. Master Vehicle Population (5,000 cars)
    print("--> 3/5 Creating dim_vehicles.csv (5,000 VINs)...")
    vehicles = []
    for i in range(1, 5001):
        car = random.choice(CAR_MODELS)
        trim = random.choice(["Core", "Plus", "Ultimate"])
        trim_mult = 1.0 if trim == "Core" else (1.08 if trim == "Plus" else 1.18)
        
        vehicles.append({
            "vehicle_id": f"VEH_{i:06d}",
            "vin": f"YV1XZ{random.choice('ABCDEFGH')}{random.randint(100000000, 999999999)}",
            "model_family": car["model"],
            "powertrain_type": car["powertrain"],
            "trim_level": trim,
            "battery_nominal_kwh": car["battery_kwh"],
            "base_msrp_eur": round(car["msrp"] * trim_mult, 2),
            "factory_unit_cost_eur": round(car["cost"] * trim_mult, 2)
        })
    veh_df = pd.DataFrame(vehicles)
    veh_df.to_csv(os.path.join(DATA_DIR, "dim_vehicles.csv"), index=False)

    # 4. Vehicle Sales Facts (4,000 sales)
    print("--> 4/5 Creating fct_vehicle_sales.csv (4,000 sales)...")
    sales = []
    for i in range(1, 4001):
        veh = vehicles[i - 1]
        dealer = random.choice(DEALERS)
        country = [c for c in COUNTRIES if c["geo_id"] == dealer["geo_id"]][0]
        
        # Date of sale
        sale_dt = start + timedelta(days=random.randint(10, 950))
        date_id = int(sale_dt.strftime("%Y%m%d"))
        
        # Channel & Discounts
        if dealer["channel"] == "Direct_Brand_Studio":
            channel = "Online_D2C"
            discount_pct = random.uniform(0.01, 0.03)
        else:
            channel = "Dealer_Wholesale"
            discount_pct = random.uniform(0.04, 0.08)
            
        msrp_eur = veh["base_msrp_eur"]
        cost_eur = veh["factory_unit_cost_eur"]
        fx = country["fx_to_eur"]
        
        msrp_local = round(msrp_eur / fx, 2)
        discount_local = round(msrp_local * discount_pct, 2)
        net_sale_price_local = msrp_local - discount_local
        
        net_rev_eur = round(net_sale_price_local * fx, 2)
        gross_profit = round(net_rev_eur - cost_eur, 2)
        gross_margin_pct = round((gross_profit / net_rev_eur) * 100, 2)
        
        sales.append({
            "sale_id": f"SAL_{i:07d}",
            "vehicle_id": veh["vehicle_id"],
            "dealer_id": dealer["dealer_id"],
            "geo_id": country["geo_id"],
            "date_id": date_id,
            "delivery_date": str(sale_dt.date()),
            "delivery_lead_days": random.randint(7, 30),
            "sale_channel": channel,
            "currency_code": country["currency"],
            "dealer_discount_local": discount_local,
            "fx_rate_to_eur": fx,
            "net_revenue_eur": net_rev_eur,
            "factory_cost_eur": cost_eur,
            "gross_profit_eur": gross_profit,
            "gross_margin_pct": gross_margin_pct
        })
    pd.DataFrame(sales).to_csv(os.path.join(DATA_DIR, "fct_vehicle_sales.csv"), index=False)

    # 5. Charging Telematics & Warranty Claims
    print("--> 5/5 Creating fct_charging_telematics.csv & fct_warranty_claims.csv...")
    ev_cars = [v for v in vehicles if v["powertrain_type"] == "Pure_EV"]
    
    # 10,000 Charging Sessions
    telematics = []
    for i in range(1, 10001):
        veh = random.choice(ev_cars)
        session_dt = start + timedelta(days=random.randint(10, 950))
        ambient = random.randint(-10, 30)
        start_soc = random.randint(15, 30)
        end_soc = random.randint(75, 90)
        kwh = round(((end_soc - start_soc) / 100.0) * veh["battery_nominal_kwh"], 2)
        speed = random.choice([11.0, 50.0, 120.0, 150.0])
        
        telematics.append({
            "session_id": f"CHG_{i:08d}",
            "vehicle_id": veh["vehicle_id"],
            "date_id": int(session_dt.strftime("%Y%m%d")),
            "ambient_temp_celsius": ambient,
            "start_soc_pct": start_soc,
            "end_soc_pct": end_soc,
            "energy_delivered_kwh": kwh,
            "avg_charging_speed_kw": speed
        })
    pd.DataFrame(telematics).to_csv(os.path.join(DATA_DIR, "fct_charging_telematics.csv"), index=False)

    # 1,000 Warranty Claims
    claims = []
    components = [
        ("HV_Battery_Pack", 4500.0),
        ("Electric_Drive_Inverter", 1850.0),
        ("Infotainment_OTA", 150.0),
        ("ADAS_Vision_Sensor", 1100.0)
    ]
    for i in range(1, 1001):
        sale = random.choice(sales)
        comp_name, part_cost = random.choice(components)
        labor = random.randint(1, 4) * 120.0
        
        claims.append({
            "claim_id": f"CLM_{i:07d}",
            "vehicle_id": sale["vehicle_id"],
            "dealer_id": sale["dealer_id"],
            "geo_id": sale["geo_id"],
            "date_id": sale["date_id"],
            "repair_date": sale["delivery_date"],
            "component_category": comp_name,
            "months_in_service": random.randint(1, 18),
            "total_claim_cost_eur": round(part_cost + labor, 2)
        })
    pd.DataFrame(claims).to_csv(os.path.join(DATA_DIR, "fct_warranty_claims.csv"), index=False)

    print("\n✅ All baseline datasets created successfully in 'data/marts/'!")
    print("=" * 60)


if __name__ == "__main__":
    generate_baseline()
