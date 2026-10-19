"""Couche Bronze : ingestion brute et incrémentale (lots mensuels)."""
import argparse
from pathlib import Path

import pandas as pd
from deltalake import DeltaTable, write_deltalake

RAW = Path("data/raw")
BRONZE = Path("lake/bronze")

STATIC = {
    "olist_customers_dataset.csv": "customers",
    "olist_products_dataset.csv": "products",
    "olist_sellers_dataset.csv": "sellers",
    "product_category_name_translation.csv": "product_category_translation",
    "olist_geolocation_dataset.csv": "geolocation",
}
CHILD = {
    "olist_order_items_dataset.csv": "order_items",
    "olist_order_payments_dataset.csv": "order_payments",
    "olist_order_reviews_dataset.csv": "order_reviews",
}


def table_path(name):
    return str(BRONZE / name)


def exists(name):
    return DeltaTable.is_deltatable(table_path(name))
def add_meta(df, source, batch):
    df = df.copy().astype(str)
    df["_ingested_at"] = pd.Timestamp.now().isoformat()
    df["_source_file"] = source
    df["_batch_month"] = batch
    return df


def batch_already_loaded(batch):
    if not exists("orders"):
        return False
    b = DeltaTable(table_path("orders")).to_pandas(columns=["_batch_month"])
    return batch in set(b["_batch_month"])


def load_static():
    for fname, table in STATIC.items():
        if exists(table):
            continue
        df = pd.read_csv(RAW / fname, dtype=str)
        write_deltalake(table_path(table), add_meta(df, fname, "static"), mode="overwrite")
        print(f"[static] {table}: {len(df)} lignes")

def load_batch(batch):
    if batch_already_loaded(batch):
        print(f"[skip] lot {batch} deja charge")
        return
    orders = pd.read_csv(RAW / "olist_orders_dataset.csv", dtype=str)
    orders["_month"] = orders["order_purchase_timestamp"].str[:7]
    lot = orders[orders["_month"] == batch].drop(columns="_month")
    if lot.empty:
        print(f"[warn] aucune commande pour {batch}")
        return
    ids = set(lot["order_id"])
    for fname, table, df_all in [("olist_orders_dataset.csv", "orders", lot)] + [
        (f, t, pd.read_csv(RAW / f, dtype=str)) for f, t in CHILD.items()
    ]:
        sub = df_all if table == "orders" else df_all[df_all["order_id"].isin(ids)]
        if sub.empty:
            print(f"[batch {batch}] {table}: 0 ligne (ignore)")
            continue
        write_deltalake(table_path(table), add_meta(sub, fname, batch),
                        mode="append", schema_mode="merge")
        print(f"[batch {batch}] {table}: {len(sub)} lignes")


def available_months():
    o = pd.read_csv(RAW / "olist_orders_dataset.csv", dtype=str,
                    usecols=["order_purchase_timestamp"])
    return sorted(o["order_purchase_timestamp"].str[:7].dropna().unique())


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--month")
    p.add_argument("--next", type=int)
    p.add_argument("--list", action="store_true")
    a = p.parse_args()
    if a.list:
        print(available_months())
    else:
        load_static()
        if a.month:
            load_batch(a.month)
        elif a.next:
            todo = [m for m in available_months() if not batch_already_loaded(m)]
            for m in todo[: a.next]:
                load_batch(m)
