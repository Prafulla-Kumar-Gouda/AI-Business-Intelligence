import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests

from recommendation_engine import build_recommendation_engine


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="AI Business Intelligence",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# CURRENCY CONFIGURATION
# ============================================================

CURRENCIES = {
    "GBP — British Pound (£)": ("GBP", "£"),
    "INR — Indian Rupee (₹)": ("INR", "₹"),
    "USD — US Dollar ($)": ("USD", "$"),
    "EUR — Euro (€)": ("EUR", "€"),
    "JPY — Japanese Yen (¥)": ("JPY", "¥"),
    "AED — UAE Dirham (د.إ)": ("AED", "د.إ"),
    "AUD — Australian Dollar (A$)": ("AUD", "A$"),
    "CAD — Canadian Dollar (C$)": ("CAD", "C$"),
    "SGD — Singapore Dollar (S$)": ("SGD", "S$")
}


# ============================================================
# LOAD MAIN DATA
# ============================================================

@st.cache_data
def load_data():

    df = pd.read_csv(
        "data/processed/retail_features.csv",
        low_memory=False
    )

    segments = pd.read_csv(
        "data/processed/customer_segments.csv",
        low_memory=False
    )

    df["InvoiceDate"] = pd.to_datetime(
        df["InvoiceDate"],
        errors="coerce"
    )

    df["Revenue"] = pd.to_numeric(
        df["Revenue"],
        errors="coerce"
    )

    df["Quantity"] = pd.to_numeric(
        df["Quantity"],
        errors="coerce"
    )

    df["Customer ID"] = pd.to_numeric(
        df["Customer ID"],
        errors="coerce"
    )

    segments["Customer ID"] = pd.to_numeric(
        segments["Customer ID"],
        errors="coerce"
    )

    return df, segments


# ============================================================
# LOAD FORECAST
# ============================================================

@st.cache_data
def load_forecast():

    try:

        forecast = pd.read_csv(
            "data/processed/sales_forecast.csv",
            low_memory=False
        )

        forecast["Month"] = pd.to_datetime(
            forecast["Month"],
            errors="coerce"
        )

        forecast["Forecast_Revenue"] = pd.to_numeric(
            forecast["Forecast_Revenue"],
            errors="coerce"
        )

        forecast = forecast.dropna(
            subset=[
                "Month",
                "Forecast_Revenue"
            ]
        )

        return forecast

    except Exception:

        return pd.DataFrame(
            columns=[
                "Month",
                "Forecast_Revenue"
            ]
        )


# ============================================================
# LOAD RECOMMENDATION ENGINE
# ============================================================

@st.cache_resource
def load_recommendations():

    # Reuse the already cached datasets instead of
    # reading the 120+ MB CSV again.
    retail_data, customer_segments = load_data()

    return build_recommendation_engine(
        retail_data=retail_data,
        customer_segments=customer_segments,
        top_n=10
    )


# ============================================================
# EXCHANGE RATE
# ============================================================

@st.cache_data(ttl=3600)
def get_exchange_rate(currency):

    if currency == "GBP":
        return 1.0, "Original GBP data"

    url = (
        "https://api.frankfurter.dev/v2/rate/gbp/"
        + currency
    )

    try:

        response = requests.get(
            url,
            timeout=10
        )

        response.raise_for_status()

        data = response.json()

        return (
            float(data["rate"]),
            data.get("date", "latest")
        )

    except Exception:

        return None, None


# ============================================================
# LOAD EVERYTHING
# ============================================================

with st.spinner(
    "Loading AI Business Intelligence..."
):

    df, segments = load_data()
    forecast_df = load_forecast()


with st.spinner(
    "Preparing recommendation intelligence..."
):

    recommendation_results = load_recommendations()


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title(
    "🎛️ Dashboard Controls"
)


# ============================================================
# THEME
# ============================================================

st.sidebar.markdown(
    "### 🎨 Appearance"
)

theme = st.sidebar.radio(
    "Choose Theme",
    [
        "🌙 Dark Mode",
        "☀️ Light Mode"
    ],
    index=0
)


if theme == "🌙 Dark Mode":

    background = "#0e1117"
    card = "#161b22"
    border = "#30363d"
    text = "#ffffff"
    muted = "#9aa4b2"
    plot_template = "plotly_dark"

else:

    background = "#f5f7fa"
    card = "#ffffff"
    border = "#d9dee7"
    text = "#1f2937"
    muted = "#5f6b7a"
    plot_template = "plotly_white"


# ============================================================
# THEME CSS
# ============================================================

st.markdown(
    f"""
    <style>

    .stApp {{
        background-color: {background};
        color: {text};
    }}

    [data-testid="stAppViewContainer"] {{
        background-color: {background};
    }}

    [data-testid="stHeader"] {{
        background-color: {background};
    }}

    .block-container {{
        padding-top: 1.5rem;
        padding-bottom: 2rem;
    }}

    h1, h2, h3, h4, h5, h6 {{
        color: {text} !important;
    }}

    [data-testid="stMetric"] {{
        background-color: {card};
        border: 1px solid {border};
        border-radius: 12px;
        padding: 18px;
    }}

    [data-testid="stMetricLabel"] {{
        color: {muted} !important;
    }}

    [data-testid="stMetricValue"] {{
        color: {text} !important;
    }}

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# CURRENCY
# ============================================================

st.sidebar.markdown(
    "### 💱 Currency"
)

currency_name = st.sidebar.selectbox(
    "Display Currency",
    list(CURRENCIES.keys()),
    index=0
)

currency_code, currency_symbol = CURRENCIES[
    currency_name
]

exchange_rate, rate_date = get_exchange_rate(
    currency_code
)


if exchange_rate is None:

    st.sidebar.warning(
        "Live exchange rate unavailable. "
        "Showing original GBP values."
    )

    exchange_rate = 1.0
    currency_code = "GBP"
    currency_symbol = "£"

else:

    if currency_code != "GBP":

        st.sidebar.success(
            f"1 GBP ≈ "
            f"{exchange_rate:,.4f} "
            f"{currency_code}"
        )

        st.sidebar.caption(
            f"Rate date: {rate_date}"
        )


# ============================================================
# COUNTRY
# ============================================================

st.sidebar.markdown(
    "### 🌍 Country"
)

countries = sorted(
    df["Country"]
    .dropna()
    .unique()
    .tolist()
)

selected_country = st.sidebar.selectbox(
    "Select Country",
    ["All Countries"] + countries
)


# ============================================================
# DATE FILTER
# ============================================================

st.sidebar.markdown(
    "### 📅 Date Filter"
)

min_date = (
    df["InvoiceDate"]
    .min()
    .date()
)

max_date = (
    df["InvoiceDate"]
    .max()
    .date()
)

date_mode = st.sidebar.selectbox(
    "Choose period",
    [
        "All Time",
        "Last 30 Days",
        "Last 90 Days",
        "Last 6 Months",
        "Last 12 Months",
        "Custom Range"
    ]
)

start_date = min_date
end_date = max_date


if date_mode == "Last 30 Days":

    start_date = (
        pd.Timestamp(max_date)
        - pd.Timedelta(days=30)
    ).date()


elif date_mode == "Last 90 Days":

    start_date = (
        pd.Timestamp(max_date)
        - pd.Timedelta(days=90)
    ).date()


elif date_mode == "Last 6 Months":

    start_date = (
        pd.Timestamp(max_date)
        - pd.DateOffset(months=6)
    ).date()


elif date_mode == "Last 12 Months":

    start_date = (
        pd.Timestamp(max_date)
        - pd.DateOffset(months=12)
    ).date()


elif date_mode == "Custom Range":

    start_date = st.sidebar.date_input(
        "From",
        value=min_date,
        min_value=min_date,
        max_value=max_date
    )

    end_date = st.sidebar.date_input(
        "To",
        value=max_date,
        min_value=min_date,
        max_value=max_date
    )


if start_date > end_date:

    st.sidebar.error(
        "Start date cannot be after end date."
    )

    st.stop()


# ============================================================
# FILTER DATA
# ============================================================

filtered_df = df.copy()


if selected_country != "All Countries":

    filtered_df = filtered_df[
        filtered_df["Country"]
        == selected_country
    ]


start_timestamp = pd.Timestamp(
    start_date
)

end_timestamp = (
    pd.Timestamp(end_date)
    + pd.Timedelta(days=1)
)


filtered_df = filtered_df[
    (filtered_df["InvoiceDate"] >= start_timestamp)
    &
    (filtered_df["InvoiceDate"] < end_timestamp)
]


if filtered_df.empty:

    st.warning(
        "No data exists for the selected filters."
    )

    st.stop()


filtered_df = filtered_df.copy()

filtered_df["DisplayRevenue"] = (
    filtered_df["Revenue"]
    * exchange_rate
)


# ============================================================
# HEADER
# ============================================================

st.title(
    "📊 AI Business Intelligence"
)

st.subheader(
    "Retail Sales & Customer Intelligence Platform"
)

st.caption(
    "Interactive business analytics powered by "
    "Python, Pandas, Plotly and Machine Learning."
)


st.info(
    f"📅 Showing: {start_date} → {end_date} | "
    f"🌍 Country: {selected_country} | "
    f"💱 Currency: {currency_code} | "
    f"🎨 Theme: "
    f"{'Dark' if theme == '🌙 Dark Mode' else 'Light'}"
)


# ============================================================
# KPI SECTION
# ============================================================

total_revenue = (
    filtered_df["DisplayRevenue"].sum()
)

total_orders = (
    filtered_df["Invoice"].nunique()
)

total_customers = (
    filtered_df["Customer ID"].nunique()
)

total_products = (
    filtered_df["StockCode"].nunique()
)

average_order_value = (
    total_revenue / total_orders
    if total_orders > 0
    else 0
)

average_customer_value = (
    total_revenue / total_customers
    if total_customers > 0
    else 0
)


st.header(
    "📊 Key Performance Indicators"
)

col1, col2, col3, col4 = st.columns(4)


with col1:

    st.metric(
        "💰 Total Revenue",
        f"{currency_symbol}"
        f"{total_revenue:,.0f}"
    )


with col2:

    st.metric(
        "🧾 Total Orders",
        f"{total_orders:,}"
    )


with col3:

    st.metric(
        "👥 Customers",
        f"{total_customers:,}"
    )


with col4:

    st.metric(
        "📦 Products",
        f"{total_products:,}"
    )


st.header(
    "📌 Additional Metrics"
)

metric1, metric2, metric3 = st.columns(3)


with metric1:

    st.metric(
        "Average Order Value",
        f"{currency_symbol}"
        f"{average_order_value:,.2f}"
    )


with metric2:

    st.metric(
        "Average Customer Value",
        f"{currency_symbol}"
        f"{average_customer_value:,.2f}"
    )


with metric3:

    st.metric(
        "Countries",
        f"{filtered_df['Country'].nunique():,}"
    )


# ============================================================
# REVENUE PERFORMANCE
# ============================================================

st.divider()

st.header(
    "📈 Revenue Performance"
)


monthly_revenue = (
    filtered_df
    .groupby(
        filtered_df["InvoiceDate"].dt.to_period("M")
    )["DisplayRevenue"]
    .sum()
    .reset_index()
)


monthly_revenue["InvoiceDate"] = (
    monthly_revenue["InvoiceDate"]
    .astype(str)
)


fig_revenue = px.line(
    monthly_revenue,
    x="InvoiceDate",
    y="DisplayRevenue",
    markers=True,
    title=f"Monthly Revenue ({currency_code})",
    template=plot_template
)


fig_revenue.update_layout(
    xaxis_title="Month",
    yaxis_title=f"Revenue ({currency_code})",
    hovermode="x unified"
)


st.plotly_chart(
    fig_revenue,
    width="stretch"
)


# ============================================================
# COUNTRY + PRODUCT
# ============================================================

col1, col2 = st.columns(2)


with col1:

    st.subheader(
        "🌍 Revenue by Country"
    )


    country_revenue = (
        filtered_df
        .groupby("Country")["DisplayRevenue"]
        .sum()
        .sort_values(ascending=False)
        .head(10)
        .reset_index()
    )


    fig_country = px.bar(
        country_revenue,
        x="DisplayRevenue",
        y="Country",
        orientation="h",
        title=f"Top 10 Countries ({currency_code})",
        template=plot_template
    )


    fig_country.update_layout(
        yaxis={
            "categoryorder": "total ascending"
        }
    )


    st.plotly_chart(
        fig_country,
        width="stretch"
    )


with col2:

    st.subheader(
        "🛍️ Top Products"
    )


    top_products_chart = (
        filtered_df
        .groupby("Description")["Quantity"]
        .sum()
        .sort_values(ascending=False)
        .head(10)
        .reset_index()
    )


    fig_products = px.bar(
        top_products_chart,
        x="Quantity",
        y="Description",
        orientation="h",
        title="Top 10 Products by Quantity",
        template=plot_template
    )


    fig_products.update_layout(
        yaxis={
            "categoryorder": "total ascending"
        }
    )


    st.plotly_chart(
        fig_products,
        width="stretch"
    )


# ============================================================
# CUSTOMER INTELLIGENCE
# ============================================================

st.divider()

st.header(
    "👥 Customer Intelligence"
)


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


segment_summary["Avg_Monetary_Display"] = (
    segment_summary["Avg_Monetary"]
    * exchange_rate
)


col1, col2 = st.columns(2)


with col1:

    fig_segments = px.pie(
        segment_summary,
        names="Segment",
        values="Customers",
        title="Customer Distribution",
        template=plot_template
    )


    st.plotly_chart(
        fig_segments,
        width="stretch"
    )


with col2:

    display_segments = segment_summary[
        [
            "Segment",
            "Customers",
            "Avg_Recency",
            "Avg_Frequency",
            "Avg_Monetary_Display"
        ]
    ].copy()


    display_segments = (
        display_segments.rename(
            columns={
                "Avg_Monetary_Display":
                f"Avg Monetary ({currency_code})"
            }
        )
    )


    display_segments["Avg_Recency"] = (
        display_segments["Avg_Recency"]
        .round(1)
    )


    display_segments["Avg_Frequency"] = (
        display_segments["Avg_Frequency"]
        .round(1)
    )


    display_segments[
        f"Avg Monetary ({currency_code})"
    ] = (
        display_segments[
            f"Avg Monetary ({currency_code})"
        ].round(2)
    )


    st.dataframe(
        display_segments,
        width="stretch",
        hide_index=True
    )


# ============================================================
# AI BUSINESS INSIGHT ENGINE
# ============================================================

st.divider()

st.header(
    "🤖 AI Business Insight Engine"
)

st.caption(
    "Automatically analyzing revenue, customers, "
    "products and markets."
)


ai_insights = []
ai_recommendations = []


# Revenue trend

ai_monthly = (
    filtered_df
    .groupby(
        filtered_df["InvoiceDate"].dt.to_period("M")
    )["DisplayRevenue"]
    .sum()
    .sort_index()
)


if len(ai_monthly) >= 2:

    latest_revenue = ai_monthly.iloc[-1]
    previous_revenue = ai_monthly.iloc[-2]


    if previous_revenue != 0:

        revenue_change = (
            (latest_revenue - previous_revenue)
            / previous_revenue
            * 100
        )


        if revenue_change >= 10:

            ai_insights.append(
                (
                    "success",
                    "📈 Strong Revenue Growth",
                    f"Revenue increased by "
                    f"{revenue_change:.1f}% "
                    "compared with the previous month."
                )
            )


            ai_recommendations.append(
                "Consider increasing inventory and marketing "
                "investment around products driving the growth."
            )


        elif revenue_change <= -10:

            ai_insights.append(
                (
                    "warning",
                    "📉 Revenue Decline Detected",
                    f"Revenue decreased by "
                    f"{abs(revenue_change):.1f}% "
                    "compared with the previous month."
                )
            )


            ai_recommendations.append(
                "Investigate products, markets and customer "
                "activity responsible for the decline."
            )


        else:

            ai_insights.append(
                (
                    "info",
                    "📊 Revenue Relatively Stable",
                    f"Revenue changed by "
                    f"{revenue_change:+.1f}% "
                    "compared with the previous month."
                )
            )


# Top country

ai_country_revenue = (
    filtered_df
    .groupby("Country")["DisplayRevenue"]
    .sum()
    .sort_values(ascending=False)
)


if not ai_country_revenue.empty:

    best_country = (
        ai_country_revenue.index[0]
    )

    best_country_revenue = (
        ai_country_revenue.iloc[0]
    )


    ai_insights.append(
        (
            "success",
            "🌍 Top Revenue Market",
            f"{best_country} generated approximately "
            f"{currency_symbol}"
            f"{best_country_revenue:,.0f}."
        )
    )


# Top product

ai_product_revenue = (
    filtered_df
    .groupby("Description")["DisplayRevenue"]
    .sum()
    .sort_values(ascending=False)
)


if not ai_product_revenue.empty:

    best_product = (
        ai_product_revenue.index[0]
    )

    best_product_revenue = (
        ai_product_revenue.iloc[0]
    )


    ai_insights.append(
        (
            "info",
            "🛍️ Best Revenue Product",
            f"{best_product} generated approximately "
            f"{currency_symbol}"
            f"{best_product_revenue:,.0f}."
        )
    )


# Largest segment

largest_segment = (
    segment_summary
    .sort_values(
        "Customers",
        ascending=False
    )
    .iloc[0]
)


ai_insights.append(
    (
        "info",
        "👥 Largest Customer Segment",
        f"{largest_segment['Segment']} contains "
        f"{int(largest_segment['Customers']):,} customers."
    )
)


# At-risk customers

at_risk_segments = segment_summary[
    segment_summary["Segment"]
    .astype(str)
    .str.contains(
        "At Risk|Inactive",
        case=False,
        regex=True,
        na=False
    )
]


if not at_risk_segments.empty:

    at_risk_count = int(
        at_risk_segments["Customers"].sum()
    )

    total_segment_customers = int(
        segment_summary["Customers"].sum()
    )

    at_risk_percentage = (
        at_risk_count
        / total_segment_customers
        * 100
        if total_segment_customers > 0
        else 0
    )


    if at_risk_percentage >= 25:

        ai_insights.append(
            (
                "warning",
                "⚠️ Customer Retention Alert",
                f"{at_risk_count:,} customers "
                f"({at_risk_percentage:.1f}%) "
                "are At Risk / Inactive."
            )
        )


        ai_recommendations.append(
            "Launch a targeted win-back campaign "
            "for At Risk / Inactive customers."
        )


    else:

        ai_insights.append(
            (
                "info",
                "👥 Customer Retention Status",
                f"{at_risk_count:,} customers "
                f"({at_risk_percentage:.1f}%) "
                "are At Risk / Inactive."
            )
        )


# Display AI insights

for insight_type, title, message in ai_insights:

    if insight_type == "success":

        st.success(
            f"**{title}**  \n{message}"
        )

    elif insight_type == "warning":

        st.warning(
            f"**{title}**  \n{message}"
        )

    else:

        st.info(
            f"**{title}**  \n{message}"
        )


st.subheader(
    "🎯 AI Business Recommendations"
)


if not ai_recommendations:

    ai_recommendations.append(
        "Continue monitoring revenue, products and "
        "customer segments for emerging opportunities."
    )


for index, recommendation in enumerate(
    ai_recommendations,
    start=1
):

    st.markdown(
        f"**{index}.** {recommendation}"
    )


# ============================================================
# SALES FORECAST
# ============================================================

st.divider()

st.header(
    "🔮 Sales Forecast"
)

st.caption(
    "Revenue forecast generated from historical monthly "
    "sales trends and seasonal patterns."
)


if forecast_df.empty:

    st.warning(
        "Forecast data is unavailable. "
        "Run sales_forecasting.py first."
    )


else:

    forecast = forecast_df.copy()


    forecast["DisplayForecast"] = (
        forecast["Forecast_Revenue"]
        * exchange_rate
    )


    total_forecast = (
        forecast["DisplayForecast"].sum()
    )


    average_forecast = (
        forecast["DisplayForecast"].mean()
    )


    first_forecast = (
        forecast["DisplayForecast"].iloc[0]
    )


    last_forecast = (
        forecast["DisplayForecast"].iloc[-1]
    )


    forecast_change = (
        (
            last_forecast
            - first_forecast
        )
        / first_forecast
        * 100
        if first_forecast != 0
        else 0
    )


    f1, f2, f3, f4 = st.columns(4)


    with f1:

        st.metric(
            "💰 Forecast Revenue",
            f"{currency_symbol}"
            f"{total_forecast:,.0f}"
        )


    with f2:

        st.metric(
            "📊 Avg Monthly Forecast",
            f"{currency_symbol}"
            f"{average_forecast:,.0f}"
        )


    with f3:

        st.metric(
            "📅 Forecast Period",
            f"{len(forecast)} Months"
        )


    with f4:

        st.metric(
            "📉 Forecast Change",
            f"{forecast_change:+.1f}%"
        )


    history = (
        df
        .groupby(
            df["InvoiceDate"].dt.to_period("M")
        )["Revenue"]
        .sum()
        .reset_index()
    )


    history["Month"] = (
        history["InvoiceDate"]
        .dt.to_timestamp()
    )


    history["DisplayRevenue"] = (
        history["Revenue"]
        * exchange_rate
    )


    fig_forecast = go.Figure()


    fig_forecast.add_trace(
        go.Scatter(
            x=history["Month"],
            y=history["DisplayRevenue"],
            mode="lines+markers",
            name="Historical Revenue"
        )
    )


    fig_forecast.add_trace(
        go.Scatter(
            x=forecast["Month"],
            y=forecast["DisplayForecast"],
            mode="lines+markers",
            name="Forecast Revenue",
            line=dict(dash="dash")
        )
    )


    fig_forecast.update_layout(
        title=(
            f"Historical Revenue & 3-Month Forecast "
            f"({currency_code})"
        ),
        xaxis_title="Month",
        yaxis_title=f"Revenue ({currency_code})",
        template=plot_template,
        hovermode="x unified"
    )


    st.plotly_chart(
        fig_forecast,
        width="stretch"
    )


    st.subheader(
        "📅 Forecast by Month"
    )


    forecast_table = forecast[
        [
            "Month",
            "DisplayForecast"
        ]
    ].copy()


    forecast_table["Month"] = (
        forecast_table["Month"]
        .dt.strftime("%B %Y")
    )


    forecast_table = (
        forecast_table.rename(
            columns={
                "Month": "Forecast Month",
                "DisplayForecast":
                f"Forecast Revenue ({currency_code})"
            }
        )
    )


    forecast_table[
        f"Forecast Revenue ({currency_code})"
    ] = (
        forecast_table[
            f"Forecast Revenue ({currency_code})"
        ].round(2)
    )


    st.dataframe(
        forecast_table,
        width="stretch",
        hide_index=True
    )


    if forecast_change <= -10:

        st.warning(
            f"📉 Forecast Alert: Revenue is projected "
            f"to decline by approximately "
            f"{abs(forecast_change):.1f}%."
        )

    elif forecast_change >= 10:

        st.success(
            f"📈 Forecast Opportunity: Revenue is projected "
            f"to increase by approximately "
            f"{forecast_change:.1f}%."
        )

    else:

        st.info(
            f"📊 Forecast Status: Revenue is projected "
            f"to remain relatively stable "
            f"({forecast_change:+.1f}%)."
        )


# ============================================================
# ADVANCED CUSTOMER INTELLIGENCE
# ============================================================

st.divider()

st.header(
    "🎯 Advanced Customer Intelligence"
)


segment_counts = (
    segments["Segment"]
    .value_counts()
)


def count_segment(keyword):

    matching = [
        name
        for name in segment_counts.index
        if keyword.lower()
        in str(name).lower()
    ]

    if not matching:
        return 0

    return int(
        segment_counts[matching].sum()
    )


vip_count = count_segment("VIP")

high_value_count = count_segment(
    "Potential High Value"
)

regular_count = count_segment(
    "Regular"
)

at_risk_count = (
    count_segment("At Risk")
    + count_segment("Inactive")
)


c1, c2, c3, c4 = st.columns(4)


with c1:

    st.metric(
        "👑 VIP / Loyal",
        f"{vip_count:,}"
    )


with c2:

    st.metric(
        "💎 Potential High Value",
        f"{high_value_count:,}"
    )


with c3:

    st.metric(
        "👤 Regular Customers",
        f"{regular_count:,}"
    )


with c4:

    st.metric(
        "⚠️ At Risk / Inactive",
        f"{at_risk_count:,}"
    )


# ============================================================
# PRODUCT RECOMMENDATION CENTER
# ============================================================

st.divider()

st.header(
    "🎯 Product Recommendation Center"
)

st.caption(
    "Personalized recommendations based on customer "
    "behavior, segments and co-purchase patterns."
)


# ============================================================
# TOP PRODUCTS
# ============================================================

st.subheader(
    "🔥 Top Products"
)


popular_products = (
    recommendation_results[
        "popular_products"
    ]
    .copy()
)


if not popular_products.empty:

    popular_display = (
        popular_products.rename(
            columns={
                "Description":
                "Product",

                "Quantity":
                "Quantity Sold",

                "Orders":
                "Orders",

                "Revenue":
                f"Revenue ({currency_code})"
            }
        )
    )


    revenue_column = (
        f"Revenue ({currency_code})"
    )


    if revenue_column in popular_display.columns:

        popular_display[
            revenue_column
        ] = (
            popular_display[
                revenue_column
            ]
            * exchange_rate
        ).round(2)


    st.dataframe(
        popular_display,
        width="stretch",
        hide_index=True
    )


# ============================================================
# SEGMENT RECOMMENDATIONS
# ============================================================

st.subheader(
    "👥 Product Recommendations by Customer Segment"
)


segment_recommendations = (
    recommendation_results[
        "segment_recommendations"
    ]
    .copy()
)


if not segment_recommendations.empty:

    available_segments = (
        segment_recommendations[
            "Segment"
        ]
        .dropna()
        .unique()
        .tolist()
    )


    selected_segment = st.selectbox(
        "Choose Customer Segment",
        available_segments,
        key="recommendation_segment"
    )


    segment_products = (
        segment_recommendations[
            segment_recommendations[
                "Segment"
            ]
            == selected_segment
        ]
        .copy()
    )


    segment_products = (
        segment_products.rename(
            columns={
                "Description":
                "Recommended Product",

                "Quantity":
                "Quantity",

                "Orders":
                "Orders",

                "Revenue":
                f"Revenue ({currency_code})"
            }
        )
    )


    segment_revenue_column = (
        f"Revenue ({currency_code})"
    )


    if (
        segment_revenue_column
        in segment_products.columns
    ):

        segment_products[
            segment_revenue_column
        ] = (
            segment_products[
                segment_revenue_column
            ]
            * exchange_rate
        ).round(2)


    st.dataframe(
        segment_products,
        width="stretch",
        hide_index=True
    )


# ============================================================
# FREQUENTLY BOUGHT TOGETHER
# ============================================================

st.subheader(
    "🔗 Frequently Bought Together"
)


product_pairs = (
    recommendation_results[
        "product_pairs"
    ]
    .copy()
)


if not product_pairs.empty:

    pair_display = (
        product_pairs.rename(
            columns={
                "Product_A":
                "Product A",

                "Product_B":
                "Product B",

                "Co_Purchase_Count":
                "Times Purchased Together"
            }
        )
    )


    st.dataframe(
        pair_display,
        width="stretch",
        hide_index=True
    )


    strongest_pair = (
        product_pairs.iloc[0]
    )


    st.success(
        f"🛍️ **Strongest Product Pair:** "
        f"{strongest_pair['Product_A']} + "
        f"{strongest_pair['Product_B']} "
        f"were purchased together "
        f"{int(strongest_pair['Co_Purchase_Count']):,} times."
    )


# ============================================================
# CUSTOMER ID LOOKUP
# ============================================================

st.divider()

st.subheader(
    "🔎 Customer ID Verification & Recommendations"
)

st.caption(
    "Select an existing customer from the list OR "
    "enter a Customer ID manually."
)


# ============================================================
# PREPARE CUSTOMER LOOKUP
# ============================================================

customer_lookup = (
    recommendation_results[
        "customer_recommendations"
    ]
    .copy()
)


customer_lookup["Customer_ID_Clean"] = pd.to_numeric(
    customer_lookup["Customer ID"],
    errors="coerce"
)


customer_lookup = customer_lookup[
    customer_lookup[
        "Customer_ID_Clean"
    ].notna()
].copy()


customer_lookup["Customer_ID_Clean"] = (
    customer_lookup[
        "Customer_ID_Clean"
    ]
    .astype(int)
)


# ============================================================
# ACTUAL CUSTOMER IDS
# ============================================================

retail_customer_ids = (
    pd.to_numeric(
        df["Customer ID"],
        errors="coerce"
    )
    .dropna()
    .astype(int)
    .unique()
)


retail_customer_id_set = set(
    retail_customer_ids
)


recommendation_customer_id_set = set(
    customer_lookup[
        "Customer_ID_Clean"
    ]
)


# ============================================================
# LOOKUP METHOD
# ============================================================

lookup_method = st.radio(
    "Choose how you want to find the customer:",
    [
        "📋 Select from Customer IDs",
        "⌨️ Enter Customer ID manually"
    ],
    horizontal=True,
    key="customer_lookup_method"
)


selected_customer_id = None


# ============================================================
# OPTION 1 — DROPDOWN
# ============================================================

if lookup_method == "📋 Select from Customer IDs":

    available_customer_ids = sorted(
        customer_lookup[
            "Customer_ID_Clean"
        ]
        .astype(int)
        .unique()
        .tolist()
    )


    if available_customer_ids:

        selected_customer_id = st.selectbox(
            "Select Customer ID",
            available_customer_ids,
            format_func=lambda x: str(x),
            key="existing_customer_id"
        )


    else:

        st.warning(
            "No customer IDs are currently available."
        )


# ============================================================
# OPTION 2 — MANUAL ENTRY
# ============================================================

else:

    manual_customer_id = st.text_input(
        "Enter Customer ID",
        placeholder="Example: 18235",
        key="manual_customer_id"
    )


    if manual_customer_id.strip() == "":

        st.info(
            "👤 Enter a Customer ID to search."
        )

    else:

        cleaned_customer_id = (
            manual_customer_id.strip()
        )


        try:

            numeric_customer_id = float(
                cleaned_customer_id
            )


            if not numeric_customer_id.is_integer():

                st.error(
                    "❌ Invalid Customer ID. "
                    "Customer IDs must be whole numbers."
                )


            else:

                selected_customer_id = int(
                    numeric_customer_id
                )


        except (
            ValueError,
            OverflowError
        ):

            st.error(
                "❌ Invalid Customer ID. "
                "Please enter a numeric Customer ID "
                "such as 18235."
            )


# ============================================================
# CUSTOMER RESULT
# ============================================================

if selected_customer_id is not None:

    # --------------------------------------------------------
    # CHECK WHETHER CUSTOMER EXISTS
    # --------------------------------------------------------

    if (
        selected_customer_id
        not in retail_customer_id_set
    ):

        st.error(
            f"❌ Customer ID "
            f"**{selected_customer_id}** "
            "was not found in the customer database."
        )


    # --------------------------------------------------------
    # EXISTS BUT NO RECOMMENDATION PROFILE
    # --------------------------------------------------------

    elif (
        selected_customer_id
        not in recommendation_customer_id_set
    ):

        st.warning(
            f"⚠️ Customer ID "
            f"**{selected_customer_id}** "
            "exists in the sales dataset, "
            "but a recommendation profile "
            "is not currently available."
        )


    # --------------------------------------------------------
    # VALID CUSTOMER
    # --------------------------------------------------------

    else:

        customer_record = (
            customer_lookup[
                customer_lookup[
                    "Customer_ID_Clean"
                ]
                == selected_customer_id
            ]
            .iloc[0]
        )


        customer_segment = (
            customer_record["Segment"]
        )


        # ----------------------------------------------------
        # SUCCESS
        # ----------------------------------------------------

        st.success(
            f"✅ Customer ID "
            f"**{selected_customer_id}** "
            "verified successfully."
        )


        st.markdown(
            f"""
            ### 👤 Customer {selected_customer_id}

            **Customer Segment:** `{customer_segment}`

            **Status:** ✅ Customer ID Verified
            """
        )


        # ----------------------------------------------------
        # PERSONALIZED RECOMMENDATIONS
        # ----------------------------------------------------

        st.markdown(
            "### 🛍️ Personalized Product Recommendations"
        )


        recommendation_columns = [
            "Recommendation 1",
            "Recommendation 2",
            "Recommendation 3",
            "Recommendation 4",
            "Recommendation 5"
        ]


        customer_products = []


        for column in recommendation_columns:

            if column in customer_record.index:

                product = (
                    customer_record[column]
                )


                if (
                    pd.notna(product)
                    and str(product).strip() != ""
                    and str(product)
                    != "No recommendation"
                ):

                    customer_products.append(
                        str(product)
                    )


        if customer_products:

            recommendation_cols = st.columns(
                len(customer_products)
            )


            for index, product in enumerate(
                customer_products
            ):

                with recommendation_cols[index]:

                    st.info(
                        f"🛍️ **Recommendation "
                        f"{index + 1}**\n\n"
                        f"{product}"
                    )


        else:

            st.warning(
                "⚠️ This customer exists, "
                "but no new product recommendations "
                "are currently available."
            )


        # ----------------------------------------------------
        # CUSTOMER STRATEGY
        # ----------------------------------------------------

        st.markdown(
            "### 🎯 Recommended Customer Strategy"
        )


        segment_lower = (
            str(customer_segment)
            .lower()
        )


        if (
            "vip" in segment_lower
            or "loyal" in segment_lower
        ):

            st.success(
                "👑 **VIP / Loyal Customer:** "
                "Focus on loyalty rewards, premium "
                "offers, exclusive products and "
                "early access."
            )


        elif (
            "potential high"
            in segment_lower
        ):

            st.info(
                "💎 **Potential High Value Customer:** "
                "Use personalized cross-selling and "
                "targeted offers to increase purchase "
                "frequency and move the customer toward "
                "VIP status."
            )


        elif "regular" in segment_lower:

            st.info(
                "👤 **Regular Customer:** "
                "Use cross-selling, product bundles "
                "and personalized recommendations "
                "to increase order frequency."
            )


        elif (
            "at risk" in segment_lower
            or "inactive" in segment_lower
        ):

            st.warning(
                "⚠️ **At Risk / Inactive Customer:** "
                "Consider a win-back campaign, "
                "personalized discounts and "
                "re-engagement offers."
            )


        else:

            st.info(
                "📊 Continue monitoring this "
                "customer's purchase behavior."
            )


# ============================================================
# CUSTOMER LOOKUP HELP
# ============================================================

with st.expander(
    "💡 How to use Customer ID Lookup"
):

    st.markdown(
        """
        ### Option 1 — Select Existing Customer

        Choose:

        **📋 Select from Customer IDs**

        Then select a Customer ID from the dropdown.

        Example:

        `18235`


        ### Option 2 — Enter Customer Manually

        Choose:

        **⌨️ Enter Customer ID manually**

        Then type:

        `18235`


        ### Wrong Customer ID

        Enter:

        `99999999`

        The system will show:

        ❌ Customer ID was not found.


        ### Invalid Customer ID

        Enter:

        `ABC123`

        The system will show:

        ❌ Invalid Customer ID.


        ### Decimal ID

        Enter:

        `18235.5`

        The system will show:

        ❌ Customer IDs must be whole numbers.
        """
    )


# ============================================================
# PRODUCT STRATEGY RECOMMENDATIONS
# ============================================================

st.subheader(
    "🤖 Product Strategy Recommendations"
)


for index, recommendation in enumerate(
    recommendation_results[
        "business_recommendations"
    ],
    start=1
):

    st.markdown(
        f"**{index}.** {recommendation}"
    )


# ============================================================
# RECOMMENDATION ENGINE SUMMARY
# ============================================================

st.subheader(
    "📊 Recommendation Engine Summary"
)


summary1, summary2, summary3 = st.columns(3)


with summary1:

    st.metric(
        "Top Products",
        f"{len(popular_products):,}"
    )


with summary2:

    st.metric(
        "Product Pairs Detected",
        f"{len(product_pairs):,}"
    )


with summary3:

    st.metric(
        "Customers with Recommendations",
        f"{len(customer_lookup):,}"
    )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "AI Business Intelligence | "
    "Python • Pandas • Plotly • Scikit-learn • Streamlit"
)

st.caption(
    f"💱 Monetary values displayed in {currency_code}. "
    "Underlying dataset is maintained in GBP."
)