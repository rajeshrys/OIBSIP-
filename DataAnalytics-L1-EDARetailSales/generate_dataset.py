import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Set random seed for reproducibility
np.random.seed(42)

# Catalog of products across categories
products_catalog = {
    'Electronics': [
        ('4K Ultra HD Smart TV', 650.0),
        ('Noise-Cancelling Headphones', 180.0),
        ('Wireless Bluetooth Earbuds', 75.0),
        ('Smart Fitness Watch', 120.0),
        ('Portable Bluetooth Speaker', 55.0)
    ],
    'Clothing': [
        ('Slim-Fit Denim Jeans', 48.0),
        ('Classic Cotton Crewneck T-Shirt', 22.0),
        ('Winter Hooded Parka', 135.0),
        ('Casual Breathable Sneakers', 70.0),
        ('Formal Oxford Shirt', 42.0)
    ],
    'Home & Kitchen': [
        ('Air Fryer Digital Oven', 110.0),
        ('Non-Stick Ceramic Cookware Set', 95.0),
        ('Espresso Coffee Machine', 160.0),
        ('Ergonomic Memory Foam Pillow', 35.0),
        ('Stainless Steel Water Bottle', 20.0)
    ],
    'Beauty & Personal Care': [
        ('Anti-Aging Retinol Night Serum', 45.0),
        ('Daily Hydrating Facial Cleanser', 18.0),
        ('Ionic Ceramic Hair Dryer', 58.0),
        ('Organic Botanical Shampoo', 24.0),
        ('Shea Butter Moisturizing Cream', 16.0)
    ],
    'Books & Stationery': [
        ('Executive Hardcover Notebook', 15.0),
        ('Fine Fountain Pen Set', 38.0),
        ('Data Science & ML Handbook', 48.0),
        ('Minimalist Wooden Desk Organizer', 28.0),
        ('Artisan Sketching Pencil Kit', 19.0)
    ]
}

n_records = 2500
start_date = datetime(2023, 1, 1)
end_date = datetime(2024, 12, 31)
date_range_days = (end_date - start_date).days

# Customers pool (600 unique customers for realistic repeat purchasing)
customer_ids = [f"CUST-{1000 + i}" for i in range(600)]
customer_age_map = {cid: int(np.clip(np.random.normal(38, 14), 18, 72)) for cid in customer_ids}
customer_gender_map = {
    cid: np.random.choice(['Female', 'Male', 'Other'], p=[0.51, 0.46, 0.03])
    for cid in customer_ids
}

records = []
categories = list(products_catalog.keys())
cat_weights = [0.28, 0.25, 0.22, 0.15, 0.10]
payment_methods = ['Credit Card', 'Debit Card', 'UPI / Digital Wallet', 'Cash']
pay_weights = [0.42, 0.24, 0.26, 0.08]

for i in range(1, n_records + 1):
    trans_id = f"TXN-{10000 + i}"
    
    # Weight date selection to show natural seasonal bumps (Q4 holiday surge, summer promotions)
    day_offset = np.random.randint(0, date_range_days + 1)
    trans_date = start_date + timedelta(days=day_offset)
    
    # Add slight probability increase for Nov & Dec (holiday season)
    if trans_date.month in [11, 12] and np.random.rand() < 0.25:
        # bias toward year end
        trans_date = trans_date.replace(month=np.random.choice([11, 12]))
    
    cid = np.random.choice(customer_ids)
    age = customer_age_map[cid]
    gender = customer_gender_map[cid]
    
    category = np.random.choice(categories, p=cat_weights)
    prod_options = products_catalog[category]
    prod_tuple = prod_options[np.random.choice(len(prod_options))]
    product_name, base_price = prod_tuple
    
    # Slight price variation (+/- 5%) to simulate dynamic retail pricing / discounts
    unit_price = round(base_price * np.random.uniform(0.95, 1.05), 2)
    
    # Quantity distribution (mostly 1-3, occasional bulk 4-6)
    quantity = int(np.random.choice([1, 2, 3, 4, 5], p=[0.55, 0.25, 0.12, 0.05, 0.03]))
    total_amount = round(quantity * unit_price, 2)
    
    # Discount rate (0%, 5%, 10%, 15%, 20%)
    discount_pct = np.random.choice([0.0, 0.05, 0.10, 0.15, 0.20], p=[0.35, 0.25, 0.20, 0.12, 0.08])
    discount_amount = round(total_amount * discount_pct, 2)
    net_amount = round(total_amount - discount_amount, 2)
    
    # Cost price estimation to compute profit and margin (typical retail COGS is 55-75% of base price)
    cogs_ratio = np.random.uniform(0.55, 0.70)
    cogs = round(unit_price * cogs_ratio * quantity, 2)
    profit = round(net_amount - cogs, 2)
    profit_margin = round((profit / net_amount) * 100, 2) if net_amount > 0 else 0.0
    
    payment = np.random.choice(payment_methods, p=pay_weights)
    
    # Customer age group
    if age < 25:
        age_group = "18-24 (Youth)"
    elif age < 36:
        age_group = "25-35 (Young Adults)"
    elif age < 51:
        age_group = "36-50 (Middle-Aged)"
    else:
        age_group = "51+ (Seniors)"
        
    records.append({
        'Transaction_ID': trans_id,
        'Date': trans_date.strftime('%Y-%m-%d'),
        'Customer_ID': cid,
        'Gender': gender,
        'Age': age,
        'Age_Group': age_group,
        'Product_Category': category,
        'Product_Name': product_name,
        'Quantity': quantity,
        'Price_Per_Unit': unit_price,
        'Total_Amount': total_amount,
        'Discount_Rate': discount_pct,
        'Discount_Amount': discount_amount,
        'Net_Amount': net_amount,
        'Cost_Of_Goods': cogs,
        'Profit': profit,
        'Profit_Margin_Pct': profit_margin,
        'Payment_Method': payment
    })

df = pd.DataFrame(records)
# Sort by date
df = df.sort_values('Date').reset_index(drop=True)
csv_path = 'd:/Rajesh/oasis_infobyte/DataAnalytics-L1-EDARetailSales/data/retail_sales_dataset.csv'
df.to_csv(csv_path, index=False)
print(f"Dataset generated successfully at {csv_path}")
print(f"Total Rows: {len(df)}, Total Columns: {len(df.columns)}")
print(df.head(3))
