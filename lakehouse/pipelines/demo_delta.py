"""Demo des fonctions Delta Lake : time travel, schema evolution, optimize, vacuum."""
import pandas as pd
import pyarrow as pa
from deltalake import DeltaTable, write_deltalake

PATH = "lake/silver/orders"
dt = DeltaTable(PATH)

# 1. Historique des versions
print("=== HISTORIQUE ===")
for h in dt.history()[:5]:
    print(h.get("version"), h.get("operation"), h.get("timestamp"))

# 2. Time travel : relire la version 0
print("\n=== TIME TRAVEL ===")
v0 = DeltaTable(PATH, version=0).to_pandas()
print("version 0 :", len(v0), "lignes")
print("version courante :", len(DeltaTable(PATH).to_pandas()), "lignes")

# 3. Modification volontaire puis retour en arriere
print("\n=== MODIFICATION PUIS RESTORE ===")
dt = DeltaTable(PATH)
n_before = dt.version()
dt.update(updates={"order_status": "'DEMO'"}, predicate="order_status = 'delivered'")
dt = DeltaTable(PATH)
print("apres update :", dt.to_pandas()["order_status"].value_counts().head(3).to_dict())
dt.restore(n_before)
dt = DeltaTable(PATH)
print("apres restore :", dt.to_pandas()["order_status"].value_counts().head(3).to_dict())

# 4. Schema evolution : ajout d'une colonne
print("\n=== SCHEMA EVOLUTION ===")
sample = DeltaTable(PATH).to_pandas().head(5).copy()
sample["demo_flag"] = "x"
write_deltalake(PATH, sample, mode="append", schema_mode="merge")
cols = DeltaTable(PATH).to_pandas().columns.tolist()
print("colonne demo_flag presente :", "demo_flag" in cols)

# 5. Compaction et nettoyage
print("\n=== OPTIMIZE / VACUUM ===")
dt = DeltaTable(PATH)
print("fichiers avant :", len(dt.file_uris()))
dt.optimize.compact()
dt = DeltaTable(PATH)
print("fichiers apres compact :", len(dt.file_uris()))
print("fichiers supprimables :", len(dt.vacuum(retention_hours=168, dry_run=True)))