import os
import sys
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

np.random.seed(42)

print("Generating deliberately messy enterprise loan applicant dataset for Data Cleaning Mastery...")

DATA_DIR = "DataAnalytics-L1-DataCleaning/data"
os.makedirs(DATA_DIR, exist_ok=True)

n_records = 3200

# Base clean values
applicant_ids = [f"APP-{10000 + i}" for i in range(n_records)]
start_date = datetime(2022, 1, 1)

genders = ['Male', 'Female', 'Other']
employment = ['Employed', 'Self-Employed', 'Unemployed', 'Retired']
marital = ['Married', 'Single', 'Divorced']
cities = ['New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix', 'Philadelphia', 'San Antonio', 'San Diego']

data = []

for i in range(n_records):
    app_id = applicant_ids[i]
    
    # 1. Date with random offsets
    rand_days = np.random.randint(0, 730)
    dt = start_date + timedelta(days=rand_days)
    
    # Inject format chaos in dates:
    date_style = np.random.choice(['iso', 'slash_dmy', 'slash_mdy', 'text', 'dotted', 'corrupted'], p=[0.40, 0.20, 0.15, 0.15, 0.08, 0.02])
    if date_style == 'iso':
        date_str = dt.strftime("%Y-%m-%d")
    elif date_style == 'slash_dmy':
        date_str = dt.strftime("%d/%m/%Y")
    elif date_style == 'slash_mdy':
        date_str = dt.strftime("%m/%d/%Y")
    elif date_style == 'text':
        date_str = dt.strftime("%B %d, %Y")
    elif date_style == 'dotted':
        date_str = dt.strftime("%Y.%m.%d")
    else:
        date_str = np.random.choice(["9999-99-99", "NULL", "Unknown", "2023-02-31"])
        
    # 2. Gender inconsistency
    base_gender = np.random.choice(genders, p=[0.52, 0.45, 0.03])
    if base_gender == 'Male':
        g_val = np.random.choice(['Male', 'male', 'M', 'm', 'MALE', '  Male  '], p=[0.5, 0.2, 0.15, 0.05, 0.05, 0.05])
    elif base_gender == 'Female':
        g_val = np.random.choice(['Female', 'female', 'F', 'f', 'FEMALE', '  Female  ', 'Femal'], p=[0.5, 0.2, 0.12, 0.05, 0.05, 0.05, 0.03])
    else:
        g_val = np.random.choice(['Other', 'other', 'OTH', 'non-binary'], p=[0.4, 0.3, 0.15, 0.15])
        
    if np.random.rand() < 0.06: # 6% missing gender
        g_val = np.nan
        
    # 3. Age with outliers and anomalies
    if np.random.rand() < 0.015:
        # Extreme / impossible age anomalies
        age_val = np.random.choice([-8, 142, 210, 0])
    elif np.random.rand() < 0.05:
        # Missing age
        age_val = np.nan
    else:
        age_val = int(np.clip(np.random.normal(39, 12), 19, 75))
        
    # 4. Income with currency formatting, strings, commas, whitespace, and negative values
    if np.random.rand() < 0.02:
        # Outlier billionaire or negative income
        income_val = np.random.choice(["-$15,000", "$99,999,999", "0", "$10,000,000.00"])
    elif np.random.rand() < 0.07:
        # Missing income
        income_val = np.nan
    else:
        raw_inc = round(float(np.random.exponential(45000) + 20000), 2)
        style = np.random.choice(['clean', 'dollar_comma', 'whitespace', 'string_plain'], p=[0.3, 0.4, 0.15, 0.15])
        if style == 'clean':
            income_val = str(raw_inc)
        elif style == 'dollar_comma':
            income_val = f"${raw_inc:,.2f}"
        elif style == 'whitespace':
            income_val = f"  ${raw_inc:,.0f}  "
        else:
            income_val = f"{int(raw_inc)}"
            
    # 5. Credit Score (300 to 850 range) with anomalies
    if np.random.rand() < 0.015:
        credit_val = np.random.choice([9999, 50, -100, 1500])
    elif np.random.rand() < 0.05:
        credit_val = np.nan
    else:
        credit_val = int(np.clip(np.random.normal(680, 75), 320, 850))
        
    # 6. Loan Amount with missing values and formatting
    if np.random.rand() < 0.06:
        loan_val = np.nan
    else:
        base_loan = round(float(np.random.gamma(5, 5000) + 5000), 2)
        if np.random.rand() < 0.35:
            loan_val = f"${base_loan:,.2f}"
        else:
            loan_val = str(base_loan)
            
    # 7. Employment Status inconsistencies
    base_emp = np.random.choice(employment, p=[0.60, 0.20, 0.12, 0.08])
    if base_emp == 'Employed':
        emp_val = np.random.choice(['Employed', 'employed', 'EMP', '  Employed  ', 'Full-Time'], p=[0.5, 0.2, 0.15, 0.1, 0.05])
    elif base_emp == 'Self-Employed':
        emp_val = np.random.choice(['Self-Employed', 'self-employed', 'Self Employed', 'Freelancer'], p=[0.5, 0.25, 0.15, 0.1])
    elif base_emp == 'Unemployed':
        emp_val = np.random.choice(['Unemployed', 'unemployed', 'UNEMP', 'None'], p=[0.5, 0.25, 0.15, 0.1])
    else:
        emp_val = np.random.choice(['Retired', 'retired', 'Ret.', 'Pensioner'], p=[0.5, 0.25, 0.15, 0.1])
        
    if np.random.rand() < 0.04:
        emp_val = np.nan
        
    # 8. Marital Status
    base_mar = np.random.choice(marital, p=[0.55, 0.35, 0.10])
    if base_mar == 'Married':
        mar_val = np.random.choice(['Married', 'married', 'M', 'MARRIED'], p=[0.6, 0.2, 0.1, 0.1])
    elif base_mar == 'Single':
        mar_val = np.random.choice(['Single', 'single', 'S', 'SINGLE'], p=[0.6, 0.2, 0.1, 0.1])
    else:
        mar_val = np.random.choice(['Divorced', 'divorced', 'D', 'DIVORCED'], p=[0.6, 0.2, 0.1, 0.1])
    if np.random.rand() < 0.03:
        mar_val = np.nan
        
    # 9. City with casing and trailing spaces
    city_choice = np.random.choice(cities)
    if np.random.rand() < 0.30:
        city_val = np.random.choice([city_choice.lower(), city_choice.upper(), f"  {city_choice}  "])
    else:
        city_val = city_choice
        
    # 10. Loan Approval target
    appr_choice = np.random.choice(['Y', 'N'], p=[0.68, 0.32])
    target_val = np.random.choice([appr_choice, appr_choice.lower(), "Yes" if appr_choice == 'Y' else "No", "1" if appr_choice == 'Y' else "0"])
    
    # 11. Dirty IDs (some whitespace, a few completely null or corrupted)
    if np.random.rand() < 0.01:
        app_id = np.nan
    elif np.random.rand() < 0.05:
        app_id = f"  {app_id}  "
        
    data.append({
        'Applicant_ID': app_id,
        'Application_Date': date_str,
        'Gender': g_val,
        'Age': age_val,
        'Annual_Income': income_val,
        'Credit_Score': credit_val,
        'Loan_Amount': loan_val,
        'Employment_Status': emp_val,
        'Marital_Status': mar_val,
        'City': city_val,
        'Loan_Approved': target_val
    })

df = pd.DataFrame(data)

# Inject Duplicate Rows:
# 1. Exact duplicates (clone 85 rows completely)
dup_indices = np.random.choice(df.index, size=85, replace=False)
duplicates_exact = df.loc[dup_indices].copy()

# 2. Key duplicates with slight variation (clone 35 rows with matching Applicant_ID)
key_dup_indices = np.random.choice(df.index, size=35, replace=False)
duplicates_key = df.loc[key_dup_indices].copy()
duplicates_key['Loan_Amount'] = "$12,345.00"

df = pd.concat([df, duplicates_exact, duplicates_key], ignore_index=True)

# Shuffle dataset
df = df.sample(frac=1.0, random_state=42).reset_index(drop=True)

output_path = os.path.join(DATA_DIR, "raw_messy_dataset.csv")
df.to_csv(output_path, index=False)
print(f"Deliberately messy dataset generated: {len(df):,} rows.")
print(f"Saved to: {output_path}")
