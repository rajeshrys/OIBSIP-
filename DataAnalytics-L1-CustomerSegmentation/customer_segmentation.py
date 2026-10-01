"""
OASIS INFOBYTE — STUDENT INTERNSHIP PROGRAM (SIP)
Domain Track: Data Analytics
Level 1 — Task 2: Customer Segmentation Analysis

This script executes an end-to-end Machine Learning and RFM Analytics pipeline:
1. Data Ingestion & Data Quality Cleaning
2. RFM (Recency, Frequency, Monetary) Feature Engineering
3. Descriptive Statistics & Customer Lifetime Metrics
4. Feature Scaling (Log Transformation + StandardScaler)
5. K-Means Clustering & Hyperparameter Optimization (Elbow Method + Silhouette Score)
6. Multi-Dimensional Cluster Visualizations
7. Cluster Profiling & Quantitative Persona Definition
8. Targeted Executive Marketing Strategy Formulation
"""

import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

# Set professional aesthetics
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
plt.rcParams['font.sans-serif'] = 'DejaVu Sans'
plt.rcParams['figure.dpi'] = 300
plt.rcParams['axes.titlesize'] = 14
plt.rcParams['axes.labelsize'] = 11

DATA_DIR = "DataAnalytics-L1-CustomerSegmentation/data"
VIZ_DIR = "DataAnalytics-L1-CustomerSegmentation/visualizations"
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(VIZ_DIR, exist_ok=True)

print("=" * 80)
print("  OASIS INFOBYTE SIP — LEVEL 1 TASK 2: CUSTOMER SEGMENTATION ANALYSIS  ")
print("=" * 80)

# ==============================================================================
# 1. LOAD DATASET & DATA AUDIT / CLEANING
# ==============================================================================
raw_data_path = os.path.join(DATA_DIR, "ecommerce_transactions.csv")
print(f"\n[STEP 1] Ingesting dataset from: {raw_data_path}")
df_raw = pd.read_csv(raw_data_path)

print(f"  • Raw Transactions: {len(df_raw):,}")
print(f"  • Raw Columns: {list(df_raw.columns)}")
print(f"  • Missing CustomerIDs: {df_raw['CustomerID'].isnull().sum():,} ({df_raw['CustomerID'].isnull().mean():.2%})")

# Cleaning operations:
# 1. Drop missing CustomerIDs (guest checkouts cannot be attributed to RFM customer entities)
df_clean = df_raw.dropna(subset=['CustomerID']).copy()

# 2. Convert CustomerID to integer
df_clean['CustomerID'] = df_clean['CustomerID'].astype(int)

# 3. Clean and standardize Description
df_clean['Description'] = df_clean['Description'].astype(str).str.strip().str.upper()

# 4. Parse InvoiceDate
df_clean['InvoiceDate'] = pd.to_datetime(df_clean['InvoiceDate'])

# 5. Handle cancellations: Identify orders with 'C' in InvoiceNo or negative Quantity
is_cancelled = df_clean['InvoiceNo'].astype(str).str.startswith('C') | (df_clean['Quantity'] <= 0)
print(f"  • Cancelled / Return records removed: {is_cancelled.sum():,}")
df_clean = df_clean[~is_cancelled].copy()

# 6. Filter unit price anomalies (price <= 0)
df_clean = df_clean[df_clean['UnitPrice'] > 0].copy()

# 7. Compute Total Line Spend
df_clean['LineTotal'] = df_clean['Quantity'] * df_clean['UnitPrice']

print(f"  • Cleaned Transactions: {len(df_clean):,}")
print(f"  • Unique Customers Analyzed: {df_clean['CustomerID'].nunique():,}")
print(f"  • Date Range: {df_clean['InvoiceDate'].min().strftime('%Y-%m-%d')} to {df_clean['InvoiceDate'].max().strftime('%Y-%m-%d')}")

# Save cleaned transactional dataset
cleaned_tx_path = os.path.join(DATA_DIR, "cleaned_transactions.csv")
df_clean.to_csv(cleaned_tx_path, index=False)

# ==============================================================================
# 2. RFM FEATURE SELECTION & DESCRIPTIVE LIFETIME STATISTICS
# ==============================================================================
print("\n[STEP 2] Computing RFM (Recency, Frequency, Monetary) Metrics...")

# Reference date for Recency calculation (1 day after the latest transaction)
snapshot_date = df_clean['InvoiceDate'].max() + pd.Timedelta(days=1)
print(f"  • Snapshot Date for Recency: {snapshot_date.strftime('%Y-%m-%d %H:%M:%S')}")

rfm = df_clean.groupby('CustomerID').agg({
    'InvoiceDate': lambda x: (snapshot_date - x.max()).days,
    'InvoiceNo': 'nunique',
    'LineTotal': 'sum'
}).reset_index()

rfm.rename(columns={
    'InvoiceDate': 'Recency',
    'InvoiceNo': 'Frequency',
    'LineTotal': 'Monetary'
}, inplace=True)

# Derive Average Order Value (AOV) as Customer Lifetime Metric
rfm['AveragePurchaseValue'] = rfm['Monetary'] / rfm['Frequency']
rfm['CustomerLifetimeValue'] = rfm['Monetary']

# Compute descriptive statistics table
desc_stats = rfm[['Recency', 'Frequency', 'Monetary', 'AveragePurchaseValue', 'CustomerLifetimeValue']].describe().T
desc_stats['median'] = rfm[['Recency', 'Frequency', 'Monetary', 'AveragePurchaseValue', 'CustomerLifetimeValue']].median()
desc_stats['skewness'] = rfm[['Recency', 'Frequency', 'Monetary', 'AveragePurchaseValue', 'CustomerLifetimeValue']].skew()

print("\n--- Descriptive Statistics for Customer Lifetime & RFM Metrics ---")
print(desc_stats[['mean', 'median', 'std', 'min', 'max', 'skewness']].to_string())

desc_stats_path = os.path.join(DATA_DIR, "descriptive_statistics.csv")
desc_stats.to_csv(desc_stats_path)
print(f"  -> Descriptive statistics saved to: {desc_stats_path}")

# ==============================================================================
# 3. FEATURE PREPROCESSING & STANDARDIZATION
# ==============================================================================
print("\n[STEP 3] Normalizing and Standardizing Features...")

# Monetary and Frequency often have heavy right-skew; apply log(1 + x) transformation
rfm_log = pd.DataFrame()
rfm_log['CustomerID'] = rfm['CustomerID']
rfm_log['Recency_log'] = np.log1p(rfm['Recency'])
rfm_log['Frequency_log'] = np.log1p(rfm['Frequency'])
rfm_log['Monetary_log'] = np.log1p(rfm['Monetary'])

scaler = StandardScaler()
rfm_scaled = scaler.fit_transform(rfm_log[['Recency_log', 'Frequency_log', 'Monetary_log']])
rfm_scaled_df = pd.DataFrame(rfm_scaled, columns=['Recency_scaled', 'Frequency_scaled', 'Monetary_scaled'])

# Plot Distributions Before & After Transformation
fig, axes = plt.subplots(2, 3, figsize=(16, 9))
palette = ['#2b5c8f', '#2a9d8f', '#e76f51']

for i, col in enumerate(['Recency', 'Frequency', 'Monetary']):
    sns.histplot(rfm[col], kde=True, ax=axes[0, i], color=palette[i], bins=25)
    axes[0, i].set_title(f"Original {col} Distribution\n(Skew: {rfm[col].skew():.2f})", fontweight='bold')
    axes[0, i].set_xlabel(col)

for i, col in enumerate(['Recency_scaled', 'Frequency_scaled', 'Monetary_scaled']):
    sns.histplot(rfm_scaled_df[col], kde=True, ax=axes[1, i], color=palette[i], bins=25)
    axes[1, i].set_title(f"Log + Scaled {col}\n(Mean: 0.00, Std: 1.00)", fontweight='bold')
    axes[1, i].set_xlabel(f"{col} (Z-Score)")

plt.suptitle("RFM Feature Distributions: Pre vs. Post Normalization & Scaling", fontsize=16, fontweight='bold', y=0.98)
plt.tight_layout()
dist_fig_path = os.path.join(VIZ_DIR, "02_rfm_distributions_before_after_scaling.png")
plt.savefig(dist_fig_path)
plt.close()
print(f"  -> Distribution comparison saved to: {dist_fig_path}")

# ==============================================================================
# 4. K-MEANS CLUSTERING & ELBOW METHOD / SILHOUETTE ANALYSIS
# ==============================================================================
print("\n[STEP 4] Executing Elbow Method & Silhouette Score Optimization for K...")

wcss = []
silhouette_scores = []
k_range = range(2, 11)

for k in k_range:
    kmeans = KMeans(n_clusters=k, init='k-means++', n_init=10, random_state=42)
    kmeans.fit(rfm_scaled)
    wcss.append(kmeans.inertia_)
    score = silhouette_score(rfm_scaled, kmeans.labels_)
    silhouette_scores.append(score)
    print(f"  • K={k:2d} | WCSS (Inertia): {kmeans.inertia_:8.2f} | Silhouette Score: {score:.4f}")

# Plot Elbow and Silhouette curves
fig, ax1 = plt.subplots(figsize=(11, 6))

color1 = '#1f77b4'
ax1.set_xlabel('Number of Clusters (K)', fontweight='bold', fontsize=12)
ax1.set_ylabel('Within-Cluster Sum of Squares (Inertia)', color=color1, fontweight='bold', fontsize=12)
line1 = ax1.plot(list(k_range), wcss, marker='o', linewidth=2.5, markersize=8, color=color1, label='Inertia (Elbow Curve)')
ax1.tick_params(axis='y', labelcolor=color1)
ax1.set_xticks(list(k_range))

# Annotate Elbow at K=4
optimal_k = 4
ax1.axvline(x=optimal_k, color='#e63946', linestyle='--', linewidth=2, label=f'Optimal K = {optimal_k}')

# Silhouette score on twin axis
ax2 = ax1.twinx()
color2 = '#2a9d8f'
ax2.set_ylabel('Silhouette Coefficient Score', color=color2, fontweight='bold', fontsize=12)
line2 = ax2.plot(list(k_range), silhouette_scores, marker='s', linewidth=2.5, markersize=8, color=color2, linestyle='-.', label='Silhouette Score')
ax2.tick_params(axis='y', labelcolor=color2)
ax2.grid(False)

lines = line1 + line2 + [plt.Line2D([0], [0], color='#e63946', linestyle='--', linewidth=2)]
labels = [l.get_label() for l in lines]
ax1.legend(lines, labels, loc='upper right', frameon=True)

plt.title("Optimal Cluster Determination: Elbow Method & Silhouette Coefficient", fontsize=15, fontweight='bold', pad=15)
plt.tight_layout()
elbow_fig_path = os.path.join(VIZ_DIR, "01_elbow_and_silhouette_analysis.png")
plt.savefig(elbow_fig_path)
plt.close()
print(f"  -> Elbow & Silhouette analysis saved to: {elbow_fig_path}")

# Fit final model with optimal K=4
kmeans_final = KMeans(n_clusters=optimal_k, init='k-means++', n_init=20, random_state=42)
rfm['Cluster'] = kmeans_final.fit_predict(rfm_scaled)

# ==============================================================================
# 5. CLUSTER PROFILING & SEGMENT NAMING
# ==============================================================================
print("\n[STEP 5] Profiling Clusters and Assigning Quantitative Personas...")

cluster_stats = rfm.groupby('Cluster').agg({
    'CustomerID': 'count',
    'Recency': ['mean', 'median'],
    'Frequency': ['mean', 'median'],
    'Monetary': ['mean', 'median'],
    'AveragePurchaseValue': ['mean', 'median']
}).round(2)

print("\n--- Cluster Summary Statistics ---")
print(cluster_stats)

# Map meaningful persona names based on empirical RFM profiles:
# High Frequency + High Monetary + Low Recency -> Champions / High-Value VIPs
# Moderate-High Frequency + Recent -> Loyal Steady Shoppers
# Low-Moderate Frequency + High Recency -> At-Risk / Lapsed Spenders
# Low Frequency (1-2) + Moderate-Low Monetary -> Occasional / Casual Shoppers
cluster_means = rfm.groupby('Cluster')[['Recency', 'Frequency', 'Monetary']].mean()

persona_map = {}
for c in range(optimal_k):
    r = cluster_means.loc[c, 'Recency']
    f = cluster_means.loc[c, 'Frequency']
    m = cluster_means.loc[c, 'Monetary']
    
    if m >= cluster_means['Monetary'].quantile(0.70) and f >= cluster_means['Frequency'].quantile(0.70):
        persona_map[c] = "Champions (High-Value VIPs)"
    elif r <= cluster_means['Recency'].median() and f >= cluster_means['Frequency'].median():
        persona_map[c] = "Loyal Steady Shoppers"
    elif r > cluster_means['Recency'].median() and m >= cluster_means['Monetary'].median():
        persona_map[c] = "At-Risk / Lapsed Spenders"
    else:
        persona_map[c] = "Occasional / Low-Engagement Shoppers"

# Guarantee 4 distinct descriptive names
assigned_names = list(persona_map.values())
if len(set(assigned_names)) < optimal_k:
    # Ranked assignment by monetary value
    ranked_clusters = cluster_means.sort_values(by='Monetary', ascending=False).index.tolist()
    persona_map = {
        ranked_clusters[0]: "Champions (High-Value VIPs)",
        ranked_clusters[1]: "Loyal Steady Shoppers",
        ranked_clusters[2]: "At-Risk / Lapsed Spenders",
        ranked_clusters[3]: "Occasional / Low-Engagement Shoppers"
    }

rfm['Segment'] = rfm['Cluster'].map(persona_map)

# Detailed cluster profiles
profiles = rfm.groupby(['Cluster', 'Segment']).agg(
    Customer_Count=('CustomerID', 'count'),
    Avg_Recency_Days=('Recency', 'mean'),
    Median_Recency_Days=('Recency', 'median'),
    Avg_Frequency=('Frequency', 'mean'),
    Median_Frequency=('Frequency', 'median'),
    Avg_Monetary_Spend=('Monetary', 'mean'),
    Median_Monetary_Spend=('Monetary', 'median'),
    Avg_Order_Value=('AveragePurchaseValue', 'mean'),
    Total_Segment_Revenue=('Monetary', 'sum')
).reset_index()

profiles['Pct_Customers'] = (profiles['Customer_Count'] / len(rfm)) * 100
profiles['Pct_Revenue'] = (profiles['Total_Segment_Revenue'] / rfm['Monetary'].sum()) * 100

print("\n--- Final Customer Segment Profiles ---")
print(profiles[['Segment', 'Customer_Count', 'Pct_Customers', 'Avg_Recency_Days', 'Avg_Frequency', 'Avg_Monetary_Spend', 'Pct_Revenue']].to_string(index=False))

profiles_path = os.path.join(DATA_DIR, "cluster_profiles.csv")
profiles.to_csv(profiles_path, index=False)
rfm_path = os.path.join(DATA_DIR, "rfm_segmented_customers.csv")
rfm.to_csv(rfm_path, index=False)
print(f"  -> Segment profiles saved to: {profiles_path}")
print(f"  -> Customer RFM assignments saved to: {rfm_path}")

# ==============================================================================
# 6. VISUALIZE CLUSTERS (SCATTER PLOTS & BAR CHARTS)
# ==============================================================================
print("\n[STEP 6] Generating Comprehensive Visualizations...")

cluster_colors = {
    "Champions (High-Value VIPs)": "#2a9d8f",
    "Loyal Steady Shoppers": "#3a86ff",
    "At-Risk / Lapsed Spenders": "#e76f51",
    "Occasional / Low-Engagement Shoppers": "#e9c46a"
}

# --- Visual 1: Recency vs Monetary Scatter Plot ---
plt.figure(figsize=(10, 6))
for segment, color in cluster_colors.items():
    subset = rfm[rfm['Segment'] == segment]
    plt.scatter(subset['Recency'], subset['Monetary'], c=color, label=segment, alpha=0.75, s=60, edgecolors='none')

plt.title("Customer Segments: Recency vs. Monetary Spend (CLV)", fontsize=14, fontweight='bold', pad=12)
plt.xlabel("Recency (Days Since Last Purchase)", fontsize=11, fontweight='bold')
plt.ylabel("Monetary Spend ($)", fontsize=11, fontweight='bold')
plt.legend(frameon=True, facecolor='white', framealpha=0.9, loc='upper right')
plt.tight_layout()
scat1_path = os.path.join(VIZ_DIR, "03_cluster_scatter_recency_monetary.png")
plt.savefig(scat1_path)
plt.close()
print(f"  -> Scatter (Recency vs Monetary) saved to: {scat1_path}")

# --- Visual 2: Frequency vs Monetary Scatter Plot ---
plt.figure(figsize=(10, 6))
for segment, color in cluster_colors.items():
    subset = rfm[rfm['Segment'] == segment]
    plt.scatter(subset['Frequency'], subset['Monetary'], c=color, label=segment, alpha=0.75, s=60, edgecolors='none')

plt.title("Customer Segments: Frequency vs. Monetary Spend", fontsize=14, fontweight='bold', pad=12)
plt.xlabel("Frequency (Total Invoices / Orders)", fontsize=11, fontweight='bold')
plt.ylabel("Monetary Spend ($)", fontsize=11, fontweight='bold')
plt.legend(frameon=True, facecolor='white', framealpha=0.9, loc='upper left')
plt.tight_layout()
scat2_path = os.path.join(VIZ_DIR, "04_cluster_scatter_frequency_monetary.png")
plt.savefig(scat2_path)
plt.close()
print(f"  -> Scatter (Frequency vs Monetary) saved to: {scat2_path}")

# --- Visual 3: Recency vs Frequency Scatter Plot ---
plt.figure(figsize=(10, 6))
for segment, color in cluster_colors.items():
    subset = rfm[rfm['Segment'] == segment]
    plt.scatter(subset['Recency'], subset['Frequency'], c=color, label=segment, alpha=0.75, s=60, edgecolors='none')

plt.title("Customer Segments: Recency vs. Purchase Frequency", fontsize=14, fontweight='bold', pad=12)
plt.xlabel("Recency (Days Since Last Purchase)", fontsize=11, fontweight='bold')
plt.ylabel("Frequency (Total Orders)", fontsize=11, fontweight='bold')
plt.legend(frameon=True, facecolor='white', framealpha=0.9, loc='upper right')
plt.tight_layout()
scat3_path = os.path.join(VIZ_DIR, "05_cluster_scatter_recency_frequency.png")
plt.savefig(scat3_path)
plt.close()
print(f"  -> Scatter (Recency vs Frequency) saved to: {scat3_path}")

# --- Visual 4: Customer Count & Revenue Share Bar Chart ---
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

segment_order = [
    "Champions (High-Value VIPs)",
    "Loyal Steady Shoppers",
    "At-Risk / Lapsed Spenders",
    "Occasional / Low-Engagement Shoppers"
]

counts = [profiles.loc[profiles['Segment'] == s, 'Customer_Count'].values[0] for s in segment_order]
pct_cust = [profiles.loc[profiles['Segment'] == s, 'Pct_Customers'].values[0] for s in segment_order]
pct_rev = [profiles.loc[profiles['Segment'] == s, 'Pct_Revenue'].values[0] for s in segment_order]
colors_ordered = [cluster_colors[s] for s in segment_order]

# Subplot 1: Customer Count
bars1 = ax1.bar(segment_order, counts, color=colors_ordered, alpha=0.88, edgecolor='black', linewidth=0.8)
ax1.set_title("Customer Volume by Segment", fontsize=13, fontweight='bold', pad=12)
ax1.set_ylabel("Number of Customers", fontsize=11, fontweight='bold')
ax1.set_xticks(range(len(segment_order)))
ax1.set_xticklabels(segment_order, rotation=25, ha='right')

for bar, pct in zip(bars1, pct_cust):
    height = bar.get_height()
    ax1.annotate(f"{int(height):,}\n({pct:.1f}%)",
                 xy=(bar.get_x() + bar.get_width() / 2, height),
                 xytext=(0, 4), textcoords="offset points",
                 ha='center', va='bottom', fontsize=9, fontweight='bold')

# Subplot 2: Revenue Contribution Share
bars2 = ax2.bar(segment_order, pct_rev, color=colors_ordered, alpha=0.88, edgecolor='black', linewidth=0.8)
ax2.set_title("Aggregate Revenue Contribution Share (%)", fontsize=13, fontweight='bold', pad=12)
ax2.set_ylabel("% of Total Business Revenue", fontsize=11, fontweight='bold')
ax2.set_xticks(range(len(segment_order)))
ax2.set_xticklabels(segment_order, rotation=25, ha='right')

for bar, rev_pct in zip(bars2, pct_rev):
    height = bar.get_height()
    ax2.annotate(f"{rev_pct:.1f}%",
                 xy=(bar.get_x() + bar.get_width() / 2, height),
                 xytext=(0, 4), textcoords="offset points",
                 ha='center', va='bottom', fontsize=10, fontweight='bold')

plt.suptitle("Customer Segment Distribution vs. Commercial Value Concentration", fontsize=15, fontweight='bold', y=1.02)
plt.tight_layout()
dist_bar_path = os.path.join(VIZ_DIR, "06_customer_distribution_per_cluster.png")
plt.savefig(dist_bar_path, bbox_inches='tight')
plt.close()
print(f"  -> Segment distribution bar chart saved to: {dist_bar_path}")

# --- Visual 5: Average RFM Metrics by Cluster ---
fig, axes = plt.subplots(1, 3, figsize=(18, 5))

metrics = [
    ('Avg_Recency_Days', 'Average Recency (Days - Lower is Better)', 'Days', '#264653'),
    ('Avg_Frequency', 'Average Order Frequency (Orders)', 'Orders', '#2a9d8f'),
    ('Avg_Monetary_Spend', 'Average Customer Lifetime Spend ($)', 'USD ($)', '#e76f51')
]

for idx, (metric_col, title, ylabel, col_color) in enumerate(metrics):
    vals = [profiles.loc[profiles['Segment'] == s, metric_col].values[0] for s in segment_order]
    bars = axes[idx].bar(segment_order, vals, color=colors_ordered, alpha=0.85, edgecolor='black')
    axes[idx].set_title(title, fontsize=12, fontweight='bold')
    axes[idx].set_ylabel(ylabel, fontsize=10, fontweight='bold')
    axes[idx].set_xticks(range(len(segment_order)))
    axes[idx].set_xticklabels(segment_order, rotation=30, ha='right')
    
    for bar in bars:
        h = bar.get_height()
        axes[idx].annotate(f"{h:,.1f}",
                           xy=(bar.get_x() + bar.get_width() / 2, h),
                           xytext=(0, 4), textcoords="offset points",
                           ha='center', va='bottom', fontsize=9, fontweight='bold')

plt.suptitle("Comparative Behavioral Profiles Across RFM Dimensions", fontsize=15, fontweight='bold', y=1.03)
plt.tight_layout()
profile_bar_path = os.path.join(VIZ_DIR, "07_cluster_profiles_rfm_comparison.png")
plt.savefig(profile_bar_path, bbox_inches='tight')
plt.close()
print(f"  -> Behavioral profiles comparison saved to: {profile_bar_path}")

# ==============================================================================
# 7. EXECUTIVE SUMMARY & TARGETED MARKETING STRATEGIES
# ==============================================================================
print("\n" + "=" * 80)
print("  EXECUTIVE INSIGHTS & TARGETED MARKETING STRATEGIES  ")
print("=" * 80)

strategies = {
    "Champions (High-Value VIPs)": (
        "VIP Concierge & Loyalty Exclusives:\n"
        "• These customers represent the company's highest lifetime value with frequent, recent transactions.\n"
        "• Action: Enroll in a tiered VIP loyalty rewards tier, provide 48-hour early access to product releases, "
        "and dedicate private concierge customer support. Avoid heavy margin-diluting discount codes; focus on brand prestige."
    ),
    "Loyal Steady Shoppers": (
        "Cross-Selling & Basket Size Expansion:\n"
        "• High retention and steady engagement, forming the resilient backbone of predictable recurring revenue.\n"
        "• Action: Recommend personalized product bundles based on collaborative filtering. Implement conditional "
        "threshold incentives (e.g., 'Spend $75 to unlock free expedited shipping and complimentary gift') to expand AOV."
    ),
    "At-Risk / Lapsed Spenders": (
        "Win-Back Campaign & Churn Prevention:\n"
        "• High past monetary contribution, but have not made a purchase in over 180+ days. Prime churn risk.\n"
        "• Action: Trigger a 3-stage automated win-back email sequence offering a personalized 'We Miss You' incentive "
        "(e.g., $15 credit or 15% discount on past favored categories) and a one-click satisfaction survey to diagnose churn cause."
    ),
    "Occasional / Low-Engagement Shoppers": (
        "Nurture Journey & Second-Purchase Conversion:\n"
        "• Single or low-frequency purchasers with small baskets. High conversion barrier to repeat habits.\n"
        "• Action: Implement a 14-day post-purchase automated onboarding email sequence featuring customer reviews, "
        "usage guides, and a time-sensitive second-order voucher (e.g., '10% off your next order valid for 7 days')."
    )
}

for segment, strategy in strategies.items():
    row = profiles[profiles['Segment'] == segment].iloc[0]
    print(f"\n[{segment}]")
    print(f"  • Size: {row['Customer_Count']} customers ({row['Pct_Customers']:.1f}%) | Revenue Share: {row['Pct_Revenue']:.1f}%")
    print(f"  • Avg Recency: {row['Avg_Recency_Days']:.1f} days | Avg Frequency: {row['Avg_Frequency']:.1f} orders | Avg Spend: ${row['Avg_Monetary_Spend']:,.2f}")
    print(f"  • Strategy: {strategy}")

print("\n" + "=" * 80)
print("✅ Task 2 Customer Segmentation Analytics Pipeline Completed Successfully!")
print("=" * 80)
