---
title: Overview
---

A snapshot of the ratings performance of the selected season of Secret Story.

```sql season_options
    select 
        distinct show_number
    from 
        tv_ratings
    order by 
        1
```

<Dropdown
    name=season_filter
    data={season_options}
    value=show_number
    title="Season"
/>

## Audience
Tracks the evolution of audience viewership and ratings over the course of the season, giving an immediate read on how it is performing.


``` sql audience_over_season
    with 
    daily_ratings as ( 
        select
            air_date,
            sum(num_viewers) as viewers,
            sum(pct_rating_total) / 100 as ratings
        from 
            tv_ratings
        where 
            show_type != 'prime'
            and show_number = '${inputs.season_filter.value}'
        group by
            1
    ), 
    base as (
        select 
            air_date
            , viewers
            , ratings 
            , date_diff('day', min(air_date) over (), air_date) as day_num
        from 
            daily_ratings
    )
    , regression as (
        select
            covar_pop(ratings, day_num) / nullif(var_pop(day_num), 0) as slope
            , avg(ratings) - (covar_pop(ratings, day_num) / nullif(var_pop(day_num), 0)) * avg(day_num) as intercept
        from 
            base
    )
    select
        b.air_date,
        b.viewers,
        b.ratings,
        r.intercept + r.slope * b.day_num as ratings_trend
    from 
        base b
    cross join 
        regression r
    order by 
        b.air_date
```

<BarChart
    data={audience_over_season}
    x=air_date
    y=viewers
    y2={['ratings', 'ratings_trend']}
    y2Fmt=pct1
    y2SeriesType=line
    colorPalette={['#a4b8fc', '#111726be']}
    chartAreaHeight=200
    title="Daily Audience Trend"
    subtitle="Weekdays only (Monday-Friday)"
    echartsOptions={{
        series: [
            {},
            {showSymbol: true, symbol: 'emptyCircle', symbolSize: 7}
        ]
    }}
/>