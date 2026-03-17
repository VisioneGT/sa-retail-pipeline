-- models/marts/fact_sales.sql
-- Central fact table joining sales with loadshedding context
-- DuckDB compatible syntax

with sales as (
    select * from {{ ref('stg_sales') }}
),

loadshedding as (
    select * from {{ ref('stg_loadshedding') }}
),

final as (
    select
        s.sale_id,
        s.sale_date,
        s.store_id,
        s.product_id,
        s.quantity,
        s.unit_price,
        s.unit_cost,
        s.revenue,
        s.cogs,
        s.gross_profit,

        -- Loadshedding context on sale date
        coalesce(l.stage, 0)                        as loadshed_stage,
        coalesce(l.hours_without_power, 0)           as loadshed_hours,
        coalesce(l.is_scheduled::boolean, false)     as was_loadshedding,
        coalesce(l.severity_label, 'None')           as loadshed_severity,

        -- Date dimensions (DuckDB syntax)
        year(s.sale_date::date)                      as sale_year,
        month(s.sale_date::date)                     as sale_month,
        strftime(s.sale_date::date, '%B')            as sale_month_name,
        strftime(s.sale_date::date, '%A')            as sale_day_of_week,
        case when dayofweek(s.sale_date::date)
                  in (0, 6) then 1 else 0
        end                                          as is_weekend

    from sales s
    left join loadshedding l
        on s.sale_date = l.loadshed_date
)

select * from final
