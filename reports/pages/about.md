--- 
title: About (𝒊)
sidebar_position: 6
---

Overview page: It is designed as the entry point of the dashboard, giving stakeholders an immediate read on how the show is performing before drilling into more detailed pages (daily episodes, prime, audience segments).
It answers the first question any stakeholder asks: how is this season doing overall? — before drilling into episode-level detail, timeslot comparisons, or audience segments on subsequent pages. TEST

``` sql overview_audience 
        select
            coalesce(
                avg(case when channel_name = 'tmc' and show_type = 'daily' then num_viewers else null end)
                , avg(case when channel_name = 'tfx' and show_type = 'daily' then num_viewers else null end)
            ) as viewers_daily
            , coalesce(
                avg(case when channel_name = 'tmc' and show_type = 'daily' then pct_rating_total else null end) / 100
                , avg(case when channel_name = 'tfx' and show_type = 'daily' then pct_rating_total else null end) / 100
            ) as ratings_daily
            , coalesce(
                avg(case when channel_name = 'tmc' and show_type = 'prime' then num_viewers else null end)
                , avg(case when channel_name = 'tfx' and show_type = 'prime' then num_viewers else null end) 
            ) as viewers_prime
            , coalesce(
                avg(case when channel_name = 'tmc' and show_type = 'prime' then pct_rating_total else null end) / 100
                , avg(case when channel_name = 'tfx' and show_type = 'prime' then pct_rating_total else null end) / 100 
            ) as ratings_prime
        from 
            tv_ratings
        where
            show_number = '${inputs.season_filter.value}' 
```

``` sql prime_weekly_audience
    with 
    weekly as (
        select
            week_number
            , avg(num_viewers) as viewers
            , avg(pct_rating_total) / 100 as ratings
            , avg(pct_rating_frda50) / 100 as ratings_frda50
            , avg(pct_rating_2549) / 100 as ratings_2549
        from 
            tv_ratings
        where
            show_type = 'prime'
            and show_number = '${inputs.season_filter.value}'
            and upper(channel_name) = '${inputs.channel_filter.value}'
        group by 
            1
    )

    select 
        week_number
        , viewers 
        , (viewers - lag(viewers, 1) over (order by week_number)) / lag(viewers, 1) over (order by week_number) as wow_pct_viewers
        , ratings
        , (ratings - lag(ratings, 1) over (order by week_number)) / lag(ratings, 1) over (order by week_number) as wow_pct_ratings
        , ratings_frda50
        , (ratings_frda50 - lag(ratings_frda50, 1) over (order by week_number)) / lag(ratings_frda50, 1) over (order by week_number) as wow_pct_ratings_frda50
    from 
        weekly)
    order by 
        1 desc
```

