{{ config(materialized='view') }}

SELECT 
    provider_id,
    hospital_name AS provider_name,
    hospital_overall_rating,
    hospital_ownership,
    city AS provider_city
FROM {{ source('medicare_source', 'hospital_general_info') }}