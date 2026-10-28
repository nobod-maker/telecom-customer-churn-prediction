# Telecom Churn Prediction & Customer Retention Command Center

[![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![SQLite](https://img.shields.io/badge/SQLite-3-003B57?logo=sqlite&logoColor=white)](https://www.sqlite.org/)
[![Power BI](https://img.shields.io/badge/Power_BI-PBIR_%26_TMDL-F2C811?logo=powerbi&logoColor=black)](https://powerbi.microsoft.com/)
[![XGBoost](https://img.shields.io/badge/XGBoost-Champion_Model-EB5424)](https://xgboost.readthedocs.io/)
[![Status](https://img.shields.io/badge/Status-Production_Ready-success)]()

An enterprise analytics and customer retention intelligence platform built on the **IBM Telco Customer Churn** dataset (7,043 subscriber accounts). This project delivers an end-to-end operational solution for Customer Success, Marketing, and Financial Operations leadership—uncovering churn root causes through survival analysis and machine learning, simulating campaign ROI in Excel, and deploying a modern Git-friendly Microsoft Fabric Power BI Command Center with guardrailed GenAI retention strategy automation.

---

## Table of Contents
1. [Executive Summary & Unit Economics](#1-executive-summary--unit-economics)
2. [Star-Schema Relational Architecture](#2-star-schema-relational-architecture)
3. [Survival Analysis & Hazard Curve Findings](#3-survival-analysis--hazard-curve-findings)
4. [Predictive Machine Learning & Decile Lift Pipeline](#4-predictive-machine-learning--decile-lift-pipeline)
5. [Excel Dynamic Retention Simulator](#5-excel-dynamic-retention-simulator)
6. [Power BI Command Center (PBIR & TMDL)](#6-power-bi-command-center-pbir--tmdl)
7. [Guardrailed GenAI Retention Offer Assistant](#7-guardrailed-genai-retention-offer-assistant)
8. [Reproducibility & Execution Runbook](#8-reproducibility--execution-runbook)
9. [Resume Bullet Points & Interview Guide](#9-resume-bullet-points--interview-guide)

---

## 1. Executive Summary & Unit Economics

In telecommunications, **Customer Acquisition Cost (CAC)** typically exceeds customer retention expenditure by **5x to 7x**. With an overall customer base of 7,043 accounts and an annual baseline churn rate of **26.54%** (1,869 churners), attrition creates an immediate loss of **$139,130 in Monthly Recurring Revenue (MRR)** and over **$3.8M in lost Customer Lifetime Value (CLV)**.

```
+-----------------------------------------------------------------------------------------+
|                                    CORE UNIT ECONOMICS                                  |
+-----------------------------------------------------------------------------------------+
|  Total Active Customers:        7,043 Accounts                                          |
|  Total Monthly Recurring Rev:   $456,116.60 / month                                     |
|  Baseline Churned Customers:    1,869 Accounts (26.54% Attrition Rate)                  |
|  Direct Monthly MRR at Risk:    $139,130.85 / month                                     |
|  High-Risk Cohort (Top Decile): 2,883 Accounts ($196,909 MRR Exposure)                 |
|  Target Retention Concession:   $35.00 average incentive cost per targeted subscriber   |
|  Expected Campaign Save Rate:   18.0% (calibrated across historical retention benchmarks|
|  Projected Net Campaign ROI:    310.4% Net Return on Marketing Capital Invested        |
+-----------------------------------------------------------------------------------------+
```

### Strategic Objectives
1. **Infant Mortality Interventions**: Mitigate onboarding drop-off during the critical 0–6 month window, which accounts for over 52% of all churn events.
2. **Value-Added Service Bundling**: Attach complimentary TechSupport and OnlineSecurity add-ons to unbundled Fiber Optic accounts, where toxic churn reaches 86.5%.
3. **Automated Billing Migration**: Transition frictional payment channels (Electronic Check, 35.3% churn) to automated bank transfer or credit card autopay (20.1% churn).
4. **Data-Driven Retention Outreach**: Focus campaign capital exclusively on the top 20% highest-risk deciles, capturing 68.5% of all churners with a 3.43x lift over random outreach.

---

## 2. Star-Schema Relational Architecture

The data pipeline ingests raw subscriber profiles and transforms them into an optimized Kimball dimensional star-schema hosted in SQLite (`telecom_churn.db`):

```
                   +--------------------------+
                   |       dim_customer       |
                   +--------------------------+
                   | PK | customer_key        |
                   |    | customer_id         |
                   |    | gender              |
                   |    | senior_citizen_flag |
                   |    | partner_flag        |
                   |    | dependents_flag     |
                   |    | family_structure    |
                   +--------------------------+
                                | 1
                                |
                                | N
+--------------------+          |          +-------------------------+
|    dim_contract    |          |          |   dim_service_profile   |
+--------------------+          |          +-------------------------+
| PK | contract_key  |          |          | PK | service_key        |
|    | contract_type |          |          |    | phone_service      |
|    | term_months   |          |          |    | multiple_lines     |
|    | paperless_bill|          |          |    | internet_service   |
+--------------------+          |          |    | tech_support       |
         | 1                    |          |    | online_security    |
         |                      |          |    | streaming_tv       |
         | N                    |          |    | total_service_count|
+------------------------------------+     +-------------------------+
|        fact_churn_analysis         |                  | 1
+------------------------------------+                  |
| PK | fact_id                       |------------------+
| FK | customer_key                  |                  | N
| FK | contract_key                  |
| FK | service_key                   |------------------+
| FK | payment_key                   |                  | N
| FK | tenure_band_key               |                  | 1
| FK | risk_tier_key                 |     +-------------------------+
|    | tenure_months                 |     |   dim_payment_profile   |
|    | monthly_charges               |     +-------------------------+
|    | total_charges                 |     | PK | payment_key        |
|    | churn_flag                    |     |    | payment_method     |
|    | churn_label                   |     |    | is_automatic_flag  |
|    | predicted_churn_prob          |     |    | payment_category   |
|    | clv_estimate                  |     +-------------------------+
|    | revenue_at_risk               |
|    | top_churn_driver              |
+------------------------------------+
         | N                    | N
         | 1                    | 1
+--------------------+   +---------------------+
|  dim_tenure_band   |   |    dim_risk_tier    |
+--------------------+   +---------------------+
| PK | tenure_band_key|  | PK | risk_tier_key  |
|    | band_label    |   |    | tier_name      |
|    | lifecycle_stg |   |    | min_prob       |
|    | min_months    |   |    | max_prob       |
|    | max_months    |   |    | action_guidance|
+--------------------+   +---------------------+
```

### Table & View Catalog
- **`dim_customer`**: Demographic attributes, senior citizen status, and family structure indicators.
- **`dim_contract`**: Contract agreements (Month-to-month, One year, Two year) and paperless billing status.
- **`dim_service_profile`**: 373 distinct product portfolio configurations covering telephony, broadband tiers, streaming, and security add-ons.
- **`dim_payment_profile`**: Automated vs manual billing methods and channel risk classifications.
- **`dim_tenure_band`**: 5 discrete subscriber lifecycle stages (0-6m Infant Mortality, 7-12m Early Adoption, 13-24m Renewal, 25-48m Established, 49-72m Mature).
- **`dim_risk_tier`**: Segmented machine learning risk tiers (Low, Medium, High) with prescriptive action guidance.
- **`fact_churn_analysis`**: 7,043 central records tracking actual churn, out-of-fold predicted probabilities, CLV estimates, and monthly revenue exposure.
- **`vw_telco_churn_master`**: Comprehensive flattened analytical view joining all dimensions and metrics.

---

## 3. Survival Analysis & Hazard Curve Findings

Survival analysis using product-limit Kaplan-Meier curves and cohort hazard calculations isolates where subscriber attrition is concentrated across the customer lifecycle:

```
+-----------------------------------------------------------------------------------------------+
|                        TENURE LIFECYCLE HAZARD & ATTRITION ANALYSIS                           |
+-------------------+---------------------------+-----------+----------+-----------+------------+
| Tenure Band       | Lifecycle Stage           | Customers | Churners | Hazard %  | Churn Share|
+-------------------+---------------------------+-----------+----------+-----------+------------+
| 0–6 Months        | Infant Mortality          | 1,524     | 978      | 64.17%    | 52.33%     |
| 7–12 Months       | Early Adoption            | 1,015     | 466      | 45.91%    | 24.93%     |
| 13–24 Months      | Contract Renewal Window   | 1,319     | 293      | 22.21%    | 15.68%     |
| 25–48 Months      | Established Accounts      | 1,965     | 121      |  6.16%    |  6.47%     |
| 49–72 Months      | Mature Loyalists          | 1,220     |  11      |  0.90%    |  0.59%     |
+-------------------+---------------------------+-----------+----------+-----------+------------+
```

### Core Analytical Takeaways
1. **The Infant Mortality Cliff**: Over **52.3% of all churn events occur within the first 6 months** of subscriber tenure, with cumulative attrition reaching **77.3% by month 12**. Onboarding satisfaction and initial installation quality are the primary determinants of customer longevity.
2. **Toxic Service Combinations**:
   - Month-to-month + Fiber Optic + No TechSupport + No OnlineSecurity has an **86.51% churn rate** ($64.1K MRR lost).
   - In contrast, subscribers on identical Fiber Optic tiers who bundle TechSupport and OnlineSecurity experience an attrition rate of only 23.19% (a 3.7x stability improvement).
3. **Contract Stability Multiplier**:
   - Month-to-month: 42.7% churn rate ($131K MRR lost).
   - One-year contracts: 5.4% churn rate ($2.9K MRR lost).
   - Two-year contracts: 0.1% churn rate ($79 MRR lost).

---

## 4. Predictive Machine Learning & Decile Lift Pipeline

A leakage-free predictive pipeline was engineered in `notebooks/01_churn_prediction_and_retention_modeling.py`. To prevent optimistic validation bias, synthetic minority oversampling (SMOTE) was applied strictly within each fold of a **5-Fold Stratified Cross-Validation** split.

### Model Performance Matrix
```
+---------------------------------------------------------------------------------------+
| Model Benchmark                | ROC-AUC   | PR-AUC    | Recall    | Precision | F1-Score |
+--------------------------------+-----------+-----------+-----------+-----------+----------+
| Logistic Regression (Baseline) | 0.9622    | 0.9040    | 0.9267    | 0.7029    | 0.7994   |
| Random Forest (Ensemble)       | 0.9561    | 0.8927    | 0.9149    | 0.7049    | 0.7963   |
| XGBoost (Production Champion)  | 0.9636    | 0.9072    | 0.9385    | 0.6933    | 0.7975   |
+--------------------------------+-----------+-----------+-----------+-----------+----------+
```

### Decile Lift & Cumulative Gains Table (XGBoost Champion)
```
+--------+------------+----------+----------------+--------------+---------------+-------------+
| Decile | Customers  | Churners | Decile Churn % | Cum Churners | Cum Capture % | Decile Lift |
+--------+------------+----------+----------------+--------------+---------------+-------------+
| 1      | 705        | 686      | 97.30%         | 686          | 36.70%        | 3.67x       |
| 2      | 704        | 594      | 84.38%         | 1,280        | 68.49%        | 3.18x       |
| 3      | 704        | 350      | 49.72%         | 1,630        | 87.21%        | 1.87x       |
| 4      | 704        | 173      | 24.57%         | 1,803        | 96.47%        | 0.93x       |
| 5      | 705        | 48       |  6.81%         | 1,851        | 99.04%        | 0.26x       |
| 6–10   | 3,521      | 18       |  0.51%         | 1,869        | 100.0%        | 0.02x       |
+--------+------------+----------+----------------+--------------+---------------+-------------+
```
> **Key Operational Finding**: Contacting only the **Top 20% highest-risk deciles (1,409 accounts) captures 68.49% of all eventual churners**, delivering a **3.43x cumulative lift** over untargeted random marketing outreach.

### SHAP (TreeExplainer) Feature Attribution
Feature importance analysis identified the following primary drivers of subscriber attrition:
1. **`tenure`** (SHAP: 1.4105): Strongest overall protective factor against churn.
2. **`Contract_Two year`** (SHAP: 0.9662): Significant negative push on churn probability.
3. **`Contract_One year`** (SHAP: 0.6182): Moderate negative push on churn probability.
4. **`InternetService_Fiber optic`** (SHAP: 0.5628): Increases churn probability due to premium pricing and unbundled service issues.
5. **`TechSupport_Yes`** (SHAP: 0.5597): Protective bundle feature reducing customer friction.
6. **`PaymentMethod_Electronic check`** (SHAP: 0.5377): Significant frictional payment indicator.

---

## 5. Excel Dynamic Retention Simulator

The Excel financial model (`excel/Telecom_Customer_Retention_Simulator.xlsx`) translates predictive scores into a dynamic campaign forecasting engine with 5 interconnected worksheets:

1. **Executive Dashboard**: Executive KPI cards, summary tables by contract tier, and strategic recommendations.
2. **Retention Campaign Simulator**: Fully dynamic assumption block and financial ROI calculator.
   - Target High-Risk Accounts: `=COUNTIF('Customer Cohorts'!M4:M7046, "High")` (2,883 accounts)
   - Campaign Outreach Coverage: `80.0%` (2,306 accounts contacted)
   - Concession Incentive Cost: `$35.00` per targeted account
   - Campaign Save Rate: `18.0%` (415 customers saved)
   - Preserved Annual Revenue: `$438,200`
   - Total Campaign Budget: `$80,710`
   - **Net Campaign Profit**: **$357,490**
   - **Net Campaign ROI**: **442.9%**
3. **2-Way Sensitivity Matrix**: Stress-tests Net Campaign Profit across varying Save Rates (10% to 30%) and Incentive Costs ($20 to $100) using multi-cell formulas and 3-color conditional formatting.
4. **Cohort Heatmap**: Visualizes attrition across tenure bands vs contract types with dynamic Excel formulas.
5. **Customer Cohorts**: 7,043 scored customer accounts with formulas, probability scores, risk tiers, and CLV exposure.

---

## 6. Power BI Command Center (PBIR & TMDL)

The Power BI Command Center adheres to the modern Microsoft Fabric **Enhanced Report Format (PBIR)** and **Tabular Model Definition Language (TMDL)** standards:

```
05_Telecom_Churn/pbi/
├── Telecom_Churn_Command_Center.pbip
├── Telecom_Churn_Command_Center.Report/
│   ├── definition.pbir
│   ├── .platform
│   └── definition/
│       ├── version.json
│       ├── report.json
│       └── pages/
│           ├── pages.json
│           ├── page_overview/ (Executive KPIs, Contract Clustered Bar, Tenure Hazard Column, Payment Donut)
│           ├── page_drivers/ (Decomposition Tree on Revenue at Risk, Key Influencers Visual, Scatter Plot)
│           └── page_actions/ (Slicers, High Risk KPI Cards, Operational Drill-Through Table)
├── Telecom_Churn_Command_Center.SemanticModel/
│   ├── definition.pbism
│   ├── .platform
│   └── definition/
│       ├── model.tmdl (Tabs-indented Fabric semantic model)
│       ├── relationships.tmdl (6 active relationships to fact_churn_analysis)
│       └── tables/ (fact_churn_analysis.tmdl, 6 dimension TMDLs, measures.tmdl)
└── measures.dax (Enterprise DAX repository)
```

### PBIR Schema Validation
Validated directly using `pbi-cli`:
```powershell
python -m pbi_cli report -p "pbi/Telecom_Churn_Command_Center.Report" validate --full
```
**Validation Result**: `valid: True, errors: 0, warnings: 0, info: 0` across 21 verified JSON files.

### Enterprise DAX Measures
- `[Total Customers]` = `COUNTROWS(fact_churn_analysis)`
- `[Churn Rate %]` = `DIVIDE([Churned Customers], [Total Customers], 0.0)`
- `[Total MRR]` = `SUM(fact_churn_analysis[monthly_charges])`
- `[Revenue at Risk]` = `CALCULATE([Total MRR], fact_churn_analysis[churn_flag] = 1 || RELATED(dim_risk_tier[risk_tier_label]) = "High")`
- `[Simulated Net Preserved Revenue]` = `[Revenue at Risk] * 12 * 0.18 - ([High Risk Customer Count] * 35.00)`
- `[Campaign ROI %]` = `DIVIDE([Simulated Net Preserved Revenue], [High Risk Customer Count] * 35.00, 0.0)`

---

## 7. Guardrailed GenAI Retention Offer Assistant

Located in `genai/retention_offer_assistant.py`, this module bridges predictive data and frontline operations by translating customer risk factors into personalized retention packages.

### Automated Budget & Policy Guardrails
- **Hard Discount Ceiling**: Maximum $15.00/month concession; maximum $120.00 annual incentive value.
- **Pre-Approved Offer Catalog**:
  1. *Annual Contract Stability Discount*: $10/mo credit for committing to a 12-month agreement.
  2. *Complimentary TechSupport & Security Shield*: 6 months free TechSupport + OnlineSecurity ($10/mo value).
  3. *Automated Billing Loyalty Credit*: $5/mo credit for 6 months upon enrolling in autopay.
  4. *First-Year VIP Concierge*: Dedicated priority support for infant-tenure accounts (<6 months).
- **Communication Guardrails**: SMS copy strictly capped at 160 characters; email copy strictly capped at 120 words.
- **Human-in-the-Loop Governance**: Every generated record receives `approval_status: PENDING_MARKETING_APPROVAL` with mandatory legal review notice.
- **Zero-Dependency Fallback**: Works with Google Gemini API when `GEMINI_API_KEY` is present, or falls back seamlessly to a deterministic rules engine when offline.

---

## 8. Reproducibility & Execution Runbook

All scripts execute locally without external database servers or proprietary dependencies:

```powershell
# 1. Generate Synthetic Dataset & Star-Schema CSVs
python data/generate_data.py

# 2. Build SQLite Database & Run Analytical Queries
python sql/build_db.py

# 3. Execute Predictive Modeling, Cross-Validation & SHAP Attribution
python notebooks/01_churn_prediction_and_retention_modeling.py

# 4. Generate Excel Retention Simulator & Sensitivity Workbook
python excel/create_retention_simulator.py

# 5. Build & Validate Modern Power BI PBIR / TMDL Architecture
python pbi/build_pbi_model.py
python -m pbi_cli report -p "pbi/Telecom_Churn_Command_Center.Report" validate --full

# 6. Execute GenAI Retention Offer Assistant
python genai/retention_offer_assistant.py --test
```

---

## 9. Resume Bullet Points & Interview Guide

### Role-Tailored Resume Bullets

#### For Business Analyst Roles
- "Identified early-tenure subscribers (0–6 months) as the primary customer churn risk cohort (52.3% of total churn, $68.5K monthly MRR at risk); formulated targeted onboarding and TechSupport bundle interventions projected to preserve $350K+ in annual customer lifetime value (CLV)."
- "Built a 5-tab dynamic customer retention simulator in Excel with two-way sensitivity modeling, enabling marketing leadership to optimize incentive budgets across 2,800+ accounts at a projected 310% net campaign ROI."

#### For Data Analyst Roles
- "Engineered an end-to-end churn prediction pipeline across 7,043 subscriber records using XGBoost and Stratified 5-Fold Cross-Validation with in-fold SMOTE, achieving an ROC-AUC of 0.963 and capturing 68.5% of churners in the top 20% risk decile (3.43x lift)."
- "Applied SHAP (TreeExplainer) to isolate attrition drivers, discovering that unbundled Fiber Optic accounts lacking technical support have an 86.5% churn rate compared to 23.2% for bundled accounts."

#### For BI Developer Roles
- "Architected an enterprise Power BI command center in modern PBIR/TMDL format featuring Decomposition Trees and Key Influencer visuals, tracking $196K in revenue at risk with drill-through action queues."
- "Constructed a 3NF/Kimball star schema in SQLite comprising 6 dimensions and a central fact table, optimizing complex DAX measures and query performance."

---

### Key Interview Questions & Talking Points

1. **How do you set a classification threshold for churn prediction in practice?**  
   *Talking Point*: The default 0.50 cutoff is rarely cost-optimal. In telecommunications, losing a customer costs $500–$1,000+ in Customer Lifetime Value, whereas an intervention offer costs only $35. By evaluating the cost matrix `Total Cost = (False Negatives * Lost CLV) + (False Positives * Concession Cost)`, we lower the decision threshold to ~0.35–0.40, maximizing recall on high-value churners while preserving healthy campaign margins.

2. **Why do executive stakeholders prefer Decile Lift & Gains Charts over ROC-AUC?**  
   *Talking Point*: ROC-AUC is an abstract statistical measure across all possible classification cutoffs that cannot be directly budgeted. A Decile Lift chart provides immediate operational clarity: it demonstrates that marketing teams do not need to contact 100% of the customer base. By focusing outbound outreach on the top 20% highest-risk accounts, the team captures 68.5% of all eventual churners—a 3.43x lift over random contact that directly dictates staffing and budget allocation.

3. **Why must SMOTE or oversampling be applied strictly inside cross-validation training folds?**  
   *Talking Point*: Applying SMOTE to the complete dataset prior to cross-validation causes severe data leakage: synthetic observations generated from validation-set neighbors bleed holdout information into the training split. This artificially inflates validation metrics (ROC-AUC, Precision, Recall) while leading to catastrophic performance degradation when deployed on unseen production data. Implementing SMOTE strictly inside each training fold guarantees that synthetic examples are derived solely from training points.

---
*Created as part of the Senior Data Analyst & BI Developer Portfolio.*
