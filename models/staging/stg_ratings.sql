with source as (

    select * from {{ source('tv_analytics', 'ratings') }}

),

renamed as (

    select

        {{ dbt_utils.generate_surrogate_key(['show_id','date','show_type','show_part']) }} as rating_id,
        show_id,
        show_name,
        show_season as show_number,
        show_week as week_number,
        date as air_date,
        lower(channel) as channel_name,
        lower(show_type) as show_type,
        show_part as show_part_number,
        views as num_viewers,
        ratings as pct_rating_total,
        ratings_frda50 as pct_rating_frda50,
        rating_2549 as pct_rating_2549,
        ratings_1524 as pct_rating_1524,
        ratings1534 as pct_rating_1534

    from source

)

select * from renamed