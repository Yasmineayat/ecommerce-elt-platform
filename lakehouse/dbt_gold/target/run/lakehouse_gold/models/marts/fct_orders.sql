
    

    create  table
      "gold"."main"."fct_orders__dbt_tmp"
  
    
    as (
      ﻿with payments as (
    select order_id, sum(payment_value) as total_payment, mode(payment_type) as main_payment_type
    from delta_scan('../../lake/silver/order_payments')
    group by order_id
),
reviews as (
    select order_id, avg(review_score) as review_score
    from delta_scan('../../lake/silver/order_reviews')
    group by order_id
)
select
    o.order_id,
    o.customer_id as customer_key,
    o.order_purchase_timestamp::date as order_date_key,
    o.order_status,
    p.total_payment,
    p.main_payment_type,
    r.review_score,
    date_diff('day', o.order_purchase_timestamp, o.order_delivered_customer_date) as delivery_days,
    (o.order_delivered_customer_date > o.order_estimated_delivery_date) as is_late
from delta_scan('../../lake/silver/orders') o
left join payments p using (order_id)
left join reviews r using (order_id)
    );
    
  