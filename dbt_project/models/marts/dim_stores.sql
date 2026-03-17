-- models/marts/dim_stores.sql
-- Store dimension table

with stores as (
    select * from {{ ref('stg_stores') }}
)

select
    store_id,
    store_name,
    city,
    province,
    case province
        when 'Gauteng'       then 'North'
        when 'Limpopo'       then 'North'
        when 'Mpumalanga'    then 'North'
        when 'North West'    then 'North'
        when 'Western Cape'  then 'South'
        when 'Eastern Cape'  then 'South'
        when 'Northern Cape' then 'South'
        when 'KwaZulu-Natal' then 'East'
        when 'Free State'    then 'Central'
        else 'Unknown'
    end as region
from stores
