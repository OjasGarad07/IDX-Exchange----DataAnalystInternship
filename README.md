# IDX Exchange — Data Analyst Internship

This repository contains work from my Data Analyst internship at IDX Exchange, where I pulled CRMLS listing and sold transaction data from the CoreLogic Trestle API, built market analytics pipelines in Python, and created Tableau dashboards to surface real estate market insights.

**Tech Stack:** Python (pandas), CoreLogic Trestle API, FRED API, Tableau Desktop, geopandas

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

### Week 6 — Feature Engineering & Market Metrics

**week6_deliverables.py**
- Loads the cleaned datasets from Weeks 4-5
- Converts date fields to datetime format
- Engineers key market metrics:
  - `price_ratio` — ClosePrice / OriginalListPrice
  - `price_per_sqft` — ClosePrice / LivingArea
  - `close_to_original_list_ratio` — ClosePrice / OriginalListPrice
  - `listing_to_contract_days` — days from listing date to accepted offer
  - `contract_to_close_days` — days from accepted offer to close (escrow period)
  - `Year`, `Month`, `YrMo` — time series variables derived from CloseDate
- Segment analysis grouped by:
  - PropertyType and PropertySubType
  - CountyOrParish and MLSAreaMajor
  - ListOfficeName and BuyerOfficeName (competitive intelligence)
- Downloads California school district boundary GeoJSON from the California government open data portal
- Performs spatial join using geopandas to assign each property a school district based on its latitude and longitude coordinates
- Saves final datasets as:
  - sold_week6.csv
  - listings_week6.csv

---

## Requirements

Python 3.x

Install required packages:

```
pip install requests pandas
```
