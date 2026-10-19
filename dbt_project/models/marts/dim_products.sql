select
    product_id   as product_key,
    category_name,
    weight_g,
    length_cm * height_cm * width_cm   as volume_cm3,
    photos_qty
from {{ ref('stg_products') }}