-- compare two db's and find missing tables if there are any'
ATTACH 'edgar.db' AS db1;
ATTACH 'edgar_transposed.db' AS db2;
SELECT name
FROM db1.sqlite_schema
WHERE type = 'table'
EXCEPT
SELECT name
FROM db2.sqlite_schema
WHERE type = 'table'

-- inspect tables properties, like cols and their respective dtypes. --
	pragma table_info('table_name');

-- create ref table view --
CREATE VIEW reference_table AS
SELECT b.short_name AS 'Table_Name',
	a.company_name AS 'Company_Name',
	a.filing_number AS 'Filing_Number',
	a.filing_date AS 'Filing_Date',
	a.cik AS 'Company_CIK',
	a.filing_type AS 'Filing_Type',
	a.table_name AS 'Full_Table_Name',
	b.report_url AS 'Link_to_Table'
FROM (
		SELECT a.filing_number,
			a.filing_date,
			a.company_name,
			a.cik,
			a.filing_type,
			b.table_name
		FROM filing_list AS a
			INNER JOIN (
				SELECT name AS table_name
				FROM sqlite_master
				WHERE type = 'table'
			) AS b ON b.table_name LIKE '%' || a.filing_number || '%'
	) AS a
	LEFT OUTER JOIN individual_report_links AS b ON (
		a.table_name LIKE '%' || REPLACE(b.short_name, ' ', '_') || '_' || b.filing_number || '%'
	)
	AND a.filing_number = b.filing_number
GROUP BY a.table_name
ORDER BY a.filing_date DESC