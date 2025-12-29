


/* 
Project: NHS Unplanned A&E Attendance & Waiting Time Analysis (England)
File: validation_script.sql
Author: Alin Vieru
Purpose: Validate cleaned provider-month dataset before Power BI reporting

Core checks:
- Row coverage (months/providers)
- Nulls and negative values
- Duplicates
- National monthly totals
- Logical constraints 
*/



CREATE DATABASE IF NOT EXISTS ae_project;
USE ae_project;

DROP TABLE IF EXISTS ae_attendances;

CREATE TABLE ae_attendances (
    YearMonth CHAR(7),
    NHS_TRUST_code VARCHAR(10),
    Region VARCHAR(255),
    NHS_TRUST_name VARCHAR(255),
    total_attendances INT,
    waited4_12 INT,
    waited12plus INT
     	
);

select * from ae_attendances;


-- count rows
SELECT COUNT(*) AS total_rows
FROM ae_attendances;
-- months nr
SELECT COUNT(DISTINCT YearMonth) AS months
FROM ae_attendances;
-- nr provders
SELECT COUNT(DISTINCT NHS_TRUST_code) AS providers
FROM ae_attendances;
-- check null
SELECT *
FROM ae_attendances
WHERE NHS_TRUST_code IS NULL
   OR NHS_TRUST_name IS NULL;
-- check null for totals
SELECT COUNT(*) AS null_totals
FROM ae_attendances
WHERE total_attendances IS NULL;

-- Negative checks
SELECT *
FROM ae_attendances
WHERE total_attendances < 0
   OR waited4_12 < 0
   OR waited12plus < 0;

-- check duplicate 
SELECT
  YearMonth,
  NHS_TRUST_code,
  COUNT(*) AS rows_per_provider
FROM ae_attendances
GROUP BY YearMonth, NHS_TRUST_code
HAVING COUNT(*) > 1;

-- totals by month 
SELECT
  YearMonth,
  SUM(total_attendances) AS national_attendances,
  SUM(waited4_12) AS national_waited_4_12,
  SUM(waited12plus) AS national_waited_12_plus
FROM ae_attendances
GROUP BY YearMonth
ORDER BY YearMonth;
-- check total bigger than waits
SELECT *
FROM ae_attendances
WHERE waited4_12 > total_attendances
   OR waited12plus > total_attendances;

-- count rows with 0 waits
SELECT
  COUNT(*) AS zero_wait_rows
FROM ae_attendances
WHERE waited4_12 = 0
  AND waited12plus = 0;
