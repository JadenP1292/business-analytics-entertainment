with source as (
    select * from {{ source('raw', 'stock_prices_daily') }}
),

renamed as (
    select
        trade_date::date          as trade_date,
        ticker::varchar           as ticker,
        open_price::float         as open_price,
        high_price::float         as high_price,
        low_price::float          as low_price,
        close_price::float        as close_price,
        volume::bigint            as volume,
        extracted_at::timestamp   as extracted_at
    from source
    where close_price is not null
      and ticker is not null
)

select * from renamed
