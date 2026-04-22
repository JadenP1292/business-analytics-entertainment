with source as (
    select * from {{ source('raw', 'company_overview') }}
),

renamed as (
    select
        ticker::varchar                       as ticker,
        company_name::varchar                 as company_name,
        sector::varchar                       as sector,
        industry::varchar                     as industry,
        country::varchar                      as country,
        currency::varchar                     as currency,
        exchange::varchar                     as exchange,
        market_capitalization::bigint         as market_capitalization,
        pe_ratio::float                       as pe_ratio,
        forward_pe::float                     as forward_pe,
        book_value::float                     as book_value,
        dividend_yield::float                 as dividend_yield,
        eps::float                            as eps,
        revenue_ttm::bigint                   as revenue_ttm,
        week_52_high::float                   as week_52_high,
        week_52_low::float                    as week_52_low,
        analyst_target_price::float           as analyst_target_price,
        analyst_rating_buy::int               as analyst_rating_buy,
        analyst_rating_hold::int              as analyst_rating_hold,
        analyst_rating_sell::int              as analyst_rating_sell,
        updated_at::timestamp                 as updated_at
    from source
    where ticker is not null
)

select * from renamed
