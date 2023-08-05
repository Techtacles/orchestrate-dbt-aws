
/*
    Welcome to your first dbt model!
    Did you know that you can also configure models directly within SQL files?
    This will override configurations stated in dbt_project.yml

    Try changing "table" to "view" below
*/

{{ config(materialized='view') }}

with products_team as (

    select * from {{ ref('bi_budget_csv') }} where team = 'Products'

)

select * from products_team

/*
    Uncomment the line below to remove records with null `id` values
*/

-- where id is not null
