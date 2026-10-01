# 🌐 Oasis Infobyte — Student Internship Program (OIBSIP)

Welcome to my official submission repository for the **Oasis Infobyte Student Internship Program (SIP)**.

![Python](https://img.shields.io/badge/Python-3.13-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Data Analytics](https://img.shields.io/badge/Track-Data_Analytics-150458?style=for-the-badge)
![Status](https://img.shields.io/badge/Internship_Requirement-Fulfilled_(3/3_Tasks)-success?style=for-the-badge)
![Repo](https://img.shields.io/badge/Repo-OIBSIP-blue?style=for-the-badge&logo=github)

---

## 👨‍💻 Intern Profile
- **Intern Name:** Rajesh
- **Domain Track:** Data Analytics
- **Assigned Repository:** `OIBSIP` ([rajeshrys/OIBSIP-](https://github.com/rajeshrys/OIBSIP-.git))
- **Cohort:** 2026
- **Internship Status:** **3 Tasks Completed — Stated Minimum Completion Requirement Met (100%)** ✅

---

## 📌 Domain Track: Data Analytics Overview

According to the official **Domain Track Matrix**, interns in the Data Analytics track must complete **at least 3 tasks** from Level 1 or Level 2 combined to satisfy the internship completion requirement.

### 📋 Task Tracker & Completion Matrix

| Level | Task | Task Name | Status | Deliverables & Directory Link |
| :---: | :---: | :--- | :---: | :--- |
| **Level 1** | **Task 1** | **EDA on Retail Sales Data** | **Completed ✅** | [📂 View Task 1](DataAnalytics-L1-EDARetailSales/) |
| **Level 1** | **Task 2** | **Customer Segmentation Analysis** | **Completed ✅** | [📂 View Task 2](DataAnalytics-L1-CustomerSegmentation/) |
| **Level 1** | **Task 3** | **Cleaning Data** | **Completed ✅** | [📂 View Task 3](DataAnalytics-L1-DataCleaning/) |
| **Level 1** | Task 4 | Sentiment Analysis | Optional | — |
| **Level 2** | Task 1 | Predicting House Prices with Linear Regression | Optional | — |
| **Level 2** | Task 2 | Wine Quality Prediction | Optional | — |
| **Level 2** | Task 3 | Fraud Detection | Optional | — |
| **Level 2** | Task 4 | Google Play Store Analysis | Optional | — |
| **Level 2** | Task 5 | Autocomplete & Autocorrect Data Analytics | Optional | — |

---

## 🎯 Summary of Completed Internship Projects

### 🛒 1. Level 1 — Task 1: Exploratory Data Analysis (EDA) on Retail Sales Data
- **Objective:** In-depth exploratory analysis on 2,500 enterprise retail sales transactions (2023–2024).
- **Key Discoveries:**
  - Quantified central tendencies and dispersion (Mean, Median, Mode, IQR, skewness).
  - Uncovered seasonal Q4 revenue spikes (+38% over mid-year baseline).
  - Identified core demographic: customers aged 25–50 generate over 65% of sales.
  - Proved the *"Discount Margin Dilution"* effect: discounts >10% erode operating profit by 27.8% without increasing basket units.
- **Link:** [DataAnalytics-L1-EDARetailSales/](DataAnalytics-L1-EDARetailSales/)

### 🛍️ 2. Level 1 — Task 2: Customer Segmentation Analysis
- **Objective:** RFM (Recency, Frequency, Monetary) behavioral feature engineering and unsupervised K-Means clustering across 25,518 valid e-commerce transactions and 848 unique customers.
- **Key Discoveries:**
  - Evaluated optimal clusters using the Elbow Method and Silhouette Analysis (peak silhouette score: **0.5125** at $K=4$).
  - Identified 4 distinct personas: **Champions (VIPs)** (17.2% of customers, driving **72.8% of total revenue**), **Loyal Steady Shoppers** (32.3% of customers, 18.3% revenue), **At-Risk / Lapsed Spenders** (22.2% of customers, 8.0% revenue), and **Occasional Shoppers** (28.3% of customers, 0.8% revenue).
  - Formulated targeted retention, upsell, win-back, and second-order onboarding marketing playbooks.
- **Link:** [DataAnalytics-L1-CustomerSegmentation/](DataAnalytics-L1-CustomerSegmentation/)

### 🧹 3. Level 1 — Task 3: Cleaning Data (Enterprise Data Quality Engineering)
- **Objective:** Professional-grade data cleaning, sanitization, and quality engineering on a corrupted loan applicant dataset (3,320 rows).
- **Key Discoveries:**
  - Audited and purged 85 exact duplicate rows and 34 primary key collisions.
  - Standardized chaotic categorical encodings (17 variations of Gender, Employment, Marital Status) into strict business taxonomies.
  - Multi-format regex date parsing across ambiguous formats into ISO `YYYY-MM-DD`.
  - Filtered impossible biological anomalies (Age < 18 or > 95, Credit Score outside 300–850) and applied IQR Winsorization on financial extremes.
  - Justified statistical imputation (Median for skewed numerics, Mode for categoricals, Forward Fill for dates, Row Deletion for unrecoverable IDs), achieving **100% data completeness with zero remaining defects**.
- **Link:** [DataAnalytics-L1-DataCleaning/](DataAnalytics-L1-DataCleaning/)

---

## 📁 Repository Directory Structure

```text
OIBSIP/
├── .gitignore
├── README.md                                       # Master repository documentation
├── TASK_COMPLETION_MESSAGE.txt                     # Official submission logs & LinkedIn templates
│
├── DataAnalytics-L1-EDARetailSales/                # Level 1 Task 1: Retail Sales EDA
│   ├── data/
│   │   ├── retail_sales_dataset.csv                # 2,500 retail transactions
│   │   └── descriptive_statistics.csv              # Statistical summary table
│   ├── visualizations/                             # 6 high-resolution exported charts
│   ├── EDA_Retail_Sales.ipynb                      # Fully executed Jupyter Notebook
│   ├── eda_retail_sales.py                         # Standalone execution pipeline
│   ├── generate_dataset.py                         # Dataset generation script
│   └── README.md                                   # Comprehensive Task 1 report
│
├── DataAnalytics-L1-CustomerSegmentation/          # Level 1 Task 2: Customer Segmentation
│   ├── data/
│   │   ├── ecommerce_transactions.csv              # 26,340 raw transactions
│   │   ├── cleaned_transactions.csv                # 25,518 valid transactions
│   │   ├── descriptive_statistics.csv              # RFM summary statistics
│   │   ├── cluster_profiles.csv                    # Quantified cluster metrics
│   │   └── rfm_segmented_customers.csv             # Customer cluster assignments
│   ├── visualizations/                             # 7 high-resolution exported charts
│   ├── Customer_Segmentation_Analysis.ipynb        # Fully executed Jupyter Notebook
│   ├── customer_segmentation.py                    # Standalone K-Means & RFM pipeline
│   ├── generate_dataset.py                         # E-commerce dataset generator
│   └── README.md                                   # Comprehensive Task 2 report
│
└── DataAnalytics-L1-DataCleaning/                  # Level 1 Task 3: Data Cleaning Mastery
    ├── data/
    │   ├── raw_messy_dataset.csv                   # 3,320 corrupted applicant rows
    │   ├── cleaned_dataset.csv                     # 3,172 sanitized, production-ready rows
    │   ├── data_quality_report_before.csv          # Pre-cleaning audit report
    │   ├── before_after_comparison_summary.csv     # Granular before vs after matrix
    │   └── macro_quality_indicators.csv            # Macro quality indicators table
    ├── visualizations/                             # 4 high-resolution exported charts
    ├── Data_Cleaning_Mastery.ipynb                 # Fully executed Jupyter Notebook
    ├── data_cleaning.py                            # Standalone end-to-end cleaning pipeline
    ├── generate_messy_dataset.py                   # Messy dataset generation engine
    └── README.md                                   # Comprehensive Task 3 report
```

---

## 🛠️ Tech Stack & Tools
- **Programming Language:** Python 3.13
- **Data Manipulation & Wrangling:** `pandas`, `numpy`
- **Machine Learning & Preprocessing:** `scikit-learn` (`KMeans`, `StandardScaler`, `silhouette_score`)
- **Data Visualization & Analytics:** `matplotlib`, `seaborn`
- **Environments:** Jupyter Notebook, VS Code
- **Version Control:** Git, GitHub

---

## 📜 Standard Internship Workflow & Compliance Checklist
1. **Review**: Comprehensive feature checklist analysis for each task card.
2. **Build**: End-to-end data pipeline, statistical modeling, machine learning, and interactive visualization.
3. **Push to GitHub**: Adhering strictly to standard folder naming: `OIBSIP/[TrackName]-[Level/Task]-[ProjectName]/`.
4. **Demo Video**: Screen-recorded walkthrough with a 2-second static title card displaying Name, Track, and Task Title.
5. **LinkedIn Post**: Published walkthrough tagging **Oasis Infobyte** with `#oasisinfobyte`.
6. **Peer Evaluation**: Substantive feedback on cohort peer submissions.
7. **Submission**: Formal submission via official Oasis Infobyte Task Submission Form.

---
*Created with dedication by **Rajesh** for the **Oasis Infobyte Student Internship Program (OIBSIP)**.*
