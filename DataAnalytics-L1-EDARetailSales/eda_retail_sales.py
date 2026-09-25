"""
Oasis Infobyte — SIP Task 1
Track: Data Analytics (Level 1)
Task: EDA on Retail Sales Data
Author: Rajesh (OIBSIP Intern)
"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Set visual style
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
plt.rcParams['font.sans-serif'] = 'DejaVu Sans'
plt.rcParams['figure.dpi'] = 300
plt.rcParams['savefig.dpi'] = 300
plt.rcParams['axes.titlesize'] = 14
plt.rcParams['axes.titleweight'] = 'bold'
plt.rcParams['axes.labelsize'] = 11
plt.rcParams['axes.labelweight'] = 'bold'

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, 'data', 'retail_sales_dataset.csv')
OUTPUT_DIR = os.path.join(BASE_DIR, 'visualizations')
os.makedirs(OUTPUT_DIR, exist_ok=True)

def run_eda():
    print("=" * 70)
    print("STEP 1: DATA LOADING & INITIAL INSPECTION")
    print("=" * 70)
    
    df = pd.read_csv(DATA_PATH)
    print(f"Dataset Dimensions: {df.shape[0]} rows, {df.shape[1]} columns")
    print("\nColumn Data Types & Non-Null Counts:")
    print(df.info())
    
    print("\nMissing Values Count per Column:")
    null_counts = df.isnull().sum()
    print(null_counts)
    
    # Ensure correct datetime parsing
    df['Date'] = pd.to_datetime(df['Date'])
    df['Year'] = df['Date'].dt.year
    df['Month'] = df['Date'].dt.month
    df['Month_Year'] = df['Date'].dt.to_period('M')
    df['Quarter'] = df['Date'].dt.to_period('Q')
    df['DayOfWeek'] = df['Date'].dt.day_name()
    df['Is_Weekend'] = df['Date'].dt.dayofweek.isin([5, 6])
    
    print("\nFirst 5 Records:")
    print(df.head())
    
    print("\n" + "=" * 70)
    print("STEP 2: DESCRIPTIVE STATISTICS (MEAN, MEDIAN, MODE, STD DEV)")
    print("=" * 70)
    
    num_cols = ['Quantity', 'Price_Per_Unit', 'Total_Amount', 'Discount_Rate', 
                'Discount_Amount', 'Net_Amount', 'Profit', 'Profit_Margin_Pct', 'Age']
    
    stats_list = []
    for col in num_cols:
        mode_val = df[col].mode().iloc[0] if not df[col].mode().empty else np.nan
        stats_list.append({
            'Feature': col,
            'Mean': round(df[col].mean(), 2),
            'Median': round(df[col].median(), 2),
            'Mode': round(mode_val, 2),
            'Std_Dev': round(df[col].std(), 2),
            'Min': round(df[col].min(), 2),
            '25%': round(df[col].quantile(0.25), 2),
            '75%': round(df[col].quantile(0.75), 2),
            'Max': round(df[col].max(), 2),
            'IQR': round(df[col].quantile(0.75) - df[col].quantile(0.25), 2)
        })
        
    stats_df = pd.DataFrame(stats_list)
    print(stats_df.to_string(index=False))
    
    # Save descriptive stats table to CSV
    stats_csv_path = os.path.join(BASE_DIR, 'data', 'descriptive_statistics.csv')
    stats_df.to_csv(stats_csv_path, index=False)
    print(f"\nDescriptive statistics saved to {stats_csv_path}")

    # =========================================================================
    # VISUALIZATION 1: TIME SERIES ANALYSIS (MONTHLY & QUARTERLY TRENDS)
    # =========================================================================
    print("\nGenerating Figure 1: Monthly & Quarterly Sales Trends...")
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(13, 10))
    
    # Monthly trend
    monthly_sales = df.groupby(df['Date'].dt.to_period('M')).agg({
        'Net_Amount': 'sum',
        'Transaction_ID': 'count'
    }).reset_index()
    monthly_sales['Date_Str'] = monthly_sales['Date'].astype(str)
    
    color_rev = '#1E3A8A'
    color_vol = '#F59E0B'
    
    ax1.plot(monthly_sales['Date_Str'], monthly_sales['Net_Amount'], 
             color=color_rev, marker='o', linewidth=2.5, label='Net Revenue ($)')
    ax1.set_ylabel('Total Net Revenue ($)', color=color_rev, weight='bold')
    ax1.tick_params(axis='y', labelcolor=color_rev)
    ax1.set_title('Monthly Revenue & Order Volume Trends (2023 - 2024)', pad=12)
    ax1.set_xticks(range(len(monthly_sales['Date_Str'])))
    ax1.set_xticklabels(monthly_sales['Date_Str'], rotation=45, ha='right', fontsize=9)
    ax1.grid(True, linestyle='--', alpha=0.5)
    
    ax1_twin = ax1.twinx()
    ax1_twin.bar(monthly_sales['Date_Str'], monthly_sales['Transaction_ID'], 
                 alpha=0.25, color=color_vol, width=0.4, label='Order Volume')
    ax1_twin.set_ylabel('Order Count', color=color_vol, weight='bold')
    ax1_twin.tick_params(axis='y', labelcolor=color_vol)
    ax1_twin.grid(False)
    
    # Quarterly trend
    quarterly_sales = df.groupby(['Year', df['Date'].dt.quarter]).agg({
        'Net_Amount': 'sum',
        'Profit': 'sum'
    }).reset_index()
    quarterly_sales.columns = ['Year', 'Quarter', 'Net_Revenue', 'Total_Profit']
    quarterly_sales['Quarter_Label'] = quarterly_sales.apply(lambda r: f"{r['Year']} Q{int(r['Quarter'])}", axis=1)
    
    x = np.arange(len(quarterly_sales))
    width = 0.35
    
    ax2.bar(x - width/2, quarterly_sales['Net_Revenue'], width, label='Net Revenue ($)', color='#2563EB', alpha=0.85)
    ax2.bar(x + width/2, quarterly_sales['Total_Profit'], width, label='Operating Profit ($)', color='#10B981', alpha=0.85)
    ax2.set_title('Quarterly Revenue vs. Operating Profit Comparison', pad=12)
    ax2.set_xlabel('Fiscal Quarter', weight='bold')
    ax2.set_ylabel('Amount ($)', weight='bold')
    ax2.set_xticks(x)
    ax2.set_xticklabels(quarterly_sales['Quarter_Label'], rotation=0, fontsize=10)
    ax2.legend(frameon=True)
    ax2.grid(True, linestyle='--', alpha=0.5)
    
    # Add values on top of bars
    for i, row in quarterly_sales.iterrows():
        ax2.annotate(f"${row['Net_Revenue']:,.0f}", (i - width/2, row['Net_Revenue']),
                     ha='center', va='bottom', fontsize=8, rotation=0, xytext=(0, 3), textcoords='offset points')
        ax2.annotate(f"${row['Total_Profit']:,.0f}", (i + width/2, row['Total_Profit']),
                     ha='center', va='bottom', fontsize=8, rotation=0, xytext=(0, 3), textcoords='offset points')
        
    plt.tight_layout()
    fig1_path = os.path.join(OUTPUT_DIR, '01_sales_trend_monthly_quarterly.png')
    plt.savefig(fig1_path)
    plt.close()
    print(f"Saved: {fig1_path}")

    # =========================================================================
    # VISUALIZATION 2: CUSTOMER DEMOGRAPHICS ANALYSIS
    # =========================================================================
    print("Generating Figure 2: Customer Demographics Analysis...")
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(14, 11))
    
    # Age Distribution
    sns.histplot(df['Age'], bins=20, kde=True, color='#3B82F6', ax=ax1, edgecolor='black', alpha=0.6)
    ax1.axvline(df['Age'].mean(), color='#EF4444', linestyle='--', linewidth=2, label=f"Mean: {df['Age'].mean():.1f}")
    ax1.axvline(df['Age'].median(), color='#10B981', linestyle='-', linewidth=2, label=f"Median: {df['Age'].median():.1f}")
    ax1.set_title('Customer Age Distribution with KDE Curve')
    ax1.set_xlabel('Age')
    ax1.set_ylabel('Customer Transaction Count')
    ax1.legend()
    
    # Age Group Spend Breakdown
    age_group_summary = df.groupby('Age_Group')['Net_Amount'].agg(['count', 'sum', 'mean']).reset_index()
    sns.barplot(data=age_group_summary, x='Age_Group', y='sum', palette='Blues_r', ax=ax2)
    ax2.set_title('Total Revenue Generated by Age Demographics')
    ax2.set_xlabel('Age Category')
    ax2.set_ylabel('Total Revenue ($)')
    for p in ax2.patches:
        ax2.annotate(f"${p.get_height():,.0f}", (p.get_x() + p.get_width() / 2., p.get_height()),
                     ha='center', va='bottom', fontsize=9, xytext=(0, 3), textcoords='offset points')
        
    # Gender Transaction Share
    gender_counts = df['Gender'].value_counts()
    ax3.pie(gender_counts, labels=gender_counts.index, autopct='%1.1f%%', 
            colors=['#EC4899', '#3B82F6', '#9CA3AF'], startangle=140, 
            wedgeprops={'edgecolor': 'white', 'linewidth': 2})
    ax3.set_title('Transaction Share by Gender')
    
    # Average Order Value (AOV) by Gender & Age Group
    aov_gender_age = df.groupby(['Age_Group', 'Gender'])['Net_Amount'].mean().reset_index()
    sns.barplot(data=aov_gender_age, x='Age_Group', y='Net_Amount', hue='Gender', 
                palette=['#EC4899', '#3B82F6', '#9CA3AF'], ax=ax4)
    ax4.set_title('Average Order Value (AOV) by Age Group & Gender')
    ax4.set_xlabel('Age Category')
    ax4.set_ylabel('Average Order Value ($)')
    ax4.legend(title='Gender', frameon=True)
    
    plt.tight_layout()
    fig2_path = os.path.join(OUTPUT_DIR, '02_customer_demographics.png')
    plt.savefig(fig2_path)
    plt.close()
    print(f"Saved: {fig2_path}")

    # =========================================================================
    # VISUALIZATION 3: PRODUCT ANALYSIS & CATEGORY REVENUE
    # =========================================================================
    print("Generating Figure 3: Product Analysis & Category Revenue...")
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7))
    
    # Top 10 Best-Selling Products by Revenue
    top_products = df.groupby('Product_Name').agg({
        'Net_Amount': 'sum',
        'Quantity': 'sum'
    }).sort_values('Net_Amount', ascending=True).tail(10)
    
    bars1 = ax1.barh(top_products.index, top_products['Net_Amount'], color='#0D9488', alpha=0.85, edgecolor='black')
    ax1.set_title('Top 10 Best-Selling Products by Net Revenue ($)')
    ax1.set_xlabel('Net Revenue ($)')
    for bar in bars1:
        ax1.annotate(f"${bar.get_width():,.0f}", (bar.get_width(), bar.get_y() + bar.get_height() / 2.),
                     ha='left', va='center', fontsize=9, xytext=(5, 0), textcoords='offset points')
    ax1.grid(True, linestyle='--', alpha=0.5)
    
    # Category Revenue & Quantity Breakdown
    category_summary = df.groupby('Product_Category').agg({
        'Net_Amount': 'sum',
        'Profit': 'sum'
    }).sort_values('Net_Amount', ascending=False)
    
    y = np.arange(len(category_summary))
    height = 0.38
    
    ax2.barh(y - height/2, category_summary['Net_Amount'], height, label='Net Revenue ($)', color='#6366F1')
    ax2.barh(y + height/2, category_summary['Profit'], height, label='Operating Profit ($)', color='#10B981')
    ax2.set_yticks(y)
    ax2.set_yticklabels(category_summary.index, fontsize=10, weight='bold')
    ax2.set_title('Revenue & Operating Profit by Product Category')
    ax2.set_xlabel('Amount ($)')
    ax2.legend(frameon=True)
    ax2.grid(True, linestyle='--', alpha=0.5)
    
    for i, row in category_summary.reset_index().iterrows():
        ax2.annotate(f"${row['Net_Amount']:,.0f}", (row['Net_Amount'], i - height/2),
                     ha='left', va='center', fontsize=8, xytext=(4, 0), textcoords='offset points')
        ax2.annotate(f"${row['Profit']:,.0f}", (row['Profit'], i + height/2),
                     ha='left', va='center', fontsize=8, xytext=(4, 0), textcoords='offset points')
        
    plt.tight_layout()
    fig3_path = os.path.join(OUTPUT_DIR, '03_product_and_category_performance.png')
    plt.savefig(fig3_path)
    plt.close()
    print(f"Saved: {fig3_path}")

    # =========================================================================
    # VISUALIZATION 4: CORRELATION MATRIX HEATMAP
    # =========================================================================
    print("Generating Figure 4: Correlation Matrix Heatmap...")
    fig, ax = plt.subplots(figsize=(10, 8))
    corr_features = ['Quantity', 'Price_Per_Unit', 'Total_Amount', 'Discount_Rate', 
                     'Net_Amount', 'Profit', 'Profit_Margin_Pct', 'Age']
    corr_matrix = df[corr_features].corr()
    
    mask = np.triu(np.ones_like(corr_matrix, dtype=bool))
    cmap = sns.diverging_palette(230, 20, as_cmap=True)
    
    sns.heatmap(corr_matrix, mask=mask, cmap=cmap, vmin=-1.0, vmax=1.0, annot=True, 
                fmt=".2f", square=True, linewidths=.8, cbar_kws={"shrink": .8}, ax=ax)
    ax.set_title('Correlation Matrix of Numerical Variables', pad=15)
    
    plt.tight_layout()
    fig4_path = os.path.join(OUTPUT_DIR, '04_correlation_matrix_heatmap.png')
    plt.savefig(fig4_path)
    plt.close()
    print(f"Saved: {fig4_path}")

    # =========================================================================
    # VISUALIZATION 5: ADDITIONAL NON-OBVIOUS INSIGHT
    # (Discount Rate vs Profitability & Margin Dilution Analysis)
    # =========================================================================
    print("Generating Figure 5: Non-Obvious Insight - Discount Impact on Margins...")
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
    
    discount_perf = df.groupby('Discount_Rate').agg({
        'Transaction_ID': 'count',
        'Quantity': 'mean',
        'Net_Amount': 'mean',
        'Profit': 'mean',
        'Profit_Margin_Pct': 'mean'
    }).reset_index()
    discount_perf['Discount_Pct_Label'] = (discount_perf['Discount_Rate'] * 100).astype(int).astype(str) + '%'
    
    # Subplot 1: Average Profit & Average Net Revenue by Discount Tier
    sns.barplot(data=discount_perf, x='Discount_Pct_Label', y='Profit', palette='Reds_r', ax=ax1, edgecolor='black')
    ax1.set_title('Average Profit per Order by Discount Tier')
    ax1.set_xlabel('Applied Discount Rate')
    ax1.set_ylabel('Average Profit ($)')
    for p in ax1.patches:
        ax1.annotate(f"${p.get_height():.2f}", (p.get_x() + p.get_width() / 2., p.get_height()),
                     ha='center', va='bottom', fontsize=9, xytext=(0, 3), textcoords='offset points')
        
    # Subplot 2: Profit Margin % vs Units per Order
    ax2.plot(discount_perf['Discount_Pct_Label'], discount_perf['Profit_Margin_Pct'], 
             color='#DC2626', marker='s', linewidth=2.5, label='Profit Margin (%)')
    ax2.set_xlabel('Applied Discount Rate')
    ax2.set_ylabel('Profit Margin (%)', color='#DC2626', weight='bold')
    ax2.tick_params(axis='y', labelcolor='#DC2626')
    ax2.set_title('Margin Erosion vs. Average Order Quantity by Discount Tier')
    ax2.grid(True, linestyle='--', alpha=0.5)
    
    ax2_twin = ax2.twinx()
    ax2_twin.plot(discount_perf['Discount_Pct_Label'], discount_perf['Quantity'], 
                  color='#2563EB', marker='o', linestyle='--', linewidth=2.5, label='Avg Units Sold')
    ax2_twin.set_ylabel('Average Units per Order', color='#2563EB', weight='bold')
    ax2_twin.tick_params(axis='y', labelcolor='#2563EB')
    ax2_twin.grid(False)
    
    plt.tight_layout()
    fig5_path = os.path.join(OUTPUT_DIR, '05_discount_impact_and_profitability.png')
    plt.savefig(fig5_path)
    plt.close()
    print(f"Saved: {fig5_path}")

    # =========================================================================
    # VISUALIZATION 6: BONUS INSIGHT - SALES BY PAYMENT METHOD & DAY OF WEEK
    # =========================================================================
    print("Generating Figure 6: Sales by Payment Method & Day of Week...")
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
    
    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    daily_sales = df.groupby('DayOfWeek')['Net_Amount'].sum().reindex(day_order).reset_index()
    
    sns.barplot(data=daily_sales, x='DayOfWeek', y='Net_Amount', palette='Purples_r', ax=ax1, edgecolor='black')
    ax1.set_title('Total Net Revenue by Day of the Week')
    ax1.set_xlabel('Day')
    ax1.set_ylabel('Total Revenue ($)')
    ax1.tick_params(axis='x', rotation=30)
    for p in ax1.patches:
        ax1.annotate(f"${p.get_height():,.0f}", (p.get_x() + p.get_width() / 2., p.get_height()),
                     ha='center', va='bottom', fontsize=8, xytext=(0, 3), textcoords='offset points')
        
    payment_summary = df.groupby('Payment_Method').agg({
        'Net_Amount': 'sum',
        'Transaction_ID': 'count'
    }).reset_index()
    
    ax2.pie(payment_summary['Net_Amount'], labels=payment_summary['Payment_Method'], 
            autopct='%1.1f%%', colors=['#3B82F6', '#10B981', '#F59E0B', '#EF4444'], 
            startangle=120, wedgeprops={'edgecolor': 'white', 'linewidth': 2})
    ax2.set_title('Revenue Distribution by Payment Method')
    
    plt.tight_layout()
    fig6_path = os.path.join(OUTPUT_DIR, '06_sales_by_day_and_payment_method.png')
    plt.savefig(fig6_path)
    plt.close()
    print(f"Saved: {fig6_path}")
    
    print("\n" + "=" * 70)
    print("EDA PROCESSING COMPLETE: ALL VISUALIZATIONS GENERATED SUCCESSFULLY!")
    print("=" * 70)

if __name__ == '__main__':
    run_eda()
