select
    p.product_id as product_key,
    coalesce(t.product_category_name_english, p.product_category_name, 'unknown') as category_name,
    p.product_weight_g as weight_g,
    p.product_length_cm * p.product_height_cm * p.product_width_cm as volume_cm3,
    p.product_photos_qty as photos_qty
from delta_scan('../../lake/silver/products') p
left join delta_scan('../../lake/silver/product_category_translation') t
    on p.product_category_name = t.product_category_name