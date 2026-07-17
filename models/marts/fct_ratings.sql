{{ config(
    materialized='incremental',
    unique_key='rating_id',
    incremental_strategy='merge'
) }}

select * from {{ ref('stg_ratings') }}

{% if is_incremental() %}
where air_date >= date_sub(current_date(), interval 2 month)
{% endif %}