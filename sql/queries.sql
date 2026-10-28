-- ============================================================================
-- Project 5: Telecom Churn - Production Analytical & KPI Queries
-- Engine: SQLite 3+ / DuckDB Compatible
-- ============================================================================

-- ============================================================================
-- 1. Raw Data Ingestion & Blank Charge Repair CTE
-- Demonstrates handling of 11 tenure=0 records with blank TotalCharges
-- ============================================================================
-- Query Name: raw_data_repair_cte
WITH raw_cleaned AS (
    SELECT 
        customerID AS customer_id,
        gender,
        CAST(SeniorCitizen AS INTEGER) AS senior_citizen,
        Partner AS partner,
        Dependents AS dependents,
        CAST(tenure AS INTEGER) AS tenure_months,
        PhoneService AS phone_service,
        MultipleLines AS multiple_lines,
        InternetService AS internet_service,
        OnlineSecurity AS online_security,
        OnlineBackup AS online_backup,
        DeviceProtection AS device_protection,
        TechSupport AS tech_support,
        StreamingTV AS streaming_tv,
        StreamingMovies AS streaming_movies,
        Contract AS contract_type,
        PaperlessBilling AS paperless_billing,
        PaymentMethod AS payment_method,
        CAST(MonthlyCharges AS REAL) AS monthly_charges,
        -- Convert blank TotalCharges for tenure=0 to 0.0
        CASE 
            WHEN TRIM(COALESCE(TotalCharges, '')) = '' THEN 0.0
            ELSE CAST(TotalCharges AS REAL)
        END AS total_charges_repaired,
        CASE WHEN Churn = 'Yes' THEN 1 ELSE 0 END AS churn_flag
    FROM raw_telco_churn
)
SELECT 
    COUNT(*) AS total_raw_records,
    SUM(CASE WHEN tenure_months = 0 THEN 1 ELSE 0 END) AS zero_tenure_count,
    SUM(CASE WHEN tenure_months = 0 AND total_charges_repaired = 0.0 THEN 1 ELSE 0 END) AS repaired_blank_charges_count,
    ROUND(100.0 * SUM(churn_flag) / COUNT(*), 2) AS raw_churn_rate_pct
FROM raw_cleaned;


-- ============================================================================
-- 2. Churn Rate & Monthly Recurring Revenue (MRR) Loss by Contract & Internet Tier
-- ============================================================================
-- Query Name: churn_and_mrr_by_contract_internet
SELECT 
    c.contract_type,
    sp.internet_service,
    COUNT(f.fact_id) AS total_customers,
    SUM(f.churn_flag) AS churned_customers,
    ROUND(100.0 * SUM(f.churn_flag) / COUNT(f.fact_id), 2) AS churn_rate_pct,
    ROUND(SUM(f.monthly_charges), 2) AS total_mrr,
    ROUND(SUM(CASE WHEN f.churn_flag = 1 THEN f.monthly_charges ELSE 0 END), 2) AS churned_mrr,
    ROUND(100.0 * SUM(CASE WHEN f.churn_flag = 1 THEN f.monthly_charges ELSE 0 END) / SUM(f.monthly_charges), 2) AS mrr_loss_pct,
    ROUND(AVG(f.monthly_charges), 2) AS avg_monthly_charge
FROM fact_churn_analysis f
JOIN dim_contract c ON f.contract_key = c.contract_key
JOIN dim_service_profile sp ON f.service_key = sp.service_key
GROUP BY c.contract_type, sp.internet_service
ORDER BY churned_mrr DESC;


-- ============================================================================
-- 3. Toxic Service Bundles: Unbundled Premium Internet vs Supported Bundles
-- ============================================================================
-- Query Name: toxic_service_bundles
SELECT 
    c.contract_type,
    sp.internet_service,
    sp.tech_support,
    sp.online_security,
    COUNT(f.fact_id) AS customer_count,
    SUM(f.churn_flag) AS churn_count,
    ROUND(100.0 * SUM(f.churn_flag) / COUNT(f.fact_id), 2) AS churn_rate_pct,
    ROUND(SUM(f.monthly_charges), 2) AS segment_mrr,
    ROUND(SUM(CASE WHEN f.churn_flag = 1 THEN f.monthly_charges ELSE 0 END), 2) AS mrr_lost,
    DENSE_RANK() OVER (ORDER BY ROUND(100.0 * SUM(f.churn_flag) / COUNT(f.fact_id), 2) DESC) AS toxic_rank
FROM fact_churn_analysis f
JOIN dim_service_profile sp ON f.service_key = sp.service_key
JOIN dim_contract c ON f.contract_key = c.contract_key
WHERE sp.internet_service != 'No'
GROUP BY 
    c.contract_type,
    sp.internet_service,
    sp.tech_support,
    sp.online_security
HAVING COUNT(f.fact_id) >= 50
ORDER BY churn_rate_pct DESC
LIMIT 10;


-- ============================================================================
-- 4. Survival & Hazard Analysis: Tenure Cohort Attrition & Cumulative Attrition
-- Uses Window Functions (SUM() OVER ()) to isolate the Infant Mortality Hazard
-- ============================================================================
-- Query Name: tenure_hazard_analysis
WITH cohort_stats AS (
    SELECT 
        tb.tenure_band_key,
        tb.tenure_band_label,
        tb.lifecycle_stage,
        COUNT(f.fact_id) AS cohort_customer_count,
        SUM(f.churn_flag) AS cohort_churn_count,
        ROUND(100.0 * SUM(f.churn_flag) / COUNT(f.fact_id), 2) AS cohort_hazard_rate_pct,
        ROUND(SUM(f.monthly_charges), 2) AS cohort_total_mrr,
        ROUND(SUM(CASE WHEN f.churn_flag = 1 THEN f.monthly_charges ELSE 0 END), 2) AS cohort_churned_mrr
    FROM fact_churn_analysis f
    JOIN dim_tenure_band tb ON f.tenure_band_key = tb.tenure_band_key
    GROUP BY tb.tenure_band_key, tb.tenure_band_label, tb.lifecycle_stage
)
SELECT 
    tenure_band_label,
    lifecycle_stage,
    cohort_customer_count,
    cohort_churn_count,
    cohort_hazard_rate_pct,
    -- Share of total churn events occurring in this tenure band
    ROUND(100.0 * cohort_churn_count / SUM(cohort_churn_count) OVER (), 2) AS share_of_all_churn_pct,
    -- Cumulative churn share across the lifecycle
    ROUND(100.0 * SUM(cohort_churn_count) OVER (ORDER BY tenure_band_key) / SUM(cohort_churn_count) OVER (), 2) AS cumulative_churn_share_pct,
    cohort_churned_mrr
FROM cohort_stats
ORDER BY tenure_band_key ASC;


-- ============================================================================
-- 5. Payment Channel Friction: Friction vs Automated Retention Analysis
-- ============================================================================
-- Query Name: payment_channel_friction
SELECT 
    pm.payment_category,
    pm.payment_method,
    pm.is_automatic_flag,
    COUNT(f.fact_id) AS total_customers,
    SUM(f.churn_flag) AS churned_customers,
    ROUND(100.0 * SUM(f.churn_flag) / COUNT(f.fact_id), 2) AS churn_rate_pct,
    ROUND(SUM(f.monthly_charges), 2) AS total_mrr,
    ROUND(SUM(CASE WHEN f.churn_flag = 1 THEN f.monthly_charges ELSE 0 END), 2) AS mrr_lost
FROM fact_churn_analysis f
JOIN dim_payment_profile pm ON f.payment_key = pm.payment_key
GROUP BY pm.payment_category, pm.payment_method, pm.is_automatic_flag
ORDER BY churn_rate_pct DESC;


-- ============================================================================
-- 6. ML Risk Tier Summary & Strategic Retention Action Queue
-- ============================================================================
-- Query Name: risk_tier_retention_summary
SELECT 
    rt.risk_tier_label,
    rt.recommended_retention_action,
    COUNT(f.fact_id) AS customer_count,
    ROUND(100.0 * COUNT(f.fact_id) / (SELECT COUNT(*) FROM fact_churn_analysis), 2) AS customer_share_pct,
    SUM(f.churn_flag) AS actual_churners,
    ROUND(100.0 * SUM(f.churn_flag) / COUNT(f.fact_id), 2) AS tier_churn_rate_pct,
    ROUND(AVG(f.predicted_churn_prob), 4) AS avg_model_prob,
    ROUND(SUM(f.revenue_at_risk), 2) AS total_monthly_rev_at_risk,
    ROUND(SUM(f.clv_estimate), 2) AS total_clv_exposure
FROM fact_churn_analysis f
JOIN dim_risk_tier rt ON f.risk_tier_key = rt.risk_tier_key
GROUP BY rt.risk_tier_label, rt.recommended_retention_action, rt.risk_tier_key
ORDER BY rt.risk_tier_key DESC;
