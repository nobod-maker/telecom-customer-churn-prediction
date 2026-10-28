"""
05_Telecom_Churn: High-Fidelity Synthetic Data Generator & Star-Schema Pipeline
Author: worker_m5_telco
Replicates the IBM Telco Customer Churn dataset (7,043 rows, 21 columns)
with realistic survival hazard curves, contract churn rates, service bundle odds ratios,
and enterprise Kimball star-schema dimension and fact tables.
"""

import os
import random
import numpy as np
import pandas as pd

def generate_telco_churn_data(seed: int = 42, n_rows: int = 7043) -> pd.DataFrame:
    np.random.seed(seed)
    random.seed(seed)
    
    # 1. Generate unique customer IDs (Format: ####-XXXXX)
    used_ids = set()
    customer_ids = []
    chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    while len(customer_ids) < n_rows:
        num_part = f"{np.random.randint(1000, 10000)}"
        char_part = "".join(random.choices(chars, k=5))
        cid = f"{num_part}-{char_part}"
        if cid not in used_ids:
            used_ids.add(cid)
            customer_ids.append(cid)
            
    # 2. Demographics
    gender = np.random.choice(['Female', 'Male'], size=n_rows, p=[0.495, 0.505])
    senior_citizen = np.random.choice([0, 1], size=n_rows, p=[0.838, 0.162])
    partner = np.random.choice(['Yes', 'No'], size=n_rows, p=[0.483, 0.517])
    # Dependents are more likely if partner is Yes
    dependents = []
    for p in partner:
        if p == 'Yes':
            dependents.append(np.random.choice(['Yes', 'No'], p=[0.51, 0.49]))
        else:
            dependents.append(np.random.choice(['Yes', 'No'], p=[0.11, 0.89]))
    dependents = np.array(dependents)
    
    # 3. Contract Types (~55% Month-to-month, ~21% One year, ~24% Two year)
    contracts = np.random.choice(
        ['Month-to-month', 'One year', 'Two year'], 
        size=n_rows, 
        p=[0.550, 0.209, 0.241]
    )
    
    # 4. Tenure distribution tailored by contract type
    # Exactly 11 customers with tenure = 0 (matching IBM dataset)
    tenure = np.zeros(n_rows, dtype=int)
    zero_indices = np.random.choice(n_rows, size=11, replace=False)
    
    for i in range(n_rows):
        if i in zero_indices:
            tenure[i] = 0
            continue
        c = contracts[i]
        if c == 'Month-to-month':
            # Skewed towards low tenure (0-20 months)
            t = int(np.random.exponential(scale=12) + 1)
            tenure[i] = min(72, max(1, t))
        elif c == 'One year':
            # Centered around 12-36 months
            t = int(np.random.normal(loc=34, scale=14))
            tenure[i] = min(72, max(1, t))
        else: # Two year
            # High tenure (36-72 months)
            t = int(np.random.beta(a=3, b=1.5) * 71 + 1)
            tenure[i] = min(72, max(1, t))

    # 5. Phone Service & Multiple Lines
    phone_service = np.random.choice(['Yes', 'No'], size=n_rows, p=[0.903, 0.097])
    multiple_lines = []
    for ps in phone_service:
        if ps == 'No':
            multiple_lines.append('No phone service')
        else:
            multiple_lines.append(np.random.choice(['Yes', 'No'], p=[0.467, 0.533]))
    multiple_lines = np.array(multiple_lines)
    
    # 6. Internet Service (~44% Fiber optic, ~34% DSL, ~22% No)
    internet_service = np.random.choice(
        ['Fiber optic', 'DSL', 'No'], 
        size=n_rows, 
        p=[0.440, 0.344, 0.216]
    )
    
    # 7. Add-on Services (OnlineSecurity, OnlineBackup, DeviceProtection, TechSupport, StreamingTV, StreamingMovies)
    def assign_addons(internet_arr):
        addons = {
            'OnlineSecurity': [],
            'OnlineBackup': [],
            'DeviceProtection': [],
            'TechSupport': [],
            'StreamingTV': [],
            'StreamingMovies': []
        }
        for net in internet_arr:
            if net == 'No':
                for k in addons:
                    addons[k].append('No internet service')
            else:
                # Fiber optic customers have lower tech support / security attach rates
                prob_sec = 0.28 if net == 'Fiber optic' else 0.42
                prob_sup = 0.27 if net == 'Fiber optic' else 0.41
                prob_bak = 0.45 if net == 'Fiber optic' else 0.38
                prob_dev = 0.46 if net == 'Fiber optic' else 0.37
                prob_tv  = 0.54 if net == 'Fiber optic' else 0.34
                prob_mov = 0.54 if net == 'Fiber optic' else 0.34
                
                addons['OnlineSecurity'].append('Yes' if np.random.rand() < prob_sec else 'No')
                addons['TechSupport'].append('Yes' if np.random.rand() < prob_sup else 'No')
                addons['OnlineBackup'].append('Yes' if np.random.rand() < prob_bak else 'No')
                addons['DeviceProtection'].append('Yes' if np.random.rand() < prob_dev else 'No')
                addons['StreamingTV'].append('Yes' if np.random.rand() < prob_tv else 'No')
                addons['StreamingMovies'].append('Yes' if np.random.rand() < prob_mov else 'No')
        return {k: np.array(v) for k, v in addons.items()}
        
    addon_dict = assign_addons(internet_service)
    
    # 8. Billing & Payment Methods
    paperless_billing = np.random.choice(['Yes', 'No'], size=n_rows, p=[0.592, 0.408])
    payment_methods = np.random.choice(
        [
            'Electronic check', 
            'Mailed check', 
            'Bank transfer (automatic)', 
            'Credit card (automatic)'
        ],
        size=n_rows,
        p=[0.336, 0.229, 0.219, 0.216]
    )
    
    # 9. Monthly Charges calculation based on portfolio bundle
    monthly_charges = np.zeros(n_rows, dtype=float)
    for i in range(n_rows):
        base = 0.0
        if phone_service[i] == 'Yes':
            base += 20.0
            if multiple_lines[i] == 'Yes':
                base += 5.0
        net = internet_service[i]
        if net == 'DSL':
            base += 25.0
        elif net == 'Fiber optic':
            base += 50.0
        
        # Add-on fees ~$5 each
        for k in ['OnlineSecurity', 'OnlineBackup', 'DeviceProtection', 'TechSupport', 'StreamingTV', 'StreamingMovies']:
            if addon_dict[k][i] == 'Yes':
                base += 5.0
                
        # Small noise (-$2 to +$3)
        base += np.random.uniform(-1.5, 2.5)
        monthly_charges[i] = round(max(18.25, min(118.75, base)), 2)
        
    # 10. Total Charges: MonthlyCharges * tenure + slight historical rate drift
    total_charges_raw = []
    for i in range(n_rows):
        t = tenure[i]
        if t == 0:
            total_charges_raw.append(" ")  # Exactly 11 whitespace strings
        else:
            # historical charges slight discount in earlier months
            drift = np.random.uniform(0.96, 1.02)
            tot = round(monthly_charges[i] * t * drift, 2)
            total_charges_raw.append(str(tot))
            
    # 11. Churn Simulation with Rigorous Odds Ratios
    # Ground truth logistic probability model calibrated to target ~26.54% overall churn
    log_odds = np.zeros(n_rows, dtype=float)
    log_odds += -1.75  # Base intercept
    
    for i in range(n_rows):
        # Contract impact (Primary driver: Month-to-month 42.7% vs Two-year 2.8%)
        if contracts[i] == 'Month-to-month':
            log_odds[i] += 2.15
        elif contracts[i] == 'One year':
            log_odds[i] += -0.40
        else: # Two year
            log_odds[i] += -2.35
            
        # Tenure hazard impact
        t = tenure[i]
        if t == 0:
            log_odds[i] = -99.0 # Zero tenure customers did not churn
        else:
            log_odds[i] -= 0.045 * t  # Continuous tenure protection
            if t <= 6:
                log_odds[i] += 1.45   # Infant mortality surge
            elif t <= 12:
                log_odds[i] += 0.60
                
        # Internet Service impact (Fiber optic 41.9% vs DSL 19% vs None 7.4%)
        if internet_service[i] == 'Fiber optic':
            log_odds[i] += 1.15
        elif internet_service[i] == 'No':
            log_odds[i] -= 0.90
            
        # Value-Added Service Bundles (TechSupport & OnlineSecurity ~2.4x - 2.8x odds ratio)
        if internet_service[i] != 'No':
            if addon_dict['TechSupport'][i] == 'No':
                log_odds[i] += 0.85
            else:
                log_odds[i] -= 0.65
                
            if addon_dict['OnlineSecurity'][i] == 'No':
                log_odds[i] += 0.70
            else:
                log_odds[i] -= 0.55
                
        # Payment Method impact (Electronic check friction 45.3% vs Automated 15-16%)
        if payment_methods[i] == 'Electronic check':
            log_odds[i] += 0.85
        elif 'automatic' in payment_methods[i]:
            log_odds[i] -= 0.50
            
        # Senior Citizen & Paperless Billing
        if senior_citizen[i] == 1:
            log_odds[i] += 0.30
        if paperless_billing[i] == 'Yes':
            log_odds[i] += 0.35
            
        # Monthly charges price elasticity
        if monthly_charges[i] > 75:
            log_odds[i] += 0.40

    # Latent response model with logistic disturbance
    noise = np.random.logistic(loc=0.0, scale=0.65, size=n_rows)
    latent_score = log_odds + noise
    latent_score[zero_indices] = -999.0
    
    # Calibrate binary Churn label to hit exactly 1,869 churners (~26.54%)
    target_churn_count = 1869
    threshold = np.percentile(latent_score, 100 * (1 - target_churn_count / n_rows))
    is_churn = (latent_score >= threshold)
    churn_labels = np.where(is_churn, 'Yes', 'No')
    
    # Calculate calibrated probabilities
    probs = 1.0 / (1.0 + np.exp(-log_odds))
    probs[zero_indices] = 0.0

    df = pd.DataFrame({
        'customerID': customer_ids,
        'gender': gender,
        'SeniorCitizen': senior_citizen,
        'Partner': partner,
        'Dependents': dependents,
        'tenure': tenure,
        'PhoneService': phone_service,
        'MultipleLines': multiple_lines,
        'InternetService': internet_service,
        'OnlineSecurity': addon_dict['OnlineSecurity'],
        'OnlineBackup': addon_dict['OnlineBackup'],
        'DeviceProtection': addon_dict['DeviceProtection'],
        'TechSupport': addon_dict['TechSupport'],
        'StreamingTV': addon_dict['StreamingTV'],
        'StreamingMovies': addon_dict['StreamingMovies'],
        'Contract': contracts,
        'PaperlessBilling': paperless_billing,
        'PaymentMethod': payment_methods,
        'MonthlyCharges': monthly_charges,
        'TotalCharges': total_charges_raw,
        'Churn': churn_labels
    })
    
    return df, probs


def build_star_schema_tables(df: pd.DataFrame, probs: np.ndarray, output_dir: str):
    """
    Constructs Kimball dimensional tables and fact table from generated telco data.
    """
    clean_dir = os.path.join(output_dir, 'clean')
    os.makedirs(clean_dir, exist_ok=True)
    
    # 1. Clean TotalCharges (handling 11 blank records)
    total_charges_clean = []
    for val in df['TotalCharges']:
        s = str(val).strip()
        if s == '':
            total_charges_clean.append(0.0)
        else:
            total_charges_clean.append(float(s))
    total_charges_clean = np.array(total_charges_clean)
    
    # 2. Dim Customer
    dim_customer = pd.DataFrame({
        'customer_key': np.arange(1, len(df) + 1),
        'customer_id': df['customerID'],
        'gender': df['gender'],
        'senior_citizen_flag': df['SeniorCitizen'],
        'senior_citizen_label': df['SeniorCitizen'].map({0: 'No', 1: 'Yes'}),
        'partner_flag': df['Partner'].map({'No': 0, 'Yes': 1}),
        'partner_label': df['Partner'],
        'dependents_flag': df['Dependents'].map({'No': 0, 'Yes': 1}),
        'dependents_label': df['Dependents'],
        'family_structure': [
            'Family with Dependents' if d == 'Yes' else ('Partner Only' if p == 'Yes' else 'Single Independent')
            for p, d in zip(df['Partner'], df['Dependents'])
        ]
    })
    dim_customer.to_csv(os.path.join(clean_dir, 'dim_customer.csv'), index=False)
    
    # 3. Dim Contract (Unique combinations)
    contract_combos = df[['Contract', 'PaperlessBilling']].drop_duplicates().reset_index(drop=True)
    contract_combos['contract_key'] = np.arange(1, len(contract_combos) + 1)
    contract_combos['term_months'] = contract_combos['Contract'].map({
        'Month-to-month': 1,
        'One year': 12,
        'Two year': 24
    })
    contract_combos['paperless_billing_flag'] = contract_combos['PaperlessBilling'].map({'No': 0, 'Yes': 1})
    contract_combos['paperless_billing_label'] = contract_combos['PaperlessBilling']
    contract_combos = contract_combos.rename(columns={'Contract': 'contract_type', 'PaperlessBilling': 'paperless_billing_str'})
    dim_contract = contract_combos[['contract_key', 'contract_type', 'term_months', 'paperless_billing_flag', 'paperless_billing_label']]
    dim_contract.to_csv(os.path.join(clean_dir, 'dim_contract.csv'), index=False)
    
    # Contract lookup map
    contract_map = {}
    for _, row in contract_combos.iterrows():
        contract_map[(row['contract_type'], row['paperless_billing_str'])] = row['contract_key']
        
    # 4. Dim Service Profile (Unique combinations)
    service_cols = [
        'PhoneService', 'MultipleLines', 'InternetService', 
        'OnlineSecurity', 'OnlineBackup', 'DeviceProtection', 
        'TechSupport', 'StreamingTV', 'StreamingMovies'
    ]
    service_combos = df[service_cols].drop_duplicates().reset_index(drop=True)
    service_combos['service_key'] = np.arange(1, len(service_combos) + 1)
    service_combos['has_tech_support_flag'] = (service_combos['TechSupport'] == 'Yes').astype(int)
    service_combos['has_online_security_flag'] = (service_combos['OnlineSecurity'] == 'Yes').astype(int)
    service_combos['has_support_bundle_flag'] = ((service_combos['TechSupport'] == 'Yes') & (service_combos['OnlineSecurity'] == 'Yes')).astype(int)
    
    def count_services(row):
        cnt = 0
        if row['PhoneService'] == 'Yes': cnt += 1
        if row['MultipleLines'] == 'Yes': cnt += 1
        if row['InternetService'] != 'No': cnt += 1
        for col in ['OnlineSecurity', 'OnlineBackup', 'DeviceProtection', 'TechSupport', 'StreamingTV', 'StreamingMovies']:
            if row[col] == 'Yes': cnt += 1
        return cnt
        
    service_combos['total_service_count'] = service_combos.apply(count_services, axis=1)
    service_combos = service_combos.rename(columns={
        'PhoneService': 'phone_service',
        'MultipleLines': 'multiple_lines',
        'InternetService': 'internet_service',
        'OnlineSecurity': 'online_security',
        'OnlineBackup': 'online_backup',
        'DeviceProtection': 'device_protection',
        'TechSupport': 'tech_support',
        'StreamingTV': 'streaming_tv',
        'StreamingMovies': 'streaming_movies'
    })
    dim_service_profile = service_combos[[
        'service_key', 'phone_service', 'multiple_lines', 'internet_service',
        'online_security', 'online_backup', 'device_protection', 'tech_support',
        'streaming_tv', 'streaming_movies', 'has_tech_support_flag',
        'has_online_security_flag', 'has_support_bundle_flag', 'total_service_count'
    ]]
    dim_service_profile.to_csv(os.path.join(clean_dir, 'dim_service_profile.csv'), index=False)
    
    # Service lookup map
    service_map = {}
    for _, row in service_combos.iterrows():
        key = tuple(row[col] for col in [
            'phone_service', 'multiple_lines', 'internet_service',
            'online_security', 'online_backup', 'device_protection',
            'tech_support', 'streaming_tv', 'streaming_movies'
        ])
        service_map[key] = row['service_key']
        
    # 5. Dim Payment Profile
    payment_combos = df[['PaymentMethod']].drop_duplicates().reset_index(drop=True)
    payment_combos['payment_key'] = np.arange(1, len(payment_combos) + 1)
    payment_combos['is_automatic_flag'] = payment_combos['PaymentMethod'].str.contains('automatic').astype(int)
    payment_combos['payment_category'] = payment_combos['PaymentMethod'].apply(
        lambda x: 'Automated Bank/Card' if 'automatic' in x else ('Electronic Direct' if 'Electronic' in x else 'Physical Check')
    )
    payment_combos = payment_combos.rename(columns={'PaymentMethod': 'payment_method'})
    dim_payment_profile = payment_combos[['payment_key', 'payment_method', 'is_automatic_flag', 'payment_category']]
    dim_payment_profile.to_csv(os.path.join(clean_dir, 'dim_payment_profile.csv'), index=False)
    
    payment_map = dict(zip(payment_combos['payment_method'], payment_combos['payment_key']))
    
    # 6. Dim Tenure Band
    dim_tenure_band = pd.DataFrame([
        {'tenure_band_key': 1, 'tenure_band_label': '0-6 Months', 'min_months': 0, 'max_months': 6, 'lifecycle_stage': 'Infant Mortality / Onboarding'},
        {'tenure_band_key': 2, 'tenure_band_label': '7-12 Months', 'min_months': 7, 'max_months': 12, 'lifecycle_stage': 'Early Adoption'},
        {'tenure_band_key': 3, 'tenure_band_label': '13-24 Months', 'min_months': 13, 'max_months': 24, 'lifecycle_stage': 'Contract Renewal Window'},
        {'tenure_band_key': 4, 'tenure_band_label': '25-48 Months', 'min_months': 25, 'max_months': 48, 'lifecycle_stage': 'Established Mid-Tenure'},
        {'tenure_band_key': 5, 'tenure_band_label': '49-72 Months', 'min_months': 49, 'max_months': 72, 'lifecycle_stage': 'Mature Loyalist'}
    ])
    dim_tenure_band.to_csv(os.path.join(clean_dir, 'dim_tenure_band.csv'), index=False)
    
    def get_tenure_band_key(m):
        if m <= 6: return 1
        elif m <= 12: return 2
        elif m <= 24: return 3
        elif m <= 48: return 4
        else: return 5
        
    # 7. Dim Risk Tier
    dim_risk_tier = pd.DataFrame([
        {'risk_tier_key': 1, 'risk_tier_label': 'Low', 'min_probability': 0.00, 'max_probability': 0.35, 'recommended_retention_action': 'Loyalty Appreciation & Digital Self-Service'},
        {'risk_tier_key': 2, 'risk_tier_label': 'Medium', 'min_probability': 0.35, 'max_probability': 0.65, 'recommended_retention_action': 'Feature Adoption & Proactive Check-in'},
        {'risk_tier_key': 3, 'risk_tier_label': 'High', 'min_probability': 0.65, 'max_probability': 1.00, 'recommended_retention_action': 'Immediate Capped Retention Offer & Contract Migration'}
    ])
    dim_risk_tier.to_csv(os.path.join(clean_dir, 'dim_risk_tier.csv'), index=False)
    
    def get_risk_tier_key(p):
        if p >= 0.65: return 3
        elif p >= 0.35: return 2
        else: return 1

    # 8. Primary Driver Assignment for explainability
    drivers = []
    for i in range(len(df)):
        c = df['Contract'].iloc[i]
        net = df['InternetService'].iloc[i]
        sup = df['TechSupport'].iloc[i]
        pm = df['PaymentMethod'].iloc[i]
        t = df['tenure'].iloc[i]
        
        reasons = []
        if c == 'Month-to-month':
            reasons.append('Month-to-month agreement')
        if t <= 6:
            reasons.append('Infant tenure (<6m)')
        if net == 'Fiber optic' and sup == 'No':
            reasons.append('Fiber optic without Tech Support')
        elif net == 'Fiber optic':
            reasons.append('High-cost Fiber Optic tier')
        if pm == 'Electronic check':
            reasons.append('Electronic check friction')
        if not reasons:
            reasons.append('Standard lifecycle baseline')
        drivers.append(" & ".join(reasons[:2]))
        
    # 9. Expected Lifetime & CLV Estimate
    # Month-to-month: 14m, One-year: 36m, Two-year: 60m
    expected_life = df['Contract'].map({
        'Month-to-month': 14.0,
        'One year': 36.0,
        'Two year': 60.0
    })
    clv_estimates = np.round(df['MonthlyCharges'].values * expected_life.values, 2)
    revenue_at_risk = np.where(
        (df['Churn'] == 'Yes') | (probs >= 0.65),
        df['MonthlyCharges'].values,
        0.0
    )
    
    # 10. Fact Churn Analysis
    fact_churn_analysis = pd.DataFrame({
        'fact_id': np.arange(1, len(df) + 1),
        'customer_key': dim_customer['customer_key'],
        'contract_key': [contract_map[(c, p)] for c, p in zip(df['Contract'], df['PaperlessBilling'])],
        'service_key': [
            service_map[tuple(df[col].iloc[i] for col in [
                'PhoneService', 'MultipleLines', 'InternetService',
                'OnlineSecurity', 'OnlineBackup', 'DeviceProtection',
                'TechSupport', 'StreamingTV', 'StreamingMovies'
            ])]
            for i in range(len(df))
        ],
        'payment_key': [payment_map[p] for p in df['PaymentMethod']],
        'tenure_band_key': [get_tenure_band_key(t) for t in df['tenure']],
        'risk_tier_key': [get_risk_tier_key(p) for p in probs],
        'tenure_months': df['tenure'],
        'monthly_charges': df['MonthlyCharges'],
        'total_charges': total_charges_clean,
        'churn_flag': (df['Churn'] == 'Yes').astype(int),
        'churn_label': df['Churn'],
        'predicted_churn_prob': np.round(probs, 4),
        'clv_estimate': clv_estimates,
        'revenue_at_risk': np.round(revenue_at_risk, 2),
        'top_churn_driver': drivers
    })
    fact_churn_analysis.to_csv(os.path.join(clean_dir, 'fact_churn_analysis.csv'), index=False)
    
    # Scored customers dataset for Excel and ML reporting
    scored_customers = pd.DataFrame({
        'customer_id': df['customerID'],
        'gender': df['gender'],
        'senior_citizen': df['SeniorCitizen'],
        'tenure_months': df['tenure'],
        'contract_type': df['Contract'],
        'internet_service': df['InternetService'],
        'tech_support': df['TechSupport'],
        'payment_method': df['PaymentMethod'],
        'monthly_charges': df['MonthlyCharges'],
        'total_charges': total_charges_clean,
        'churn_actual': (df['Churn'] == 'Yes').astype(int),
        'churn_probability': np.round(probs, 4),
        'risk_tier': fact_churn_analysis['risk_tier_key'].map({1: 'Low', 2: 'Medium', 3: 'High'}),
        'top_churn_driver': drivers,
        'clv_estimate': clv_estimates,
        'revenue_at_risk': np.round(revenue_at_risk, 2)
    })
    scored_customers.to_csv(os.path.join(clean_dir, 'telco_scored_customers.csv'), index=False)


def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(base_dir, 'data')
    raw_dir = os.path.join(data_dir, 'raw')
    os.makedirs(raw_dir, exist_ok=True)
    
    print("[1/3] Generating synthetic IBM Telco Churn dataset (7,043 rows, 21 columns)...")
    df, probs = generate_telco_churn_data(seed=42, n_rows=7043)
    
    raw_csv_path = os.path.join(raw_dir, 'telco_customer_churn.csv')
    df.to_csv(raw_csv_path, index=False)
    # Also save as sample_data.csv in data/
    df.to_csv(os.path.join(data_dir, 'sample_data.csv'), index=False)
    
    churn_count = (df['Churn'] == 'Yes').sum()
    churn_rate = churn_count / len(df) * 100
    blank_charges = (df['TotalCharges'].str.strip() == '').sum()
    
    print(f"      Rows generated: {len(df):,}")
    print(f"      Total Churners: {churn_count:,} ({churn_rate:.2f}%)")
    print(f"      Retained: {len(df) - churn_count:,} ({100 - churn_rate:.2f}%)")
    print(f"      Blank TotalCharges records (tenure=0): {blank_charges}")
    print(f"      Saved raw CSV: {raw_csv_path}")
    
    print("[2/3] Constructing Kimball star-schema dimensional tables & facts...")
    build_star_schema_tables(df, probs, data_dir)
    print("      Saved: dim_customer, dim_contract, dim_service_profile, dim_payment_profile, dim_tenure_band, dim_risk_tier, fact_churn_analysis, telco_scored_customers")
    
    print("[3/3] Data generation successfully complete!")

if __name__ == '__main__':
    main()
