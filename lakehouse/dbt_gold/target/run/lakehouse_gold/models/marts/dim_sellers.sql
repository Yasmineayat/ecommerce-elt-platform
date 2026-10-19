
    

    create  table
      "gold"."main"."dim_sellers__dbt_tmp"
  
    
    as (
      ﻿select
    seller_id as seller_key,
    seller_zip_code_prefix as zip_code_prefix,
    upper(left(seller_city, 1)) || lower(substr(seller_city, 2)) as city,
    upper(seller_state) as state
from delta_scan('../../lake/silver/sellers')
    );
    
  