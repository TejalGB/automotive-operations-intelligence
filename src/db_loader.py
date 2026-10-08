"""
PROJECT: Global Connected Automotive & Commercial Intelligence (AutoOps 360)
MODULE: src/db_loader.py
DESCRIPTION: Simple, standard MySQL Database Loader.
             Uses basic SQL INSERT statements to load data from `data/marts/`
             into your local MySQL database (`auto_ops_dw`).
"""

import os
import sys
import pandas as pd
import pymysql

# Ensure UTF-8 stdout for Windows consoles
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_MARTS_DIR = os.path.join(BASE_DIR, "data", "marts")
SQL_DIR = os.path.join(BASE_DIR, "sql")

# Simple MySQL Configuration
DB_CONFIG = {
    "host": os.getenv("MYSQL_HOST", "localhost"),
    "user": os.getenv("MYSQL_USER", "root"),
    "password": os.getenv("MYSQL_PASSWORD", "password"),
    "database": os.getenv("MYSQL_DATABASE", "auto_ops_dw"),
    "port": int(os.getenv("MYSQL_PORT", 3306)),
    "autocommit": True
}

TABLE_LOAD_ORDER = [
    ("dim_dates", "dim_dates.csv"),
    ("dim_geography", "dim_geography.csv"),
    ("dim_dealers", "dim_dealers.csv"),
    ("dim_vehicles", "dim_vehicles.csv"),
    ("dim_exchange_rates", "dim_exchange_rates.csv"),
    ("fct_vehicle_sales", "fct_vehicle_sales.csv"),
    ("fct_charging_telematics", "fct_charging_telematics.csv"),
    ("fct_warranty_claims", "fct_warranty_claims.csv")
]


def execute_sql_file(cursor, file_path):
    """Executes a standard .sql script file statement by statement."""
    with open(file_path, "r", encoding="utf-8") as f:
        sql_content = f.read()
    
    statements = sql_content.split(";")
    for stmt in statements:
        cleaned = stmt.strip()
        if cleaned:
            cursor.execute(cleaned)


def load_csv_to_table(cursor, table_name, csv_path):
    """Reads a CSV file and inserts rows into MySQL using standard SQL INSERTs."""
    df = pd.read_csv(csv_path)
    # Replace NaN with None so SQL receives NULL
    df = df.where(pd.notnull(df), None)
    
    cols = ", ".join([f"`{c}`" for c in df.columns])
    placeholders = ", ".join(["%s"] * len(df.columns))
    insert_sql = f"INSERT INTO `{table_name}` ({cols}) VALUES ({placeholders})"
    
    # Convert dataframe to list of tuples for batch insert
    records = [tuple(row) for row in df.to_numpy()]
    
    # Insert in batches of 1,000 rows
    batch_size = 1000
    for i in range(0, len(records), batch_size):
        batch = records[i:i + batch_size]
        cursor.executemany(insert_sql, batch)
        
    print(f"   ✓ Loaded {len(records):,} rows into `{table_name}`")


def main():
    print("=" * 70)
    print(f"🗄️ [AutoOps 360] Loading Data Marts into MySQL ({DB_CONFIG['host']}:{DB_CONFIG['port']})...")
    print("=" * 70)
    
    try:
        conn = pymysql.connect(**DB_CONFIG)
        cursor = conn.cursor()
        print("✅ Connected to MySQL database successfully.\n")
    except Exception as e:
        print(f"⚠️ Could not connect to MySQL server: {e}")
        print("💡 Hint: Ensure MySQL is running on your machine (e.g. MySQL Workbench / XAMPP).")
        print("👉 You can also import the CSV files directly in Power BI Desktop from 'data/marts/'!")
        return

    # 1. Initialize schema
    ddl_file = os.path.join(SQL_DIR, "01_schema_ddl.sql")
    if os.path.exists(ddl_file):
        print("--> Executing 01_schema_ddl.sql to create tables...")
        execute_sql_file(cursor, ddl_file)
        print("   ✓ Tables created successfully.\n")

    # 2. Insert data
    print("--> Ingesting Star Schema data from CSV files...")
    for table_name, csv_filename in TABLE_LOAD_ORDER:
        csv_path = os.path.join(DATA_MARTS_DIR, csv_filename)
        if os.path.exists(csv_path):
            load_csv_to_table(cursor, table_name, csv_path)
            
    # 3. Create views
    views_file = os.path.join(SQL_DIR, "02_analytical_views.sql")
    if os.path.exists(views_file):
        print("\n--> Creating Analytical Views (02_analytical_views.sql)...")
        execute_sql_file(cursor, views_file)
        print("   ✓ Analytical views ready for Power BI.\n")

    cursor.close()
    conn.close()
    print("=" * 70)
    print("✅ MySQL Database Setup Complete! Ready for Power BI & Queries.")
    print("=" * 70)


if __name__ == "__main__":
    main()
