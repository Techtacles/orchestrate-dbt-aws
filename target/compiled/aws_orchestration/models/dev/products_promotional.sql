
with products as (
    select * from "dbtaws"."public"."products_team"  limit 100

),
promotional as (
    select * from "dbtaws"."public"."promotional_team"  limit 100

),
products_promotional as (
    select * from products union select * from promotional
)

select * from products_promotional