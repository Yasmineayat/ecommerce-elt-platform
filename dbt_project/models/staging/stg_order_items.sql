select
    order_id,
    order_item_id::int                                  as order_item_number,
    product_id,
    seller_id,
    nullif(shipping_limit_date, '')::timestamp          as shipping_limit_at,
    nullif(price, '')::numeric(10,2)                    as price,
    nullif(freight_value, '')::numeric(10,2)            as freight_value,
    {{ dbt_utils.generate_surrogate_key(['order_id', 'order_item_id']) }} as order_item_key
from {{ source('olist', 'order_items') }}