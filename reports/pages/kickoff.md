---
title: Kick-off
---

A comparison snapshot of rating performance for the kick-off of the French TV show 👁️.  


``` sql kickoff_ratings
    select 
        distinct show_number
        , max(case when show_part_number = 1 then num_viewers end) as viewers_part_1
        , max(case when show_part_number = 2 then num_viewers end) as viewers_part_2
        , max(case when show_part_number = 1 then pct_rating_total / 100 end) as pct_rating_total_1
        , max(case when show_part_number = 2 then pct_rating_total end) as pct_rating_total_2
        , avg(num_viewers) as avg_viewers
        , avg(pct_rating_total) as avg_pct_rating_total
       , concat(
        round(avg(num_viewers)),
        ' - ',
        round(avg(pct_rating_total), 1),
        '%'
    ) as bar_label
    from 
        tv_ratings
    where
        show_type = 'prime' 
        and channel_name = 'tf1'  
    group by 
        1
```

<BarChart
    data={kickoff_ratings}
    x=show_number
    xType=category
    y=avg_viewers
    yFmt=num0
    colorPalette={['#a4b8fc', '#111726ae']}
    chartAreaHeight=300
    title="Prime Audience Trend"
    subtitle="Average across episode (parts 1 & 2)"
    swapXY=true
    labels=true
/>

<Grid cols=2>

<!-- Left side: 4 KPIs in a 2x2 grid -->
<Grid cols=2>

<BigValue
    data={kickoff_ratings}
    value=avg_viewers
    title="Daily Viewers"
/>

<BigValue
    data={kickoff_ratings}
    value=avg_viewers
    title="Daily Viewers"
/>

<BigValue
    data={kickoff_ratings}
    value=avg_viewers
    title="Daily Viewers"
/>

<BigValue
    data={kickoff_ratings}
    value=avg_viewers
    title="Daily Viewers"
/>

</Grid>

<!-- Right side: chart -->
<BarChart
    data={kickoff_ratings}
    x=show_number
    xType=category
    y=avg_viewers
    yFmt=num0 
    colorPalette={['#a4b8fc', '#111726ae']}
    chartAreaHeight=400
    title="Prime Audience Trend"
    subtitle="Average across episode (parts 1 & 2)"
    labels=true
/>

</Grid>

<Grid cols=2>

<Grid cols=1>

<BigValue
    data={kickoff_ratings}
    value=avg_viewers
    title="Daily Viewers"
/>

<BigValue
    data={kickoff_ratings}
    value=avg_viewers
    title="Daily Viewers"
/>

<BigValue
    data={kickoff_ratings}
    value=avg_viewers
    title="Daily Viewers"
/>

<BigValue
    data={kickoff_ratings}
    value=avg_viewers
    title="Daily Viewers"
/>

</Grid>

<BarChart
data={kickoff_ratings}
x=show_number
xType=category
y=avg_viewers
yFmt=num0
colorPalette={['#a4b8fc', '#111726ae']}
chartAreaHeight=400
title="Prime Audience Trend"
subtitle="Average across episode (parts 1 & 2)"
labels=true
/>

</Grid>


<Grid cols=2>
<BarChart
    data={kickoff_ratings}
    x=show_number
    xType=category
    y=viewers_part_1
    yFmt=num0
    y2=pct_rating_total_1
    y2Fmt=pct1
    y2SeriesType=line
    colorPalette={['#a4b8fc', '#111726ae']}
    chartAreaHeight=300
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
<BarChart
    data={kickoff_ratings}
    x=show_number
    xType=category
    y=viewers_part_2
    yFmt=num0
    yMax=1000000
     y2=pct_rating_total_2
    y2Fmt=pct1
    y2SeriesType=line
    colorPalette={['#a4b8fc', '#111726ae']}
    chartAreaHeight=300
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

</Grid>

