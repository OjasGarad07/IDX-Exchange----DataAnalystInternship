import pandas as pd
import os

# Path to your CRMLS folder
folder = '/Users/ojasgarad/Desktop/CRMLS/'

# ── LISTINGS ──────────────────────────────────────────────────────────────────

listing_files = [
    'CRMLSListing202403.csv', 'CRMLSListing202404.csv', 'CRMLSListing202405.csv',
    'CRMLSListing202406.csv', 'CRMLSListing202407.csv', 'CRMLSListing202408.csv',
    'CRMLSListing202409.csv', 'CRMLSListing202410.csv', 'CRMLSListing202411.csv',
    'CRMLSListing202412.csv', 'CRMLSListing202501.csv', 'CRMLSListing202502.csv',
    'CRMLSListing202503.csv', 'CRMLSListing202504.csv', 'CRMLSListing202505.csv',
    'CRMLSListing202506.csv', 'CRMLSListing202507.csv', 'CRMLSListing202508.csv',
    'CRMLSListing202509.csv', 'CRMLSListing202510.csv', 'CRMLSListing202511.csv',
    'CRMLSListing202512.csv', 'CRMLSListing202601.csv', 'CRMLSListing202602.csv',
    'CRMLSListing202603.csv', 'CRMLSListing202604.csv'
]

listing_dfs = []
for f in listing_files:
    path = folder + f
    if os.path.exists(path):
        df = pd.read_csv(path)
        listing_dfs.append(df)
    else:
        print('Missing listing file:', f)

listings = pd.concat(listing_dfs)
print('Listings rows before filter:', len(listings))

listings = listings[listings['PropertyType'] == 'Residential']
print('Listings rows after Residential filter:', len(listings))

listings.to_csv(folder + 'CRMLSListingCombined.csv', index=False)
print('Saved CRMLSListingCombined.csv')


# ── SOLD ──────────────────────────────────────────────────────────────────────

sold_files = [
    'CRMLSSold202401.csv', 'CRMLSSold202402.csv', 'CRMLSSold202403.csv',
    'CRMLSSold202404.csv', 'CRMLSSold202405.csv', 'CRMLSSold202406.csv',
    'CRMLSSold202407.csv', 'CRMLSSold202408.csv', 'CRMLSSold202409.csv',
    'CRMLSSold202410.csv', 'CRMLSSold202411.csv', 'CRMLSSold202412.csv',
    'CRMLSSold202501.csv', 'CRMLSSold202502.csv', 'CRMLSSold202503.csv',
    'CRMLSSold202504.csv', 'CRMLSSold202505.csv', 'CRMLSSold202506.csv',
    'CRMLSSold202507.csv', 'CRMLSSold202508.csv', 'CRMLSSold202509.csv',
    'CRMLSSold202510.csv', 'CRMLSSold202511.csv', 'CRMLSSold202512.csv',
    'CRMLSSold202601.csv', 'CRMLSSold202602.csv', 'CRMLSSold202603.csv',
    'CRMLSSold202604.csv'
]

sold_dfs = []
for f in sold_files:
    path = folder + f
    if os.path.exists(path):
        df = pd.read_csv(path)
        sold_dfs.append(df)
    else:
        print('Missing sold file:', f)

sold = pd.concat(sold_dfs)
print('Sold rows before filter:', len(sold))

sold = sold[sold['PropertyType'] == 'Residential']
print('Sold rows after Residential filter:', len(sold))

sold.to_csv(folder + 'CRMLSSoldCombined.csv', index=False)
print('Saved CRMLSSoldCombined.csv')