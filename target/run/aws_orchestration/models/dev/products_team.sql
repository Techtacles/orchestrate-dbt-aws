
  create view "dbtaws"."public"."products_team__dbt_tmp" as (
    /*
    Welcome to your first dbt model!
    Did you know that you can also configure models directly within SQL files?
    This will override configurations stated in dbt_project.yml

    Try changing "table" to "view" below
*/



with products_team as (

    select * from "dbtaws"."public"."bi_budget_csv" where team = 'Products'

)

select * from products_team

/*
    Uncomment the line below to remove records with null `id` values
*/

-- where id is not null
  );