select
    order_id,
    customer_id             as customer_key,
    purchased_at::date      as order_date_key,
    order_status,
    total_payment,
    main_payment_type,
    review_score,
    delivery_days,
    is_late
from {{ ref('int_orders_enriched') }}