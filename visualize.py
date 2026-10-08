import pandas as pd
import matplotlib.pyplot as plt

# ==========================================
# LOAD DATA
# ==========================================

print("Loading data...")

df = pd.read_csv("data/processed/retail_features.csv")

# Convert date
df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"])

print("Data loaded successfully!")
print("Rows:", len(df))


# ==========================================
# 1. MONTHLY REVENUE
# ==========================================

print("\nCreating monthly revenue chart...")

monthly = (
    df.groupby(
        df["InvoiceDate"].dt.to_period("M")
    )["Revenue"]
    .sum()
)

plt.figure(figsize=(12, 6))

monthly.plot()

plt.title("Monthly Revenue Trend")
plt.xlabel("Month")
plt.ylabel("Revenue")

plt.xticks(rotation=45)

plt.tight_layout()

plt.savefig(
    "data/processed/monthly_revenue.png",
    dpi=150
)

plt.close()


# ==========================================
# 2. TOP 10 COUNTRIES
# ==========================================

print("Creating country revenue chart...")

countries = (
    df.groupby("Country")["Revenue"]
    .sum()
    .sort_values(ascending=False)
    .head(10)
)

plt.figure(figsize=(10, 6))

countries.sort_values().plot(
    kind="barh"
)

plt.title("Top 10 Countries by Revenue")
plt.xlabel("Revenue")
plt.ylabel("Country")

plt.tight_layout()

plt.savefig(
    "data/processed/top_countries.png",
    dpi=150
)

plt.close()


# ==========================================
# 3. TOP 10 PRODUCTS
# ==========================================

print("Creating product revenue chart...")

products = (
    df.groupby("Description")["Revenue"]
    .sum()
    .sort_values(ascending=False)
    .head(10)
)

plt.figure(figsize=(10, 6))

products.sort_values().plot(
    kind="barh"
)

plt.title("Top 10 Products by Revenue")
plt.xlabel("Revenue")
plt.ylabel("Product")

plt.tight_layout()

plt.savefig(
    "data/processed/top_products.png",
    dpi=150
)

plt.close()


# ==========================================
# 4. TOP 10 CUSTOMERS
# ==========================================

print("Creating customer revenue chart...")

customers = (
    df.dropna(subset=["Customer ID"])
    .groupby("Customer ID")["Revenue"]
    .sum()
    .sort_values(ascending=False)
    .head(10)
)

plt.figure(figsize=(10, 6))

customers.sort_values().plot(
    kind="barh"
)

plt.title("Top 10 Customers by Revenue")
plt.xlabel("Revenue")
plt.ylabel("Customer ID")

plt.tight_layout()

plt.savefig(
    "data/processed/top_customers.png",
    dpi=150
)

plt.close()


# ==========================================
# COMPLETE
# ==========================================

print("\n================================")
print("VISUALIZATION COMPLETE")
print("================================")

print("\nCharts created:")

print("1. monthly_revenue.png")
print("2. top_countries.png")
print("3. top_products.png")
print("4. top_customers.png")

print("\nLocation:")
print("data/processed/")