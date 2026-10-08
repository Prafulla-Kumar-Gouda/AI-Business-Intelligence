import pandas as pd

# File location
file_path = "data/raw/online_retail_II.xlsx"

# Read both sheets
df_2009 = pd.read_excel(
    file_path,
    sheet_name="Year 2009-2010"
)

df_2010 = pd.read_excel(
    file_path,
    sheet_name="Year 2010-2011"
)

# Combine both years
df = pd.concat(
    [df_2009, df_2010],
    ignore_index=True
)

print("================================")
print("DATASET OVERVIEW")
print("================================")

print("Total rows:", len(df))
print("Total columns:", len(df.columns))

print("\nColumns:")
print(df.columns.tolist())

print("\nMissing values:")
print(df.isnull().sum())

print("\nDuplicate rows:")
print(df.duplicated().sum())

print("\nQuantity statistics:")
print(df["Quantity"].describe())

print("\nPrice statistics:")
print(df["Price"].describe())

print("\n================================")
print("TRANSACTION ANALYSIS")
print("================================")

# Negative quantity
negative_quantity = (df["Quantity"] < 0).sum()
print("Negative quantity rows:", negative_quantity)

# Zero or negative price
bad_price = (df["Price"] <= 0).sum()
print("Zero/negative price rows:", bad_price)

# Cancelled invoices
cancelled_invoices = df["Invoice"].astype(str).str.startswith("C").sum()
print("Cancelled invoice rows:", cancelled_invoices)

# Unique customers
unique_customers = df["Customer ID"].nunique()
print("Unique customers:", unique_customers)

# Unique products
unique_products = df["StockCode"].nunique()
print("Unique products:", unique_products)

# Countries
unique_countries = df["Country"].nunique()
print("Countries:", unique_countries)

# Customer ID availability
customer_id_available = df["Customer ID"].notna().sum()
print("Rows with Customer ID:", customer_id_available)

customer_id_missing = df["Customer ID"].isna().sum()
print("Rows without Customer ID:", customer_id_missing)