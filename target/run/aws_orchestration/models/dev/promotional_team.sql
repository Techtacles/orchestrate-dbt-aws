
  create view "dbtaws"."public"."promotional_team__dbt_tmp" as (
    -- Use the `ref` function to select from other models




with promotional_team as (

    select * from "dbtaws"."public"."bi_budget_csv" where team='Promotional'

)

select * from promotional_team
  );