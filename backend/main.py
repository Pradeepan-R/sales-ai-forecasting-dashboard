from fastapi import FastAPI, Depends, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import pandas as pd
import io

import models
from database import engine, get_db
from ml_engine import ai_model

# Create DB Tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="AI Sales Forecasting API")

# Setup CORS for Frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def health_check():
    return {"status": "ok", "message": "Backend is running"}

@app.post("/upload/")
async def upload_dataset(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Only CSV files are allowed")
    
    contents = await file.read()
    df = pd.read_csv(io.StringIO(contents.decode('utf-8')))
    
    # Rename columns to match model
    column_mapping = {
        'ID': 'id', 'Date': 'date', 'Product': 'product', 'Region': 'region',
        'Store_Type': 'store_type', 'Price': 'price', 'Discount': 'discount',
        'Marketing_Spend': 'marketing_spend', 'Sales': 'sales', 
        'no of units sold': 'units_sold', 'season': 'season'
    }
    df = df.rename(columns=column_mapping)
    df['date'] = pd.to_datetime(df['date'], format='%d-%m-%Y', errors='coerce')
    df = df.dropna(subset=['date'])
    
    # Fast database insertion using Pandas & SQLAlchemy
    df.to_sql('sales_data', engine, if_exists='replace', index=False)
    
    return {"message": f"Successfully uploaded and processed {len(df)} records."}

@app.get("/train/")
def train_model(db: Session = Depends(get_db)):
    # Read all data from DB
    df = pd.read_sql_table('sales_data', engine)
    success = ai_model.train(df)
    
    if success:
        return {"message": "AI Model trained successfully."}
    return {"message": "Failed to train model. No data available."}

@app.get("/predict/{days}")
def predict_sales(days: int, db: Session = Depends(get_db)):
    try:
        if not ai_model.is_trained:
            df = pd.read_sql_table('sales_data', engine)
            if df.empty:
                raise Exception("No data available to train the model.")
            ai_model.train(df)
            
        predictions = ai_model.predict(days=days)
        return {"predictions": predictions}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/historical/")
def get_historical_data(db: Session = Depends(get_db)):
    query = "SELECT date, SUM(sales) as total_sales FROM sales_data GROUP BY date ORDER BY date"
    df = pd.read_sql_query(query, engine)
    df['date'] = df['date'].astype(str)
    return {"data": df.to_dict(orient='records')}

@app.get("/product-breakdown/")
def get_product_breakdown(db: Session = Depends(get_db)):
    query = "SELECT product as name, SUM(units_sold) as total_units FROM sales_data GROUP BY product ORDER BY total_units DESC"
    df = pd.read_sql_query(query, engine)
    return {"data": df.to_dict(orient='records')}
