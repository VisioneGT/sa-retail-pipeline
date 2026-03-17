-- models/staging/stg_sales.sql
-- Cleans and casts the raw sales staging table

with source as (
    select * from {{ source('staging', 'stg_sales') }}
),

cleaned as (
    select
        sale_id                                         as sale_id,
        cast(date as date)                              as sale_date,
        upper(trim(store_id))                           as store_id,
        upper(trim(product_id))                         as product_id,
        cast(quantity as int)                           as quantity,
        cast(unit_price as decimal(10,2))               as unit_price,
        cast(unit_cost  as decimal(10,2))               as unit_cost,
        cast(revenue    as decimal(10,2))               as revenue,
        cast(cogs       as decimal(10,2))               as cogs,
        cast(revenue - cogs as decimal(10,2))           as gross_profit,
        cast(_loaded_at as datetime)                    as loaded_at
    from source
    where sale_id is not null
      and date   is not null
      and quantity > 0
      and revenue  > 0
)

select * from cleaned
