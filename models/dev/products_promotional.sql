{{ config(materialized='table') }}
with products as (
    select * from {{ ref("products_team") }}  limit 100

),
promotional as (
    select * from {{ ref("promotional_team") }}  limit 100

),
products_promotional as (
    select * from products union select * from promotional
)

select * from products_promotional
