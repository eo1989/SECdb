SELECT
  *
FROM
  reference_table
WHERE
  "Table Name" LIKE '%balance sheet%'
  AND "Company Name" LIKE 'microsoft%'
  AND "Filing Type" LIKE '10-K%'
