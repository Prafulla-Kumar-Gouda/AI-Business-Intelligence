import pandas as pd

# ==========================================
# 1. LOAD CLEAN DATA
# ==========================================

input_file = "data/processed/retail_cleaned.csv"

df = pd.read_csv(input_file)

print("Rows loaded:", len(df))


# ==========================================
# 2. CONVERT DATE COLUMN
# ==========================================

df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"])


# ==========================================
# 3. CREATE REVENUE
# ==========================================

df["Revenue"] = df["Quantity"] * df["Price"]


# ==========================================
# 4. CREATE DATE FEATURES
# ==========================================

df["Year"] = df["InvoiceDate"].dt.year

df["Month"] = df["InvoiceDate"].dt.month

df["Month_Name"] = df["InvoiceDate"].dt.month_name()

df["Day"] = df["InvoiceDate"].dt.day

df["Day_of_Week"] = df["InvoiceDate"].dt.day_name()

df["Hour"] = df["InvoiceDate"].dt.hour


# ==========================================
# 5. CHECK RESULT
# ==========================================

print("\nNew columns created:")

print([
    "Revenue",
    "Year",
    "Month",
    "Month_Name",
    "Day",
    "Day_of_Week",
    "Hour"
])


print("\nSample data:")

print(
    df[
        [
            "Invoice",
            "Description",
            "Quantity",
            "Price",
            "Revenue",
            "InvoiceDate",
            "Year",
            "Month",
            "Month_Name",
            "Day_of_Week",
            "Hour"
        ]
    ].head()
)


# ==========================================
# 6. SAVE FEATURE-ENGINEERED DATA
# ==========================================

output_file = "data/processed/retail_features.csv"

df.to_csv(
    output_file,
    index=False
)

print("\n================================")
print("FEATURE ENGINEERING COMPLETE")
print("================================")

print("Final rows:", len(df))

print("Final columns:", len(df.columns))

print("Saved to:", output_file)