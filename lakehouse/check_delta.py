import duckdb

c = duckdb.connect()
c.execute("install delta")
c.execute("load delta")
print(c.execute("select count(*) from delta_scan('lake/silver/orders')").fetchone())