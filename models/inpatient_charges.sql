{{ config(materialized='table') }}
SELECT
  provider_id,
  provider_name,
  provider_city,
  average_covered_charges,
  average_total_payments,
  average_covered_charges - average_total_payments AS variance
FROM
  bigquery-public-data.cms_medicare.inpatient_charges_2015