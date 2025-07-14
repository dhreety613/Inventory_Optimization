import os
import joblib
import numpy as np
from datetime import datetime
from tensorflow import keras
from lstm_utils import fetch_sales_data, preprocess
from sklearn.metrics import mean_squared_error
from dotenv import load_dotenv

# ✅ Load environment variables
load_dotenv()

# --- Config ---
LAST_RETRAIN_FILE = 'last_retrain.txt'
MODEL_FILE = os.path.join(os.path.dirname(__file__), 'base_lstm_model.h5')
SCALER_FILE = 'scaler.pkl'

# --- Functions ---

def days_since_last_retrain():
    """
    Return days since last retrain recorded in LAST_RETRAIN_FILE.
    """
    if not os.path.exists(LAST_RETRAIN_FILE):
        return float('inf')  # trigger retrain on first run
    with open(LAST_RETRAIN_FILE, 'r') as f:
        last_date = datetime.strptime(f.read().strip(), "%Y-%m-%d")
    delta = datetime.utcnow() - last_date
    return delta.days

def update_last_retrain_date():
    """
    Write current UTC date to LAST_RETRAIN_FILE.
    """
    with open(LAST_RETRAIN_FILE, 'w') as f:
        f.write(datetime.utcnow().strftime("%Y-%m-%d"))

def retrain_and_evaluate():
    """
    Fetch data, retrain model, compare performance, and save if better.
    """
    print("🔍 Fetching latest data from autodb...")
    df = fetch_sales_data(2021, 2024)  # adjust years if needed
    print(f"✅ Fetched {len(df)} rows.")

    print("⚙️ Preprocessing data...")
    X, y, scaler = preprocess(df, window_size=5)

    split = int(len(X) * 0.8)
    X_train, X_val = X[:split], X[split:]
    y_train, y_val = y[:split], y[split:]

    print("📦 Loading existing model...")
    old_model = keras.models.load_model(MODEL_FILE)

    print("📈 Retraining model...")
    retrained_model = keras.models.clone_model(old_model)
    retrained_model.set_weights(old_model.get_weights())
    retrained_model.compile(optimizer='adam', loss='mse')
    retrained_model.fit(X_train, y_train, epochs=5, batch_size=32, verbose=1)

    print("🔍 Evaluating models on validation data...")
    old_preds = old_model.predict(X_val)
    retrained_preds = retrained_model.predict(X_val)

    old_mse = mean_squared_error(y_val, old_preds)
    retrained_mse = mean_squared_error(y_val, retrained_preds)

    print(f"✅ Old model MSE: {old_mse:.4f}")
    print(f"✅ Retrained model MSE: {retrained_mse:.4f}")

    if retrained_mse < old_mse:
        retrained_model.save(MODEL_FILE)
        joblib.dump(scaler, SCALER_FILE)
        update_last_retrain_date()
        print("🎉 Retrained model is better! Saved as new base model.")
    else:
        print("⚖️ Old model performs better; keeping existing model.")

# --- Entrypoint ---
if __name__ == "__main__":
    days = days_since_last_retrain()
    print(f"⏱ Last retrain was {days} days ago.")
    if days >= 30:
        retrain_and_evaluate()
    else:
        print("✅ No retraining needed yet (less than 30 days).")
