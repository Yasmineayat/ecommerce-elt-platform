with dates as (
    select unnest(generate_series(date '2016-01-01', date '2018-12-31', interval 1 day))::date as date_key
)
select
    date_key,
    year(date_key)  as year,
    month(date_key) as month,
    dayofweek(date_key) as day_of_week
from dates