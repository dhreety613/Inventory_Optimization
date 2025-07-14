import os
import sys
import joblib
import pandas as pd
from datetime import datetime
from tensorflow import keras
from dotenv import load_dotenv
import psycopg2

# Load env vars
load_dotenv()

# Adjust path to import lstm_utils etc.
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'lstm_project')))
from lstm_utils import fetch_sales_data, preprocess_with_meta
from retrain_lstm_if_needed import days_since_last_retrain

# Paths
MODEL_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "lstm_project", "base_lstm_model.h5"))
SCALER_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "lstm_project", "scaler.pkl"))

def get_supabase_conn():
    """
    Create psycopg2 connection to Supabase Postgres using env vars.
    """
    return psycopg2.connect(
        dbname=os.getenv("AUTODB_NAME"),
        user=os.getenv("AUTODB_USER"),
        password=os.getenv("AUTODB_PASSWORD"),
        host=os.getenv("AUTODB_HOST"),
        port=os.getenv("AUTODB_PORT", "5432")
    )

def load_current_model():
    days = days_since_last_retrain()
    print(f"⏱ Days since last retrain: {days}")
    model = keras.models.load_model(MODEL_FILE)
    scaler = joblib.load(SCALER_FILE) if os.path.exists(SCALER_FILE) else None
    return model, scaler

def run_abc_logic():
    print("🔍 Loading model...")
    model, scaler = load_current_model()

    print("📦 Fetching latest sales data...")
    current_year = datetime.utcnow().year
    df = fetch_sales_data(2021, current_year)

    print("⚙️ Preprocessing...")
    X, _, meta = preprocess_with_meta(df, window_size=5)

    if meta is None or len(meta) == 0:
        raise ValueError("Preprocessing returned empty meta data!")

    print(f"📈 Predicting next 14 days sales...")
    preds = model.predict(X).flatten()

    pred_df = pd.DataFrame(meta)
    pred_df['predicted_sales'] = preds

    # 🔗 Use Supabase connection to get shelf life & stock
    conn = get_supabase_conn()
    skus_df = pd.read_sql("SELECT sku_id, shelf_life_days FROM skus", conn)
    stock_df = pd.read_sql("""
        SELECT store_id, sku_id, final as current_stock 
        FROM sales_data 
        WHERE date = (SELECT max(date) FROM sales_data)
    """, conn)
    conn.close()

    merged = pred_df.merge(stock_df, on=['store_id', 'sku_id'], how='left')
    merged = merged.merge(skus_df, on='sku_id', how='left')

    # Group by SKU to find store with max predicted sales (for reroute target)
    sku_store_max = pred_df.groupby('sku_id')['predicted_sales'].idxmax()
    reroute_targets = pred_df.loc[sku_store_max][['sku_id', 'store_id']]
    reroute_targets = reroute_targets.rename(columns={'store_id': 'target_store_id'})

    action_plan = []

    for _, row in merged.iterrows():
        sku = row['sku_id']
        store = row['store_id']
        shelf_days = row.get('shelf_life_days', 14)
        predicted = row['predicted_sales']
        stock = row['current_stock'] if pd.notna(row['current_stock']) else 0

        if predicted > 0:
            days_to_sell = stock / predicted * 14
        else:
            days_to_sell = float('inf')

        days_left = shelf_days
        gap = days_left - days_to_sell

        # Default extra fields
        target_store_id = ''
        bundle_with_sku = ''

        if days_to_sell < days_left and gap >= 15:
            action = 'keep_on_shelf_and_restock'
            restock_amt = max(0, predicted*2 - stock)
            action_plan.append({
                'store_id': store, 'sku_id': sku, 'action': action, 'restock': int(restock_amt),
                'target_store_id': target_store_id, 'bundle_with_sku': bundle_with_sku
            })

        elif 8 < gap < 15:
            action = 'reroute_to_high_demand_store'
            target_row = reroute_targets[(reroute_targets['sku_id']==sku) & (reroute_targets['target_store_id'] != store)]
            if not target_row.empty:
                target_store_id = target_row.iloc[0]['target_store_id']
            action_plan.append({
                'store_id': store, 'sku_id': sku, 'action': action, 'restock': '',
                'target_store_id': target_store_id, 'bundle_with_sku': bundle_with_sku
            })

        elif 6 < gap <= 8:
            action = 'clearance_sale_tier1_30_50'
            keep_skus = [x['sku_id'] for x in action_plan if x['store_id']==store and x['action']=='keep_on_shelf_and_restock']
            if keep_skus:
                bundle_with_sku = keep_skus[0]
            action_plan.append({
                'store_id': store, 'sku_id': sku, 'action': action, 'restock': '',
                'target_store_id': target_store_id, 'bundle_with_sku': bundle_with_sku
            })

        elif 4 < days_left - days_to_sell <= 6:
            action = 'flash_sale_tier2_80_90'
            keep_skus = [x['sku_id'] for x in action_plan if x['store_id']==store and x['action']=='keep_on_shelf_and_restock']
            if keep_skus:
                bundle_with_sku = keep_skus[0]
            action_plan.append({
                'store_id': store, 'sku_id': sku, 'action': action, 'restock': '',
                'target_store_id': target_store_id, 'bundle_with_sku': bundle_with_sku
            })

        else:
            action = 'donate'
            action_plan.append({
                'store_id': store, 'sku_id': sku, 'action': action, 'restock': '',
                'target_store_id': target_store_id, 'bundle_with_sku': bundle_with_sku
            })

    action_df = pd.DataFrame(action_plan)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    action_df.to_csv(f'actionplan.csv', index=False)
    print(f"✅ Saved action plan to actionplan.csv")

    return action_df

if __name__ == "__main__":
    run_abc_logic()

