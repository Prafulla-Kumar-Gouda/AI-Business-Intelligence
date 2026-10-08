import pandas as pd
import numpy as np

from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans


# ==========================================
# 1. LOAD DATA
# ==========================================

print("Loading data...")

df = pd.read_csv(
    "data/processed/retail_features.csv"
)

df["InvoiceDate"] = pd.to_datetime(
    df["InvoiceDate"]
)

print("Rows loaded:", len(df))


# ==========================================
# 2. REMOVE CUSTOMERS WITHOUT CUSTOMER ID
# ==========================================

customer_df = df.dropna(
    subset=["Customer ID"]
).copy()

print(
    "Rows with customer information:",
    len(customer_df)
)


# ==========================================
# 3. CREATE REFERENCE DATE
# ==========================================

reference_date = (
    customer_df["InvoiceDate"].max()
    + pd.Timedelta(days=1)
)


# ==========================================
# 4. CREATE RFM FEATURES
# ==========================================

rfm = customer_df.groupby(
    "Customer ID"
).agg({

    "InvoiceDate": lambda x:
        (reference_date - x.max()).days,

    "Invoice": "nunique",

    "Revenue": "sum"

})


# Rename columns

rfm.columns = [
    "Recency",
    "Frequency",
    "Monetary"
]


print("\nRFM DATA:")
print(rfm.head())


# ==========================================
# 5. REMOVE INVALID VALUES
# ==========================================

rfm = rfm[
    (rfm["Frequency"] > 0) &
    (rfm["Monetary"] > 0)
]


# ==========================================
# 6. LOG TRANSFORMATION
# ==========================================

rfm_log = np.log1p(rfm)


# ==========================================
# 7. STANDARDIZE FEATURES
# ==========================================

scaler = StandardScaler()

rfm_scaled = scaler.fit_transform(
    rfm_log
)


# ==========================================
# 8. K-MEANS CLUSTERING
# ==========================================

print("\nRunning K-Means...")

kmeans = KMeans(
    n_clusters=4,
    random_state=42,
    n_init=10
)

rfm["Cluster"] = kmeans.fit_predict(
    rfm_scaled
)


# ==========================================
# 9. SHOW CLUSTER SUMMARY
# ==========================================

print("\n==============================")
print("CUSTOMER SEGMENTS")
print("==============================")

summary = rfm.groupby(
    "Cluster"
)[
    ["Recency", "Frequency", "Monetary"]
].mean()

print(summary)


# ==========================================
# 10. CUSTOMER COUNT PER CLUSTER
# ==========================================

print("\nCustomers per segment:")

print(
    rfm["Cluster"]
    .value_counts()
    .sort_index()
)


# ==========================================
# 11. SAVE RESULTS
# ==========================================

output_file = (
    "data/processed/customer_segments.csv"
)

# ==========================================
# 12. ASSIGN BUSINESS-FRIENDLY SEGMENT NAMES
# ==========================================

segment_names = {
    0: "At Risk / Inactive",
    1: "Regular Customers",
    2: "Potential High Value",
    3: "VIP / Loyal Customers"
}

rfm["Segment"] = rfm["Cluster"].map(segment_names)


# ==========================================
# 13. SAVE FINAL CUSTOMER SEGMENTS
# ==========================================

output_file = (
    "data/processed/customer_segments.csv"
)

rfm.to_csv(output_file)


# ==========================================
# 14. SHOW SEGMENT SUMMARY
# ==========================================

print("\n==============================")
print("FINAL CUSTOMER SEGMENTS")
print("==============================")

segment_summary = (
    rfm.groupby("Segment")
    .agg(
        Customers=("Segment", "count"),
        Avg_Recency=("Recency", "mean"),
        Avg_Frequency=("Frequency", "mean"),
        Avg_Monetary=("Monetary", "mean")
    )
    .sort_values(
        "Avg_Monetary",
        ascending=False
    )
)

print(segment_summary)


# ==========================================
# COMPLETE
# ==========================================

print("\n==============================")
print("SEGMENTATION COMPLETE")
print("==============================")

print(
    "Saved to:",
    output_file
)