```sql ratings  
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

```sql ratings_tbl
    with 
    date_trans_tbl as ( 
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
    )

    select 
        cast(air_date as date) as air_date
        , num_viewers
    from 
        date_trans_tbl 
    order by 
        1
```