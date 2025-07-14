-- Create database manually first if you want:
-- CREATE DATABASE autodb;

-- Table: skus
CREATE TABLE IF NOT EXISTS skus (
    sku_id TEXT PRIMARY KEY,
    name TEXT,
    shelf_life_days INTEGER
);

-- Table: stores
CREATE TABLE IF NOT EXISTS stores (
    store_id TEXT PRIMARY KEY,
    geo TEXT,
    religion TEXT
);

-- Table: store_skus (which SKUs belong to which store)
CREATE TABLE IF NOT EXISTS store_skus (
    store_id TEXT,
    sku_id TEXT,
    PRIMARY KEY (store_id, sku_id),
    FOREIGN KEY (store_id) REFERENCES stores(store_id),
    FOREIGN KEY (sku_id) REFERENCES skus(sku_id)
);

-- Table: sales_data
CREATE TABLE IF NOT EXISTS sales_data (
    store_id TEXT,
    sku_id TEXT,
    year INTEGER,
    day INTEGER,
    date DATE,
    type_of_day TEXT,
    initial INTEGER,
    sold INTEGER,
    returns INTEGER,
    donations INTEGER,
    reroutes_in INTEGER,
    reroutes_out INTEGER,
    recycled INTEGER,
    final INTEGER,
    PRIMARY KEY (store_id, sku_id, year, day),
    FOREIGN KEY (store_id) REFERENCES stores(store_id),
    FOREIGN KEY (sku_id) REFERENCES skus(sku_id)
);
