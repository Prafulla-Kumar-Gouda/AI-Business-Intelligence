import pandas as pd

# ==========================================
# 1. LOAD DATA
# ==========================================

file_path = "data/raw/online_retail_II.xlsx"

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

print("Original rows:", len(df))


# ==========================================
# 2. REMOVE DUPLICATES
# ==========================================

df = df.drop_duplicates()

print("After removing duplicates:", len(df))


# ==========================================
# 3. REMOVE INVALID PRICES
# ==========================================

df = df[df["Price"] > 0]

print("After removing invalid prices:", len(df))


# ==========================================
# 4. REMOVE INVALID QUANTITIES
# ==========================================

df = df[df["Quantity"] > 0]

print("After removing invalid quantities:", len(df))


# ==========================================
# 5. REMOVE CANCELLED INVOICES
# ==========================================

df = df[
    ~df["Invoice"].astype(str).str.startswith("C")
]

print("After removing cancelled invoices:", len(df))


# ==========================================
# 6. CLEAN DESCRIPTION
# ==========================================

df["Description"] = df["Description"].fillna("Unknown Product")

df["Description"] = (
    df["Description"]
    .astype(str)
    .str.strip()
)


# ==========================================
# 7. CREATE REVENUE COLUMN
# ==========================================

df["Revenue"] = df["Quantity"] * df["Price"]


# ==========================================
# 8. SAVE CLEAN DATA
# ==========================================

output_file = "data/processed/retail_cleaned.csv"

df.to_csv(
    output_file,
    index=False
)

print("\n================================")
print("CLEANING COMPLETE")
print("================================")

print("Final rows:", len(df))
print("Final columns:", len(df.columns))
print("Saved to:", output_file)