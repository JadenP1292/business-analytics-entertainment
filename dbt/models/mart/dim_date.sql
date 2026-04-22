with date_spine as (
    select
        dateadd(day, seq4(), '2025-01-01'::date) as full_date
    from table(generator(rowcount => 731))
)

select
    to_number(to_char(full_date, 'YYYYMMDD'))                          as date_key,
    full_date,
    dayofweek(full_date)                                               as day_of_week,
    dayname(full_date)                                                 as day_name,
    weekofyear(full_date)                                              as week_of_year,
    month(full_date)                                                   as month,
    monthname(full_date)                                               as month_name,
    quarter(full_date)                                                 as quarter,
    year(full_date)                                                    as year,
    case when dayofweek(full_date) in (0, 6) then true else false end  as is_weekend
from date_spine
