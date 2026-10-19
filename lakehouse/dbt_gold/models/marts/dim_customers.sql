select
    customer_id as customer_key,
    customer_unique_id,
    customer_zip_code_prefix as zip_code_prefix,
    upper(left(customer_city, 1)) || lower(substr(customer_city, 2)) as city,
    upper(customer_state) as state
from {{ silver('customers') }}
