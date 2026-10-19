select
    customer_id   as customer_key,
    customer_unique_id,
    zip_code_prefix,
    city,
    state
from {{ ref('stg_customers') }}