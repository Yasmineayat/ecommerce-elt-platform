select
    i.order_item_key,
    i.order_id,
    o.customer_id               as customer_key,
    i.product_id                as product_key,
    i.seller_id                 as seller_key,
    o.purchased_at::date        as order_date_key,
    o.order_status,
    i.price,
    i.freight_value,
    i.price + i.freight_value   as total_item_value
from {{ ref('stg_order_items') }} i
join {{ ref('int_orders_enriched') }} o using (order_id)