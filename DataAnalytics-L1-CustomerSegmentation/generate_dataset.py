import pandas as pd
import numpy as np
from datetime import datetime, timedelta

import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# Set random seed for exact reproducibility
np.random.seed(42)

print("Generating synthetic e-commerce transactional dataset for Customer Segmentation...")

products = [
    ("22423", "REGENCY CAKESTAND 3 TIER", 12.75, "Home & Kitchen"),
    ("85123A", "WHITE HANGING HEART T-LIGHT HOLDER", 2.95, "Home Decor"),
    ("47566", "PARTY BUNTING", 4.95, "Party Supplies"),
    ("84879", "ASSORTED COLOUR BIRD ORNAMENT", 1.69, "Home Decor"),
    ("22720", "SET OF 3 CAKE TINS PANTRY DESIGN", 4.95, "Home & Kitchen"),
    ("22197", "POPCORN HOLDER", 0.85, "Dining"),
    ("21212", "PACK OF 72 RETROSPOT CAKE CASES", 0.55, "Dining"),
    ("20725", "LUNCH BAG RED RETROSPOT", 1.65, "Bags & Storage"),
    ("23203", "JUMBO BAG DOILEY PATTERNS", 2.08, "Bags & Storage"),
    ("22383", "LUNCH BAG SUKI DESIGN", 1.65, "Bags & Storage"),
    ("85099B", "JUMBO BAG RED RETROSPOT", 2.08, "Bags & Storage"),
    ("22457", "NATURAL SLATE HEART CHALKBOARD", 2.95, "Home Decor"),
    ("22666", "RECIPE BOX PANTRY DESIGN", 7.95, "Home & Kitchen"),
    ("22960", "JAM MAKING SET WITH JARS", 4.25, "Kitchen Essentials"),
    ("21733", "RED HANGING HEART T-LIGHT HOLDER", 2.95, "Home Decor"),
    ("22086", "PAPER CHAIN KIT 50'S CHRISTMAS", 2.95, "Seasonal"),
    ("22699", "ROSES REGENCY TEACUP AND SAUCER", 8.50, "Dining"),
    ("22910", "PAPER CHAIN KIT VINTAGE CHRISTMAS", 2.95, "Seasonal"),
    ("23209", "LUNCH BAG VINTAGE DOILY", 1.65, "Bags & Storage"),
    ("22722", "SET OF 6 SPICE TINS PANTRY DESIGN", 3.95, "Home & Kitchen"),
    ("POST", "POSTAGE", 18.00, "Shipping Services"),
    ("22386", "JUMBO BAG PINK POLKADOT", 2.08, "Bags & Storage"),
    ("22469", "HEART OF WICKER SMALL", 1.65, "Home Decor"),
    ("22470", "HEART OF WICKER LARGE", 3.95, "Home Decor"),
    ("21931", "JUMBO STORAGE BAG SUKI", 2.08, "Bags & Storage")
]

countries = [
    ("United Kingdom", 0.78),
    ("Germany", 0.08),
    ("France", 0.06),
    ("Spain", 0.03),
    ("Australia", 0.02),
    ("United States", 0.02),
    ("Netherlands", 0.01)
]
country_names, country_probs = zip(*countries)

# 850 unique customer IDs
n_customers = 850
customer_ids = [12000 + i for i in range(n_customers)]

# Define archetypes to generate distinct, realistic purchasing behaviors
# 1. VIP / Champions: High frequency (8-25 orders), very recent, high basket volume
# 2. Loyal Shoppers: Moderate frequency (4-10 orders), relatively recent, steady basket
# 3. At-Risk / Lapsed: Moderate-to-high past frequency (3-12 orders), high recency (>180 days ago)
# 4. One-Time / Occasional: Low frequency (1-2 orders), varied recency, small basket
customer_archetypes = {}
for cid in customer_ids:
    arch = np.random.choice(["Champion", "Loyal", "AtRisk", "Occasional"], p=[0.15, 0.35, 0.20, 0.30])
    country = np.random.choice(country_names, p=country_probs)
    customer_archetypes[cid] = (arch, country)

reference_date = datetime(2024, 12, 31)
start_period = datetime(2023, 1, 1)
total_days = (reference_date - start_period).days

transactions = []
invoice_counter = 536000

for cid, (arch, country) in customer_archetypes.items():
    if arch == "Champion":
        n_invoices = np.random.randint(8, 22)
        # Orders occur frequently up until near reference_date
        invoice_days = np.random.choice(range(total_days - 60, total_days), size=min(n_invoices, 55), replace=False)
        items_per_invoice_range = (4, 10)
        qty_range = (5, 30)
    elif arch == "Loyal":
        n_invoices = np.random.randint(4, 9)
        # Orders occur across the last 150 days
        invoice_days = np.random.choice(range(total_days - 180, total_days), size=min(n_invoices, 80), replace=False)
        items_per_invoice_range = (2, 6)
        qty_range = (2, 16)
    elif arch == "AtRisk":
        n_invoices = np.random.randint(3, 8)
        # Orders occurred long ago (more than 180 to 500 days ago)
        invoice_days = np.random.choice(range(30, total_days - 160), size=min(n_invoices, 100), replace=False)
        items_per_invoice_range = (2, 5)
        qty_range = (3, 15)
    else: # Occasional
        n_invoices = np.random.randint(1, 3)
        invoice_days = np.random.choice(range(0, total_days), size=n_invoices, replace=False)
        items_per_invoice_range = (1, 3)
        qty_range = (1, 8)

    for day_offset in sorted(invoice_days):
        invoice_counter += 1
        inv_no = str(invoice_counter)
        inv_date = start_period + timedelta(days=int(day_offset), hours=np.random.randint(8, 19), minutes=np.random.randint(0, 59))
        
        n_items = np.random.randint(items_per_invoice_range[0], items_per_invoice_range[1] + 1)
        selected_prods = np.random.choice(len(products), size=min(n_items, len(products)), replace=False)
        
        for p_idx in selected_prods:
            stock_code, desc, base_price, category = products[p_idx]
            qty = int(np.random.randint(qty_range[0], qty_range[1] + 1))
            # Minor random variation in unit price
            unit_price = round(base_price * np.random.uniform(0.95, 1.05), 2)
            
            transactions.append({
                "InvoiceNo": inv_no,
                "StockCode": stock_code,
                "Description": desc,
                "Quantity": qty,
                "InvoiceDate": inv_date.strftime("%Y-%m-%d %H:%M:%S"),
                "UnitPrice": unit_price,
                "CustomerID": float(cid),
                "Country": country
            })
            
        # Add realistic cancellation behavior (~2% probability for non-occasional customers)
        if arch in ["Champion", "Loyal", "AtRisk"] and np.random.rand() < 0.03:
            canc_p_idx = np.random.choice(selected_prods)
            stock_code, desc, base_price, _ = products[canc_p_idx]
            canc_qty = -int(np.random.randint(1, 5))
            transactions.append({
                "InvoiceNo": f"C{inv_no}",
                "StockCode": stock_code,
                "Description": f"Cancelled: {desc}",
                "Quantity": canc_qty,
                "InvoiceDate": (inv_date + timedelta(hours=np.random.randint(1, 24))).strftime("%Y-%m-%d %H:%M:%S"),
                "UnitPrice": round(base_price, 2),
                "CustomerID": float(cid),
                "Country": country
            })

df = pd.DataFrame(transactions)

# Inject realistic messy data elements:
# 1. Null customer IDs for guest transactions (~2.5% of rows)
guest_indices = np.random.choice(df.index, size=int(len(df) * 0.025), replace=False)
df.loc[guest_indices, "CustomerID"] = np.nan

# 2. Add some whitespace / casing variations in Description
whitespace_indices = np.random.choice(df.index, size=40, replace=False)
df.loc[whitespace_indices, "Description"] = df.loc[whitespace_indices, "Description"].apply(lambda x: f"  {x.lower()}  ")

# Save raw dataset
output_path = "DataAnalytics-L1-CustomerSegmentation/data/ecommerce_transactions.csv"
df.to_csv(output_path, index=False)
print(f"✅ Generated {len(df)} transactions across {df['CustomerID'].nunique()} unique customers.")
print(f"Dataset successfully saved to: {output_path}")
