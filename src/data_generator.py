"""
==============================================================================
PROJECT: AutoOps 360 - Automotive Data Analytics
FILE: src/data_generator.py
DESCRIPTION: Master Synthetic Data Generator.
             Generates consistent Kimball Star Schema data marts with realistic
             EV charging kinetics (temperature/SoC curves) and accurate warranty
             lifecycles.
==============================================================================
"""

import os
import sys
import random
from datetime import datetime, timedelta
import pandas as pd

# Set UTF-8 encoding for console output
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data", "marts")
os.makedirs(DATA_DIR, exist_ok=True)

random.seed(42)

# -----------------------------------------------------------------------------
# 1. REFERENCE DIMENSIONS
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
    {"geo_id": "GEO_US", "country": "United States", "region": "Americas", "currency": "USD", "fx_to_eur": 0.920},
    {"geo_id": "GEO_IT", "country": "Italy", "region": "Southern_Europe", "currency": "EUR", "fx_to_eur": 1.000},
    {"geo_id": "GEO_NL", "country": "Netherlands", "region": "Western_Europe", "currency": "EUR", "fx_to_eur": 1.000}
]

DEALERS = [
    {"dealer_id": "DLR_SE_001", "name": "Stockholm Central Studio", "geo_id": "GEO_SE", "channel": "Direct_Brand_Studio"},
    {"dealer_id": "DLR_SE_002", "name": "Gothenburg Nordic Bilia", "geo_id": "GEO_SE", "channel": "Franchised_Retailer"},
    {"dealer_id": "DLR_NO_001", "name": "Oslo Fjord Mobility", "geo_id": "GEO_NO", "channel": "Direct_Brand_Studio"},
    {"dealer_id": "DLR_NO_002", "name": "Bergen EV Center", "geo_id": "GEO_NO", "channel": "Franchised_Retailer"},
    {"dealer_id": "DLR_DE_001", "name": "Berlin Brand Experience", "geo_id": "GEO_DE", "channel": "Direct_Brand_Studio"},
    {"dealer_id": "DLR_DE_002", "name": "Munich Premium Autohaus", "geo_id": "GEO_DE", "channel": "Franchised_Retailer"},
    {"dealer_id": "DLR_IT_001", "name": "Milan Design District Auto", "geo_id": "GEO_IT", "channel": "Franchised_Retailer"},
    {"dealer_id": "DLR_IT_002", "name": "Rome Metropolitan Retail", "geo_id": "GEO_IT", "channel": "Franchised_Retailer"},
    {"dealer_id": "DLR_NL_001", "name": "Amsterdam Canal Mobility", "geo_id": "GEO_NL", "channel": "Care_Subscription_Hub"},
    {"dealer_id": "DLR_NL_002", "name": "Rotterdam Port Auto", "geo_id": "GEO_NL", "channel": "Franchised_Retailer"},
    {"dealer_id": "DLR_UK_001", "name": "London Mayfair Studio", "geo_id": "GEO_UK", "channel": "Direct_Brand_Studio"},
    {"dealer_id": "DLR_US_001", "name": "New York Manhattan Hub", "geo_id": "GEO_US", "channel": "Direct_Brand_Studio"}
]

CHARGER_PROTOCOLS = [
    {"protocol": "AC_Wallbox_11kW", "base_speed": 11.0, "weight": 0.60},
    {"protocol": "DC_Fast_150kW", "base_speed": 140.0, "weight": 0.25},
    {"protocol": "DC_UltraFast_250kW", "base_speed": 220.0, "weight": 0.15}
]

DEFECT_CATEGORIES = [
    {"category": "HV_Battery_Pack", "part_cost": 4500.0, "safety": True, "weight": 0.35},
    {"category": "Electric_Drive_Inverter", "part_cost": 1850.0, "safety": True, "weight": 0.25},
    {"category": "Air_Suspension", "part_cost": 850.0, "safety": False, "weight": 0.15},
    {"category": "ADAS_Vision_Sensor", "part_cost": 1100.0, "safety": True, "weight": 0.15},
    {"category": "Infotainment_OTA", "part_cost": 150.0, "safety": False, "weight": 0.10}
]


def generate_baseline():
    print("=" * 60)
    print("🚗 GENERATING BASELINE AUTOMOTIVE STAR SCHEMA DATASETS...")
    print("=" * 60)

    # 1. Master Dates (2024-01-01 to 2026-12-31 = 1096 days)
    print("--> 1/6 Creating dim_dates.csv...")
    dates = []
    start = datetime(2024, 1, 1)
    for d in range(1096):
        curr = start + timedelta(days=d)
        q = (curr.month - 1) // 3 + 1
        dates.append({
            "date_id": int(curr.strftime("%Y%m%d")),
            "full_date": str(curr.date()),
            "month_name": curr.strftime("%B"),
            "month_num": curr.month,
            "calendar_quarter": f"Q{q}",
            "calendar_year": curr.year,
            "fiscal_quarter": f"FY{curr.strftime('%y')}-Q{q}"
        })
    date_df = pd.DataFrame(dates)
    date_df.to_csv(os.path.join(DATA_DIR, "dim_dates.csv"), index=False)

    # 2. Master Geography & Dealers & Exchange Rates
    print("--> 2/6 Creating dim_geography.csv, dim_dealers.csv, dim_exchange_rates.csv...")
    pd.DataFrame(COUNTRIES).to_csv(os.path.join(DATA_DIR, "dim_geography.csv"), index=False)
    pd.DataFrame(DEALERS).to_csv(os.path.join(DATA_DIR, "dim_dealers.csv"), index=False)
    
    fx_rates = [
        {"currency_code": "EUR", "fx_rate_to_eur": 1.000, "effective_year": 2025},
        {"currency_code": "SEK", "fx_rate_to_eur": 0.088, "effective_year": 2025},
        {"currency_code": "NOK", "fx_rate_to_eur": 0.086, "effective_year": 2025},
        {"currency_code": "GBP", "fx_rate_to_eur": 1.185, "effective_year": 2025},
        {"currency_code": "USD", "fx_rate_to_eur": 0.920, "effective_year": 2025}
    ]
    pd.DataFrame(fx_rates).to_csv(os.path.join(DATA_DIR, "dim_exchange_rates.csv"), index=False)

    # 3. Master Vehicle Population (12,000 VINs)
    print("--> 3/6 Creating dim_vehicles.csv (12,000 VINs)...")
    vehicles = []
    for i in range(1, 12001):
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

    # 4. Vehicle Sales Facts (10,051 Sales)
    print("--> 4/6 Creating fct_vehicle_sales.csv (10,051 Sales)...")
    sales = []
    for i in range(1, 10052):
        veh = vehicles[i - 1]
        dealer = random.choice(DEALERS)
        country = [c for c in COUNTRIES if c["geo_id"] == dealer["geo_id"]][0]
        
        sale_dt = start + timedelta(days=random.randint(10, 900))
        date_id = int(sale_dt.strftime("%Y%m%d"))
        lead_days = random.randint(7, 35)
        order_dt = sale_dt - timedelta(days=lead_days)
        
        # Channel economics
        if dealer["channel"] == "Direct_Brand_Studio":
            channel = "Direct_Brand_Studio"
            discount_pct = round(random.uniform(0.015, 0.035), 4)
        elif dealer["channel"] == "Care_Subscription_Hub":
            channel = "Care_Subscription_Hub"
            discount_pct = 0.0
        else:
            channel = "Franchised_Retailer"
            discount_pct = round(random.uniform(0.045, 0.075), 4)
            
        msrp_eur = veh["base_msrp_eur"]
        cost_eur = veh["factory_unit_cost_eur"]
        fx = country["fx_to_eur"]
        
        msrp_local = round(msrp_eur / fx, 2)
        discount_local = round(msrp_local * discount_pct, 2)
        net_sale_price_local = round(msrp_local - discount_local, 2)
        
        net_rev_eur = round(net_sale_price_local * fx, 2)
        gross_profit = round(net_rev_eur - cost_eur, 2)
        gross_margin_pct = round((gross_profit / net_rev_eur) * 100, 2)
        
        sales.append({
            "sale_id": f"SAL_{i:07d}",
            "vehicle_id": veh["vehicle_id"],
            "dealer_id": dealer["dealer_id"],
            "geo_id": country["geo_id"],
            "date_id": date_id,
            "order_date": str(order_dt.date()),
            "delivery_date": str(sale_dt.date()),
            "delivery_lead_days": lead_days,
            "sale_channel": channel,
            "financing_type": random.choice(["Cash", "Finance_Loan", "Operating_Lease"]),
            "currency_code": country["currency"],
            "gross_list_price_local": msrp_local,
            "dealer_discount_local": discount_local,
            "net_sale_price_local": net_sale_price_local,
            "fx_rate_to_eur": fx,
            "net_revenue_eur": net_rev_eur,
            "factory_cost_eur": cost_eur,
            "gross_profit_eur": gross_profit,
            "gross_margin_pct": gross_margin_pct
        })
    pd.DataFrame(sales).to_csv(os.path.join(DATA_DIR, "fct_vehicle_sales.csv"), index=False)

    # 5. Connected EV Charging Telematics (35,000 Sessions with Realistic Physics)
    print("--> 5/6 Creating fct_charging_telematics.csv (35,000 Sessions)...")
    ev_cars = [v for v in vehicles if v["powertrain_type"] == "Pure_EV"]
    proto_choices = [p["protocol"] for p in CHARGER_PROTOCOLS]
    proto_weights = [p["weight"] for p in CHARGER_PROTOCOLS]
    
    telematics = []
    for i in range(1, 35001):
        veh = random.choice(ev_cars)
        session_dt = start + timedelta(days=random.randint(10, 950))
        protocol_name = random.choices(proto_choices, weights=proto_weights)[0]
        proto_info = [p for p in CHARGER_PROTOCOLS if p["protocol"] == protocol_name][0]
        
        # Realistic ambient temperature distribution
        ambient = random.randint(-25, 38)
        
        # Battery state of charge (SoC %)
        start_soc = round(random.uniform(10.0, 35.0), 1)
        end_soc = round(random.uniform(70.0, 92.0), 1)
        
        # Realistic EV Charging Speed Physics Calculation:
        # Base speed based on protocol
        base_speed = proto_info["base_speed"]
        
        if protocol_name == "AC_Wallbox_11kW":
            actual_speed = round(random.uniform(9.5, 11.0), 1)
        else:
            # Cold-weather temperature penalty (reduces speed by 25-38% if <0°C)
            if ambient < -10:
                temp_factor = random.uniform(0.60, 0.72)
            elif ambient < 0:
                temp_factor = random.uniform(0.72, 0.85)
            elif ambient < 15:
                temp_factor = random.uniform(0.88, 0.95)
            else:
                temp_factor = random.uniform(0.95, 1.02)
                
            # SoC curve tapering (speed reduces at higher end SoC)
            soc_factor = 0.82 if end_soc > 80 else 1.0
            
            actual_speed = round(base_speed * temp_factor * soc_factor, 1)
        
        kwh_delivered = round(((end_soc - start_soc) / 100.0) * veh["battery_nominal_kwh"], 2)
        duration_mins = round((kwh_delivered / actual_speed) * 60.0 + random.uniform(2.0, 8.0), 1)
        
        telematics.append({
            "session_id": f"CHG_{i:08d}",
            "vehicle_id": veh["vehicle_id"],
            "date_id": int(session_dt.strftime("%Y%m%d")),
            "session_start_time": f"{session_dt.strftime('%Y-%m-%d')} {random.randint(6, 22):02d}:{random.randint(0, 59):02d}:00",
            "session_end_time": f"{session_dt.strftime('%Y-%m-%d')} {random.randint(6, 23):02d}:{random.randint(0, 59):02d}:00",
            "session_duration_minutes": duration_mins,
            "charger_protocol": protocol_name,
            "ambient_temp_celsius": ambient,
            "start_soc_pct": start_soc,
            "end_soc_pct": end_soc,
            "energy_delivered_kwh": kwh_delivered,
            "avg_charging_speed_kw": actual_speed,
            "battery_temp_start_celsius": max(5.0, ambient + random.uniform(5.0, 12.0)),
            "battery_temp_end_celsius": max(15.0, ambient + random.uniform(15.0, 25.0)),
            "battery_temp_delta_celsius": round(random.uniform(2.0, 12.0), 1),
            "battery_preconditioned": ambient >= 10 or random.choice([True, False]),
            "estimated_range_gained_km": round(kwh_delivered * 5.5, 1)
        })
    pd.DataFrame(telematics).to_csv(os.path.join(DATA_DIR, "fct_charging_telematics.csv"), index=False)

    # 6. Warranty Claims Facts (3,000 Claims with Realistic Lifecycles)
    print("--> 6/6 Creating fct_warranty_claims.csv (3,000 Claims)...")
    comp_cats = [c["category"] for c in DEFECT_CATEGORIES]
    comp_weights = [c["weight"] for c in DEFECT_CATEGORIES]
    
    claims = []
    for i in range(1, 3001):
        sale = random.choice(sales)
        delivery_dt = datetime.strptime(sale["delivery_date"], "%Y-%m-%d")
        
        # Months in service (1 to 24 MIS)
        mis = random.randint(1, 24)
        repair_dt = delivery_dt + timedelta(days=int(mis * 30.4))
        
        # Cap repair date to calendar window
        if repair_dt > datetime(2026, 12, 31):
            repair_dt = datetime(2026, 12, 28)
            
        category_name = random.choices(comp_cats, weights=comp_weights)[0]
        cat_info = [c for c in DEFECT_CATEGORIES if c["category"] == category_name][0]
        
        labor_hrs = random.choice([1.5, 2.0, 3.5, 5.0])
        labor_cost = round(labor_hrs * 120.0, 2)
        parts_cost = cat_info["part_cost"]
        total_claim_cost = round(labor_cost + parts_cost, 2)
        
        claims.append({
            "claim_id": f"CLM_{i:07d}",
            "vehicle_id": sale["vehicle_id"],
            "dealer_id": sale["dealer_id"],
            "geo_id": sale["geo_id"],
            "date_id": int(repair_dt.strftime("%Y%m%d")),
            "repair_date": str(repair_dt.date()),
            "component_category": category_name,
            "failure_symptom_code": f"ERR_{category_name.upper()}_DIAG",
            "months_in_service": mis,
            "mileage_at_failure_km": int(mis * random.randint(1100, 1800)),
            "labor_hours": labor_hrs,
            "labor_cost_eur": labor_cost,
            "parts_cost_eur": parts_cost,
            "total_claim_cost_eur": total_claim_cost,
            "is_safety_critical": cat_info["safety"],
            "claim_status": random.choice(["Approved", "Reimbursed", "Under_Investigation"])
        })
    pd.DataFrame(claims).to_csv(os.path.join(DATA_DIR, "fct_warranty_claims.csv"), index=False)

    print("\n✅ All Star Schema data marts successfully generated with realistic physics & lifecycles!")
    print("=" * 60)


if __name__ == "__main__":
    generate_baseline()
