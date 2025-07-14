import psycopg2
from datetime import datetime
import pytz
import requests
from tqdm import tqdm
from dotenv import load_dotenv
import os

load_dotenv()

# --- Supabase DB configs ---
SRC_DB = {
    'dbname': os.getenv('SRC_DB_NAME'),
    'user': os.getenv('SRC_DB_USER'),
    'password': os.getenv('SRC_DB_PASSWORD'),
    'host': os.getenv('SRC_DB_HOST'),
    'port': os.getenv('SRC_DB_PORT')
}

TGT_DB = {
    'dbname': os.getenv('TGT_DB_NAME'),
    'user': os.getenv('TGT_DB_USER'),
    'password': os.getenv('TGT_DB_PASSWORD'),
    'host': os.getenv('TGT_DB_HOST'),
    'port': os.getenv('TGT_DB_PORT')
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

def copy_sales_data_incremental(src_cur, tgt_cur):
    # Find max date already in target sales_data
    tgt_cur.execute("SELECT MAX(date) FROM sales_data")
    max_date = tgt_cur.fetchone()[0]

    if max_date:
        print(f"📦 Last copied date: {max_date} — copying new rows after this.")
        src_cur.execute("""
            SELECT store_id, sku_id, year, day, date, type_of_day,
                   initial, sold, returns, donations, reroutes_in, reroutes_out, recycled, final
            FROM sales_data
            WHERE date > %s
            ORDER BY date
        """, (max_date,))
    else:
        print("📦 No data in target yet — copying all rows.")
        src_cur.execute("""
            SELECT store_id, sku_id, year, day, date, type_of_day,
                   initial, sold, returns, donations, reroutes_in, reroutes_out, recycled, final
            FROM sales_data
            ORDER BY date
        """)

    rows = src_cur.fetchall()
    print(f"Found {len(rows)} new sales_data rows to copy.")

    for row in tqdm(rows, desc="Inserting new sales_data"):
        sql = """
            INSERT INTO sales_data (
                store_id, sku_id, year, day, date, type_of_day,
                initial, sold, returns, donations, reroutes_in, reroutes_out, recycled, final
            ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            ON CONFLICT (store_id, sku_id, year, day) DO NOTHING
        """
        tgt_cur.execute(sql, row)
    print(f"✅ Done copying incremental sales_data")

def main():
    today = get_today_date_from_ip()

    print("🔗 Connecting to source and target DBs...")
    src_conn = psycopg2.connect(**SRC_DB)
    tgt_conn = psycopg2.connect(**TGT_DB)
    src_cur = src_conn.cursor()
    tgt_cur = tgt_conn.cursor()

    tgt_conn.autocommit = True

    # --- Copy small/static tables every time ---
    copy_all_rows(src_cur, tgt_cur, "skus", ["sku_id", "name", "shelf_life_days"], pk="sku_id")
    copy_all_rows(src_cur, tgt_cur, "stores", ["store_id", "geo", "religion"], pk="store_id")
    copy_all_rows(src_cur, tgt_cur, "store_skus", ["store_id", "sku_id"], pk="store_id, sku_id")

    # --- Copy sales data incrementally ---
    copy_sales_data_incremental(src_cur, tgt_cur)

    src_cur.close()
    tgt_cur.close()
    src_conn.close()
    tgt_conn.close()
    print("✅ Sync complete!")

if __name__ == "__main__":
    main()
