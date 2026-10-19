import duckdb

con = duckdb.connect("data/warehouse.duckdb")
for s in ["raw", "staging", "intermediate", "marts"]:
    con.execute(f"create schema if not exists {s}")

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

for f, t in FILES.items():
    con.execute(f"""
        create or replace table raw.{t} as
        select *, now() as _loaded_at
        from read_csv('data/raw/{f}', all_varchar=true)
    """)
    n = con.execute(f"select count(*) from raw.{t}").fetchone()[0]
    print(f"{t}: {n} lignes chargées")

con.close()