
    

    create  table
      "gold"."main"."dim_date__dbt_tmp"
  
    
    as (
      ﻿select
    d::date as date_key,
    year(d) as year,
    month(d) as month,
    monthname(d) as month_name,
    quarter(d) as quarter,
    isodow(d) as day_of_week,
    isodow(d) in (6, 7) as is_weekend
from generate_series(date '2016-01-01', date '2019-01-01', interval 1 day) as t(d)
    );
    
  