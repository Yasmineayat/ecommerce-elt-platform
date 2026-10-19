import os
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine

load_dotenv()

ENGINE = create_engine(
    f"postgresql+psycopg2://{os.getenv('WH_USER')}:{os.getenv('WH_PASSWORD')}"
    f"@localhost:5433/{os.getenv('WH_DB')}"
)

DATA_DIR = Path("data/raw")

FILES = {
    "olist_customers_dataset.csv": "customers",
    "olist_geolocation_dataset.csv": "geolocation",
    "olist_order_items_dataset.csv": "order_items",
    "olist_order_payments_dataset.csv": "order_payments",
    "olist_order_reviews_dataset.csv": "order_reviews",
    "olist_orders_dataset.csv": "orders",
    "olist_products_dataset.csv": "products",
    "olist_sellers_dataset.csv": "sellers",
    "product_category_name_translation.csv": "product_category_translation",
}

for filename, table in FILES.items():
    df = pd.read_csv(DATA_DIR / filename, dtype=str)
    df["_loaded_at"] = pd.Timestamp.now()
    df.to_sql(table, ENGINE, schema="raw", if_exists="replace",
              index=False, chunksize=10_000, method="multi")
    print(f"{table}: {len(df)} lignes chargées")
