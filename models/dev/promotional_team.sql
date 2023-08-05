
-- Use the `ref` function to select from other models


{{ config(materialized='view') }}

with promotional_team as (

    select * from {{ ref('bi_budget_csv') }} where team='Promotional'

)

select * from promotional_team
