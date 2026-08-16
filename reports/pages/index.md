---
title: Overview
---

A snapshot of ratings performance for the selected season of the French TV show 👁️, filterable by channel.


```sql season_options
    select 
        distinct show_number
    from 
        tv_ratings
    order by 
        1 desc
```

<Dropdown
    name=season_filter
    data={season_options}
    value=show_number
    title="Season"
    order=show_number
/>

## Audience
Evolution of audience viewership and ratings across the season, daily and prime shows.

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

<BigValue
    data={overview_audience}
    value=viewers_daily
    title="Daily Viewers"
    <Info description="Season average — TMC for season 14, TFX for season 13"
/>

<BigValue
    data={overview_audience}
    value=ratings_daily
    title="Daily Ratings 4+"
    fmt=pct1
     <Info description="Season average — TMC for season 14, TFX for season 13"
/>

<BigValue
    data={overview_audience}
    value=viewers_prime
    title="Prime Viewers"
     <Info description="Season average — TMC for season 14, TFX for season 13"
/>

<BigValue
    data={overview_audience}
    value=ratings_prime
    title="Prime Ratings 4+"
    fmt=pct1
    <Info description="Season average — TMC for season 14, TFX for season 13"
/>

<Tabs background=true fullWidth=true color=primary>
    <Tab label="Daily"> 

    ```sql channel_listing
    select 
        distinct upper(channel_name) as channel_name
    from 
        tv_ratings
    where 
        channel_name != 'tf1'
        and show_number = '${inputs.season_filter.value}'
    order by 
        1
```

``` sql daily_weekly_audience_kpis
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
            show_type != 'prime'
            and show_number = '${inputs.season_filter.value}' 
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
        , ratings_2549
        , (ratings_2549 - lag(ratings_2549, 1) over (order by week_number)) / lag(ratings_2549, 1) over (order by week_number) as wow_pct_ratings_2549
    from 
        weekly
    order by 
        1 desc
```

<BigValue
    data={daily_weekly_audience_kpis}
    value=viewers
    title="Viewers"
    comparison=wow_pct_viewers
    comparisonFmt=pct1
    comparisonTitle="WoW"
    <Info description="Latest week average"
    emptySet=pass
    emptyMessage="Season 13 data available on TFX only"
/>

<BigValue
    data={daily_weekly_audience_kpis}
    value=ratings
    title="Ratings 4+"
    fmt=pct1
    comparison=wow_pct_ratings
    comparisonFmt=pct1
    comparisonTitle="WoW"
    <Info description="Latest week average"
    emptySet=pass
    emptyMessage="Season 13 data available on TFX only"
/>

<BigValue
    data={daily_weekly_audience_kpis}
    value=ratings_frda50
    title="Ratings FRDA50"
    fmt=pct1
    comparison=wow_pct_ratings_frda50
    comparisonFmt=pct1
    comparisonTitle="WoW"
    <Info description="Latest week average"
    emptySet=pass
    emptyMessage="Season 13 data available on TFX only"
/>

<BigValue
    data={daily_weekly_audience_kpis}
    value=ratings_2549
    title="Ratings 25-49"
    fmt=pct1
    comparison=wow_pct_ratings_2549
    comparisonFmt=pct1
    comparisonTitle="WoW"
    <Info description="Latest week average"
    emptySet=pass
    emptyMessage="Season 13 data available on TFX only"
/> 

``` sql weekly_audience_over_season
    -- Evidence shifts BigQuery DATE values back by 1 day when loading via `npm run sources` 
    -- Fix: correct the actual DATE value at the source with `+ interval 1 day`, so air_date stays a true DATE type and matches BigQuery exactly. 
    -- The function strftime() cannot work as it only reformats the value to text 

    with 
    daily_ratings as ( 
        select
            air_date
            , channel_name
            , week_number
            , sum(num_viewers) as viewers
            , sum(pct_rating_total) / 100 as ratings
        from 
            tv_ratings
        where 
            show_type != 'prime'
            and show_number = '${inputs.season_filter.value}'
        group by
            1, 2, 3
    )
    , weekly_ratings as (
        select
            distinct channel_name
            , week_number as air_date_week
            , avg(viewers) over(partition by channel_name, week_number) as viewers_channel
            , avg(ratings) over(partition by channel_name, week_number) as ratings_channel
            , avg(viewers) over(partition by week_number) as viewers
            , avg(ratings) over(partition by week_number) as ratings
        from 
            daily_ratings  
    )
    , base as (
        select 
            air_date_week
            , channel_name
            , viewers_channel
            , ratings_channel 
            , viewers
            , ratings
            , air_date_week - min(air_date_week) over () as week_num
        from 
            weekly_ratings
    )
    , regression as (
        select
            covar_pop(ratings, week_num) / nullif(var_pop(week_num), 0) as slope
            , avg(ratings) - (covar_pop(ratings, week_num) / nullif(var_pop(week_num), 0)) * avg(week_num) as intercept
        from 
            base
    )
    select
        b.*
        , r.intercept + r.slope * b.week_num as ratings_trend
    from 
        base b
    cross join 
        regression r
    order by 
        b.air_date_week
```

<BarChart
    data={weekly_audience_over_season}
    x=air_date_week
    y=viewers_channel  
    series=channel_name
    colorPalette={['#a4b8fc', '#111726ae']}
    title="Daily Audience Trend"
    subtitle="Weekdays only (Monday-Friday)"
    emptySet=pass
    emptyMessage="Season 13 data available on TFX only"
    echartsOptions={{
        series: [
            {},
            {showSymbol: true, symbol: 'emptyCircle', symbolSize: 7},
            {
                lineStyle: {type: 'dashed', width: 1.5, color: '#ffb432'},
                itemStyle: {color: '#ffb432'},
                color: '#ffb432'
            }
        ]
    }}
/>

</Tab>
<Tab label="Prime">


    ```sql channel_listing
    select 
        distinct upper(channel_name) as channel_name
    from 
        tv_ratings
    where 
        channel_name != 'tf1'
        and show_number = '${inputs.season_filter.value}'
    order by 
        1 desc
```

<Dropdown
    name=channel_filter
    data={channel_listing}
    value=channel_name
    title="Channel"
    order=true
/>

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
        weekly
    order by 
        1 desc
```

<BigValue
    data={prime_weekly_audience}
    value=viewers
    title="Viewers"
    comparison=wow_pct_viewers
    comparisonFmt=pct1
    comparisonTitle="WoW"
    emptySet=pass
    emptyMessage="Prime data available on TMC for season 14, TFX for season 13"
    <Info description="Latest week average"
/>

<BigValue
    data={prime_weekly_audience}
    value=ratings
    title="Ratings 4+"
    fmt=pct1
    comparison=wow_pct_ratings
    comparisonFmt=pct1
    comparisonTitle="WoW"
    emptySet=pass
    emptyMessage="Prime data available on TMC for season 14, TFX for season 13"
    <Info description="Latest week average"
/>

<BigValue
    data={prime_weekly_audience}
    value=ratings_frda50
    title="Ratings FRDA50"
    fmt=pct1
    comparison=wow_pct_ratings_frda50
    comparisonFmt=pct1
    comparisonTitle="WoW"
    emptySet=pass
    emptyMessage="Prime data available on TMC for season 14, TFX for season 13"
    <Info description="Latest week average"
/>

``` sql prime_audience_over_season

    -- Evidence shifts BigQuery DATE values back by 1 day when loading via `npm run sources` 
    -- Fix: correct the actual DATE value at the source with `+ interval 1 day`, so air_date stays a true DATE type and matches BigQuery exactly. 
    -- The function strftime() cannot work as it only reformats the value to text 

    with 
    daily_ratings as ( 
        select
            air_date + interval 1 day as air_date
            , round(week_number, 0) as week_number
            , concat('Prime', ' ', cast(week_number as bigint)) as week_number_label
            , avg(num_viewers) as viewers
            , avg(pct_rating_total) / 100 as ratings
        from 
            tv_ratings
        where 
            show_type = 'prime'
            and show_number = '${inputs.season_filter.value}'
            and upper(channel_name) = '${inputs.channel_filter.value}'
        group by
            1, 2, 3
    ), 
    base as (
        select 
            air_date
            , week_number
            , week_number_label
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
        b.air_date
        , b.week_number 
        , b.week_number_label
        , b.viewers
        , b.ratings
        , r.intercept + r.slope * b.day_num as ratings_trend
    from 
        base b
    cross join 
        regression r 
    order by 
        2
```

<BarChart
    data={prime_audience_over_season}
    x=week_number_label
    y=viewers
    y2={['ratings', 'ratings_trend']}
    y2Fmt=pct1
    y2SeriesType=line
    y2AxisTitle="Ratings"
    emptySet=pass
    emptyMessage="Prime data available on TMC for season 14, TFX for season 13"
    sort=false
    colorPalette={['#a4b8fc', '#111726ae']}
    title="Prime Audience Trend"
    subtitle="Average across episode (parts 1 & 2)"
    echartsOptions={{
        series: [
            {},
            {showSymbol: true, symbol: 'emptyCircle', symbolSize: 7},
            {
                lineStyle: {type: 'dashed', width: 1.5, color: '#ffb432'},
                itemStyle: {color: '#ffb432'},
                color: '#ffb432'
            }
        ]
    }}
/>

``` sql prime_audience_over_season_by_part
    
    select
        distinct week_number 
        , concat('Prime', ' ', cast(week_number as bigint)) as week_number_label
        , concat('Part', ' ', cast(show_part_number as bigint)) as show_part_number_label
        , num_viewers as viewers
        , pct_rating_total as ratings
    from 
        tv_ratings
    where 
        show_type = 'prime'
        and show_number = '${inputs.season_filter.value}'
        and upper(channel_name) = '${inputs.channel_filter.value}'
    order by 
        1, 3
```

<BarChart
    data={prime_audience_over_season_by_part}
    x=week_number_label
    y=viewers
    series=show_part_number_label
    type=grouped
    sort=false
    emptySet=pass
    emptyMessage="Prime data available on TMC for season 14, TFX for season 13"
    labels=true
    labelFmt=num0k
    colorPalette={['#a4b8fc', '#111726be']}
    title="Prime Audience Trend by Part"
    subtitle="Parts 1 vs. 2"
/>

</Tab>
</Tabs>