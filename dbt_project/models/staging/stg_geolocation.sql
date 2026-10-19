select
    geolocation_zip_code_prefix              as zip_code_prefix,
    avg(geolocation_lat::numeric)            as latitude,
    avg(geolocation_lng::numeric)            as longitude,
    max(initcap(geolocation_city))           as city,
    max(upper(geolocation_state))            as state
from {{ source('olist', 'geolocation') }}
group by geolocation_zip_code_prefix