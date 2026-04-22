with prices as (
    select * from {{ ref('stg_stock_prices') }}
),

dim_company as (
    select company_key, ticker from {{ ref('dim_company') }}
),

final as (
    select
        c.company_key,
        p.ticker,
        p.trade_date,
        p.open_price,
        p.high_price,
        p.low_price,
        p.close_price,
        p.volume,
        p.extracted_at
    from prices p
    left join dim_company c on p.ticker = c.ticker
)

select * from final
