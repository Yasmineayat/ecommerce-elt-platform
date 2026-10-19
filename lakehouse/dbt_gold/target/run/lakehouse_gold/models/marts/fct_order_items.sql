
    

    create  table
      "gold"."main"."fct_order_items__dbt_tmp"
  
    
    as (
      ﻿select
    i.order_id || '-' || i.order_item_id as order_item_key,
    i.order_id,
    o.customer_id as customer_key,
    i.product_id as product_key,
    i.seller_id as seller_key,
    o.order_purchase_timestamp::date as order_date_key,
    o.order_status,
    i.price,
    i.freight_value,
    i.price + i.freight_value as total_item_value
from delta_scan('../../lake/silver/order_items') i
join delta_scan('../../lake/silver/orders') o using (order_id)
    );
    
  