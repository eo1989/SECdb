select *
from reference_table
where
    "Table Name" like '%balance sheet%'
    and "Company Name" like 'microsoft%'
    and "Filing Type" like '10-K%'

