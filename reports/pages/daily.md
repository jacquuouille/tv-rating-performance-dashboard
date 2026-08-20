---
title: Daily
sidebar_position: 2
---

A snapshot of daily ratings performance for the selected season of the French TV show 👁️, with performance filterable by channel.

```sql season_listing
    select 
        distinct show_number
    from 
        tv_ratings
    order by 
        1 desc
```

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

```sql week_number_listing
    select 
        distinct week_number
    from 
        tv_ratings
    where 
        show_number = '${inputs.season_filter.value}'
    order by 
        1
```

<Dropdown
    name=season_filter
    data={season_listing}
    value=show_number
    title="Season"
/>

<Dropdown
    name=channel_filter
    data={channel_listing}
    value=channel_name
    title="Channel"
    order=channel_name
/> 

<Dropdown
    name=week_filter
    data={week_number_listing}
    value=week_number
    title="Week"
    order=week_number 
    sort=true
    multiple=true
    selectAllByDefault=true
/> 

``` sql weekly_audience_kpis
    with 
    weekly as (
        select
            week_number
            , ceil(
                    coalesce(
                    avg(case when channel_name = 'tmc' and show_type = 'daily' then num_viewers else null end)
                    , avg(case when channel_name = 'tfx' and show_type = 'daily' then num_viewers else null end)
                    ) / 100
                ) * 100 as viewers
            , coalesce(
                    avg(case when channel_name = 'tmc' and show_type = 'daily' then pct_rating_total else null end) / 100
                    , avg(case when channel_name = 'tfx' and show_type = 'daily' then pct_rating_total else null end) / 100
            ) as ratings
            , coalesce(
                    avg(case when channel_name = 'tmc' and show_type = 'daily' then pct_rating_frda50 else null end) / 100
                    , avg(case when channel_name = 'tfx' and show_type = 'daily' then pct_rating_frda50 else null end) / 100
            ) as ratings_frda50
            , coalesce(
                    avg(case when channel_name = 'tmc' and show_type = 'daily' then pct_rating_2549 else null end) / 100
                    , avg(case when channel_name = 'tfx' and show_type = 'daily' then pct_rating_2549 else null end) / 100
            ) as ratings_2549
        from 
            tv_ratings
        where
            show_type != 'prime'
            and show_number = '${inputs.season_filter.value}' 
            and week_number in ${inputs.week_filter.value}
        group by 
            1
    )

    select 
        week_number
        , viewers
        , (viewers - lag(viewers, 1) over (order by week_number)) / lag(viewers, 1) over (order by week_number) as wow_pct_viewers
        , ratings
        , (ratings - lag(ratings, 1) over (order by week_number)) / lag(ratings, 1) over (order by week_number) as wow_pct_ratings
        ,  ratings_frda50
        , (ratings_frda50 - lag(ratings_frda50, 1) over (order by week_number)) / lag(ratings_frda50, 1) over (order by week_number) as wow_pct_ratings_frda50
        , ratings_2549
        , (ratings_2549 - lag(ratings_2549, 1) over (order by week_number)) / lag(ratings_2549, 1) over (order by week_number) as wow_pct_ratings_2549
    from 
        weekly
    order by 
        1 desc
```

<BigValue
    data={weekly_audience_kpis}
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
    data={weekly_audience_kpis}
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
    data={weekly_audience_kpis}
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
    data={weekly_audience_kpis}
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

``` sql daily_audience_over_season
    -- Evidence shifts BigQuery DATE values back by 1 day when loading via `npm run sources` 
    -- Fix: correct the actual DATE value at the source with `+ interval 1 day`, so air_date stays a true DATE type and matches BigQuery exactly. 
    -- The function strftime() cannot work as it only reformats the value to text.

    with 
    season_bounds as (
        select
            min(air_date) + interval 1 day as season_min,
            max(air_date) + interval 1 day as season_max
        from 
            tv_ratings
        where 
            show_type != 'prime'
            and show_number = '${inputs.season_filter.value}'
    )
   

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
        and week_number in ${inputs.week_filter.value}
    group by
        1
```

<BarChart
    data={daily_audience_over_season}
    x=air_date
    y=viewers
    y2={['ratings']}
    y2Fmt=pct1
    y2SeriesType=line
    y2AxisTitle="Ratings"
    colorPalette={['#a4b8fc', '#111726ae']}
    title="Daily Audience Trend"
    subtitle="Weekdays only (Monday-Friday)"
    emptySet=pass
    emptyMessage="Season 13 data available on TFX only"
    chartAreaHeight=200
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