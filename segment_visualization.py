import pandas as pd
import matplotlib.pyplot as plt


# ==========================================
# LOAD CUSTOMER SEGMENTS
# ==========================================

df = pd.read_csv(
    "data/processed/customer_segments.csv"
)


# ==========================================
# CUSTOMER COUNT BY SEGMENT
# ==========================================

segment_counts = (
    df["Segment"]
    .value_counts()
)


# ==========================================
# CREATE CHART
# ==========================================

plt.figure(figsize=(10, 6))

segment_counts.sort_values().plot(
    kind="barh"
)

plt.title("Customer Segments")
plt.xlabel("Number of Customers")
plt.ylabel("Segment")

plt.tight_layout()


# ==========================================
# SAVE CHART
# ==========================================

output_file = (
    "data/processed/customer_segments.png"
)

plt.savefig(
    output_file,
    dpi=150
)

plt.close()


print("\n================================")
print("SEGMENT VISUALIZATION COMPLETE")
print("================================")

print("Saved to:")
print(output_file)