select
    o.order_id,
    o.customer_id,
    o.order_status,
    o.purchased_at,
    o.delivered_at,
    o.estimated_delivery_at,
    p.total_payment,
    p.main_payment_type,
    r.review_score,
    extract(day from (o.delivered_at - o.purchased_at))   as delivery_days,
    (o.delivered_at > o.estimated_delivery_at)            as is_late
from {{ ref('stg_orders') }} o
left join {{ ref('int_order_payments_agg') }} p using (order_id)
left join (
    select order_id, avg(review_score) as review_score
    from {{ ref('stg_order_reviews') }}
    group by order_id
) r using (order_id)