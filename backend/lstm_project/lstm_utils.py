import os
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv
from sklearn.preprocessing import MinMaxScaler
import joblib
import numpy as np

# ✅ Load environment variables
load_dotenv()

def get_engine():
    """
    Create SQLAlchemy engine for autodb using environment variables.
    """
    dbname = os.getenv("AUTODB_NAME")
    user = os.getenv("AUTODB_USER")
    password = os.getenv("AUTODB_PASSWORD")
    host = os.getenv("AUTODB_HOST")
    port = os.getenv("AUTODB_PORT", "5432")   # default to 5432 if not set
    return create_engine(f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{dbname}")

def fetch_sales_data(start_year, end_year):
    """
    Fetch full sales_data from autodb between given years.
    """
    print("🔍 Fetching sales_data from autodb...")
    engine = get_engine()
    query = f"""
        SELECT store_id, sku_id, year, day, date, type_of_day,
               initial, sold, returns, donations, reroutes_in, reroutes_out, recycled, final
        FROM sales_data
        WHERE date >= '{start_year}-01-01' AND date <= '{end_year}-12-31'
        ORDER BY date
    """
    df = pd.read_sql(query, engine)
    print(f"✅ Fetched {len(df)} rows from sales_data")
    return df

def preprocess(df, window_size=5):
    """
    Scale numerical columns and create LSTM input windows.
    """
    print("⚙️ Preprocessing data...")

    features = ['initial', 'sold', 'returns', 'donations', 
                'reroutes_in', 'reroutes_out', 'recycled', 'final']

    scaler = MinMaxScaler()
    scaled = scaler.fit_transform(df[features])

    # Save scaler locally for later inference/retrain
    joblib.dump(scaler, "scaler.pkl")
    print("✅ Saved scaler to scaler.pkl")

    X, y = [], []
    for i in range(window_size, len(scaled)):
        X.append(scaled[i - window_size:i])
        y.append(scaled[i][features.index('sold')])  # predict 'sold'

    X, y = np.array(X), np.array(y)
    print(f"✅ Created sequences: X shape {X.shape}, y shape {y.shape}")
    return X, y, scaler

def preprocess_with_meta(df, window_size=5):
    """
    Same as preprocess, but also return metadata (store_id, sku_id, date).
    """
    print("⚙️ Preprocessing data with metadata...")

    features = ['initial', 'sold', 'returns', 'donations', 
                'reroutes_in', 'reroutes_out', 'recycled', 'final']

    scaler = MinMaxScaler()
    scaled = scaler.fit_transform(df[features])

    joblib.dump(scaler, "scaler.pkl")
    print("✅ Saved scaler to scaler.pkl")

    X, y, meta = [], [], []

    for i in range(window_size, len(scaled)):
        X.append(scaled[i - window_size:i])
        y.append(scaled[i][features.index('sold')])
        meta.append({
            'store_id': df.iloc[i]['store_id'],
            'sku_id': df.iloc[i]['sku_id'],
            'date': df.iloc[i]['date']
        })

    X, y = np.array(X), np.array(y)
    print(f"✅ Created sequences: X shape {X.shape}, y shape {y.shape}")
    return X, y, meta
