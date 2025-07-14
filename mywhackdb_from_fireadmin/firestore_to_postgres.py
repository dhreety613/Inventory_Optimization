import psycopg2
from tqdm import tqdm
import firebase_admin
from firebase_admin import credentials, firestore

# --- Initialize Firebase ---
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

# --- Initialize Postgres connection ---
pg_conn = psycopg2.connect(
    dbname='mywhackdb',
    user='myuser',
    password='rafaelnadal',
    host='localhost'
)
pg_conn.autocommit = True
pg_cur = pg_conn.cursor()

# --- Fetch SKUs ---
print("Fetching SKUs from Firestore...")
sku_docs = list(db.collection('skus').stream())
print(f"Found {len(sku_docs)} SKUs.")

# --- Fetch Stores ---
print("Fetching Stores from Firestore...")
store_docs = list(db.collection('stores').stream())
print(f"Found {len(store_docs)} stores.")

# --- Insert SKUs ---
print("Inserting SKUs into Postgres...")
for doc in tqdm(sku_docs):
    sku = doc.to_dict()
    pg_cur.execute("""
        INSERT INTO skus (sku_id, name, shelf_life_days)
        VALUES (%s, %s, %s)
        ON CONFLICT (sku_id) DO NOTHING
    """, (doc.id, sku.get('name'), sku.get('shelf_life_days')))

# --- Insert Stores & store_skus & sales_data ---
print("Inserting Stores, Store-SKUs and Sales Data into Postgres...")
for doc in tqdm(store_docs):
    store = doc.to_dict()
    details = store.get('details', {})
    sales_data = store.get('sales_data', [])

    store_id = doc.id
    geo = details.get('geo')
    religion = details.get('religion')
    skus = details.get('skus', [])

    # Insert into stores table
    pg_cur.execute("""
        INSERT INTO stores (store_id, geo, religion)
        VALUES (%s, %s, %s)
        ON CONFLICT (store_id) DO NOTHING
    """, (store_id, geo, religion))

    # Insert into store_skus table
    for sku_id in skus:
        pg_cur.execute("""
            INSERT INTO store_skus (store_id, sku_id)
            VALUES (%s, %s)
            ON CONFLICT DO NOTHING
        """, (store_id, sku_id))

    # Insert into sales_data table
    for entry in sales_data:
        sku_id = entry.get('sku')
        year = entry.get('year')
        data_points = entry.get('data', [])

        for dp in data_points:
            pg_cur.execute("""
                INSERT INTO sales_data (
                    store_id, sku_id, year, day, date, type_of_day,
                    initial, sold, returns, donations, reroutes_in, reroutes_out, recycled, final
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                store_id, sku_id, year,
                dp.get('day'),
                dp.get('date'),
                dp.get('type_of_day'),
                dp.get('initial'),
                dp.get('sold'),
                dp.get('returns'),
                dp.get('donations'),
                dp.get('reroutes_in'),
                dp.get('reroutes_out'),
                dp.get('recycled'),
                dp.get('final')
            ))

print("✅ ETL completed! Data now in Postgres.")

# --- Cleanup ---
pg_cur.close()
pg_conn.close()
