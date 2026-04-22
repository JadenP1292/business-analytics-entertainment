with source as (
    select * from {{ ref('stg_company_overview') }}
),

dim_company as (
    select company_key, ticker from {{ ref('dim_company') }}
),

final as (
    select
        c.company_key,
        s.ticker,
        s.updated_at::date          as snapshot_date,
        s.market_capitalization,
        s.pe_ratio,
        s.forward_pe,
        s.book_value,
        s.dividend_yield,
        s.eps,
        s.revenue_ttm,
        s.week_52_high,
        s.week_52_low,
        s.analyst_target_price,
        s.analyst_rating_buy,
        s.analyst_rating_hold,
        s.analyst_rating_sell
    from source s
    left join dim_company c on s.ticker = c.ticker
)

select * from final
