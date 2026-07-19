import pandas as pd
import os

folder = '/Users/ojasgarad/Desktop/CRMLS/'

# Load the EDA cleaned datasets from Week 2-3
sold = pd.read_csv(folder + 'sold_eda.csv', low_memory=False)
listings = pd.read_csv(folder + 'listing_eda.csv', low_memory=False)

print('Sold shape:', sold.shape)
print('Listings shape:', listings.shape)

# ── STEP 1: Convert Date Fields to Datetime ───────────────────────────────────
# Converting all date fields from string to datetime format so they can be used
# in calculations and consistency checks.

date_fields = ['CloseDate', 'PurchaseContractDate', 'ListingContractDate', 'ContractStatusChangeDate']

for col in date_fields:
    if col in sold.columns:
        sold[col] = pd.to_datetime(sold[col], errors='coerce')
        print(f'Sold - {col}: {sold[col].dtype}')

for col in date_fields:
    if col in listings.columns:
        listings[col] = pd.to_datetime(listings[col], errors='coerce')
        print(f'Listings - {col}: {listings[col].dtype}')

# ── STEP 2: Ensure Numeric Fields are Properly Typed ─────────────────────────
# Checking that key numeric fields are stored as numbers and converting any that aren't.

numeric_fields = ['ClosePrice', 'ListPrice', 'OriginalListPrice', 'LivingArea',
                  'LotSizeAcres', 'BedroomsTotal', 'BathroomsTotalInteger', 'DaysOnMarket']

for col in numeric_fields:
    if col in sold.columns:
        sold[col] = pd.to_numeric(sold[col], errors='coerce')
    if col in listings.columns:
        listings[col] = pd.to_numeric(listings[col], errors='coerce')

print('\nSold numeric dtypes:')
print(sold[numeric_fields].dtypes)

print('\nListings numeric dtypes:')
print(listings[[col for col in numeric_fields if col in listings.columns]].dtypes)

# ── STEP 3: Flag Invalid Numeric Values ──────────────────────────────────────
# Flagging records with invalid values: ClosePrice <= 0, LivingArea <= 0,
# DaysOnMarket < 0, negative Bedrooms or Bathrooms.

print('\nSold rows before invalid value removal:', len(sold))
print('Listings rows before invalid value removal:', len(listings))

# Flag invalid records in sold
sold['invalid_closeprice'] = sold['ClosePrice'] <= 0
sold['invalid_livingarea'] = sold['LivingArea'] <= 0
sold['invalid_dom'] = sold['DaysOnMarket'] < 0
sold['invalid_bedrooms'] = sold['BedroomsTotal'] < 0
sold['invalid_bathrooms'] = sold['BathroomsTotalInteger'] < 0

print('\nSold invalid value counts:')
print('ClosePrice <= 0:', sold['invalid_closeprice'].sum())
print('LivingArea <= 0:', sold['invalid_livingarea'].sum())
print('DaysOnMarket < 0:', sold['invalid_dom'].sum())
print('Bedrooms < 0:', sold['invalid_bedrooms'].sum())
print('Bathrooms < 0:', sold['invalid_bathrooms'].sum())

# Flag invalid records in listings
listings['invalid_listprice'] = listings['ListPrice'] <= 0
listings['invalid_livingarea'] = listings['LivingArea'] <= 0
listings['invalid_dom'] = listings['DaysOnMarket'] < 0
listings['invalid_bedrooms'] = listings['BedroomsTotal'] < 0
listings['invalid_bathrooms'] = listings['BathroomsTotalInteger'] < 0

print('\nListings invalid value counts:')
print('ListPrice <= 0:', listings['invalid_listprice'].sum())
print('LivingArea <= 0:', listings['invalid_livingarea'].sum())
print('DaysOnMarket < 0:', listings['invalid_dom'].sum())
print('Bedrooms < 0:', listings['invalid_bedrooms'].sum())
print('Bathrooms < 0:', listings['invalid_bathrooms'].sum())

# ── STEP 4: Remove Invalid Records ───────────────────────────────────────────
# Removing records flagged as invalid. Row counts before and after are documented.

sold_clean = sold[
    (sold['ClosePrice'] > 0) &
    (sold['LivingArea'] > 0) &
    (sold['DaysOnMarket'] >= 0) &
    (sold['BedroomsTotal'] >= 0) &
    (sold['BathroomsTotalInteger'] >= 0)
].copy()

listings_clean = listings[
    (listings['ListPrice'] > 0) &
    (listings['LivingArea'] > 0) &
    (listings['DaysOnMarket'] >= 0) &
    (listings['BedroomsTotal'] >= 0) &
    (listings['BathroomsTotalInteger'] >= 0)
].copy()

print('\nSold rows before:', len(sold))
print('Sold rows after:', len(sold_clean))
print('Sold rows removed:', len(sold) - len(sold_clean))

print('\nListings rows before:', len(listings))
print('Listings rows after:', len(listings_clean))
print('Listings rows removed:', len(listings) - len(listings_clean))

# ── STEP 5: Drop Flag Columns ─────────────────────────────────────────────────
# Removing the flag columns used for validation since they are no longer needed.

flag_cols_sold = ['invalid_closeprice', 'invalid_livingarea', 'invalid_dom',
                  'invalid_bedrooms', 'invalid_bathrooms']

flag_cols_listings = ['invalid_listprice', 'invalid_livingarea', 'invalid_dom',
                      'invalid_bedrooms', 'invalid_bathrooms']

sold_clean = sold_clean.drop(columns=flag_cols_sold)
listings_clean = listings_clean.drop(columns=flag_cols_listings)

print('\nSold final shape:', sold_clean.shape)
print('Listings final shape:', listings_clean.shape)

# ── STEP 6: Save Clean Datasets ───────────────────────────────────────────────
sold_clean.to_csv(folder + 'sold_clean.csv', index=False)
listings_clean.to_csv(folder + 'listings_clean.csv', index=False)

print('\nSaved sold_clean.csv and listings_clean.csv')