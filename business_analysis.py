import pandas as pd

# ==========================================
# 1. LOAD FEATURE DATA
# ==========================================

file_path = "data/processed/retail_features.csv"

df = pd.read_csv(file_path)

print("Rows loaded:", len(df))


# ==========================================
# 2. TOTAL REVENUE
# ==========================================

total_revenue = df["Revenue"].sum()

print("\n==============================")
print("TOTAL REVENUE")
print("==============================")

print(f"£{total_revenue:,.2f}")


# ==========================================
# 3. TOP COUNTRIES BY REVENUE
# ==========================================

country_revenue = (
    df.groupby("Country")["Revenue"]
    .sum()
    .sort_values(ascending=False)
    .head(10)
)

print("\n==============================")
print("TOP 10 COUNTRIES")
print("==============================")

print(country_revenue)


# ==========================================
# 4. TOP PRODUCTS BY REVENUE
# ==========================================

product_revenue = (
    df.groupby("Description")["Revenue"]
    .sum()
    .sort_values(ascending=False)
    .head(10)
)

print("\n==============================")
print("TOP 10 PRODUCTS BY REVENUE")
print("==============================")

print(product_revenue)


# ==========================================
# 5. MONTHLY REVENUE
# ==========================================

monthly_revenue = (
    df.groupby(["Year", "Month"])["Revenue"]
    .sum()
    .sort_values(ascending=False)
)

print("\n==============================")
print("TOP MONTHS BY REVENUE")
print("==============================")

print(monthly_revenue.head(10))


# ==========================================
# 6. TOP CUSTOMERS
# ==========================================

customer_revenue = (
    df.dropna(subset=["Customer ID"])
    .groupby("Customer ID")["Revenue"]
    .sum()
    .sort_values(ascending=False)
    .head(10)
)

print("\n==============================")
print("TOP 10 CUSTOMERS")
print("==============================")

print(customer_revenue)


# ==========================================
# 7. TOP PRODUCTS BY QUANTITY
# ==========================================

product_quantity = (
    df.groupby("Description")["Quantity"]
    .sum()
    .sort_values(ascending=False)
    .head(10)
)

print("\n==============================")
print("TOP 10 PRODUCTS BY QUANTITY")
print("==============================")

print(product_quantity)