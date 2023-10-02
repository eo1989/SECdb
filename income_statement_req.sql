SELECT date AS 'Date',
	CAST(revenue AS integer) AS 'Revenue',
	CAST(cost_of_revenue AS integer) AS 'Cost of Revenue',
	CAST(net_income AS integer) AS 'Net Income',
	CAST(operating_income AS integer) AS 'Operating Income',
	CAST(gross_margin AS integer) AS 'Gross Margin',
	CAST(income_before_income_taxes AS integer) AS 'Income Before Income Taxes',
	CAST(provision_for_income_taxes AS integer) AS 'Provision for Income Taxes',
	CAST(research_and_development AS integer) AS 'Research and Development',
	CAST(sales_and_marketing AS integer) AS 'Sales and Marketing',
	CAST(general_and_administrative AS integer) AS 'General and Administrative'
FROM (
		SELECT date,
			revenue,
			cost_of_revenue,
			net_income,
			operating_income,
			gross_margin,
			income_before_income_taxes,
			provision_for_income_taxes,
			research_and_development,
			sales_and_marketing,
			general_and_administrative
		FROM '10_K2015_07_31_INCOME_STATEMENTS_14278151019135'
		UNION
		SELECT date,
			revenue,
			cost_of_revenue,
			net_income,
			operating_income,
			gross_margin,
			income_before_income_taxes,
			provision_for_income_taxes,
			research_and_development,
			sales_and_marketing,
			general_and_administrative
		FROM '10_K2016_07_28_INCOME_STATEMENTS_137845161790278'
		UNION
		SELECT date,
			revenue,
			cost_of_revenue,
			net_income,
			operating_income,
			gross_margin,
			income_before_income_taxes,
			provision_for_income_taxes,
			research_and_development,
			sales_and_marketing,
			general_and_administrative
		FROM '10_K2017_08_02_INCOME_STATEMENTS_137845171000067'
		UNION
		SELECT date,
			revenue,
			cost_of_revenue,
			net_income,
			operating_income,
			gross_margin,
			income_before_income_taxes,
			provision_for_income_taxes,
			research_and_development,
			sales_and_marketing,
			general_and_administrative
		FROM '10_K2018_08_03_INCOME_STATEMENTS_13784518990758'
		UNION
		SELECT date,
			revenue,
			cost_of_revenue,
			net_income,
			operating_income,
			gross_margin,
			income_before_income_taxes,
			provision_for_income_taxes,
			research_and_development,
			sales_and_marketing,
			general_and_administrative
		FROM '10_K2019_08_01_INCOME_STATEMENTS_13784519992755' L
		UNION
		SELECT date,
			revenue,
			cost_of_revenue,
			net_income,
			operating_income,
			gross_margin,
			income_before_income_taxes,
			provision_for_income_taxes,
			research_and_development,
			sales_and_marketing,
			general_and_administrative
		FROM '10_K2020_07_30_INCOME_STATEMENTS_137845201063171'
		UNION
		SELECT date,
			revenue,
			cost_of_revenue,
			net_income,
			operating_income,
			gross_margin,
			income_before_income_taxes,
			provision_for_income_taxes,
			research_and_development,
			sales_and_marketing,
			general_and_administrative
		FROM '10_K2021_07_29_INCOME_STATEMENTS_137845211127769'
	)
WHERE (
		revenue || cost_of_revenue || net_income || operating_income || gross_margin || income_before_income_taxes || provision_for_income_taxes || research_and_development || sales_and_marketing || general_and_administrative
	) IS NOT NULL
GROUP BY date
ORDER BY date