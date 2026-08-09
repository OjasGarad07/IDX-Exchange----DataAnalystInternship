import pandas as pd
import os

folder = '/Users/ojasgarad/Desktop/CRMLS/'

# Load the Week 6 cleaned datasets
sold = pd.read_csv(folder + 'sold_week6.csv', low_memory=False)
listings = pd.read_csv(folder + 'listings_week6.csv', low_memory=False)

print('Sold shape:', sold.shape)
print('Listings shape:', listings.shape)

# ── IQR OUTLIER DETECTION ─────────────────────────────────────────────────────
# The IQR method flags records that fall outside Q1 - 1.5*IQR and Q3 + 1.5*IQR
# Rather than deleting records, we flag them and create a separate filtered dataset

fields_to_check = ['ClosePrice', 'LivingArea', 'DaysOnMarket']

for col in fields_to_check:
    if col in sold.columns:
        Q1 = sold[col].quantile(0.25)
        Q3 = sold[col].quantile(0.75)
        IQR = Q3 - Q1
        lower = Q1 - 1.5 * IQR
        upper = Q3 + 1.5 * IQR
        sold[f'outlier_{col}'] = ~sold[col].between(lower, upper)
        print(f'Sold {col} — Q1: {Q1}, Q3: {Q3}, IQR: {IQR}, Lower: {lower}, Upper: {upper}')
        print(f'Sold {col} outliers flagged: {sold[f"outlier_{col}"].sum()}')

for col in fields_to_check:
    if col in listings.columns:
        Q1 = listings[col].quantile(0.25)
        Q3 = listings[col].quantile(0.75)
        IQR = Q3 - Q1
        lower = Q1 - 1.5 * IQR
        upper = Q3 + 1.5 * IQR
        listings[f'outlier_{col}'] = ~listings[col].between(lower, upper)
        print(f'Listings {col} — Q1: {Q1}, Q3: {Q3}, IQR: {IQR}, Lower: {lower}, Upper: {upper}')
        print(f'Listings {col} outliers flagged: {listings[f"outlier_{col}"].sum()}')

# ── DATASET SIZE AND MEDIAN BEFORE FILTERING ──────────────────────────────────
print('\nBefore filtering:')
print('Sold rows:', len(sold))
print('Sold median ClosePrice:', sold['ClosePrice'].median())
print('Sold median LivingArea:', sold['LivingArea'].median())
print('Sold median DaysOnMarket:', sold['DaysOnMarket'].median())

print('\nListings rows:', len(listings))
print('Listings median ListPrice:', listings['ListPrice'].median())
print('Listings median LivingArea:', listings['LivingArea'].median())
print('Listings median DaysOnMarket:', listings['DaysOnMarket'].median())

# ── CREATE FILTERED ANALYSIS DATASET ─────────────────────────────────────────
# Remove flagged outliers to create a clean analysis-ready dataset
# Raw dataset with flags is preserved above

sold_filtered = sold[
    (sold['outlier_ClosePrice'] == False) &
    (sold['outlier_LivingArea'] == False) &
    (sold['outlier_DaysOnMarket'] == False)
].copy()

listings_filtered = listings[
    (listings['outlier_LivingArea'] == False) &
    (listings['outlier_DaysOnMarket'] == False)
].copy()

# ── DATASET SIZE AND MEDIAN AFTER FILTERING ───────────────────────────────────
print('\nAfter filtering:')
print('Sold rows:', len(sold_filtered))
print('Sold rows removed:', len(sold) - len(sold_filtered))
print('Sold median ClosePrice:', sold_filtered['ClosePrice'].median())
print('Sold median LivingArea:', sold_filtered['LivingArea'].median())
print('Sold median DaysOnMarket:', sold_filtered['DaysOnMarket'].median())

print('\nListings rows:', len(listings_filtered))
print('Listings rows removed:', len(listings) - len(listings_filtered))
print('Listings median ListPrice:', listings_filtered['ListPrice'].median())
print('Listings median LivingArea:', listings_filtered['LivingArea'].median())
print('Listings median DaysOnMarket:', listings_filtered['DaysOnMarket'].median())

# ── SAVE BOTH DATASETS ────────────────────────────────────────────────────────
# Save full flagged dataset
sold.to_csv(folder + 'sold_week7_flagged.csv', index=False)
listings.to_csv(folder + 'listings_week7_flagged.csv', index=False)

# Save clean filtered dataset
sold_filtered.to_csv(folder + 'sold_week7_filtered.csv', index=False)
listings_filtered.to_csv(folder + 'listings_week7_filtered.csv', index=False)

print('\nSaved sold_week7_flagged.csv and listings_week7_flagged.csv')
print('Saved sold_week7_filtered.csv and listings_week7_filtered.csv')


# ── WRITTEN COMPARISON ────────────────────────────────────────────────────────
# Sold dataset: 349,271 rows before filtering → 295,541 after (53,730 removed)
# Median ClosePrice: $820,000 before → $780,000 after
# Median LivingArea: 1,643 sq ft before → 1,570 sq ft after
# Median DaysOnMarket: 19 days before → 17 days after
#
# Listings dataset: 510,545 rows before filtering → 444,256 after (66,289 removed)
# Median ListPrice: $849,000 before → $824,900 after
# Median LivingArea: 1,672 sq ft before → 1,623 sq ft after
# Median DaysOnMarket: 10 days before → 9 days after
#
# The drop in median ClosePrice from $820K to $780K after filtering confirms
# that high-value outliers were skewing the market upward. DOM dropping from
# 19 to 17 days shows that properties sitting on the market for extremely long
# periods were inflating the average. The filtered dataset is more representative
# of typical market conditions.