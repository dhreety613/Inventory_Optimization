import random
import datetime
from tqdm import tqdm
import firebase_admin
from firebase_admin import credentials, firestore

# --- Init Firebase ---
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

# --- Constants ---
NUM_SKUS = 20
NUM_STORES = 10
YEARS = [2021, 2022, 2023, 2024, 2025]
WEEKENDS_PER_YEAR = 52
GOOD_NORMAL_BAD_RATIO = (0.3, 0.6, 0.1)  # approx 3:6:1

geo_options = ['hills', 'plains', 'beach']
religion_options = ['hindu', 'muslim', 'christian']

# Festival / seasonal peak months by geo+religion combo
peak_months = {
    ('hills', 'hindu'): [7, 11],        # July, Nov (Diwali & local)
    ('hills', 'muslim'): [4, 5],        # Apr-May (Ramadan/Eid)
    ('hills', 'christian'): [12],       # Dec (Christmas)
    ('plains', 'hindu'): [10, 11],      # Oct-Nov (Diwali)
    ('plains', 'muslim'): [4, 5],
    ('plains', 'christian'): [12],
    ('beach', 'hindu'): [3, 10, 11],    # Mar (Holi), Oct-Nov
    ('beach', 'muslim'): [4, 5],
    ('beach', 'christian'): [5, 12],    # May (Easter/Pentecost), Dec
}

# --- Step 1: Create SKU master dataset ---
def generate_skus():
    skus = []
    for i in range(1, NUM_SKUS + 1):
        sku_id = f'SKU{str(i).zfill(2)}'
        shelf_life_days = random.randint(14, 105)  # 2–15 weeks
        skus.append({
            'id': sku_id,
            'name': sku_id,
            'shelf_life_days': shelf_life_days
        })
    return skus

# --- Step 2: Generate 10 stores with geo+religion combos & 12 random SKUs ---
def generate_stores(skus):
    combos = []
    for geo in geo_options:
        for religion in religion_options:
            combos.append((geo, religion))
    random.shuffle(combos)
    stores = []
    for i in range(1, NUM_STORES + 1):
        store_id = f'store{str(i).zfill(2)}'
        geo, religion = combos[i % len(combos)]
        store_skus = random.sample([sku['id'] for sku in skus], 12)
        stores.append({
            'id': store_id,
            'geo': geo,
            'religion': religion,
            'skus': store_skus
        })
    return stores

# --- Step 3: Generate weekend dates for a year ---
def get_weekend_dates(year):
    first_day = datetime.date(year, 1, 1)
    weekends = []
    d = first_day
    # Find first Saturday or Sunday
    while d.weekday() not in [5,6]:
        d += datetime.timedelta(days=1)
    while len(weekends) < WEEKENDS_PER_YEAR:
        weekends.append(d)
        d += datetime.timedelta(days=7)
    return weekends[:WEEKENDS_PER_YEAR]

# --- Step 4: Generate good/normal/bad days per year, aligned with peak months ---
def classify_days(dates, peak_months_list):
    num_good = int(WEEKENDS_PER_YEAR * GOOD_NORMAL_BAD_RATIO[0])
    num_bad = int(WEEKENDS_PER_YEAR * GOOD_NORMAL_BAD_RATIO[2])
    num_normal = WEEKENDS_PER_YEAR - num_good - num_bad

    good_days = []
    for d in dates:
        if d.month in peak_months_list:
            good_days.append(d)
    # If not enough good days, fill randomly
    while len(good_days) < num_good:
        d = random.choice(dates)
        if d not in good_days:
            good_days.append(d)
    good_days = good_days[:num_good]

    remaining = [d for d in dates if d not in good_days]
    bad_days = random.sample(remaining, num_bad)
    normal_days = [d for d in remaining if d not in bad_days]

    day_types = {}
    for d in good_days:
        day_types[d] = 'good'
    for d in normal_days:
        day_types[d] = 'normal'
    for d in bad_days:
        day_types[d] = 'bad'
    return day_types

# --- Step 5: Generate sales data per SKU, per store, per year ---
def simulate_sales_data(store, years):
    sales_data = []
    peaks = peak_months.get((store['geo'], store['religion']), [])

    for sku in store['skus']:
        for year in years:
            dates = get_weekend_dates(year)
            day_types = classify_days(dates, peaks)

            sku_year_data = []
            stock = random.randint(80, 150)  # initial stock for the year

            for idx, date in enumerate(dates):
                type_of_day = day_types[date]

                # Sold numbers depend on type_of_day
                if type_of_day == 'good':
                    sold = random.randint(10, 20)
                elif type_of_day == 'normal':
                    sold = random.randint(5, 10)
                else:  # bad
                    sold = random.randint(1, 5)

                returns = random.randint(0, sold//5)
                donations = random.randint(0,1) if random.random()<0.1 else 0
                reroutes_in = random.randint(0,2) if random.random()<0.05 else 0
                reroutes_out = random.randint(0,2) if random.random()<0.05 else 0
                recycled = random.randint(0,1) if random.random()<0.05 else 0

                final_stock = stock - sold + returns + reroutes_in - reroutes_out - donations - recycled
                if final_stock < 0:
                    final_stock = 0

                sku_year_data.append({
                    'day': idx+1,
                    'date': date.isoformat(),
                    'type_of_day': type_of_day,
                    'initial': stock,
                    'sold': sold,
                    'returns': returns,
                    'donations': donations,
                    'reroutes_in': reroutes_in,
                    'reroutes_out': reroutes_out,
                    'recycled': recycled,
                    'final': final_stock
                })

                stock = final_stock  # carry over to next weekend

            sales_data.append({
                'sku': sku,
                'year': year,
                'data': sku_year_data
            })
    return sales_data

# --- Step 6: Upload to Firestore ---
def upload_to_firestore(skus, stores):
    print("Uploading SKUs...")
    for sku in tqdm(skus):
        db.collection('skus').document(sku['id']).set({
            'name': sku['name'],
            'shelf_life_days': sku['shelf_life_days']
        })

    print("Uploading Stores & Sales data...")
    for store in tqdm(stores):
        details = {
            'geo': store['geo'],
            'religion': store['religion'],
            'skus': store['skus']
        }
        sales_data = simulate_sales_data(store, YEARS)

        db.collection('stores').document(store['id']).set({
            'details': details,
            'sales_data': sales_data
        })

# --- Run all ---
if __name__ == '__main__':
    skus = generate_skus()
    stores = generate_stores(skus)
    upload_to_firestore(skus, stores)
    print("✅ All data uploaded successfully!")