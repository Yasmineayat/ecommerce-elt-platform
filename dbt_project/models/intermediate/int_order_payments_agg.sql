select
    order_id,
    sum(payment_value)                              as total_payment,
    count(*)                                        as payment_count,
    max(payment_installments)                       as max_installments,
    mode() within group (order by payment_type)     as main_payment_type
from {{ ref('stg_order_payments') }}
group by order_id