import pandas as pd
import os

folder = '/Users/ojasgarad/Desktop/CRMLS/'

# Load the EDA cleaned datasets from Week 2-3
sold = pd.read_csv(folder + 'sold_eda.csv', low_memory=False)
listings = pd.read_csv(folder + 'listing_eda.csv', low_memory=False)

print('Sold shape:', sold.shape)
print('Listings shape:', listings.shape)

# ── STEP 1: Convert Date Fields to Datetime ───────────────────────────────────
date_fields = ['CloseDate', 'PurchaseContractDate', 'ListingContractDate', 'ContractStatusChangeDate']

for col in date_fields:
    if col in sold.columns:
        sold[col] = pd.to_datetime(sold[col], errors='coerce')
        print(f'Sold - {col}: {sold[col].dtype}')

for col in date_fields:
    if col in listings.columns:
        listings[col] = pd.to_datetime(listings[col], errors='coerce')
        print(f'Listings - {col}: {listings[col].dtype}')

# ── STEP 2: Drop Redundant and Unnecessary Columns ───────────────────────────
# Dropping columns that are duplicates, metadata only, or not needed for analysis

cols_to_drop = [
    'BuyerAgentAOR', 'ListAgentAOR', 'BuyerOfficeAOR',
    'ListingKeyNumeric', 'StreetNumberNumeric',
    'OriginatingSystemName', 'OriginatingSystemSubName',
    'BuyerAgencyCompensationType', 'BuyerAgencyCompensation',
    'latfilled', 'lonfilled'
]

sold_drop = [col for col in cols_to_drop if col in sold.columns]
sold = sold.drop(columns=sold_drop)
print('\nSold columns dropped:', sold_drop)

listings_drop = [col for col in cols_to_drop if col in listings.columns]
listings = listings.drop(columns=listings_drop)
print('Listings columns dropped:', listings_drop)

# ── STEP 3: Handle .1 Duplicate Columns in Listings ──────────────────────────
listing_dupes = [col for col in listings.columns if col.endswith('.1')]
for col in listing_dupes:
    original = col.replace('.1', '')
    if original in listings.columns:
        same = listings[col].equals(listings[original])
        print(f'{original} vs {col}: same values = {same}')
    else:
        print(f'{col}: no original column found')

listings = listings.drop(columns=listing_dupes)
print('Listings .1 duplicate columns dropped:', listing_dupes)

# ── STEP 4: Check Missing Values in Key Fields ───────────────────────────────
key_fields = ['ListOfficeName', 'BuyerOfficeName', 'ListAgentFullName',
              'BuyerAgentFirstName', 'BuyerAgentLastName',
              'Latitude', 'Longitude', 'PropertySubType', 'MLSAreaMajor']

print('\nSold missing % for key fields:')
for col in key_fields:
    if col in sold.columns:
        pct = round(sold[col].isnull().sum() / len(sold) * 100, 2)
        print(f'{col}: {pct}%')

print('\nListings missing % for key fields:')
for col in key_fields:
    if col in listings.columns:
        pct = round(listings[col].isnull().sum() / len(listings) * 100, 2)
        print(f'{col}: {pct}%')

# ── STEP 5: Drop Rows Where Core Fields are Null ─────────────────────────────
core_fields = ['LivingArea', 'City', 'BathroomsTotalInteger', 'YearBuilt']

print('\nSold rows before core field null drop:', len(sold))
sold = sold.dropna(subset=core_fields)
print('Sold rows after core field null drop:', len(sold))

print('Listings rows before core field null drop:', len(listings))
listings = listings.dropna(subset=core_fields)
print('Listings rows after core field null drop:', len(listings))

# ── STEP 6: Ensure Numeric Fields are Properly Typed ─────────────────────────
numeric_fields = ['ClosePrice', 'ListPrice', 'OriginalListPrice', 'LivingArea',
                  'LotSizeAcres', 'BedroomsTotal', 'BathroomsTotalInteger', 'DaysOnMarket']

for col in numeric_fields:
    if col in sold.columns:
        sold[col] = pd.to_numeric(sold[col], errors='coerce')
    if col in listings.columns:
        listings[col] = pd.to_numeric(listings[col], errors='coerce')

# Convert integer fields to Int64
int_fields = ['BedroomsTotal', 'BathroomsTotalInteger', 'YearBuilt']

for col in int_fields:
    if col in sold.columns:
        sold[col] = sold[col].astype('Int64')
    if col in listings.columns:
        listings[col] = listings[col].astype('Int64')

print('\nSold after int conversion:')
for col in int_fields:
    print(f'{col}: {sold[col].dtype}')

print('\nListings after int conversion:')
for col in int_fields:
    print(f'{col}: {listings[col].dtype}')

# ── STEP 7: Flag Invalid Numeric Values ──────────────────────────────────────
sold['invalid_closeprice'] = sold['ClosePrice'] <= 0
sold['invalid_livingarea'] = sold['LivingArea'] <= 0
sold['invalid_dom'] = sold['DaysOnMarket'] < 0
sold['invalid_bedrooms'] = sold['BedroomsTotal'] < 0
sold['invalid_bathrooms'] = sold['BathroomsTotalInteger'] < 0

listings['invalid_listprice'] = listings['ListPrice'] <= 0
listings['invalid_livingarea'] = listings['LivingArea'] <= 0
listings['invalid_dom'] = listings['DaysOnMarket'] < 0
listings['invalid_bedrooms'] = listings['BedroomsTotal'] < 0
listings['invalid_bathrooms'] = listings['BathroomsTotalInteger'] < 0

print('\nSold invalid value counts:')
print('ClosePrice <= 0:', sold['invalid_closeprice'].sum())
print('LivingArea <= 0:', sold['invalid_livingarea'].sum())
print('DaysOnMarket < 0:', sold['invalid_dom'].sum())
print('Bedrooms < 0:', sold['invalid_bedrooms'].sum())
print('Bathrooms < 0:', sold['invalid_bathrooms'].sum())

print('\nListings invalid value counts:')
print('ListPrice <= 0:', listings['invalid_listprice'].sum())
print('LivingArea <= 0:', listings['invalid_livingarea'].sum())
print('DaysOnMarket < 0:', listings['invalid_dom'].sum())
print('Bedrooms < 0:', listings['invalid_bedrooms'].sum())
print('Bathrooms < 0:', listings['invalid_bathrooms'].sum())

# ── STEP 8: Remove Invalid Records ───────────────────────────────────────────
sold_clean = sold[
    (sold['invalid_closeprice'] == False) &
    (sold['invalid_livingarea'] == False) &
    (sold['invalid_dom'] == False)
].copy()

listings_clean = listings[
    (listings['invalid_livingarea'] == False) &
    (listings['invalid_dom'] == False)
].copy()

print('\nSold rows before:', len(sold))
print('Sold rows after:', len(sold_clean))
print('Sold rows removed:', len(sold) - len(sold_clean))

print('\nListings rows before:', len(listings))
print('Listings rows after:', len(listings_clean))
print('Listings rows removed:', len(listings) - len(listings_clean))

# ── STEP 9: Drop Flag Columns ─────────────────────────────────────────────────
flag_cols_sold = ['invalid_closeprice', 'invalid_livingarea', 'invalid_dom',
                  'invalid_bedrooms', 'invalid_bathrooms']

flag_cols_listings = ['invalid_listprice', 'invalid_livingarea', 'invalid_dom',
                      'invalid_bedrooms', 'invalid_bathrooms']

sold_clean = sold_clean.drop(columns=flag_cols_sold)
listings_clean = listings_clean.drop(columns=flag_cols_listings)

print('\nSold final shape:', sold_clean.shape)
print('Listings final shape:', listings_clean.shape)

# ── STEP 10: Save Clean Datasets ──────────────────────────────────────────────
sold_clean.to_csv(folder + 'sold_clean.csv', index=False)
listings_clean.to_csv(folder + 'listings_clean.csv', index=False)

print('\nSaved sold_clean.csv and listings_clean.csv')

# ── WEEK 5: Date Consistency Checks ──────────────────────────────────────────

# Flag records where dates are in the wrong logical order
sold_clean['listing_after_close_flag'] = sold_clean['ListingContractDate'] > sold_clean['CloseDate']
sold_clean['purchase_after_close_flag'] = sold_clean['PurchaseContractDate'] > sold_clean['CloseDate']
sold_clean['negative_timeline_flag'] = sold_clean['PurchaseContractDate'] < sold_clean['ListingContractDate']

print('Date Consistency Checks - Sold:')
print('ListingContractDate after CloseDate:', sold_clean['listing_after_close_flag'].sum())
print('PurchaseContractDate after CloseDate:', sold_clean['purchase_after_close_flag'].sum())
print('PurchaseContractDate before ListingContractDate:', sold_clean['negative_timeline_flag'].sum())

# ── WEEK 5: Geographic Data Checks ───────────────────────────────────────────

# Sold geographic checks
sold_clean['flag_missing_coords'] = sold_clean['Latitude'].isnull() | sold_clean['Longitude'].isnull()
sold_clean['flag_zero_coords'] = (sold_clean['Latitude'] == 0) | (sold_clean['Longitude'] == 0)
sold_clean['flag_positive_longitude'] = sold_clean['Longitude'] > 0

print('\nGeographic Data Checks - Sold:')
print('Missing coordinates:', sold_clean['flag_missing_coords'].sum())
print('Zero coordinates:', sold_clean['flag_zero_coords'].sum())
print('Positive longitude (should be negative for CA):', sold_clean['flag_positive_longitude'].sum())

# Listings geographic checks
listings_clean['flag_missing_coords'] = listings_clean['Latitude'].isnull() | listings_clean['Longitude'].isnull()
listings_clean['flag_zero_coords'] = (listings_clean['Latitude'] == 0) | (listings_clean['Longitude'] == 0)
listings_clean['flag_positive_longitude'] = listings_clean['Longitude'] > 0

print('\nGeographic Data Checks - Listings:')
print('Missing coordinates:', listings_clean['flag_missing_coords'].sum())
print('Zero coordinates:', listings_clean['flag_zero_coords'].sum())
print('Positive longitude (should be negative for CA):', listings_clean['flag_positive_longitude'].sum())

# ── SAVE FINAL DATASETS ───────────────────────────────────────────────────────
sold_clean.to_csv(folder + 'sold_week4_5.csv', index=False)
listings_clean.to_csv(folder + 'listings_week4_5.csv', index=False)

print('\nSaved sold_week4_5.csv and listings_week4_5.csv')