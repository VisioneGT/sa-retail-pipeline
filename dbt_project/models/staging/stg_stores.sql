-- models/staging/stg_stores.sql
with source as (
    select * from {{ source('staging', 'stg_stores') }}
),
cleaned as (
    select
        upper(trim(store_id))   as store_id,
        trim(name)              as store_name,
        trim(city)              as city,
        trim(province)          as province
    from source
    where store_id is not null
)
select * from cleaned
