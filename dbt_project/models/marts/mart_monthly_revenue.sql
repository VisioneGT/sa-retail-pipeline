-- models/marts/mart_monthly_revenue.sql
-- Monthly revenue aggregated with loadshedding averages
-- Primary table that Power BI / analysis connects to
-- DuckDB compatible syntax

with fact as (
    select * from {{ ref('fact_sales') }}
),

monthly as (
    select
        sale_year,
        sale_month,
        sale_month_name,
        store_id,

        -- Revenue metrics
        count(distinct sale_id)                             as total_transactions,
        sum(quantity)                                       as total_units_sold,
        round(sum(revenue), 2)                              as total_revenue,
        round(sum(cogs), 2)                                 as total_cogs,
        round(sum(gross_profit), 2)                         as total_gross_profit,
        round(
            sum(gross_profit) / nullif(sum(revenue), 0) * 100
        , 2)                                                as gross_margin_pct,

        -- Loadshedding metrics
        round(avg(loadshed_stage::float), 2)                as avg_loadshed_stage,
        sum(loadshed_hours)                                 as total_loadshed_hours,
        sum(was_loadshedding::int)                          as days_with_loadshedding,

        -- Weekend vs weekday split
        round(sum(case when is_weekend = 1
                       then revenue else 0 end), 2)         as weekend_revenue,
        round(sum(case when is_weekend = 0
                       then revenue else 0 end), 2)         as weekday_revenue

    from fact
    group by
        sale_year,
        sale_month,
        sale_month_name,
        store_id
)

select * from monthly
order by sale_year, sale_month, store_id
