
"""

Project: NHS Unplanned A&E Attendance & Waiting Time Analysis (England)
File: workingscript.py
Author: Alin Vieru
Purpose:
    - Combine 23 NHS A&E provider CSV files into one clean dataset
    - Standardise column names across files
    - Extract a consistent Year-Month field
    - Calculate Total Unplanned A&E Attendances using NHS definitions:
          Type 1 + Type 2 + Type 3 (Other A&E / UTC)
      (Booked appointments are intentionally NOT included in total_attendances)
    - Keep Decision-to-Admit (DTA) waits as separate “pressure” metrics:
          4–12 hours and 12+ hours from DTA to admission

Inputs:
    - Folder of monthly CSV files (raw_data)
Output:
    - ae_working_set.csv (cleaned_data)
    
"""


import pandas as pd             ### use to process
from pathlib import Path        ### use for path
import re                       ### use to normalise


### path from raw to clean data
BASE_DIR = Path(__file__).resolve().parents[1]  # go up from /scripts to project root
DATA_DIR = BASE_DIR / "raw_data"
OUT_PATH = BASE_DIR / "cleaned_data" / "ae_working_set.csv"
OUT_PATH.parent.mkdir(parents=True, exist_ok=True)



### use for converting to nr
MONTH_MAP = {
    "january": "01", "february": "02", "march": "03", "april": "04",
    "may": "05", "june": "06", "july": "07", "august": "08",
    "september": "09", "october": "10", "november": "11", "december": "12"
}




### clean columns name (lowercase, _ , 2x_ )
def normalise_cols(cols):
    out = []
    for c in cols:
        c = c.strip().lower()
        # replace ALL non-alphanumeric with underscore (handles &, +, -, etc.)
        c = re.sub(r"[^a-z0-9]+", "_", c) #### replace all with "_"
        c = re.sub(r"_+", "_", c).strip("_") ### remove 2x_
        out.append(c)
    ### make unique if duplicates happen
    seen = {}
    unique = [] 
    for c in out:
        ### check dubles
        if c not in seen:
            seen[c] = 0
            unique.append(c)
        else:
            seen[c] += 1
            unique.append(f"{c}_{seen[c]}")
    return unique

### use month_map to return the right numeric format: YEAR-MONTH for year_month
def parse_year_month_from_filename(stem: str):
    s = stem.lower()
    m = re.search(r"(january|february|march|april|may|june|july|august|september|october|november|december)[-_ ]*(20\d{2})", s)
    if not m:
        return None
    month_name, year = m.group(1), m.group(2)
    return f"{year}-{MONTH_MAP[month_name]}"
### load the files
files = sorted(DATA_DIR.glob("*.csv"))
if not files:
    raise SystemExit("No CSV files found in raw_data. Check the folder path.")

dfs = []

### column names AFTER normalisation  ( the ones to get unplanned attendances )
ATT_COLS = [
    "a_e_attendances_type_1",
    "a_e_attendances_type_2",
    "a_e_attendances_other_a_e_department",
    
]
### not to be aggregated with total_attendances, metrics for pressure
WAIT_4_12 = "patients_who_have_waited_4_12_hs_from_dta_to_admission"
WAIT_12P  = "patients_who_have_waited_12_hrs_from_dta_to_admission"  ###  "+" becomes nothing after normalised
### every file
for f in files:
    df = pd.read_csv(f)
    ###
    df.columns = normalise_cols(df.columns)

    ym = parse_year_month_from_filename(f.stem)
    if ym is None:
        ###for MSitAE-APRIL-2025
        if "period" in df.columns:
            p = str(df.loc[0, "period"]).lower()
            m = re.search(r"(january|february|march|april|may|june|july|august|september|october|november|december)[-_ ]*(20\d{2})", p)
            ym = f"{m.group(2)}-{MONTH_MAP[m.group(1)]}" if m else "unknown"
        else:
            ym = "unknown"

    df["year_month"] = ym

    ### missing (put a 0)
    for col in (ATT_COLS + [WAIT_4_12, WAIT_12P, "org_code", "parent_org", "org_name"]):
        if col not in df.columns:
            df[col] = 0

    ### remove the annoying TOTAL rows 
    df = df[~df["org_code"].astype(str).str.strip().str.lower().eq("total")]
    df = df[~df["org_name"].astype(str).str.strip().str.lower().eq("total")]

    ### put 0 in blanks, convert text to nr
    for col in (ATT_COLS + [WAIT_4_12, WAIT_12P]):
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)

    ### sum of totals (attendances only) ( 3 columns )
    df["total_attendances"] = df[ATT_COLS].sum(axis=1)

    ### output 
    out = df[[
        "year_month",
        "org_code",
        "parent_org",
        "org_name",
        "total_attendances",
        WAIT_4_12,
        WAIT_12P
    ]].copy()

    ### rename wainting columns
    out = out.rename(columns={
        WAIT_4_12: "waited_4_12h_dta_to_admission",
        WAIT_12P:  "waited_12h_plus_dta_to_admission"
    })

    dfs.append(out)
###  the file
ae = pd.concat(dfs, ignore_index=True)

### check
print("Rows:", len(ae))
print("Unique months:", ae["year_month"].nunique())
print("Unique providers:", ae["org_code"].nunique())
print("Total attendances sum:", ae["total_attendances"].sum())
### save it
ae.to_csv(OUT_PATH, index=False)
print("Saved:", OUT_PATH)
