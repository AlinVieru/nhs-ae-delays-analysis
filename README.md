

                                      
# A&E Unplanned Attendances vs 12+ Hour Delays (Jan 2024 – Nov 2025)  
 
## 1. Project overview
This project analyses A&E demand and waiting-time pressure across NHS providers in England 
using official NHS England monthly data.

The aim is to understand:

     **Do unplanned A&E attendances drive 12+ hour delays?**

### Data sources:
- For collecting data: https://www.england.nhs.uk/statistics/statistical-work-areas/ae-waiting-times-and-activity/ 
                      for 23 months latest available at the moment of writing
- For definitions / guidance: https://www.england.nhs.uk/statistics/wp-content/uploads/sites/2/2020/08/AE-Attendances-Emergency-Definitions-v5.0-final-August-2020.pdf

### Data structure in raw format

 Each monthly CSV contains:
 - Period,Org Code,Parent Org,Org name,
 - A&E attendances Type 1,A&E attendances Type 2,A&E attendances Other A&E Department,
 - A&E attendances Booked Appointments Type 1,A&E attendances Booked Appointments Type 2,A&E attendances Booked Appointments Other Department,
 - Attendances over 4hrs Type 1,Attendances over 4hrs Type 2,Attendances over 4hrs Other Department,
 - Attendances over 4hrs Booked Appointments Type 1,Attendances over 4hrs Booked Appointments Type 2,Attendances over 4hrs Booked  Appointments OtherDepartment,
 - Patients who have waited 4-12 hours from DTA to admission,Patients who have waited 12+ hrs from DTA to admission,
 - Emergency admissions via A&E - Type 1,Emergency admissions via A&E - Type 2,Emergency admissions via A&E - Other A&E department,Other emergency    admissions

 Row detail:
  **1 row = 1 NHS provider in 1 month**

### Reasoning for choosing columns (from the monthly CSV files)

The raw monthly CSV contains many measures. I selected only the columns needed to answer the project question.
#### Columns included
  **Period**
   Used to assign each record to the correct month (year_month), so trends can be analysed across Jan 2024-Nov 2025.

 **Provider identifiers (to keep 1 row = 1 provider per month)**
   Org Code
   Parent Org
   Org name
   Used to:
   - confirm uniqueness (provider + month)
   - aggregate safely to national totals
   - allow future drill-down by provider/region if needed

 **Unplanned attendance columns (demand variable)**
   A&E attendances Type 1
   A&E attendances Type 2
   A&E attendances Other A&E Department
   These represent unplanned A&E activity. I summed them to create:
   `total_attendances = Type 1 + Type 2 + Other A&E Department`

 **Waiting-time pressure columns (outcome variables)**
   Patients who have waited 4-12 hours from DTA to admission
   Patients who have waited 12+ hrs from DTA to admission
   These are the main pressure indicators. I kept them as separate measures and used the 12+ hours field as the primary outcome.

#### Columns excluded
   -A&E attendances Booked Appointments Type 1
   -A&E attendances Booked Appointments Type 2
   -A&E attendances Booked Appointments Other Department
   Reason: booked appointments are not unplanned demand, so including them would inflate attendances and weaken the comparison.

   -Attendances over 4hrs Type 1 / Type 2 / Other Department
   -Attendances over 4hrs Booked Appointments Type 1 / Type 2 / Other Department
   Reason: useful for wider performance reporting, but not needed to answer the 12+ hour DTA question.

   -Emergency admissions via A&E - Type 1 / Type 2 / Other A&E department
    Other emergency admissions
   Reason: describes admissions outcomes, but the project focus is on unplanned attendances vs long waits (12+ hours from DTA).

---

## 2. Data preparation
 All data preparation is done in Python (pandas) before analysis or visualisation.
 -Loaded 23 monthly CSV files

 -Standardised column names
   -Converted to lowercase
   -Replaced special characters (&, +, -, spaces)
   -Ensured column names are unique

 -Extracted year_month
   -Parsed from file names (e.g. April-2025)
   -Fallback parsing from period column if needed

 -Removed summary rows
   -Excluded rows labelled TOTAL

 -Ensured numeric consistency
   -Converted all numeric fields safely
   -Missing values set to 0

### Final dataset: 
 -`year_month` (YYYY-MM)  
 -`org_code` (NHS provider code)  
 -`parent_org` (NHS England region)  
 -`org_name` (NHS provider name)  
 -`total_attendances` (Type 1 + Type 2 + Other A&E Department)  
 -`waited_4_12h_dta_to_admission` (patients waiting 4–12 hours)  
 -`waited_12h_plus_dta_to_admission` (patients waiting 12+ hours)

### Dataset size: 
 -Rows: 4562
 -Unique months: 23
 -Unique providers: 208
 -Total attendances sum: 51023505  

---

## 3. Data Validation
  Data quality checks were performed using:
   - Python checks (row counts, totals, uniqueness)

   - SQL validation queries after import into MySQL
     (e.g totals, null checks, duplicate detection)
     SQL was used to validate the cleaned dataset, 
     including row counts, duplicate checks, null detection, 
     and aggregation checks at monthly level.    
   - A composite key (year_month + org_code) can be added if the table is used beyond validation. 
   
---

## 4. Data visualisation
Power BI analysis and visualisation is done after the dataset is cleaned and validated.

 -Loaded the final dataset into Power BI

 ### Power Query (data preparation inside Power BI)
   -Created MonthDate column in Power Query
   -Used MonthDate to sort the month timeline correctly

 ### Created display column for reporting
   -Created `Year Month (Display)`
   -Used to show a readable month label in visuals: `MMMM/yyyy`
 
 ### Sorted the month timeline correctly
   -`year_month` sorted by `MonthDate`
   -Charts display in the correct order (Jan 2024 -> Nov 2025)

 ### Created the key measures used in the report
   -Total Attendances:
   SUM(ae_working_set[total_attendances])

   -DTA 4–12h:
   SUM(ae_working_set[waited_4_12h_dta_to_admission])

   -DTA 12h+:
   SUM(ae_working_set[waited_12h_plus_dta_to_admission])

   -12h+ delays per 1,000 (normalised rate):
   DIVIDE([DTA 12h+], [Total Attendances]) * 1000

   Formatted measures (for KPI display):
   
   -FORMAT([Total Attendances], "#,##0")
   
   -FORMAT([DTA 12h+], "#,##0")
   
   -FORMAT([DTA 4–12h], "#,##0")

   -FORMAT ( [DTA 12h+ per 1,000], "0.00" ) & " per 1,000"
   Year Month (Display) = FORMAT(ae_working_set[MonthDate], "MMMM/yyyy")
   
### Dashboard
 -Built the dashboard visuals to answer the question
 
 -KPI cards for headline totals and rate
 
 -Monthly trend charts for attendances and delays per 1,000
 
 -Scatter plot comparing attendances vs 12+ delays to test the relationship
 
 -Added reference lines and a trend line to support the conclusion
 
 -Calculated the correlation coefficient (r) between monthly total unplanned attendances and monthly 12+ hour delays,and displayed it.
 
 -Set interactions to keep the dashboard stable
 
 -Clicking a month updates KPIs
 
 -Cross-filtering between the main charts is disabled to avoid charts collapsing

### Summarised what the visuals show and the overall takeaway: 
 
  **Demand alone does not explain 12+ hour delays.**
---



