"""Injecte de mauvaises lignes dans Bronze et verifie que Silver les rejette."""
import pandas as pd
from deltalake import DeltaTable, write_deltalake

BAD_ITEMS = pd.DataFrame({
    "order_id": ["BAD_1", "BAD_2", "BAD_3"],
    "order_item_id": ["1", "1", "1"],
    "product_id": ["p", "p", "p"],
    "seller_id": ["s", "s", "s"],
    "shipping_limit_date": ["2018-01-01 00:00:00"] * 3,
    "price": ["-10.0", "abc", "25.0"],       # negatif, non numerique, valide
    "freight_value": ["1.0", "1.0", "1.0"],
    "_ingested_at": [pd.Timestamp.now().isoformat()] * 3,
    "_source_file": ["test_injection"] * 3,
    "_batch_month": ["test"] * 3,
})

write_deltalake("lake/bronze/order_items", BAD_ITEMS, mode="append", schema_mode="merge")
print("3 lignes injectees dans bronze/order_items (2 invalides, 1 valide)")