-- ============================================================================
-- Project 5: Telecom Churn Prediction and Retention Strategy
-- Star-Schema Relational Architecture & Analytical Views
-- Engine: SQLite 3+ / DuckDB Compatible
-- ============================================================================

-- 1. Dimension: Customer Demographics
CREATE TABLE IF NOT EXISTS dim_customer (
    customer_key INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id TEXT NOT NULL UNIQUE,
    gender TEXT NOT NULL,
    senior_citizen_flag INTEGER NOT NULL,
    senior_citizen_label TEXT NOT NULL,
    partner_flag INTEGER NOT NULL,
    partner_label TEXT NOT NULL,
    dependents_flag INTEGER NOT NULL,
    dependents_label TEXT NOT NULL,
    family_structure TEXT NOT NULL
);

-- 2. Dimension: Contract Terms
CREATE TABLE IF NOT EXISTS dim_contract (
    contract_key INTEGER PRIMARY KEY AUTOINCREMENT,
    contract_type TEXT NOT NULL,
    term_months INTEGER NOT NULL,
    paperless_billing_flag INTEGER NOT NULL,
    paperless_billing_label TEXT NOT NULL
);

-- 3. Dimension: Service Profile & Add-on Products
CREATE TABLE IF NOT EXISTS dim_service_profile (
    service_key INTEGER PRIMARY KEY AUTOINCREMENT,
    phone_service TEXT NOT NULL,
    multiple_lines TEXT NOT NULL,
    internet_service TEXT NOT NULL,
    online_security TEXT NOT NULL,
    online_backup TEXT NOT NULL,
    device_protection TEXT NOT NULL,
    tech_support TEXT NOT NULL,
    streaming_tv TEXT NOT NULL,
    streaming_movies TEXT NOT NULL,
    has_tech_support_flag INTEGER NOT NULL,
    has_online_security_flag INTEGER NOT NULL,
    has_support_bundle_flag INTEGER NOT NULL,
    total_service_count INTEGER NOT NULL
);

-- 4. Dimension: Payment & Billing Profile
CREATE TABLE IF NOT EXISTS dim_payment_profile (
    payment_key INTEGER PRIMARY KEY AUTOINCREMENT,
    payment_method TEXT NOT NULL,
    is_automatic_flag INTEGER NOT NULL,
    payment_category TEXT NOT NULL
);

-- 5. Dimension: Tenure Lifecycle Bands
CREATE TABLE IF NOT EXISTS dim_tenure_band (
    tenure_band_key INTEGER PRIMARY KEY,
    tenure_band_label TEXT NOT NULL,
    min_months INTEGER NOT NULL,
    max_months INTEGER NOT NULL,
    lifecycle_stage TEXT NOT NULL
);

-- 6. Dimension: ML Churn Risk Tier
CREATE TABLE IF NOT EXISTS dim_risk_tier (
    risk_tier_key INTEGER PRIMARY KEY,
    risk_tier_label TEXT NOT NULL,
    min_probability REAL NOT NULL,
    max_probability REAL NOT NULL,
    recommended_retention_action TEXT NOT NULL
);

-- 7. Central Fact: Customer Subscription & Churn Metrics
CREATE TABLE IF NOT EXISTS fact_churn_analysis (
    fact_id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_key INTEGER NOT NULL,
    contract_key INTEGER NOT NULL,
    service_key INTEGER NOT NULL,
    payment_key INTEGER NOT NULL,
    tenure_band_key INTEGER NOT NULL,
    risk_tier_key INTEGER NOT NULL,
    tenure_months INTEGER NOT NULL,
    monthly_charges REAL NOT NULL,
    total_charges REAL NOT NULL,
    churn_flag INTEGER NOT NULL,
    churn_label TEXT NOT NULL,
    predicted_churn_prob REAL NOT NULL,
    clv_estimate REAL NOT NULL,
    revenue_at_risk REAL NOT NULL,
    top_churn_driver TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_key) REFERENCES dim_customer (customer_key),
    FOREIGN KEY (contract_key) REFERENCES dim_contract (contract_key),
    FOREIGN KEY (service_key) REFERENCES dim_service_profile (service_key),
    FOREIGN KEY (payment_key) REFERENCES dim_payment_profile (payment_key),
    FOREIGN KEY (tenure_band_key) REFERENCES dim_tenure_band (tenure_band_key),
    FOREIGN KEY (risk_tier_key) REFERENCES dim_risk_tier (risk_tier_key)
);

-- Indexes for Aggregation and Filtering Performance
CREATE INDEX IF NOT EXISTS idx_fact_churn_risk ON fact_churn_analysis(risk_tier_key, churn_flag);
CREATE INDEX IF NOT EXISTS idx_fact_churn_cust ON fact_churn_analysis(customer_key);
CREATE INDEX IF NOT EXISTS idx_fact_churn_contract ON fact_churn_analysis(contract_key);
CREATE INDEX IF NOT EXISTS idx_fact_churn_service ON fact_churn_analysis(service_key);
CREATE INDEX IF NOT EXISTS idx_fact_churn_tenure ON fact_churn_analysis(tenure_band_key);

-- 8. Master View for BI and Analytics
DROP VIEW IF EXISTS vw_telco_churn_master;
CREATE VIEW vw_telco_churn_master AS
SELECT 
    f.fact_id,
    c.customer_id,
    c.gender,
    c.senior_citizen_label,
    c.partner_label,
    c.dependents_label,
    c.family_structure,
    ct.contract_type,
    ct.term_months,
    ct.paperless_billing_label,
    sp.phone_service,
    sp.multiple_lines,
    sp.internet_service,
    sp.online_security,
    sp.online_backup,
    sp.device_protection,
    sp.tech_support,
    sp.streaming_tv,
    sp.streaming_movies,
    sp.has_tech_support_flag,
    sp.has_online_security_flag,
    sp.has_support_bundle_flag,
    sp.total_service_count,
    pm.payment_method,
    pm.is_automatic_flag,
    pm.payment_category,
    tb.tenure_band_label,
    tb.lifecycle_stage,
    rt.risk_tier_label,
    rt.recommended_retention_action,
    f.tenure_months,
    f.monthly_charges,
    f.total_charges,
    f.churn_flag,
    f.churn_label,
    f.predicted_churn_prob,
    f.clv_estimate,
    f.revenue_at_risk,
    f.top_churn_driver
FROM fact_churn_analysis f
JOIN dim_customer c ON f.customer_key = c.customer_key
JOIN dim_contract ct ON f.contract_key = ct.contract_key
JOIN dim_service_profile sp ON f.service_key = sp.service_key
JOIN dim_payment_profile pm ON f.payment_key = pm.payment_key
JOIN dim_tenure_band tb ON f.tenure_band_key = tb.tenure_band_key
JOIN dim_risk_tier rt ON f.risk_tier_key = rt.risk_tier_key;
