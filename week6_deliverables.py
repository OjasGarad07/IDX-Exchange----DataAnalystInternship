import pandas as pd
import geopandas as gpd
import os
import ssl
import urllib.request

folder = '/Users/ojasgarad/Desktop/CRMLS/'

# Load cleaned datasets from Weeks 4-5
sold = pd.read_csv(folder + 'sold_week4_5.csv', low_memory=False)
listings = pd.read_csv(folder + 'listings_week4_5.csv', low_memory=False)

print('Sold shape:', sold.shape)
print('Listings shape:', listings.shape)

# ── STEP 1: Convert Date Fields to Datetime ───────────────────────────────────
date_fields = ['CloseDate', 'PurchaseContractDate', 'ListingContractDate', 'ContractStatusChangeDate']

for col in date_fields:
    if col in sold.columns:
        sold[col] = pd.to_datetime(sold[col], errors='coerce')
    if col in listings.columns:
        listings[col] = pd.to_datetime(listings[col], errors='coerce')

# ── STEP 2: Feature Engineering ──────────────────────────────────────────────

# Price Ratio — ClosePrice / OriginalListPrice
sold['price_ratio'] = sold['ClosePrice'] / sold['OriginalListPrice']

# Price Per Square Foot — ClosePrice / LivingArea
sold['price_per_sqft'] = sold['ClosePrice'] / sold['LivingArea']

# Close to Original List Ratio
sold['close_to_original_list_ratio'] = sold['ClosePrice'] / sold['OriginalListPrice']

# Listing to Contract Days — days from listing to accepted offer
sold['listing_to_contract_days'] = (sold['PurchaseContractDate'] - sold['ListingContractDate']).dt.days

# Contract to Close Days — escrow and closing period
sold['contract_to_close_days'] = (sold['CloseDate'] - sold['PurchaseContractDate']).dt.days

# Year, Month, YrMo derived from CloseDate
sold['Year'] = sold['CloseDate'].dt.year
sold['Month'] = sold['CloseDate'].dt.month
sold['YrMo'] = sold['CloseDate'].dt.to_period('M').astype(str)

print('\nSample of engineered metrics:')
print(sold[['CloseDate', 'ClosePrice', 'OriginalListPrice', 'LivingArea',
            'price_ratio', 'price_per_sqft', 'listing_to_contract_days',
            'contract_to_close_days', 'Year', 'Month', 'YrMo']].head())

# ── STEP 3: Segment Analysis ──────────────────────────────────────────────────

# By PropertyType and PropertySubType
print('\nMedian ClosePrice by PropertyType:')
print(sold.groupby('PropertyType')['ClosePrice'].median().sort_values(ascending=False))

print('\nMedian ClosePrice by PropertySubType:')
print(sold.groupby('PropertySubType')['ClosePrice'].median().sort_values(ascending=False).head(10))

# By CountyOrParish and MLSAreaMajor
print('\nMedian ClosePrice by CountyOrParish:')
print(sold.groupby('CountyOrParish')['ClosePrice'].median().sort_values(ascending=False).head(10))

print('\nMedian ClosePrice by MLSAreaMajor:')
print(sold.groupby('MLSAreaMajor')['ClosePrice'].median().sort_values(ascending=False).head(10))

# By ListOfficeName and BuyerOfficeName
print('\nTop 10 Listing Offices by Sales Volume:')
print(sold.groupby('ListOfficeName')['ClosePrice'].sum().sort_values(ascending=False).head(10))

print('\nTop 10 Buyer Offices by Sales Volume:')
print(sold.groupby('BuyerOfficeName')['ClosePrice'].sum().sort_values(ascending=False).head(10))

# ── STEP 4: School District Joining ──────────────────────────────────────────
geojson_url = "https://data.ca.gov/dataset/california-school-district-areas-2024-25/resource/7dfaf005-58eb-45db-93b1-7aff091b2172/download/DistrictAreas2526.geojson"

ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

print('\nDownloading school district boundaries...')
with urllib.request.urlopen(geojson_url, context=ssl_context) as response:
    districts = gpd.read_file(response)

# Filter to Unified school districts only
districts = districts[districts['DistrictTy'] == 'Unified']
print('Unified school districts found:', len(districts))

# Convert sold and listings to GeoDataFrames using Latitude/Longitude
sold_valid_coords = sold.dropna(subset=['Latitude', 'Longitude']).copy()
listings_valid_coords = listings.dropna(subset=['Latitude', 'Longitude']).copy()

sold_geo = gpd.GeoDataFrame(
    sold_valid_coords,
    geometry=gpd.points_from_xy(sold_valid_coords['Longitude'], sold_valid_coords['Latitude']),
    crs='EPSG:4326'
)

listing_geo = gpd.GeoDataFrame(
    listings_valid_coords,
    geometry=gpd.points_from_xy(listings_valid_coords['Longitude'], listings_valid_coords['Latitude']),
    crs='EPSG:4326'
)

# Align CRS
districts = districts.to_crs('EPSG:4326')

# Spatial join
sold_with_districts = gpd.sjoin(sold_geo, districts[['DistrictNa', 'geometry']],
                                 how='left', predicate='within')

listing_with_districts = gpd.sjoin(listing_geo, districts[['DistrictNa', 'geometry']],
                                    how='left', predicate='within')

# Add DistrictName back to original dataframes
sold['DistrictName'] = None
sold.loc[sold_valid_coords.index, 'DistrictName'] = sold_with_districts['DistrictNa'].values

listings['DistrictName'] = None
listings.loc[listings_valid_coords.index, 'DistrictName'] = listing_with_districts['DistrictNa'].values

print('Sold properties with district assigned:', sold['DistrictName'].notna().sum())
print('Listing properties with district assigned:', listings['DistrictName'].notna().sum())

# ── STEP 5: Save Final Datasets ───────────────────────────────────────────────
sold.to_csv(folder + 'sold_week6.csv', index=False)
listings.to_csv(folder + 'listings_week6.csv', index=False)

print('\nSaved sold_week6.csv and listings_week6.csv')