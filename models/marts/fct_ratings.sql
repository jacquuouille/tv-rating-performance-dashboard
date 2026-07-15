{{ config(
    materialized='incremental',
    unique_key='rating_id'
) }}

with source as (

    select *
    from {{ ref('stg_ratings') }}

    {% if is_incremental() %}
        where air_date >= (
            select date_sub(max(air_date), interval 7 day)
            from {{ this }}
        )
    {% endif %}

)

select
    rating_id,
    show_id,
    show_name,
    show_number as season_number,
    week_number,
    air_date,
    channel_name,
    show_type,
    show_part_number,
    num_viewers,
    pct_rating_total,
    pct_rating_frda50,
    pct_rating_2549,
    pct_rating_1524,
    pct_rating_1534

from source