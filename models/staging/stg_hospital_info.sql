{{ config(materialized='view') }}

SELECT 
    provider_id,
    hospital_name,
    hospital_overall_rating,
    hospital_ownership
FROM {{ source('medicare_source', 'hospital_general_info') }}