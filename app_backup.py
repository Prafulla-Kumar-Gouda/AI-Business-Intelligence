import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# ==============================
# PAGE CONFIGURATION
# ==============================

st.set_page_config(
    page_title="AI Business Intelligence",
    page_icon="📊",
    layout="wide"
)

# ==============================
# TITLE
# ==============================

st.title("📊 AI Business Intelligence Dashboard")
st.markdown(
    "### Retail Sales & Customer Intelligence Platform"
)

st.write(
    "This dashboard analyzes retail transactions, revenue trends, "
    "products, customers and customer segments."
)

# ==============================
# LOAD DATA
# ==============================

@st.cache_data
def load_data():

    df = pd.read_csv(
        "data/processed/retail_features.csv",
        low_memory=False
    )

    segments = pd.read_csv(
        "data/processed/customer_segments.csv"
    )

    df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"])

    return df, segments


df, segments = load_data()

# ==============================
# SIDEBAR
# ==============================

st.sidebar.title("🎛️ Dashboard Controls")

countries = sorted(df["Country"].dropna().unique())

selected_country = st.sidebar.selectbox(
    "Select Country",
    ["All Countries"] + countries
)

# Filter data

if selected_country != "All Countries":
    filtered_df = df[df["Country"] == selected_country]
else:
    filtered_df = df.copy()

# ==============================
# KPI CALCULATIONS
# ==============================

total_revenue = filtered_df["Revenue"].sum()

total_orders = filtered_df["Invoice"].nunique()

total_customers = filtered_df["Customer ID"].nunique()

total_products = filtered_df["StockCode"].nunique()

# ==============================
# KPI CARDS
# ==============================

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "💰 Total Revenue",
    f"£{total_revenue:,.0f}"
)

col2.metric(
    "🧾 Orders",
    f"{total_orders:,}"
)

col3.metric(
    "👥 Customers",
    f"{total_customers:,}"
)

col4.metric(
    "📦 Products",
    f"{total_products:,}"
)

st.divider()

# ==============================
# MONTHLY REVENUE
# ==============================

st.subheader("📈 Monthly Revenue Trend")

monthly_revenue = (
    filtered_df
    .groupby(
        filtered_df["InvoiceDate"].dt.to_period("M")
    )["Revenue"]
    .sum()
)

monthly_revenue.index = monthly_revenue.index.astype(str)

fig, ax = plt.subplots(figsize=(12, 5))

ax.plot(
    monthly_revenue.index,
    monthly_revenue.values,
    marker="o"
)

ax.set_xlabel("Month")
ax.set_ylabel("Revenue")

ax.set_title("Monthly Revenue")

plt.xticks(rotation=45)

plt.tight_layout()

st.pyplot(fig)

# ==============================
# TOP COUNTRIES
# ==============================

st.subheader("🌍 Top Countries by Revenue")

country_revenue = (
    filtered_df
    .groupby("Country")["Revenue"]
    .sum()
    .sort_values(ascending=False)
    .head(10)
)

fig, ax = plt.subplots(figsize=(10, 5))

country_revenue.sort_values().plot(
    kind="barh",
    ax=ax
)

ax.set_xlabel("Revenue")
ax.set_ylabel("Country")

plt.tight_layout()

st.pyplot(fig)

# ==============================
# TOP PRODUCTS
# ==============================

st.subheader("🏆 Top Products by Quantity")

top_products = (
    filtered_df
    .groupby("Description")["Quantity"]
    .sum()
    .sort_values(ascending=False)
    .head(10)
)

st.dataframe(
    top_products.reset_index(),
    use_container_width=True
)

# ==============================
# CUSTOMER SEGMENTS
# ==============================

st.subheader("👥 Customer Segmentation")

segment_summary = (
    segments
    .groupby("Segment")
    .agg(
        Customers=("Customer ID", "count"),
        Avg_Recency=("Recency", "mean"),
        Avg_Frequency=("Frequency", "mean"),
        Avg_Monetary=("Monetary", "mean")
    )
    .reset_index()
)

st.dataframe(
    segment_summary,
    use_container_width=True
)

# ==============================
# SEGMENT CHART
# ==============================

fig, ax = plt.subplots(figsize=(10, 5))

segment_summary.set_index("Segment")["Customers"].plot(
    kind="bar",
    ax=ax
)

ax.set_ylabel("Number of Customers")
ax.set_xlabel("Customer Segment")

plt.xticks(rotation=20)

plt.tight_layout()

st.pyplot(fig)

# ==============================
# FOOTER
# ==============================

st.divider()

st.caption(
    "AI Business Intelligence | Built with Python, Pandas, "
    "Scikit-learn, Matplotlib and Streamlit"
)