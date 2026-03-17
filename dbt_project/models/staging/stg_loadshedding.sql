-- models/staging/stg_loadshedding.sql
with source as (
    select * from {{ source('staging', 'stg_loadshedding') }}
),
cleaned as (
    select
        cast(date as date)                  as loadshed_date,
        cast(stage as int)                  as stage,
        cast(hours_without_power as int)    as hours_without_power,
        cast(scheduled as bit)              as is_scheduled,
        case
            when stage = 0 then 'None'
            when stage <= 2 then 'Low'
            when stage <= 4 then 'Medium'
            else 'High'
        end                                 as severity_label
    from source
    where date is not null
)
select * from cleaned
