import psycopg2
import os
from dotenv import load_dotenv
from datetime import datetime
import pytz
import requests
from tqdm import tqdm

load_dotenv()

# --- DB configs ---
SRC_DB = {
    'dbname': os.getenv("MYWHACKDB_NAME"),
    'user': os.getenv("MYWHACKDB_USER"),
    'password': os.getenv("MYWHACKDB_PASSWORD"),
    'host': os.getenv("MYWHACKDB_HOST")
}
TGT_DB = {
    'dbname': os.getenv("AUTODB_NAME"),
    'user': os.getenv("AUTODB_USER"),
    'password': os.getenv("AUTODB_PASSWORD"),
    'host': os.getenv("AUTODB_HOST")
}

def get_today_date_from_ip():
    try:
        resp = requests.get("https://ipapi.co/json/")
        data = resp.json()
        timezone_str = data.get("timezone", "UTC")
        timezone = pytz.timezone(timezone_str)
        now = datetime.now(timezone)
        print(f"📍 Detected timezone: {timezone_str}, current local date: {now.date()}")
        return now.date()
    except Exception as e:
        print(f"⚠️ Could not detect timezone, defaulting to UTC. Error: {e}")
        return datetime.utcnow().date()

def copy_all_rows(src_cur, tgt_cur, table, columns, pk):
    """
    Copy all rows from src table to tgt table, skipping duplicates by PK.
    """
    print(f"🔄 Copying table: {table}")
    src_cur.execute(f"SELECT {', '.join(columns)} FROM {table}")
    rows = src_cur.fetchall()
    print(f"Found {len(rows)} rows.")
    for row in tqdm(rows, desc=f"Inserting into {table}"):
        placeholders = ', '.join(['%s'] * len(columns))
        sql = f"""
            INSERT INTO {table} ({', '.join(columns)})
            VALUES ({placeholders})
            ON CONFLICT ({pk}) DO NOTHING
        """
        tgt_cur.execute(sql, row)
    print(f"✅ Done: {table}")

def copy_sales_data_until_date(src_cur, tgt_cur, date):
    print(f"🔄 Copying sales_data until date: {date}")
    src_cur.execute("""
        SELECT store_id, sku_id, year, day, date, type_of_day,
               initial, sold, returns, donations, reroutes_in, reroutes_out, recycled, final
        FROM sales_data
        WHERE date <= %s
    """, (date,))
    rows = src_cur.fetchall()
    print(f"Found {len(rows)} sales_data rows.")
    for row in tqdm(rows, desc="Inserting sales_data"):
        sql = """
            INSERT INTO sales_data (
                store_id, sku_id, year, day, date, type_of_day,
                initial, sold, returns, donations, reroutes_in, reroutes_out, recycled, final
            ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            ON CONFLICT (store_id, sku_id, year, day) DO NOTHING
        """
        tgt_cur.execute(sql, row)
    print(f"✅ Done: sales_data")

def main():
    today = get_today_date_from_ip()

    print("🔗 Connecting to source and target DBs...")
    src_conn = psycopg2.connect(**SRC_DB)
    tgt_conn = psycopg2.connect(**TGT_DB)
    src_cur = src_conn.cursor()
    tgt_cur = tgt_conn.cursor()

    tgt_conn.autocommit = True

    # --- Copy tables ---
    copy_all_rows(src_cur, tgt_cur, "skus", ["sku_id", "name", "shelf_life_days"], pk="sku_id")
    copy_all_rows(src_cur, tgt_cur, "stores", ["store_id", "geo", "religion"], pk="store_id")
    copy_all_rows(src_cur, tgt_cur, "store_skus", ["store_id", "sku_id"], pk="store_id, sku_id")
    copy_sales_data_until_date(src_cur, tgt_cur, today)

    src_cur.close()
    tgt_cur.close()
    src_conn.close()
    tgt_conn.close()
    print("✅ Sync complete!")

if __name__ == "__main__":
    main()
