import duckdb
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="E-commerce Overview", layout="wide")
st.title("E-commerce Overview (Olist)")

con = duckdb.connect("data/warehouse.duckdb", read_only=True)

kpi = con.execute("""
    select count(*), round(sum(total_payment)), round(avg(review_score), 2)
    from marts.fct_orders where order_status <> 'canceled'
""").fetchone()
c1, c2, c3 = st.columns(3)
c1.metric("Commandes", f"{kpi[0]:,}")
c2.metric("Chiffre d'affaires", f"{kpi[1]:,.0f} R$")
c3.metric("Note moyenne", kpi[2])

ca = con.execute("""
    select make_date(d.year, d.month, 1) as mois, round(sum(o.total_payment)) as ca
    from marts.fct_orders o join marts.dim_date d on o.order_date_key = d.date_key
where o.order_status <> 'canceled'
  and d.date_key >= date '2017-01-01'
  and d.date_key <  date '2018-09-01'  
  group by 1 order by 1
""").df()
st.plotly_chart(px.line(ca, x="mois", y="ca", title="CA mensuel"), use_container_width=True)

cat = con.execute("""
    select p.category_name, round(sum(i.price)) as ca
    from marts.fct_order_items i join marts.dim_products p on i.product_key = p.product_key
    where i.order_status <> 'canceled'
    group by 1 order by 2 desc limit 10
""").df()
st.plotly_chart(px.bar(cat, x="ca", y="category_name", orientation="h",
                       title="Top 10 catégories"), use_container_width=True)

late = con.execute("""
    select c.state, round(100.0 * avg(case when o.is_late then 1 else 0 end), 1) as pct_retard
    from marts.fct_orders o join marts.dim_customers c on o.customer_key = c.customer_key
    where o.order_status = 'delivered'
    group by 1 having count(*) > 100 order by 2 desc
""").df()
st.plotly_chart(px.bar(late, x="state", y="pct_retard",
                       title="% de livraisons en retard par État"), use_container_width=True)