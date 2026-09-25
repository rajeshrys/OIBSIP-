"""
Retail Sales EDA Dashboard - FastAPI Web Application
Deployable on Render, Railway, Heroku, or locally with Uvicorn.
"""

import os
from typing import Optional
import pandas as pd
import numpy as np
from fastapi import FastAPI, Query, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, 'data', 'retail_sales_dataset.csv')
STATIC_DIR = os.path.join(BASE_DIR, 'static')
TEMPLATES_DIR = os.path.join(BASE_DIR, 'templates')

app = FastAPI(
    title="Retail Sales Analytics Dashboard",
    description="Interactive Executive Analytics Platform for Oasis Infobyte SIP Task 1",
    version="1.0.0"
)

# Mount static files & templates
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
templates = Jinja2Templates(directory=TEMPLATES_DIR)

# Load data at startup
def load_data():
    if not os.path.exists(DATA_PATH):
        raise FileNotFoundError(f"Dataset not found at {DATA_PATH}")
    df = pd.read_csv(DATA_PATH)
    df['Date'] = pd.to_datetime(df['Date'])
    df['Year'] = df['Date'].dt.year
    df['Month'] = df['Date'].dt.month
    df['Month_Year'] = df['Date'].dt.to_period('M').astype(str)
    df['Quarter'] = df['Date'].dt.to_period('Q').astype(str)
    df['DayOfWeek'] = df['Date'].dt.day_name()
    return df

df_master = load_data()

def filter_dataframe(
    category: Optional[str] = None,
    gender: Optional[str] = None,
    age_group: Optional[str] = None,
    year: Optional[int] = None
) -> pd.DataFrame:
    df = df_master.copy()
    if category and category != 'All':
        df = df[df['Product_Category'] == category]
    if gender and gender != 'All':
        df = df[df['Gender'] == gender]
    if age_group and age_group != 'All':
        df = df[df['Age_Group'] == age_group]
    if year and year != 0:
        df = df[df['Year'] == year]
    return df

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    categories = ['All'] + sorted(df_master['Product_Category'].unique().tolist())
    genders = ['All'] + sorted(df_master['Gender'].unique().tolist())
    age_groups = ['All'] + sorted(df_master['Age_Group'].unique().tolist())
    years = [0] + sorted(df_master['Year'].unique().tolist())
    
    return templates.TemplateResponse("index.html", {
        "request": request,
        "categories": categories,
        "genders": genders,
        "age_groups": age_groups,
        "years": years
    })

@app.get("/api/kpis")
async def get_kpis(
    category: Optional[str] = None,
    gender: Optional[str] = None,
    age_group: Optional[str] = None,
    year: Optional[int] = None
):
    df = filter_dataframe(category, gender, age_group, year)
    
    total_rev = float(df['Net_Amount'].sum())
    total_orders = int(len(df))
    aov = float(df['Net_Amount'].mean()) if total_orders > 0 else 0.0
    total_profit = float(df['Profit'].sum())
    avg_margin = float(df['Profit_Margin_Pct'].mean()) if total_orders > 0 else 0.0
    total_units = int(df['Quantity'].sum())
    avg_discount = float(df['Discount_Rate'].mean() * 100) if total_orders > 0 else 0.0
    
    return {
        "total_revenue": round(total_rev, 2),
        "total_orders": total_orders,
        "average_order_value": round(aov, 2),
        "total_profit": round(total_profit, 2),
        "average_profit_margin": round(avg_margin, 2),
        "total_units_sold": total_units,
        "average_discount_pct": round(avg_discount, 2)
    }

@app.get("/api/trends")
async def get_trends(
    category: Optional[str] = None,
    gender: Optional[str] = None,
    age_group: Optional[str] = None,
    year: Optional[int] = None
):
    df = filter_dataframe(category, gender, age_group, year)
    
    # Monthly trend
    monthly = df.groupby('Month_Year').agg({
        'Net_Amount': 'sum',
        'Profit': 'sum',
        'Transaction_ID': 'count'
    }).reset_index().sort_values('Month_Year')
    
    # Quarterly trend
    quarterly = df.groupby('Quarter').agg({
        'Net_Amount': 'sum',
        'Profit': 'sum'
    }).reset_index().sort_values('Quarter')
    
    return {
        "monthly": {
            "labels": monthly['Month_Year'].tolist(),
            "revenue": [round(v, 2) for v in monthly['Net_Amount'].tolist()],
            "profit": [round(v, 2) for v in monthly['Profit'].tolist()],
            "orders": monthly['Transaction_ID'].tolist()
        },
        "quarterly": {
            "labels": quarterly['Quarter'].tolist(),
            "revenue": [round(v, 2) for v in quarterly['Net_Amount'].tolist()],
            "profit": [round(v, 2) for v in quarterly['Profit'].tolist()]
        }
    }

@app.get("/api/categories")
async def get_categories(
    gender: Optional[str] = None,
    age_group: Optional[str] = None,
    year: Optional[int] = None
):
    df = filter_dataframe(None, gender, age_group, year)
    cat_summary = df.groupby('Product_Category').agg({
        'Net_Amount': 'sum',
        'Profit': 'sum',
        'Quantity': 'sum',
        'Transaction_ID': 'count'
    }).reset_index().sort_values('Net_Amount', ascending=False)
    
    return {
        "labels": cat_summary['Product_Category'].tolist(),
        "revenue": [round(v, 2) for v in cat_summary['Net_Amount'].tolist()],
        "profit": [round(v, 2) for v in cat_summary['Profit'].tolist()],
        "quantity": cat_summary['Quantity'].tolist(),
        "orders": cat_summary['Transaction_ID'].tolist()
    }

@app.get("/api/demographics")
async def get_demographics(
    category: Optional[str] = None,
    year: Optional[int] = None
):
    df = filter_dataframe(category, None, None, year)
    
    # Age group summary
    age_summary = df.groupby('Age_Group').agg({
        'Net_Amount': 'sum',
        'Transaction_ID': 'count',
        'Profit': 'sum'
    }).reset_index().sort_values('Net_Amount', ascending=False)
    
    # Gender summary
    gender_summary = df.groupby('Gender').agg({
        'Net_Amount': 'sum',
        'Transaction_ID': 'count'
    }).reset_index()
    
    return {
        "age_groups": {
            "labels": age_summary['Age_Group'].tolist(),
            "revenue": [round(v, 2) for v in age_summary['Net_Amount'].tolist()],
            "orders": age_summary['Transaction_ID'].tolist()
        },
        "gender": {
            "labels": gender_summary['Gender'].tolist(),
            "revenue": [round(v, 2) for v in gender_summary['Net_Amount'].tolist()],
            "orders": gender_summary['Transaction_ID'].tolist()
        }
    }

@app.get("/api/products")
async def get_top_products(
    category: Optional[str] = None,
    year: Optional[int] = None
):
    df = filter_dataframe(category, None, None, year)
    top_p = df.groupby('Product_Name').agg({
        'Net_Amount': 'sum',
        'Quantity': 'sum',
        'Profit': 'sum'
    }).reset_index().sort_values('Net_Amount', ascending=False).head(10)
    
    return {
        "labels": top_p['Product_Name'].tolist(),
        "revenue": [round(v, 2) for v in top_p['Net_Amount'].tolist()],
        "units": top_p['Quantity'].tolist(),
        "profit": [round(v, 2) for v in top_p['Profit'].tolist()]
    }

@app.get("/api/discounts")
async def get_discount_impact():
    disc = df_master.groupby('Discount_Rate').agg({
        'Transaction_ID': 'count',
        'Quantity': 'mean',
        'Profit': 'mean',
        'Profit_Margin_Pct': 'mean'
    }).reset_index().sort_values('Discount_Rate')
    
    labels = [(f"{int(r * 100)}%") for r in disc['Discount_Rate'].tolist()]
    return {
        "labels": labels,
        "avg_profit": [round(v, 2) for v in disc['Profit'].tolist()],
        "avg_margin": [round(v, 2) for v in disc['Profit_Margin_Pct'].tolist()],
        "avg_quantity": [round(v, 2) for v in disc['Quantity'].tolist()],
        "orders_count": disc['Transaction_ID'].tolist()
    }

@app.get("/api/transactions")
async def get_transactions(limit: int = 50):
    sample = df_master.sort_values('Date', ascending=False).head(limit)
    records = []
    for _, r in sample.iterrows():
        records.append({
            "id": r['Transaction_ID'],
            "date": r['Date'].strftime('%Y-%m-%d'),
            "customer": r['Customer_ID'],
            "gender": r['Gender'],
            "age": int(r['Age']),
            "category": r['Product_Category'],
            "product": r['Product_Name'],
            "quantity": int(r['Quantity']),
            "unit_price": float(r['Price_Per_Unit']),
            "discount": f"{int(r['Discount_Rate'] * 100)}%",
            "net_amount": float(r['Net_Amount']),
            "profit": float(r['Profit']),
            "payment": r['Payment_Method']
        })
    return {"transactions": records}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("app:app", host="0.0.0.0", port=port, reload=True)
