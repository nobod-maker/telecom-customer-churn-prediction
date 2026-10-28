"""
05_Telecom_Churn: SQLite Database Builder & Analytical Query Runner
Author: worker_m5_telco
Builds telecom_churn.db, executes star-schema DDL, loads dimensions/facts,
and runs all production SQL analytics and validation checks.
"""

import os
import sqlite3
import pandas as pd

def build_telecom_database():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sql_dir = os.path.join(base_dir, 'sql')
    data_dir = os.path.join(base_dir, 'data')
    raw_dir = os.path.join(data_dir, 'raw')
    clean_dir = os.path.join(data_dir, 'clean')
    
    # Store DB in both base_dir and sql_dir for convenient access
    db_paths = [
        os.path.join(base_dir, 'telecom_churn.db'),
        os.path.join(sql_dir, 'telecom_churn.db')
    ]
    
    print("=" * 75)
    print("Project 5: Telecom Churn - SQLite Star Schema Database Builder")
    print("=" * 75)
    
    for db_path in db_paths:
        if os.path.exists(db_path):
            os.remove(db_path)
            
    primary_db = db_paths[0]
    conn = sqlite3.connect(primary_db)
    cursor = conn.cursor()
    
    # Enable foreign keys
    cursor.execute("PRAGMA foreign_keys = ON;")
    
    # 1. Execute schema.sql
    schema_path = os.path.join(sql_dir, 'schema.sql')
    print(f"\n[1/5] Applying DDL schema from {schema_path}...")
    with open(schema_path, 'r', encoding='utf-8') as f:
        schema_sql = f.read()
    cursor.executescript(schema_sql)
    conn.commit()
    print("      Star-schema tables, indexes, and views created successfully.")
    
    # 2. Ingest raw dataset into raw_telco_churn table (for raw CTE verification)
    raw_csv = os.path.join(raw_dir, 'telco_customer_churn.csv')
    if not os.path.exists(raw_csv):
        raw_csv = os.path.join(data_dir, 'sample_data.csv')
    print(f"\n[2/5] Loading raw data into raw_telco_churn table from {raw_csv}...")
    df_raw = pd.read_csv(raw_csv)
    df_raw.to_sql('raw_telco_churn', conn, if_exists='replace', index=False)
    conn.commit()
    print(f"      Ingested {len(df_raw):,} raw records into raw_telco_churn.")
    
    # 3. Populate Star-Schema Dimensions & Fact
    print("\n[3/5] Populating dimensional and fact tables from clean CSVs...")
    tables = [
        ('dim_customer', 'dim_customer.csv'),
        ('dim_contract', 'dim_contract.csv'),
        ('dim_service_profile', 'dim_service_profile.csv'),
        ('dim_payment_profile', 'dim_payment_profile.csv'),
        ('dim_tenure_band', 'dim_tenure_band.csv'),
        ('dim_risk_tier', 'dim_risk_tier.csv'),
        ('fact_churn_analysis', 'fact_churn_analysis.csv')
    ]
    
    for tbl_name, csv_name in tables:
        csv_path = os.path.join(clean_dir, csv_name)
        df_tbl = pd.read_csv(csv_path)
        df_tbl.to_sql(tbl_name, conn, if_exists='append', index=False)
        print(f"      Table '{tbl_name}': {len(df_tbl):,} rows inserted.")
    conn.commit()
    
    # 4. Integrity and Row Count Verification
    print("\n[4/5] Running relational integrity verification...")
    cursor.execute("SELECT COUNT(*) FROM fact_churn_analysis;")
    fact_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*), SUM(churn_flag) FROM fact_churn_analysis;")
    total_cust, churn_cust = cursor.fetchone()
    churn_rate = (churn_cust / total_cust) * 100
    
    # Check foreign key violations
    cursor.execute("PRAGMA foreign_key_check;")
    fk_errors = cursor.fetchall()
    
    print(f"      Total Fact Records: {fact_count:,}")
    print(f"      Total Churned Customers: {churn_cust:,} ({churn_rate:.2f}%)")
    print(f"      Foreign Key Violations: {len(fk_errors)}")
    assert fact_count == 7043, f"Expected 7,043 rows, found {fact_count}"
    assert len(fk_errors) == 0, f"Foreign key check failed: {fk_errors}"
    
    # 5. Execute production analytical queries from queries.sql
    queries_path = os.path.join(sql_dir, 'queries.sql')
    print(f"\n[5/5] Executing analytical queries from {queries_path}...")
    with open(queries_path, 'r', encoding='utf-8') as f:
        full_sql = f.read()
        
    # Split queries by semicolon separator
    statements = [s.strip() for s in full_sql.split(';') if s.strip()]
    query_names = [
        "Raw Data Repair CTE",
        "Churn & MRR Loss by Contract & Internet Tier",
        "Toxic Service Bundles",
        "Survival & Hazard Analysis (Tenure Cohort Attrition)",
        "Payment Channel Friction Analysis",
        "ML Risk Tier Summary & Retention Action Queue"
    ]
    
    for idx, stmt in enumerate(statements):
        title = query_names[idx] if idx < len(query_names) else f"Query {idx+1}"
        print(f"\n--- {title} ---")
        try:
            df_res = pd.read_sql_query(stmt, conn)
            print(df_res.head(8).to_string(index=False))
        except Exception as e:
            print(f"Error executing {title}: {e}")
            raise e
            
    conn.close()
    
    # Copy DB to sql/telecom_churn.db as secondary copy
    import shutil
    shutil.copyfile(db_paths[0], db_paths[1])
    print(f"\n[SUCCESS] SQLite database successfully built and verified:")
    print(f"          - {db_paths[0]}")
    print(f"          - {db_paths[1]}")

if __name__ == '__main__':
    build_telecom_database()
