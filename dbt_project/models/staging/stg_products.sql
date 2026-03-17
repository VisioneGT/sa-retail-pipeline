-- models/staging/stg_products.sql
with source as (
    select * from {{ source('staging', 'stg_products') }}
),
cleaned as (
    select
        upper(trim(product_id))                         as product_id,
        trim(name)                                      as product_name,
        trim(category)                                  as category,
        cast(cost  as decimal(10,2))                    as unit_cost,
        cast(price as decimal(10,2))                    as unit_price,
        cast(price - cost as decimal(10,2))             as margin,
        cast((price - cost) / nullif(price,0) * 100
             as decimal(5,2))                           as margin_pct
    from source
    where product_id is not null
)
select * from cleaned
