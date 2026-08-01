```sql ratings_tbl
    select 
        distinct strftime(air_date, '%Y-%m-%d') as air_date
        , num_viewers
    from 
        tv_ratings
    where 
        show_number = 14 
        and channel_name = 'tfx'
    order by 
        air_date
```