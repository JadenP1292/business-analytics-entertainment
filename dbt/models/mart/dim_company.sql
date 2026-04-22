with source as (
    select * from {{ ref('stg_company_overview') }}
),

final as (
    select
        row_number() over (order by ticker)  as company_key,
        ticker,
        company_name,
        sector,
        industry,
        country,
        currency,
        exchange
    from source
)

select * from final
