---
title: Overview
---

A snapshot of the ratings performance of the selected season of Secret Story.

```sql season_options
    select distinct show_number
    from tv_ratings
    order by 1
```

<Dropdown
    name=season_filter
    data={season_options}
    value=show_number
    title="Season"
/>

<Dropdown
    name=season_filter
    data={season_options}
    value=show_number
    title="Season"
/>

## Audience
Tracks the evolution of audience viewership and ratings over the course of the season, giving an immediate read on how it is performing.