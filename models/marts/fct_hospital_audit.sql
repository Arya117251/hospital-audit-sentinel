{{ config(materialized='table') }}

WITH charges AS (
    SELECT 
        provider_id,
        drg_definition,
        average_covered_charges,
        average_total_payments
    FROM {{ source('medicare_source', 'inpatient_charges_2015') }}
),

info AS (
    SELECT * FROM {{ ref('stg_hospital_info') }}
)

SELECT 
    i.hospital_name,
    i.hospital_overall_rating,
    c.drg_definition,
    (c.average_covered_charges - c.average_total_payments) as price_variance
FROM charges c
JOIN info i ON c.provider_id = i.provider_id