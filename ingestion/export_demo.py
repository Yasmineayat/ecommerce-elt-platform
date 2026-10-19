import os
import duckdb

SRC = "data/warehouse.duckdb"
DST = "dashboard/demo/demo.duckdb"

os.makedirs("dashboard/demo", exist_ok=True)
if os.path.exists(DST):
    os.remove(DST)

con = duckdb.connect(DST)
con.execute(f"attach '{SRC}' as src (read_only)")
con.execute("create schema marts")

tables = [
    r[0]
    for r in con.execute(
        "select table_name from information_schema.tables "
        "where table_catalog = 'src' and table_schema = 'marts'"
    ).fetchall()
]

for t in tables:
    con.execute(f"create table marts.{t} as select * from src.marts.{t}")
    n = con.execute(f"select count(*) from marts.{t}").fetchone()[0]
    print(f"{t}: {n} lignes")

con.execute("detach src")
con.close()