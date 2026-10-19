select
    p.product_id,
    p.product_category_name                              as category_name_pt,
    coalesce(t.product_category_name_english,
             p.product_category_name, 'unknown')         as category_name,
    nullif(p.product_name_lenght, '')::int               as name_length,
    nullif(p.product_description_lenght, '')::int        as description_length,
    nullif(p.product_photos_qty, '')::int                as photos_qty,
    nullif(p.product_weight_g, '')::numeric              as weight_g,
    nullif(p.product_length_cm, '')::numeric             as length_cm,
    nullif(p.product_height_cm, '')::numeric             as height_cm,
    nullif(p.product_width_cm, '')::numeric              as width_cm
from {{ source('olist', 'products') }} p
left join {{ source('olist', 'product_category_translation') }} t
    on p.product_category_name = t.product_category_name