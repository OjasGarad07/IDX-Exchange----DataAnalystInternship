import pandas as pd
import os
import ssl
import urllib.request

pd.set_option('display.float_format', '{:,.2f}'.format)
pd.set_option('display.max_columns', None)

folder = '/Users/ojasgarad/Desktop/CRMLS/'

# Load datasets
sold = pd.read_csv(folder + 'CRMLSSoldCombined.csv', low_memory=False)
listings = pd.read_csv(folder + 'CRMLSListingCombined.csv', low_memory=False)

# ── STEP 1: Dataset Shape ─────────────────────────────────────────────────────
print('Sold Dataset')
print('Rows:', sold.shape[0])
print('Columns:', sold.shape[1])

print('\nListings Dataset')
print('Rows:', listings.shape[0])
print('Columns:', listings.shape[1])

# ── STEP 2: Column Data Types ─────────────────────────────────────────────────
print('\nSold Data Types:')
print(sold.dtypes)

print('\nListings Data Types:')
print(listings.dtypes)

# ── STEP 3: Missing Value Analysis ───────────────────────────────────────────
sold_missing_counts = sold.isnull().sum()
sold_missing_percent = (sold.isnull().mean() * 100).round(2)

listing_missing_counts = listings.isnull().sum()
listing_missing_percent = (listings.isnull().mean() * 100).round(2)

sold_missing_summary = pd.DataFrame({
    'Missing Count': sold_missing_counts,
    'Missing %': sold_missing_percent
}).sort_values('Missing %', ascending=False)

listing_missing_summary = pd.DataFrame({
    'Missing Count': listing_missing_counts,
    'Missing %': listing_missing_percent
}).sort_values('Missing %', ascending=False)

print('\nSold Missing Value Summary:')
print(sold_missing_summary)

print('\nListings Missing Value Summary:')
print(listing_missing_summary)

# ── STEP 4: Flag and Drop High-Null Columns (>90%) ───────────────────────────
sold_flagged = sold_missing_percent[sold_missing_percent > 90]
listing_flagged = listing_missing_percent[listing_missing_percent > 90]

print('\nSold columns with >90% missing:')
print(sold_flagged)

print('\nListings columns with >90% missing:')
print(listing_flagged)

sold_cleaned = sold.drop(columns=sold_flagged.index)
listing_cleaned = listings.drop(columns=listing_flagged.index)

print('\nSold columns before drop:', sold.shape[1])
print('Sold columns after drop:', sold_cleaned.shape[1])

print('\nListings columns before drop:', listings.shape[1])
print('Listings columns after drop:', listing_cleaned.shape[1])

# ── STEP 5: Numeric Distribution Summary ─────────────────────────────────────
numeric_fields = ['ClosePrice', 'ListPrice', 'OriginalListPrice', 'LivingArea',
                  'LotSizeAcres', 'BedroomsTotal', 'BathroomsTotalInteger',
                  'DaysOnMarket', 'YearBuilt']

sold_numeric = [col for col in numeric_fields if col in sold_cleaned.columns]
listing_numeric = [col for col in numeric_fields if col in listing_cleaned.columns]

print('\nSold Numeric Summary:')
print(sold_cleaned[sold_numeric].describe())

print('\nListings Numeric Summary:')
print(listing_cleaned[listing_numeric].describe())

# ── STEP 6: Unique Property Types ────────────────────────────────────────────
print('\nUnique Property Types in Sold:')
print(sold_cleaned['PropertyType'].unique())

print('\nUnique Property Types in Listings:')
print(listing_cleaned['PropertyType'].unique())

# ── STEP 7: Save Cleaned Datasets ────────────────────────────────────────────
sold_cleaned.to_csv(folder + 'sold_eda.csv', index=False)
listing_cleaned.to_csv(folder + 'listing_eda.csv', index=False)
print('\nSaved sold_eda.csv and listing_eda.csv')

# ── STEP 8: Mortgage Rate Enrichment ─────────────────────────────────────────
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

url = "https://fred.stlouisfed.org/graph/fredgraph.csv?id=MORTGAGE30US"

with urllib.request.urlopen(url, context=ssl_context) as response:
    mortgage = pd.read_csv(response)

mortgage.columns = ['date', 'rate_30yr_fixed']
mortgage['date'] = pd.to_datetime(mortgage['date'])

mortgage['year_month'] = mortgage['date'].dt.to_period('M')
mortgage_monthly = (
    mortgage.groupby('year_month')['rate_30yr_fixed']
    .mean()
    .reset_index()
)

sold_cleaned['year_month'] = pd.to_datetime(sold_cleaned['CloseDate'], errors='coerce').dt.to_period('M')
listing_cleaned['year_month'] = pd.to_datetime(listing_cleaned['ListingContractDate'], errors='coerce').dt.to_period('M')

sold_with_rates = sold_cleaned.merge(mortgage_monthly, on='year_month', how='left')
listing_with_rates = listing_cleaned.merge(mortgage_monthly, on='year_month', how='left')

print('\nSold null rates after merge:', sold_with_rates['rate_30yr_fixed'].isnull().sum())
print('Listings null rates after merge:', listing_with_rates['rate_30yr_fixed'].isnull().sum())

print(sold_with_rates[['CloseDate', 'year_month', 'ClosePrice', 'rate_30yr_fixed']].head())

# ── STEP 9: Suggested Intern Questions ───────────────────────────────────────
print('\nMedian ClosePrice:', sold_cleaned['ClosePrice'].median())
print('Mean ClosePrice:', sold_cleaned['ClosePrice'].mean())

print('\nDays on Market Summary:')
print(sold_cleaned['DaysOnMarket'].describe())

sold_valid = sold_cleaned[sold_cleaned['ClosePrice'] > 0].copy()
sold_valid['above_list'] = sold_valid['ClosePrice'] > sold_valid['ListPrice']
above = sold_valid['above_list'].sum()
below = (~sold_valid['above_list']).sum()
total = len(sold_valid)
print('\nHomes sold above list price:', round(above/total*100, 2), '%')
print('Homes sold below list price:', round(below/total*100, 2), '%')

print('\nTop 10 Counties by Median ClosePrice:')
print(sold_cleaned.groupby('CountyOrParish')['ClosePrice'].median().sort_values(ascending=False).head(10))

sold_cleaned['CloseDate'] = pd.to_datetime(sold_cleaned['CloseDate'], errors='coerce')
sold_cleaned['ListingContractDate'] = pd.to_datetime(sold_cleaned['ListingContractDate'], errors='coerce')
sold_cleaned['PurchaseContractDate'] = pd.to_datetime(sold_cleaned['PurchaseContractDate'], errors='coerce')

listing_after_close = (sold_cleaned['ListingContractDate'] > sold_cleaned['CloseDate']).sum()
purchase_after_close = (sold_cleaned['PurchaseContractDate'] > sold_cleaned['CloseDate']).sum()

print('\nRecords where ListingContractDate is after CloseDate:', listing_after_close)
print('Records where PurchaseContractDate is after CloseDate:', purchase_after_close)

# ── STEP 10: Save Enriched Datasets ──────────────────────────────────────────
sold_with_rates.to_csv(folder + 'sold_with_rates.csv', index=False)
listing_with_rates.to_csv(folder + 'listing_with_rates.csv', index=False)
print('\nSaved sold_with_rates.csv and listing_with_rates.csv')
