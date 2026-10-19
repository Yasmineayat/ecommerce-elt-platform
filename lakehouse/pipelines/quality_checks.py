"""Controles de qualite entre les couches. Code de sortie 1 si un controle echoue."""
import sys
import duckdb
from deltalake import DeltaTable

def n(path):
    return len(DeltaTable(path).to_pandas(columns=[DeltaTable(path).schema().to_arrow().names[0]]))

results = []

def check(name, ok, detail=""):
    results.append(ok)
    print(("PASS" if ok else "FAIL"), name, detail)

# Reconciliation Bronze -> Silver (rejets + doublons expliques)
for t in ["orders", "customers", "products", "sellers"]:
    b, s = n(f"lake/bronze/{t}"), n(f"lake/silver/{t}")
    check(f"bronze=silver {t}", b == s, f"({b} vs {s})")

# Silver -> Gold
con = duckdb.connect("lake/gold/gold.duckdb", read_only=True)
silver_orders = n("lake/silver/orders")
gold_orders = con.execute("select count(*) from fct_orders").fetchone()[0]
check("silver=gold orders", silver_orders == gold_orders, f"({silver_orders} vs {gold_orders})")

# Regles metier sur Gold
neg = con.execute("select count(*) from fct_order_items where price < 0").fetchone()[0]
check("aucun prix negatif en gold", neg == 0, f"({neg})")
orphans = con.execute("""select count(*) from fct_order_items i
    left join dim_products p on i.product_key = p.product_key
    where p.product_key is null""").fetchone()[0]
check("pas d'article orphelin", orphans == 0, f"({orphans})")

sys.exit(0 if all(results) else 1)