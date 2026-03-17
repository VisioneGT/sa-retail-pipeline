-- models/marts/dim_products.sql
-- Product dimension table

with products as (
    select * from {{ ref('stg_products') }}
)

select
    product_id,
    product_name,
    category,
    unit_cost,
    unit_price,
    margin,
    margin_pct,
    case
        when margin_pct >= 40 then 'High Margin'
        when margin_pct >= 25 then 'Medium Margin'
        else 'Low Margin'
    end as margin_tier
from products
