"""Couche Silver : typage, dedoublonnage, MERGE, table de rejets."""
import json
from pathlib import Path

import pandas as pd
import pyarrow as pa
from deltalake import DeltaTable, write_deltalake

BRONZE = Path("lake/bronze")
SILVER = Path("lake/silver")

NULL = lambda d, c: d[c].isna()

CONFIG = {
    "orders": dict(
        key=["order_id"],
        ts=["order_purchase_timestamp", "order_approved_at",
            "order_delivered_carrier_date", "order_delivered_customer_date",
            "order_estimated_delivery_date"],
        num={},
        rules=[
            ("order_id_null", lambda d: NULL(d, "order_id")),
            ("customer_id_null", lambda d: NULL(d, "customer_id")),
            ("purchase_date_invalid", lambda d: NULL(d, "order_purchase_timestamp")),
        ],
    ),
    "order_items": dict(
        key=["order_id", "order_item_id"],
        ts=["shipping_limit_date"],
        num={"order_item_id": "int", "price": "float", "freight_value": "float"},
        rules=[
            ("order_id_null", lambda d: NULL(d, "order_id")),
            ("price_invalid", lambda d: d["price"].isna() | (d["price"] < 0)),
            ("freight_invalid", lambda d: d["freight_value"] < 0),
        ],
    ),
    "order_payments": dict(
        key=["order_id", "payment_sequential"],
        ts=[],
        num={"payment_sequential": "int", "payment_installments": "int",
             "payment_value": "float"},
        rules=[
            ("order_id_null", lambda d: NULL(d, "order_id")),
            ("payment_invalid", lambda d: d["payment_value"].isna() | (d["payment_value"] < 0)),
        ],
    ),
    "order_reviews": dict(
        key=["review_id", "order_id"],
        ts=["review_creation_date", "review_answer_timestamp"],
        num={"review_score": "int"},
        rules=[
            ("review_id_null", lambda d: NULL(d, "review_id")),
            ("score_out_of_range",
             lambda d: ~d["review_score"].between(1, 5).fillna(False).astype(bool)),
        ],
    ),
    "customers": dict(
        key=["customer_id"], ts=[], num={},
        rules=[("customer_id_null", lambda d: NULL(d, "customer_id"))],
    ),
    "products": dict(
        key=["product_id"], ts=[],
        num={"product_name_lenght": "int", "product_description_lenght": "int",
             "product_photos_qty": "int", "product_weight_g": "float",
             "product_length_cm": "float", "product_height_cm": "float",
             "product_width_cm": "float"},
        rules=[("product_id_null", lambda d: NULL(d, "product_id"))],
    ),
    "sellers": dict(
        key=["seller_id"], ts=[], num={},
        rules=[("seller_id_null", lambda d: NULL(d, "seller_id"))],
    ),
    "product_category_translation": dict(
        key=["product_category_name"], ts=[], num={},
        rules=[("category_null", lambda d: NULL(d, "product_category_name"))],
    ),
}


def upsert(name, df, key):
    path = str(SILVER / name)
    if not DeltaTable.is_deltatable(path):
        write_deltalake(path, df, mode="overwrite")
        return "create", len(df)
    pred = " AND ".join(f"t.{k} = s.{k}" for k in key)
    res = (DeltaTable(path)
           .merge(source=pa.Table.from_pandas(df, preserve_index=False),
                  predicate=pred, source_alias="s", target_alias="t")
           .when_matched_update_all()
           .when_not_matched_insert_all()
           .execute())
    return "merge", res


def write_rejects(name, bad, reasons):
    path = str(SILVER / "_rejects")
    if DeltaTable.is_deltatable(path):
        DeltaTable(path).delete(f"_table = '{name}'")
    if bad.empty:
        return
    rej = pd.DataFrame({
        "_table": name,
        "_reason": reasons[bad.index].astype(str).values,
        "_rejected_at": pd.Timestamp.now().isoformat(),
        "_payload": [json.dumps(r, default=str) for r in bad.astype(str).to_dict("records")],
    })
    write_deltalake(path, rej, mode="append")


def build(name, cfg):
    df = DeltaTable(str(BRONZE / name)).to_pandas()
    df = df.replace({"nan": None, "": None})
    n_bronze = len(df)

    df = df.sort_values("_ingested_at").drop_duplicates(cfg["key"], keep="last")
    n_dedup = len(df)

    for c in cfg["ts"]:
        df[c] = pd.to_datetime(df[c], errors="coerce").astype("datetime64[us]")
    for c, t in cfg["num"].items():
        df[c] = pd.to_numeric(df[c], errors="coerce")
        if t == "int":
            df[c] = df[c].astype("Int64")

    reasons = pd.Series("", index=df.index)
    for reason, rule in cfg["rules"]:
        m = rule(df).fillna(False).astype(bool)
        reasons = reasons.where(~m | (reasons != ""), reason)
    is_bad = reasons != ""

    write_rejects(name, df[is_bad], reasons)
    good = df[~is_bad].drop(columns=["_batch_month"])
    mode, info = upsert(name, good, cfg["key"])
    print(f"{name:32} bronze={n_bronze:>7} dedup={n_dedup:>7} "
          f"rejets={int(is_bad.sum()):>5} silver<-{len(good):>7} ({mode})")


if __name__ == "__main__":
    SILVER.mkdir(parents=True, exist_ok=True)
    for table, config in CONFIG.items():
        build(table, config)