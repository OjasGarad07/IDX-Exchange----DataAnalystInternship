# IDX Exchange — Data Analyst Internship

This repository contains work from my Data Analyst internship at IDX Exchange, where I pulled CRMLS listing and sold transaction data from the CoreLogic Trestle API, built market analytics pipelines in Python, and created Tableau dashboards to surface real estate market insights.

**Tech Stack:** Python (pandas), CoreLogic Trestle API, FRED API, Tableau Desktop

**Data Source:** CRMLS (California Regional Multiple Listing Service) via the CoreLogic Trestle API

**Program:** 12-week MLS Analytics & Tableau Dashboard internship

---

## Repository Contents

### Extraction Scripts

**crmls_listed.py**
- Extracts property listing records for a specified month from the CoreLogic Trestle API
- Filters records based on ListingContractDate
- Handles pagination to retrieve all records
- Exports data to a monthly CSV file (e.g. CRMLSListing202605.csv)

**crmls_sold.py**
- Extracts sold property records for a specified month from the CoreLogic Trestle API
- Filters records based on CloseDate and MlsStatus = Closed
- Handles pagination to retrieve all records
- Exports data to a monthly CSV file (e.g. CRMLSSold202605.csv)

### Week 1 — Monthly Dataset Aggregation

**week1_deliverable.py / week1_deliverable.ipynb**
- Loads all monthly listing CSV files from March 2024 through April 2026
- Loads all monthly sold CSV files from January 2024 through April 2026
- Concatenates all monthly files into two unified datasets
- Filters both datasets to residential properties only (PropertyType == 'Residential')
- Prints row counts before and after concatenation and before and after the residential filter
- Saves the combined datasets as:
  - CRMLSListingCombined.csv
  - CRMLSSoldCombined.csv

### Weeks 2-3 — EDA & Dataset Structuring

**week2_3_deliverable.py / week2_3_deliverable.ipynb**
- Loads the combined sold and listing datasets from Week 1
- Step 1 — prints row and column counts for both datasets
- Step 2 — prints all column data types to identify mistyped fields
- Step 3 — calculates missing value counts and percentages per column, flags columns with more than 90% missing values, and drops flagged columns
- Step 4 — produces numeric distribution summary for key fields: ClosePrice, ListPrice, OriginalListPrice, LivingArea, LotSizeAcres, BedroomsTotal, BathroomsTotalInteger, DaysOnMarket, YearBuilt
- Confirms both datasets are filtered to Residential only
- Fetches the 30-year fixed mortgage rate (MORTGAGE30US) from the FRED API
- Resamples weekly mortgage rates to monthly averages
- Merges monthly mortgage rates onto both datasets using a year_month key
- Answers suggested intern EDA questions: median vs mean close price, DOM distribution, % sold above vs below list price, top counties by median price, date consistency issues
- Saves cleaned and enriched datasets as:
  - sold_eda.csv
  - listing_eda.csv
  - sold_with_rates.csv
  - listing_with_rates.csv

### Weeks 4-5 — Data Cleaning, Consistency Checks & Geographic Validation

**week4_deliverables.py / week4_deliverables.ipynb**
- Loads the EDA cleaned datasets from Weeks 2-3
- Converts all date fields to datetime format (CloseDate, PurchaseContractDate, ListingContractDate, ContractStatusChangeDate)
- Drops redundant and unnecessary columns (BuyerAgentAOR, ListingKeyNumeric, StreetNumberNumeric, OriginatingSystemName, etc.)
- Identifies and drops .1 duplicate columns in the listings dataset
- Checks missing value percentages for key fields (Latitude, Longitude, ListOfficeName, MLSAreaMajor, etc.)
- Drops rows where core fields are null (LivingArea, City, BathroomsTotalInteger, YearBuilt)
- Ensures numeric fields are properly typed and converts integer fields to Int64
- Flags invalid numeric values: ClosePrice <= 0, LivingArea <= 0, DaysOnMarket < 0, negative bedrooms or bathrooms
- Removes invalid records and documents row counts before and after
- Date consistency checks — flags records where:
  - ListingContractDate is after CloseDate
  - PurchaseContractDate is after CloseDate
  - PurchaseContractDate is before ListingContractDate
- Geographic data checks — flags records with:
  - Missing coordinates (Latitude or Longitude is null)
  - Zero coordinates (sentinel null values)
  - Positive longitude (should always be negative for California)
- Saves final cleaned datasets as:
  - sold_clean.csv
  - listings_clean.csv
  - sold_week4_5.csv
  - listings_week4_5.csv

---

## Requirements

Python 3.x

Install required packages:

pip install requests pandas
python crmls_listed.py
python crmls_sold.py

---

## Running the Scripts

### Generating Monthly Listing Data

Update the date filter and output filename in crmls_listed.py:

```python
'$filter': f"ListingContractDate ge 2026-05-01T00:00:00Z and ListingContractDate lt 2026-06-01T00:00:00Z"
csv_file = 'CRMLSListing202605.csv'
```

Then run:

### Generating Monthly Sold Data

Update the date filter and output filename in crmls_sold.py:

```python
'$filter': f"MlsStatus eq 'Closed' and CloseDate ge 2026-05-01T00:00:00Z and CloseDate lt 2026-06-01T00:00:00Z"
csv_file = 'CRMLSSold202605.csv'
```

Then run:

---

## Output Files

| File | Description |
|------|-------------|
| CRMLSListingYYYYMM.csv | Monthly listing extract |
| CRMLSSoldYYYYMM.csv | Monthly sold extract |
| CRMLSListingCombined.csv | All residential listings combined |
| CRMLSSoldCombined.csv | All residential sold transactions combined |
| sold_eda.csv | Sold dataset with >90% null columns removed |
| listing_eda.csv | Listing dataset with >90% null columns removed |
| sold_with_rates.csv | Sold dataset enriched with monthly mortgage rates |
| listing_with_rates.csv | Listing dataset enriched with monthly mortgage rates |
| sold_clean.csv | Sold dataset after full cleaning pipeline |
| listings_clean.csv | Listing dataset after full cleaning pipeline |
| sold_week4_5.csv | Final sold dataset with date and geographic flags |
| listings_week4_5.csv | Final listing dataset with date and geographic flags |

---

## Key EDA Findings (Weeks 2-3)

**Dataset Size**
- Sold: 350,179 rows, 82 columns (67 after dropping high-null columns)
- Listings: 512,665 rows, 84 columns (69 after dropping high-null columns)

**Missing Value Summary**
- 15 columns dropped from sold dataset, 15 from listing dataset, all with more than 90% missing values
- Notable dropped columns: WaterfrontYN (99.94%), FireplacesTotal (100%), TaxYear (100%), ElementarySchoolDistrict (100%)

**Numeric Field Observations**
- Median close price: $820,000 — median preferred over mean due to heavy skew from outliers (max $989.5M)
- Median days on market: 19 days — mean of 38.5 days inflated by extreme outliers
- 38.85% of homes sold above list price, 61.15% at or below
- Top counties by median close price: San Mateo ($1.68M), Santa Clara ($1.59M), Santa Cruz ($1.2M)

**Date Consistency Issues**
- 55 records where ListingContractDate is after CloseDate
- 189 records where PurchaseContractDate is after CloseDate
- Flagged for handling in Weeks 4-5

**Mortgage Rate Enrichment**
- 30-year fixed mortgage rate data fetched from FRED (MORTGAGE30US series)
- Weekly rates resampled to monthly averages and merged onto both datasets
- Zero null mortgage rate values after merge confirming a complete join

**Data Cleaning Results (Weeks 4-5)**
- Sold: 349,271 final rows after cleaning (removed 908 invalid records)
- Listings: 510,545 final rows after cleaning (removed 2,120 invalid records)
- Geographic flags: 15,782 sold records and 71,214 listing records with missing coordinates

---

*This repository is maintained throughout my IDX Exchange internship to document project progress and track individual contributions.*
