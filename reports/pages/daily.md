---
title: Daily
---

A snapshot of daily ratings performance for the selected season of the French TV show 👁️, with performance filterable by channel.

```sql season_listing
    select 
        distinct show_number
    from 
        tv_ratings
```

```sql channel_listing
    select 
        distinct upper(channel_name) as channel_name
    from 
        tv_ratings
    where 
        channel_name != 'tf1'
        and show_number = '${inputs.season_filter.value}'
```

```sql season_dates
    select 
        distinct air_date
    from 
        tv_ratings
    where 
        show_number = '${inputs.season_filter.value}'
```

<Dropdown
    name=season_filter
    data={season_listing}
    value=show_number
    title="Season"
    order=show_number
/>

<Dropdown
    name=channel_filter
    data={channel_listing}
    value=channel_name
    title="Channel"
    order=channel_name
/> 

<DateRange
    name=date_range_filter
    data={season_dates}
    dates=air_date
/>

``` sql daily_audience_over_season
    -- Evidence shifts BigQuery DATE values back by 1 day when loading via `npm run sources` 
    -- Fix: correct the actual DATE value at the source with `+ interval 1 day`, so air_date stays a true DATE type and matches BigQuery exactly. 
    -- The function strftime() cannot work as it only reformats the value to text  

with 
    season_bounds as (
        select
            min(air_date) + interval 1 day as season_min,
            max(air_date) + interval 1 day as season_max
        from tv_ratings
        where show_type != 'prime'
            and show_number = '${inputs.season_filter.value}'
    ),
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
            and air_date + interval 1 day between 
                greatest('${inputs.date_range_filter.start}'::date, (select season_min from season_bounds))
                and least('${inputs.date_range_filter.end}'::date, (select season_max from season_bounds))
        group by
            1
    ), 
    base as (
        select 
            air_date,
            viewers,
            ratings, 
            date_diff('day', min(air_date) over (), air_date) as day_num
        from 
            daily_ratings
    ),
    regression as (
        select
            covar_pop(ratings, day_num) / nullif(var_pop(day_num), 0) as slope,
            avg(ratings) - (covar_pop(ratings, day_num) / nullif(var_pop(day_num), 0)) * avg(day_num) as intercept
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