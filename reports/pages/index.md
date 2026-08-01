---
title: Overview
---

A snapshot of the ratings performance of the selected season of Secret Story, filtered by channel.


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

<Dropdown
    name=channel_filter
    data={channel_listing}
    value=channel_name
    title="Channel"
/>

<Tabs background=true fullWidth=true color=primary>
    <Tab label="Daily"> 

``` sql daily_weekly_audience
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
        , ratings_2549
        , (ratings_2549 - lag(ratings_2549, 1) over (order by week_number)) / lag(ratings_2549, 1) over (order by week_number) as wow_pct_ratings_2549
    from 
        weekly
    order by 
        1 desc
```

<BigValue
    data={daily_weekly_audience}
    value=viewers
    title="Viewers"
    comparison=wow_pct_viewers
    comparisonFmt=pct1
    comparisonTitle="WoW"
    <Info description="Latest week average"
/>

<BigValue
    data={daily_weekly_audience}
    value=ratings
    title="Ratings 4+"
    fmt=pct1
    comparison=wow_pct_ratings
    comparisonFmt=pct1
    comparisonTitle="WoW"
    <Info description="Latest week average"
/>

<BigValue
    data={daily_weekly_audience}
    value=ratings_frda50
    title="Ratings FRDA50"
    fmt=pct1
    comparison=wow_pct_ratings_frda50
    comparisonFmt=pct1
    comparisonTitle="WoW"
    <Info description="Latest week average"
/>

<BigValue
    data={daily_weekly_audience}
    value=ratings_2549
    title="Ratings 25-49"
    fmt=pct1
    comparison=wow_pct_ratings_2549
    comparisonFmt=pct1
    comparisonTitle="WoW"
    <Info description="Latest week average"
/> 

``` sql daily_audience_over_season

    -- Evidence shifts BigQuery DATE values back by 1 day when loading via `npm run sources` 
    -- Fix: correct the actual DATE value at the source with `+ interval 1 day`, so air_date stays a true DATE type and matches BigQuery exactly. 
    -- The function strftime() cannot work as it only reformats the value to text 

    with 
    daily_ratings as ( 
        select
            air_date + interval 1 day as air_date, 
            sum(num_viewers) as viewers,
            sum(pct_rating_total) / 100 as ratings
        from 
            tv_ratings
        where 
            show_type != 'prime'
            and show_number = '${inputs.season_filter.value}'
            and upper(channel_name) = '${inputs.channel_filter.value}'
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
    data={daily_audience_over_season}
    x=air_date
    y=viewers
    y2={['ratings', 'ratings_trend']}
    y2Fmt=pct1
    y2SeriesType=line
    y2AxisTitle="Ratings"
    colorPalette={['#a4b8fc', '#111726ae']}
    chartAreaHeight=200
    title="Daily Audience Trend"
    subtitle="Weekdays only (Monday-Friday)"
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
    emptyMessage="No prime data for this channel"
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
    emptyMessage="No prime data for this channel"
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
    emptyMessage="No prime data for this channel"
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
    emptyMessage="No prime data for this channel"
    sort=false
    colorPalette={['#a4b8fc', '#111726ae']}
    chartAreaHeight=200
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
    chartAreaHeight=200
    emptySet=pass
    emptyMessage="No prime data for this channel"
    labels=true
    labelFmt=num0k
    colorPalette={['#a4b8fc', '#111726be']}
    title="Prime Audience Trend by Part"
    subtitle="Parts 1 vs. 2"
/>

</Tab>
</Tabs>