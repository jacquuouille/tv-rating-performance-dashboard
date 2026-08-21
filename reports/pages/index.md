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
/>

## Audience
Evolution of audience viewership and ratings across the season, daily and prime shows.

``` sql overview_audience 
        select
            ceil(
                coalesce(
                avg(case when channel_name = 'tmc' and show_type = 'daily' then num_viewers else null end)
                , avg(case when channel_name = 'tfx' and show_type = 'daily' then num_viewers else null end)
                ) / 100
             ) * 100 as viewers_daily
            , coalesce(
                avg(case when channel_name = 'tmc' and show_type = 'daily' then pct_rating_total else null end) / 100
                , avg(case when channel_name = 'tfx' and show_type = 'daily' then pct_rating_total else null end) / 100
            ) as ratings_daily
            , ceil(
                coalesce(
                avg(case when channel_name = 'tmc' and show_type = 'prime' then num_viewers else null end)
                , avg(case when channel_name = 'tfx' and show_type = 'prime' then num_viewers else null end) 
                ) / 100
            ) * 100 as viewers_prime
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

``` sql daily_audience_over_season
    -- Evidence shifts BigQuery DATE values back by 1 day when loading via `npm run sources` 
    -- Fix: correct the actual DATE value at the source with `+ interval 1 day`, so air_date stays a true DATE type and matches BigQuery exactly. 
    -- The function strftime() cannot work as it only reformats the value to text.

    select
        week_number
        , concat('Week', ' ', cast(week_number as bigint)) as week_number_label
        , coalesce(
            avg(case when channel_name = 'tmc' and show_type = 'daily' then num_viewers else null end)
            , avg(case when channel_name = 'tfx' and show_type = 'daily' then num_viewers else null end)
        ) as viewers
        , coalesce(
            avg(case when channel_name = 'tmc' and show_type = 'daily' then pct_rating_total else null end) / 100
            , avg(case when channel_name = 'tfx' and show_type = 'daily' then pct_rating_total else null end) / 100
        ) as ratings
    from 
        tv_ratings
    where 
        show_type != 'prime'
        and show_number = '${inputs.season_filter.value}'
    group by
        1, 2
```

<BarChart
    data={daily_audience_over_season}
    x=week_number_label
    y=viewers
    yAxisTitle=""
    y2={['ratings']}
    y2Fmt=pct1
    y2SeriesType=line
    sort=false
    labels=true
    labelFmt=num0k
    y2LabelFmt=pct1
    colorPalette={['#a4b8fc', '#111726ae']}
    title="Daily Audience Performance"
    subtitle="TMC only for season 14, TFX for season 13 (Weekdays & Sundays)"
    chartAreaHeight=250
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

``` sql weekly_audience_over_season
    -- Evidence shifts BigQuery DATE values back by 1 day when loading via `npm run sources` 
    -- Fix: correct the actual DATE value at the source with `+ interval 1 day`, so air_date stays a true DATE type and matches BigQuery exactly. 
    -- The function strftime() cannot work as it only reformats the value to text 

    with 
    daily_ratings as ( 
        select
            air_date
            , week_number
            , concat('Week', ' ', cast(week_number as bigint)) as week_number_label
            , upper(channel_name) as channel_name
            , sum(num_viewers) as viewers
            , sum(pct_rating_total) / 100 as ratings
        from 
            tv_ratings
        where 
            show_type != 'prime'
            and show_number = '${inputs.season_filter.value}'
        group by
            1, 2, 3, 4
    ) 

    select
        week_number
        , week_number_label
        , channel_name
        , avg(viewers) as viewers
    from 
        daily_ratings  
    group by 
        1, 2, 3
    order by 
        1
```

<BarChart
    data={weekly_audience_over_season}
    x=week_number_label
    y=viewers
    series=channel_name
    labels=true
    sort=false
    labelFmt=num0k
    showAllLabels=false
    colorPalette={['#a4b8fc', '#111726ae']}
    title="Daily Audience Performance by Channel"
    subtitle="Weekdays & Sundays"
    chartAreaHeight=250
/>

</Tab>
<Tab label="Prime">


``` sql prime_weekly_audience
        select
            week_number
            , concat('Prime', ' ', cast(week_number as bigint)) as week_number_label
            , avg(num_viewers) as viewers
            , avg(pct_rating_total) / 100 as ratings
        from 
            tv_ratings
        where
            show_type = 'prime'
            and channel_name != 'tf1'
            and show_number = '${inputs.season_filter.value}'
        group by 
            1
```

<BarChart
    data={prime_weekly_audience}
    x=week_number_label
    y=viewers
    y2={['ratings']}
    y2Fmt=pct1
    y2SeriesType=line
    y2AxisTitle="Ratings"
    sort=false
    labels=true
    labelFmt=num0k
    y2LabelFmt=pct1
    colorPalette={['#a4b8fc', '#111726ae']}
    title="Prime Audience Trend"
    subtitle="Average across episode (parts 1 & 2)"
    chartAreaHeight=250
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
        and channel_name != 'tf1'
        and show_number = '${inputs.season_filter.value}'
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
    labels=true
    labelFmt=num0k
    colorPalette={['#a4b8fc', '#111726be']}
    title="Prime Audience Trend by Part"
    subtitle="Parts 1 vs. 2"
    chartAreaHeight=250
/>

</Tab>
</Tabs>