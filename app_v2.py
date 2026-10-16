"""
Universal AI Business Intelligence - V2

----------------------------------------

Universal Business Intelligence Platform


Features:

- CSV / XLSX / XLS upload

- Up to 10 GB configured upload limit

- Fast dataset preview

- Automatic business column detection

- Data cleaning

- Dataset health overview

- KPI analytics

- Monthly revenue

- Top products

- Top customers

- Revenue by country

- Customer segmentation

- Session-based caching

- Floating Analysis Tips button
"""


from pathlib import Path

import time


import pandas as pd

import streamlit as st


from modules.data_loader import (
    load_uploaded_file,
    preview_uploaded_file,
    get_dataset_summary,
    detect_columns,
)


from modules.data_cleaner import (
    clean_dataset,
)


from modules.analytics import (
    calculate_kpis,
    monthly_revenue,
    top_products,
    top_customers,
    revenue_by_country,
)


from modules.segmentation import (
    segment_customers,
    segment_summary,
    segment_insights,
)
from modules.forecasting import (
    forecast_sales,
    forecast_summary,
    forecast_accuracy,
    forecast_insights,
)

from modules.ai_insights import (
    generate_ai_insights,
    generate_business_actions,
    generate_customer_insights,
    generate_forecast_insights,
    generate_product_insights,
    generate_revenue_insights,
)

from modules.recommendations import (
    customer_recommendations,
    frequently_bought_together,
    product_strategy_recommendations,
    recommendation_summary,
   
)

# ============================================================
# PAGE CONFIGURATION
# ============================================================


st.set_page_config(
    page_title="Universal AI Business Intelligence",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# ============================================================
# CUSTOM CSS
# ============================================================


def load_custom_css():

    css_path = (
        Path(__file__).resolve().parent
        / "assets"
        / "style.css"
    )

    if css_path.exists():

        with open(
            css_path,
            "r",
            encoding="utf-8",
        ) as css_file:

            css = css_file.read()

        st.markdown(
            f"<style>{css}</style>",
            unsafe_allow_html=True,
        )


load_custom_css()


# ============================================================
# FUNCTIONAL FLOATING ANALYSIS TIPS STYLES
# ============================================================


st.markdown(
    """
    <style>

    /* ========================================================
       FLOATING ANALYSIS TIPS BUTTON
       ======================================================== */

    .st-key-analysis_tips_button_container {
        position: fixed !important;
        right: 24px !important;
        bottom: 24px !important;
        z-index: 999999 !important;
        width: auto !important;
    }


    .st-key-analysis_tips_button_container button {
        border-radius: 999px !important;

        background: linear-gradient(
            135deg,
            #5b5ff7,
            #16b8d4
        ) !important;

        color: white !important;

        border: none !important;

        padding: 10px 18px !important;

        font-size: 14px !important;
        font-weight: 700 !important;

        box-shadow:
            0 8px 25px rgba(0, 0, 0, 0.35) !important;

        transition:
            transform 0.2s ease,
            box-shadow 0.2s ease !important;
    }


    .st-key-analysis_tips_button_container button:hover {
        transform: translateY(-3px) !important;

        box-shadow:
            0 12px 30px rgba(0, 0, 0, 0.45) !important;

        border: none !important;
    }


    /* ========================================================
       FLOATING ANALYSIS TIPS PANEL
       ======================================================== */

    .st-key-analysis_tips_panel {
        position: fixed !important;

        right: 24px !important;
        bottom: 82px !important;

        width: 340px !important;
        max-height: 70vh !important;

        overflow-y: auto !important;

        z-index: 999998 !important;

        padding: 20px !important;

        border-radius: 18px !important;

        background: rgba(20, 24, 38, 0.97) !important;

        border: 1px solid rgba(255, 255, 255, 0.12) !important;

        box-shadow:
            0 15px 45px rgba(0, 0, 0, 0.45) !important;

        backdrop-filter: blur(16px) !important;
    }


    .st-key-analysis_tips_panel h3 {
        margin-top: 0 !important;
    }


    /* ========================================================
       SEGMENTATION CARDS
       ======================================================== */

    .segment-insight {
        padding: 10px 12px;
        border-radius: 10px;
        margin-bottom: 8px;
    }


    /* ========================================================
       MOBILE
       ======================================================== */

    @media (max-width: 768px) {

        .st-key-analysis_tips_button_container {
            right: 14px !important;
            bottom: 14px !important;
        }


        .st-key-analysis_tips_panel {
            right: 14px !important;
            bottom: 72px !important;

            width: calc(100vw - 28px) !important;

            max-height: 65vh !important;
        }

    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# SESSION STATE
# ============================================================


session_defaults = {

    "analysis_completed": False,

    "raw_data": None,

    "cleaned_data": None,

    "detected_columns": {},

    "cleaning_report": None,

    "file_signature": None,

    "preview_signature": None,

    "preview_result": None,

    "analysis_results": None,

    "analysis_seconds": None,

    "tips_open": False,
}


for key, value in session_defaults.items():

    if key not in st.session_state:

        st.session_state[key] = value


# ============================================================
# HELPER FUNCTIONS
# ============================================================


def get_file_signature(uploaded_file):

    if uploaded_file is None:

        return None

    return (
        uploaded_file.name,
        getattr(uploaded_file, "size", None),
    )


def reset_for_new_file(signature):

    previous_signature = (
        st.session_state.file_signature
    )

    if (
        previous_signature is not None
        and previous_signature != signature
    ):

        st.session_state.analysis_completed = False

        st.session_state.raw_data = None

        st.session_state.cleaned_data = None

        st.session_state.detected_columns = {}

        st.session_state.cleaning_report = None

        st.session_state.preview_result = None

        st.session_state.preview_signature = None

        st.session_state.analysis_results = None

        st.session_state.analysis_seconds = None

        st.session_state.tips_open = False

        st.session_state.quick_summary_open = False


    st.session_state.file_signature = signature


def format_field_name(value):

    return (
        str(value)
        .replace("_", " ")
        .title()
    )


# ============================================================
# HERO
# ============================================================


st.title(
    "📊 Universal AI Business Intelligence"
)


st.subheader(
    "Turn raw business data into clear, actionable intelligence."
)


st.caption(
    "Analyze sales, retail, customer, transaction and other "
    "business datasets automatically."
)



st.caption(
    "CSV • XLSX • XLS  |  Automatic Detection • Cleaning • Analytics"
)


st.divider()


# ============================================================
# VALUE PROPOSITION
# ============================================================


st.subheader(
    "Why use Universal AI BI?"
)


value_col1, value_col2, value_col3 = st.columns(3)


with value_col1:

    with st.container(border=True):

        st.markdown(
            "### ⚡ Fast Dataset Review"
        )

        st.write(
            "Quickly understand your dataset "
            "before running full analysis."
        )


with value_col2:

    with st.container(border=True):

        st.markdown(
            "### 🧠 Automatic Intelligence"
        )

        st.write(
            "Automatically detect customers, "
            "products, dates, prices and quantities."
        )


with value_col3:

    with st.container(border=True):

        st.markdown(
            "### 📈 Business Insights"
        )

        st.write(
            "Turn raw business data into "
            "meaningful decisions and insights."
        )


st.divider()


# ============================================================
# UPLOAD SECTION
# ============================================================


st.header(
    "📂 Upload Your Dataset"
)


st.write(
    "Upload a CSV or Excel dataset to start your "
    "business intelligence analysis."
)


upload_col1, upload_col2, upload_col3 = st.columns(3)


with upload_col1:

    with st.container(border=True):

        st.markdown(
            "### 📄 CSV"
        )

        st.caption(
            "Fast and lightweight"
        )


with upload_col2:

    with st.container(border=True):

        st.markdown(
            "### 📊 XLSX / XLS"
        )

        st.caption(
            "Excel business datasets"
        )


with upload_col3:

    with st.container(border=True):

        st.markdown(
            "### 🚀 Up to 10 GB"
        )

        st.caption(
            "Configured upload capacity"
        )


st.write("")


# ============================================================
# FILE UPLOADER
# ============================================================


uploaded_file = st.file_uploader(
    "Choose or drop your business dataset",
    type=[
        "csv",
        "xlsx",
        "xls",
    ],
    help=(
        "Supported formats: CSV, XLSX and XLS. "
        "Upload capacity is configured separately "
        "through Streamlit."
    ),
)


# ============================================================
# EMPTY STATE
# ============================================================


if uploaded_file is None:

    st.info(
        "👆 Upload a dataset to unlock the Business "
        "Intelligence dashboard."
    )

    st.subheader(
        "What happens after you upload?"
    )

    process_col1, process_col2 = st.columns(2)


    with process_col1:

        with st.container(border=True):

            st.markdown(
                "### 01 · ⚡ Quick Review"
            )

            st.write(
                "We quickly inspect your dataset structure "
                "without processing the entire file."
            )


        with st.container(border=True):

            st.markdown(
                "### 03 · 🧹 Clean"
            )

            st.write(
                "Invalid records, duplicates and unsuitable "
                "values are identified and cleaned."
            )


    with process_col2:

        with st.container(border=True):

            st.markdown(
                "### 02 · 🔍 Detect"
            )

            st.write(
                "Business columns such as Customer, Product, "
                "Price, Quantity and Date are detected automatically."
            )


        with st.container(border=True):

            st.markdown(
                "### 04 · 📊 Analyze"
            )

            st.write(
                "Generate KPIs, revenue trends, products, "
                "customers and country performance."
            )


    st.stop()


# ============================================================
# FILE SIGNATURE
# ============================================================


current_signature = get_file_signature(
    uploaded_file
)


reset_for_new_file(
    current_signature
)


# ============================================================
# MAIN DATA PROCESSING
# ============================================================


try:

    # ========================================================
    # QUICK PREVIEW
    # ========================================================


    if (
        st.session_state.preview_result is None
        or st.session_state.preview_signature
        != current_signature
    ):

        with st.spinner(
            "⚡ Quickly reviewing your dataset..."
        ):

            preview_result = preview_uploaded_file(
                uploaded_file,
                preview_rows=1000,
            )


        st.session_state.preview_result = (
            preview_result
        )

        st.session_state.preview_signature = (
            current_signature
        )

    else:

        preview_result = (
            st.session_state.preview_result
        )


    preview_df = preview_result["preview"]

    filename = preview_result["filename"]

    extension = preview_result["extension"]


    # ========================================================
    # FILE RECEIVED
    # ========================================================


    st.success(
        f"✅ Dataset received: {filename}"
    )


    # ========================================================
    # QUICK DATASET REVIEW
    # ========================================================


    st.header(
        "⚡ Quick Dataset Review"
    )


    review_col1, review_col2, review_col3 = (
        st.columns(3)
    )


    with review_col1:

        st.metric(
            "Preview Rows",
            f"{len(preview_df):,}",
        )


    with review_col2:

        st.metric(
            "Columns",
            f"{preview_df.shape[1]:,}",
        )


    with review_col3:

        st.metric(
            "File Type",
            extension.upper(),
        )


    # ========================================================
    # AUTOMATIC COLUMN DETECTION
    # ========================================================


    st.header(
        "🔍 Automatic Column Detection"
    )


    detected_preview_columns = detect_columns(
        preview_df
    )


    if detected_preview_columns:

        detection_rows = []


        for (
            business_field,
            column,
        ) in detected_preview_columns.items():

            detection_rows.append(
                {
                    "Business Field": format_field_name(
                        business_field
                    ),
                    "Detected Column": column,
                    "Status": "✓ Detected",
                }
            )


        detection_df = pd.DataFrame(
            detection_rows
        )


        st.dataframe(
            detection_df,
            hide_index=True,
            width="stretch",
        )

    else:

        st.warning(
            "⚠️ No recognized business columns "
            "were detected."
        )


    # ========================================================
    # SAMPLE DATA
    # ========================================================


    with st.expander(
        "👀 View Sample Data",
        expanded=True,
    ):

        st.dataframe(
            preview_df.head(100),
            hide_index=True,
            width="stretch",
        )


    # ========================================================
    # ANALYSIS CTA
    # ========================================================


    st.divider()


    st.header(
        "🚀 Ready to analyze your data?"
    )


    st.write(
        "Run a complete analysis to generate your "
        "Business Intelligence dashboard."
    )


    analyze_clicked = st.button(
        "🚀 Analyze My Dataset",
        type="primary",
        width="stretch",
    )


    # ========================================================
    # RUN ANALYSIS
    # ========================================================


    if analyze_clicked:

        analysis_start = time.perf_counter()


        # ----------------------------------------------------
        # LOAD DATASET
        # ----------------------------------------------------


        if (
            st.session_state.raw_data is not None
            and st.session_state.file_signature
            == current_signature
        ):

            df = st.session_state.raw_data

            st.info(
                "⚡ Reusing the already loaded dataset."
            )

        else:

            with st.spinner(
                "📥 Loading the complete dataset..."
            ):

                df = load_uploaded_file(
                    uploaded_file
                )


        # ----------------------------------------------------
        # DETECT BUSINESS COLUMNS
        # ----------------------------------------------------


        with st.spinner(
            "🔍 Detecting business columns..."
        ):

            detected_columns = detect_columns(
                df
            )


        # ----------------------------------------------------
        # CLEAN DATA
        # ----------------------------------------------------


        with st.spinner(
            "🧹 Cleaning and validating the dataset..."
        ):

            cleaned_df, cleaning_report = (
                clean_dataset(
                    df,
                    detected_columns,
                )
            )


        # ----------------------------------------------------
        # BUSINESS ANALYTICS
        # ----------------------------------------------------


        with st.spinner(
            "📊 Calculating business analytics..."
        ):

            kpis = calculate_kpis(
                cleaned_df,
                detected_columns,
            )


            monthly = monthly_revenue(
                cleaned_df,
                detected_columns,
            )


            products = top_products(
                cleaned_df,
                detected_columns,
                limit=10,
            )


            customers = top_customers(
                cleaned_df,
                detected_columns,
                limit=10,
            )


            countries = revenue_by_country(
                cleaned_df,
                detected_columns,
                limit=10,
            )


        # ----------------------------------------------------
        # CUSTOMER SEGMENTATION
        # ----------------------------------------------------


        with st.spinner(
            "👥 Segmenting customers..."
        ):

            segmented_customers = (
                segment_customers(
                    cleaned_df,
                    detected_columns,
                    n_clusters=4,
                )
            )


            customer_segment_summary = (
                segment_summary(
                    segmented_customers
                )
            )


            customer_segment_insights = (
                segment_insights(
                    customer_segment_summary
                )
            )
    # ---------------------------------------------------------
    # SALES FORECASTING
    # ---------------------------------------------------------
        with st.spinner("📈 Generating sales forecast..."):

            sales_forecast = forecast_sales(
                cleaned_df,
                detected_columns,
                periods=3
            )

            sales_forecast_summary = forecast_summary(
                sales_forecast
            )

            sales_forecast_accuracy = forecast_accuracy(
                cleaned_df,
                detected_columns
            )

            sales_forecast_insights = forecast_insights(
                sales_forecast,
             
    )
        # ====================================================
        # RECOMMENDATION ENGINE
        # ====================================================

        with st.spinner(
            "🛍️ Generating business recommendations..."
        ):

            customer_recommendation_results = (
                customer_recommendations(
                    cleaned_df,
                    detected_columns,
                    limit=5,
                )
            )

            product_pair_recommendations = (
                frequently_bought_together(
                    cleaned_df,
                    detected_columns,
                    limit=10,
                )
            )

            product_strategy_results = (
                product_strategy_recommendations(
                    cleaned_df,
                    detected_columns,
                    segmented_customers=segmented_customers,
                    limit=6,
                )
            )

            recommendation_results_summary = (
                recommendation_summary(
                    cleaned_df,
                    detected_columns,
                    segmented_customers=segmented_customers,
                )
            )

        # =====================================================
        # AI BUSINESS INSIGHTS
        # =====================================================

        with st.spinner("🤖 Generating AI business insights..."):

            ai_business_insights = generate_ai_insights(
                cleaned_df,
                detected_columns,
                segmented_customers=segmented_customers,
                forecast=sales_forecast,
                recommendations=customer_recommendation_results,
            )

            ai_business_actions = generate_business_actions(
                segmented_customers=segmented_customers,
                recommendations=customer_recommendation_results,
            )

        
        # ----------------------------------------------------
        # SAVE DATA IN SESSION
        # ----------------------------------------------------


        st.session_state.raw_data = df


        st.session_state.cleaned_data = (
            cleaned_df
        )


        st.session_state.detected_columns = (
            detected_columns
        )


        st.session_state.cleaning_report = (
            cleaning_report
        )


        st.session_state.analysis_results = {

            "kpis": kpis,

            "monthly": monthly,

            "products": products,

            "customers": customers,
        

            "countries": countries,

            "segmented_customers": (
                segmented_customers
            ),

            "customer_segment_summary": (
                customer_segment_summary
            ),

            "customer_segment_insights": (
                customer_segment_insights
            ),
            "sales_forecast": sales_forecast,
            "sales_forecast_summary": sales_forecast_summary,
            "sales_forecast_accuracy": sales_forecast_accuracy,
            "sales_forecast_insights": sales_forecast_insights,
        }


        st.session_state.analysis_completed = True


        elapsed = (
            time.perf_counter()
            - analysis_start
        )


        st.session_state.analysis_seconds = (
            elapsed
        )


        st.session_state.tips_open = False
        st.session_state.quick_summary_open = False

        st.success(
            "🎉 Business analysis completed successfully! "
            f"Processing time: {elapsed:.2f} seconds."
        )
        analysis_results = {
            # -----------------------------------------
            # BASIC BUSINESS ANALYTICS
            # -----------------------------------------

            "kpis": kpis,
            "monthly": monthly,
            "products": products,
            "customers": customers,
            "countries": countries,

            # -----------------------------------------
            # CUSTOMER SEGMENTATION
            # -----------------------------------------

            "segmented_customers": segmented_customers,
            "customer_segment_summary": customer_segment_summary,
            "customer_segment_insights": customer_segment_insights,

            # -----------------------------------------
            # SALES FORECASTING
            # -----------------------------------------

            "sales_forecast": sales_forecast,
            "sales_forecast_summary": sales_forecast_summary,
            "sales_forecast_accuracy": sales_forecast_accuracy,
            "sales_forecast_insights": sales_forecast_insights,
            "ai_business_insights": ai_business_insights,
            "ai_business_actions": ai_business_actions,

            # -----------------------------------------
            # RECOMMENDATIONS
            # -----------------------------------------

            "customer_recommendations": customer_recommendation_results,
            "product_pair_recommendations": product_pair_recommendations,
            "product_strategy_recommendations": product_strategy_results,
            "recommendation_summary": recommendation_results_summary,
        }

        st.session_state.analysis_results = analysis_results

    # ========================================================
    # SHOW ANALYSIS
    # ========================================================


    if (
        st.session_state.analysis_completed
        and st.session_state.analysis_results
        is not None
    ):

        # ----------------------------------------------------
        # GET CACHED DATA
        # ----------------------------------------------------


        df = st.session_state.raw_data


        cleaned_df = (
            st.session_state.cleaned_data
        )


        detected_columns = (
            st.session_state.detected_columns
        )


        cleaning_report = (
            st.session_state.cleaning_report
        )


        analysis_results = (
            st.session_state.analysis_results
        )


        kpis = analysis_results["kpis"]


        monthly = analysis_results["monthly"]


        products = analysis_results["products"]


        customers = analysis_results["customers"]


        countries = analysis_results["countries"]


        segmented_customers = (
            analysis_results.get(
                "segmented_customers",
                pd.DataFrame(),
            )
        )


        customer_segment_summary = (
            analysis_results.get(
                "customer_segment_summary",
                pd.DataFrame(),
            )
        )


        customer_segment_insights = (
            analysis_results.get(
                "customer_segment_insights",
                [],
            )
        )
        # ====================================================
        # RECOMMENDATION RESULTS
        # ====================================================

        customer_recommendation_results = (
            analysis_results.get(
                "customer_recommendations",
                [],
            )
        )

        product_pair_recommendations = (
            analysis_results.get(
                "product_pair_recommendations",
                [],
            )
        )

        product_strategy_results = (
            analysis_results.get(
                "product_strategy_recommendations",
                [],
            )
        )

        recommendation_results_summary = (
            analysis_results.get(
                "recommendation_summary",
                {},
            )
        )

        # =====================================================
        # AI BUSINESS INSIGHTS RESULTS
        # =====================================================

        ai_business_insights = (
            analysis_results.get(
                "ai_business_insights",
                {}
            )
        )

        ai_business_actions = (
            analysis_results.get(
                "ai_business_actions",
                []
            )
        )

        # ====================================================
        # SALES FORECASTING RESULTS
        # ====================================================

        sales_forecast = analysis_results.get(
            "sales_forecast",
            pd.DataFrame(
                columns=["Month", "Forecast Revenue"]
            ),
        )

        sales_forecast_summary = analysis_results.get(
            "sales_forecast_summary",
            {
                "forecast_periods": 0,
                "total_forecast": 0.0,
                "average_monthly_forecast": 0.0,
            },
        )

        sales_forecast_accuracy = analysis_results.get(
            "sales_forecast_accuracy",
            {
                "mae": None,
                "rmse": None,
            },
        )

        sales_forecast_insights = analysis_results.get(
            "sales_forecast_insights",
            {},
        )

        



    # ============================================================
    # FLOATING QUICK ACTION BUTTONS
    # ============================================================

    with st.container(
        key="quick_actions_container"
    ):

        # QUICK SUMMARY
        if st.button(
            "📊 Quick Summary",
            key="quick_summary_button_final",
        ):
            st.session_state.quick_summary_open = (
                not st.session_state.quick_summary_open
            )

        # ANALYSIS TIPS
        if st.button(
            "💡 Analysis Tips",
            key="analysis_tips_button_final",
        ):
            st.session_state.tips_open = (
                not st.session_state.tips_open
            )

        
        # ====================================================
        # FLOATING ANALYSIS TIPS PANEL
        # ====================================================


        if st.session_state.tips_open:

            with st.container(
                key="analysis_tips_panel"
            ):

                st.markdown(
                    "### 💡 Analysis Tips"
                )


                st.markdown(
                    """
                    **📊 Dataset Quality**

                    Check missing values, duplicates and invalid records before trusting the results.

                    **📈 Revenue Trends**

                    Look for major peaks, sudden drops and repeating seasonal patterns.

                    **👥 Customers**

                    Compare high-value customers with regular and inactive customers.

                    **🛒 Products**

                    A product generating high revenue does not automatically mean it has high profitability.

                    **🎯 Segmentation**

                    At-risk customers may require targeted win-back campaigns.

                    **🔮 Forecast**

                    Forecast values are estimates based on historical patterns — they are not guarantees.

                    **🤖 AI Insights**

                    Use generated recommendations as decision support, not as a replacement for business judgement.
                    """
                )


                st.markdown("---")


                if st.button(
                    "✕ Close",
                    key="close_analysis_tips",
                ):

                    st.session_state.tips_open = False
                    st.session_state.quick_summary_open = False
                    st.rerun()
        # ============================================================
        # FLOATING QUICK SUMMARY PANEL
        # ============================================================

        if (
            st.session_state.get("quick_summary_open", False)
            and st.session_state.get("analysis_completed", False)
            and st.session_state.get("analysis_results")
        ):

            quick_results = st.session_state.analysis_results

            quick_kpis = quick_results.get("kpis", {})
            quick_segments = quick_results.get(
                "customer_segment_summary"
            )
            quick_forecast = quick_results.get(
                "sales_forecast_summary",
                {}
            )
            quick_insights = quick_results.get(
                "ai_business_insights"
            )

            with st.container(
                key="quick_summary_panel"
            ):

                st.markdown(
                    "### 📊 Quick Business Summary"
                )

                # ----------------------------------------------------
                # KPI SUMMARY
                # ----------------------------------------------------

                quick_revenue = quick_kpis.get(
                    "revenue",
                    0
                )

                quick_orders = quick_kpis.get(
                    "orders",
                    0
                )

                quick_customers = quick_kpis.get(
                    "customers",
                    0
                )

                quick_products = quick_kpis.get(
                    "products",
                    0
                )

                q1, q2 = st.columns(2)

                with q1:
                    st.metric(
                        "💰 Revenue",
                        f"{quick_revenue:,.2f}"
                    )

                    st.metric(
                        "🛒 Orders",
                        f"{quick_orders:,}"
                    )

                with q2:
                    st.metric(
                        "👥 Customers",
                        f"{quick_customers:,}"
                    )

                    st.metric(
                        "📦 Products",
                        f"{quick_products:,}"
                    )

                # ----------------------------------------------------
                # CUSTOMER SUMMARY
                # ----------------------------------------------------

                st.markdown(
                    "#### 👥 Customer Snapshot"
                )

                if (
                    isinstance(
                        quick_segments,
                        pd.DataFrame
                    )
                    and not quick_segments.empty
                ):

                    segment_text = []

                    for _, row in quick_segments.iterrows():

                        segment_name = str(
                            row.get(
                                "Segment",
                                "Customer Segment"
                            )
                        )

                        customer_count = row.get(
                            "Customers",
                            0
                        )

                        segment_text.append(
                            f"• **{segment_name}:** "
                            f"{int(customer_count):,} customers"
                        )

                    for item in segment_text[:4]:
                        st.write(item)

                else:
                    st.info(
                        "Customer segmentation data is not available."
                    )

                # ----------------------------------------------------
                # FORECAST SUMMARY
                # ----------------------------------------------------

                st.markdown(
                    "#### 🔮 Forecast Snapshot"
                )

                if isinstance(
                    quick_forecast,
                    dict
                ):

                    forecast_periods = quick_forecast.get(
                        "forecast_periods",
                        0
                    )

                    total_forecast = quick_forecast.get(
                        "total_forecast",
                        0
                    )

                    st.write(
                        f"• Forecast period: **"
                        f"{forecast_periods} months**"
                    )

                    st.write(
                        f"• Expected revenue: **"
                        f"{total_forecast:,.2f}**"
                    )

                # ----------------------------------------------------
                # AI BUSINESS INSIGHTS
                # ----------------------------------------------------

                st.markdown(
                    "#### 🤖 Key Insight"
                )

                if quick_insights:

                    if isinstance(
                        quick_insights,
                        dict
                    ):

                        shown = False

                        for title, insight in (
                            quick_insights.items()
                        ):

                            if insight:

                                st.info(
                                    f"💡 **{str(title).replace('_', ' ').title()}**\n\n"
                                    f"{insight}"
                                )

                                shown = True
                                break

                        if not shown:
                            st.info(
                                "No major AI insight is available."
                            )

                    elif isinstance(
                        quick_insights,
                        list
                    ):

                        if len(quick_insights) > 0:

                            st.info(
                                f"💡 {quick_insights[0]}"
                            )

                        else:
                            st.info(
                                "No major AI insight is available."
                            )

                    else:

                        st.info(
                            f"💡 {quick_insights}"
                        )

                else:

                    st.info(
                        "No AI business insight is available."
                    )

                # ----------------------------------------------------
                # CLOSE BUTTON
                # ----------------------------------------------------

                if st.button(
                    "✕ Close Quick Summary",
                    key="close_quick_summary",
                ):

                    st.session_state.quick_summary_open = False
                    st.rerun()
                


        # ----------------------------------------------------
        # CACHE MESSAGE
        # ----------------------------------------------------


        if not analyze_clicked:

            st.success(
                "✅ This dataset has already been analyzed. "
                "The cached analysis is being reused."
            )


        # ====================================================
        # DATASET OVERVIEW
        # ====================================================


        st.header(
            "📋 Dataset Overview"
        )
        if st.session_state.cleaned_data is None:
            st.warning("⚠️ Please analyze the dataset first.")
            st.stop()

        summary = get_dataset_summary(
            st.session_state.cleaned_data
        )

        # FOUR COLUMNS — FIXED


        overview_col1, overview_col2, overview_col3, overview_col4 = (
            st.columns(4)
        )


        with overview_col1:

            st.metric(
                "Total Rows",
                f"{summary['rows']:,}",
            )


        with overview_col2:

            st.metric(
                "Columns",
                f"{summary['columns']:,}",
            )


        with overview_col3:

            st.metric(
                "Missing Values",
                f"{summary['missing_values']:,}",
            )


        with overview_col4:

            st.metric(
                "Duplicate Rows",
                f"{summary['duplicate_rows']:,}",
            )


        # ====================================================
        # DETECTED BUSINESS FIELDS
        # ====================================================


        st.subheader(
            "🧠 Detected Business Fields"
        )


        if detected_columns:

            full_detection_rows = []


            for (
                business_field,
                column,
            ) in detected_columns.items():

                full_detection_rows.append(
                    {
                        "Business Field": format_field_name(
                            business_field
                        ),
                        "Detected Column": column,
                        "Status": "✓ Ready",
                    }
                )


            st.dataframe(
                pd.DataFrame(
                    full_detection_rows
                ),
                hide_index=True,
                width="stretch",
            )

        else:

            st.warning(
                "⚠️ No business fields were detected."
            )


        # ====================================================
        # CLEANING RESULTS
        # ====================================================


        st.header(
            "🧹 Data Cleaning"
        )


        clean_col1, clean_col2, clean_col3 = (
            st.columns(3)
        )


        with clean_col1:

            st.metric(
                "Original Rows",
                f"{cleaning_report['original_rows']:,}",
            )


        with clean_col2:

            st.metric(
                "Clean Rows",
                f"{cleaning_report['final_rows']:,}",
            )


        with clean_col3:

            st.metric(
                "Rows Removed",
                f"{cleaning_report['rows_removed']:,}",
            )


        with st.expander(
            "🔎 View Cleaning Details"
        ):

            cleaning_rows = []


            for (
                key,
                value,
            ) in cleaning_report.items():

                cleaning_rows.append(
                    {
                        "Cleaning Check": format_field_name(
                            key
                        ),
                        "Result": value,
                    }
                )


            st.dataframe(
                pd.DataFrame(
                    cleaning_rows
                ),
                hide_index=True,
                width="stretch",
            )


        # ====================================================
        # BUSINESS ANALYTICS
        # ====================================================


        st.divider()


        st.header(
            "📊 Business Analytics"
        )


        # ====================================================
        # KPI CARDS
        # ====================================================


        st.subheader(
            "💰 Key Performance Indicators"
        )


        kpi_col1, kpi_col2, kpi_col3, kpi_col4 = (
            st.columns(4)
        )


        with kpi_col1:

            st.metric(
                "Total Revenue",
                f"{kpis['revenue']:,.2f}",
            )


        with kpi_col2:

            st.metric(
                "Orders",
                f"{kpis['orders']:,}",
            )


        with kpi_col3:

            st.metric(
                "Customers",
                f"{kpis['customers']:,}",
            )


        with kpi_col4:

            st.metric(
                "Products",
                f"{kpis['products']:,}",
            )


        kpi_col5, kpi_col6, kpi_col7 = (
            st.columns(3)
        )


        with kpi_col5:

            st.metric(
                "Quantity Sold",
                f"{kpis['quantity']:,.0f}",
            )


        with kpi_col6:

            st.metric(
                "Average Order Value",
                f"{kpis['average_order_value']:,.2f}",
            )


        with kpi_col7:

            st.metric(
                "Average Customer Value",
                f"{kpis['average_customer_value']:,.2f}",
            )


        # ====================================================
        # MONTHLY REVENUE
        # ====================================================


        st.subheader(
            "📈 Monthly Revenue"
        )


        if not monthly.empty:

            st.line_chart(
                monthly.set_index(
                    "Month"
                )[["Revenue"]]
            )

        else:

            st.info(
                "ℹ️ Monthly revenue could not be generated "
                "because a valid date column was not detected."
            )


        # ====================================================
        # PRODUCTS + COUNTRY
        # ====================================================


        chart_col1, chart_col2 = (
            st.columns(2)
        )


        with chart_col1:

            st.subheader(
                "🏆 Top Products"
            )


            if not products.empty:

                st.bar_chart(
                    products.set_index(
                        "Product"
                    )[["Revenue"]]
                )


                with st.expander(
                    "View Product Details"
                ):

                    st.dataframe(
                        products,
                        hide_index=True,
                        width="stretch",
                    )

            else:

                st.info(
                    "Product information was not detected."
                )


        with chart_col2:

            st.subheader(
                "🌍 Revenue by Country"
            )


            if not countries.empty:

                st.bar_chart(
                    countries.set_index(
                        "Country"
                    )[["Revenue"]]
                )


                with st.expander(
                    "View Country Details"
                ):

                    st.dataframe(
                        countries,
                        hide_index=True,
                        width="stretch",
                    )

            else:

                st.info(
                    "Country information was not detected."
                )


        # ====================================================
        # TOP CUSTOMERS
        # ====================================================


        st.subheader(
            "👤 Top Customers"
        )


        if not customers.empty:

            st.dataframe(
                customers,
                hide_index=True,
                width="stretch",
            )

        else:

            st.info(
                "Customer information was not detected."
            )


        # ====================================================
        # CUSTOMER SEGMENTATION
        # ====================================================


        st.divider()


        st.header(
            "👥 Customer Segmentation"
        )


        st.write(
            "Automatically group customers according to "
            "their purchasing behaviour using RFM features "
            "and K-Means clustering."
        )


        if not customer_segment_summary.empty:

            # ------------------------------------------------
            # SEGMENT KPIs
            # ------------------------------------------------

            segment_kpi1, segment_kpi2, segment_kpi3, segment_kpi4 = (
                st.columns(4)
            )


            segment_names = (
                customer_segment_summary[
                    "Segment"
                ]
                .tolist()
            )


            def get_segment_count(
                segment_name
            ):

                matching = (
                    customer_segment_summary[
                        customer_segment_summary[
                            "Segment"
                        ]
                        == segment_name
                    ]
                )

                if matching.empty:

                    return 0

                return int(
                    matching.iloc[0][
                        "Customers"
                    ]
                )


            with segment_kpi1:

                st.metric(
                    "👑 VIP / Loyal",
                    f"{get_segment_count('VIP / Loyal Customers'):,}",
                )


            with segment_kpi2:

                st.metric(
                    "💎 Potential High Value",
                    f"{get_segment_count('Potential High Value'):,}",
                )


            with segment_kpi3:

                st.metric(
                    "👤 Regular",
                    f"{get_segment_count('Regular Customers'):,}",
                )


            with segment_kpi4:

                st.metric(
                    "⚠️ At Risk / Inactive",
                    f"{get_segment_count('At Risk / Inactive'):,}",
                )


            # ------------------------------------------------
            # SEGMENT SUMMARY
            # ------------------------------------------------

            st.subheader(
                "📊 Segment Performance"
            )


            display_segment_summary = (
                customer_segment_summary[
                    [
                        "Segment",
                        "Customers",
                        "Revenue",
                        "Revenue_Percentage",
                        "Average_Recency",
                        "Average_Frequency",
                        "Average_Monetary",
                    ]
                ]
                .copy()
            )


            display_segment_summary = (
                display_segment_summary.rename(
                    columns={
                        "Revenue": "Revenue",
                        "Revenue_Percentage": "Revenue %",
                        "Average_Recency": "Avg. Recency",
                        "Average_Frequency": "Avg. Frequency",
                        "Average_Monetary": "Avg. Monetary",
                    }
                )
            )


            st.dataframe(
                display_segment_summary,
                hide_index=True,
                width="stretch",
            )


            # ------------------------------------------------
            # SEGMENT CHARTS
            # ------------------------------------------------

            segment_chart_col1, segment_chart_col2 = (
                st.columns(2)
            )


            with segment_chart_col1:

                st.subheader(
                    "👥 Customers by Segment"
                )


                customer_chart = (
                    customer_segment_summary
                    .set_index("Segment")
                    [["Customers"]]
                )


                st.bar_chart(
                    customer_chart
                )


            with segment_chart_col2:

                st.subheader(
                    "💰 Revenue by Segment"
                )


                revenue_chart = (
                    customer_segment_summary
                    .set_index("Segment")
                    [["Revenue"]]
                )


                st.bar_chart(
                    revenue_chart
                )


            # ------------------------------------------------
            # BUSINESS INSIGHTS
            # ------------------------------------------------

            st.subheader(
                "💡 Customer Segment Insights"
            )


            if customer_segment_insights:

                for insight in (
                    customer_segment_insights
                ):

                    st.info(
                        f"**{insight['Segment']}**\n\n"
                        f"{insight['Insight']}"
                    )

            else:

                st.info(
                    "No segment-specific insights were generated."
                )


            # ------------------------------------------------
            # CUSTOMER LEVEL DATA
            # ------------------------------------------------

            with st.expander(
                "🔍 View Customer-Level Segmentation"
            ):

                if not segmented_customers.empty:

                    customer_segment_display = (
                        segmented_customers[
                            [
                                "Customer ID",
                                "Recency",
                                "Frequency",
                                "Monetary",
                                "Cluster",
                                "Segment",
                            ]
                        ]
                        .copy()
                    )


                    st.dataframe(
                        customer_segment_display,
                        hide_index=True,
                        width="stretch",
                    )

                else:

                    st.info(
                        "Customer-level segmentation data "
                        "is not available."
                    )


        else:

            st.warning(
                "⚠️ Customer segmentation could not be generated. "
                "A valid Customer ID, Date and transaction structure "
                "are required for this analysis."
            )

        # ====================================================
        # SALES FORECASTING
        # ====================================================

        st.header(
            "📈 Sales Forecasting"
        )

        st.write(
            "Estimate future monthly revenue based on "
            "historical sales patterns."
        )

        if (
            sales_forecast is not None
            and not sales_forecast.empty
        ):

            # ------------------------------------------------
            # FORECAST SUMMARY
            # ------------------------------------------------

            forecast_col1, forecast_col2, forecast_col3 = (
                st.columns(3)
            )

            with forecast_col1:
                st.metric(
                    "Forecast Period",
                    f"{sales_forecast_summary.get('forecast_periods', 0)} months"
                )

            with forecast_col2:
                st.metric(
                    "Total Forecast Revenue",
                    f"{sales_forecast_summary.get('total_forecast', 0):,.2f}"
                )

            with forecast_col3:
                st.metric(
                    "Average Monthly Forecast",
                    f"{sales_forecast_summary.get('average_monthly_forecast', 0):,.2f}"
                )
            # ------------------------------------------------
            # HISTORICAL VS FORECAST CHART
            # ------------------------------------------------

            st.subheader(
                "📊 Historical vs Forecast Revenue"
            )

            historical_chart = monthly[
                ["Month", "Revenue"]
            ].copy()

            historical_chart = historical_chart.rename(
                columns={
                    "Revenue": "Historical Revenue"
                }
            )

            forecast_chart = sales_forecast[
                ["Month", "Forecast Revenue"]
            ].copy()

            historical_chart["Month"] = pd.to_datetime(
                historical_chart["Month"],
                errors="coerce"
            )

            forecast_chart["Month"] = pd.to_datetime(
                forecast_chart["Month"],
                errors="coerce"
            )

            combined_forecast_chart = pd.merge(
                historical_chart,
                forecast_chart,
                on="Month",
                how="outer",
            ).sort_values(
                "Month"
            )

            st.line_chart(
                combined_forecast_chart.set_index(
                    "Month"
                )
            )

            # ------------------------------------------------
            # FORECAST TABLE
            # ------------------------------------------------

            st.subheader(
                "📅 Forecasted Monthly Revenue"
            )

            display_forecast = sales_forecast.copy()

            if "Month" in display_forecast.columns:
                display_forecast["Month"] = (
                    pd.to_datetime(
                        display_forecast["Month"],
                        errors="coerce"
                    ).dt.strftime("%b %Y")
                )

            if "Forecast Revenue" in display_forecast.columns:
                display_forecast["Forecast Revenue"] = (
                    display_forecast["Forecast Revenue"].round(2)
                )

            st.dataframe(
                display_forecast,
                hide_index=True,
                width="stretch",
            )

            # ------------------------------------------------
            # FORECAST INSIGHT
            # ------------------------------------------------

            st.subheader(
                "💡 Forecast Business Insight"
            )

            if isinstance(
                sales_forecast_insights,
                dict
            ):
                st.info(
                    sales_forecast_insights.get(
                        "message",
                        "No forecast insight is available."
                    )
                )
            else:
                st.info(
                    "Forecast generated successfully from "
                    "historical revenue patterns."
                )

            # ------------------------------------------------
            # FORECAST ACCURACY
            # ------------------------------------------------

            with st.expander(
                "📐 View Forecast Model Accuracy"
            ):

                mae = sales_forecast_accuracy.get(
                    "mae"
                )

                rmse = sales_forecast_accuracy.get(
                    "rmse"
                )

                accuracy_col1, accuracy_col2 = (
                    st.columns(2)
                )

                with accuracy_col1:
                    st.metric(
                        "MAE",
                        (
                            f"{mae:,.2f}"
                            if mae is not None
                            else "N/A"
                        )
                    )

                with accuracy_col2:
                    st.metric(
                        "RMSE",
                        (
                            f"{rmse:,.2f}"
                            if rmse is not None
                            else "N/A"
                        )
                    )

                st.caption(
                    "MAE and RMSE evaluate the forecast model "
                    "using a simple historical holdout approach. "
                    "Lower values generally indicate smaller "
                    "prediction errors."
                )

            st.caption(
                "⚠️ Forecasts are estimates based on historical "
                "patterns and should be used as decision support, "
                "not as guaranteed future results."
            )

        else:

            st.warning(
                "⚠️ Sales forecasting could not be generated. "
                "At least two valid historical months are required."
            )

        # ====================================================
        # COMPLETION
        # ====================================================

        st.divider()

        st.success(
            "🎉 Business analysis completed successfully!"
        )


        # ====================================================
        # INTELLIGENCE MODULES
        # ====================================================

        st.header(
            "🚀 Intelligence Modules"
        )

        intelligence_col1, intelligence_col2 = (
            st.columns(2)
        )

        # ====================================================
        # CUSTOMER SEGMENTATION MODULE
        # ====================================================

        with intelligence_col1:

            with st.container(border=True):

                st.markdown(
                    "### 👥 Customer Segmentation"
                )

                if (
                    customer_segment_summary is not None
                    and not customer_segment_summary.empty
                ):

                    total_segmented = len(
                        segmented_customers
                    )

                    st.success(
                        f"✅ {total_segmented:,} "
                        "customers segmented"
                    )

                    st.write(
                        "Customers are grouped into "
                        "behaviour-based segments using "
                        "RFM analysis and K-Means clustering."
                    )

                else:

                    st.warning(
                        "Customer segmentation is not available."
                    )

           
        # ====================================================
        # FORECASTING + AI INSIGHTS
        # ====================================================

        with intelligence_col2:

            with st.container(border=True):

                st.markdown(
                    "### 🔮 Sales Forecasting"
                )

                if (
                    sales_forecast is not None
                    and not sales_forecast.empty
                ):

                    st.success(
                        "✅ Sales forecast generated"
                    )

                    st.write(
                        f"Forecast generated for "
                        f"{len(sales_forecast)} future months."
                    )

                else:

                    st.warning(
                        "Sales forecasting is not available."
                    )

            with st.container(border=True):

                st.markdown(
                    "### 🤖 AI Business Insights"
                )

                st.write(
                    "Turn analytical results into "
                    "actionable business decisions."
                )

        if ai_business_insights:

            st.success("🤖 AI Business Insights generated")

            if isinstance(ai_business_insights, dict):

                for title, insight in ai_business_insights.items():

                    if insight:
                        st.info(
                            f"💡 **{str(title).replace('_', ' ').title()}**\n\n"
                            f"{insight}"
                        )

            elif isinstance(ai_business_insights, list):

                for insight in ai_business_insights:

                    if insight:
                        st.info(f"💡 {insight}")

            else:

                st.info(
                    f"💡 {ai_business_insights}"
                )

        else:

            st.warning(
                "⚠️ No AI business insights were generated for this dataset."
            )    
        # =================================================
        # RECOMMENDATIONS MODULE
        # =================================================

        with st.container(border=True):

            st.markdown(
                "### 🛍️ Recommendations"
            )

            st.write(
                "Discover product, customer, and "
                "cross-selling opportunities."
            )

            # -------------------------------------------------
            # GET RECOMMENDATION DATA DIRECTLY
            # -------------------------------------------------

            recommendation_data = (
                st.session_state.analysis_results
                if st.session_state.get(
                    "analysis_results"
                )
                else {}
            )


            customer_recommendation_results = (
                recommendation_data.get(
                    "customer_recommendations",
                    pd.DataFrame(),
                )
            )

            product_pair_recommendations = (
                recommendation_data.get(
                    "product_pair_recommendations",
                    pd.DataFrame(),
                )
            )

            product_strategy_results = (
                recommendation_data.get(
                    "product_strategy_recommendations",
                    [],
                )
            )

            recommendation_results_summary = (
                recommendation_data.get(
                    "recommendation_summary",
                    {},
                )
            )

            # -------------------------------------------------
            # SAFE COUNTS
            # -------------------------------------------------

            if isinstance(
                customer_recommendation_results,
                pd.DataFrame
            ):
                total_customer_recommendations = len(
                    customer_recommendation_results
                )
            elif isinstance(
                customer_recommendation_results,
                (list, tuple)
            ):
                total_customer_recommendations = len(
                    customer_recommendation_results
                )
            else:
                total_customer_recommendations = 0

            if isinstance(
                product_pair_recommendations,
                pd.DataFrame
            ):
                total_product_pairs = len(
                    product_pair_recommendations
                )
            elif isinstance(
                product_pair_recommendations,
                (list, tuple)
            ):
                total_product_pairs = len(
                    product_pair_recommendations
                )
            else:
                total_product_pairs = 0

            if isinstance(
                product_strategy_results,
                (list, tuple)
            ):
                total_business_recommendations = len(
                    product_strategy_results
                )
            elif isinstance(
                product_strategy_results,
                pd.DataFrame
            ):
                total_business_recommendations = len(
                    product_strategy_results
                )
            else:
                total_business_recommendations = 0

            # -------------------------------------------------
            # SUMMARY CARDS
            # -------------------------------------------------

            summary_col1, summary_col2, summary_col3 = (
                st.columns(3)
            )

            with summary_col1:

                st.metric(
                    "Customer Recommendations",
                    f"{total_customer_recommendations:,}",
                )

            with summary_col2:

                st.metric(
                    "Product Pairs",
                    f"{total_product_pairs:,}",
                )

            with summary_col3:

                st.metric(
                    "Business Recommendations",
                    f"{total_business_recommendations:,}",
                )

            # -------------------------------------------------
            # CUSTOMER RECOMMENDATIONS
            # -------------------------------------------------

            if (
                isinstance(
                    customer_recommendation_results,
                    pd.DataFrame,
                )
                and not customer_recommendation_results.empty
            ):

                st.markdown(
                    "#### 👤 Customer Recommendations"
                )

                st.dataframe(
                    customer_recommendation_results.head(100),
                    hide_index=True,
                    width="stretch",
                )

            # -------------------------------------------------
            # FREQUENTLY BOUGHT TOGETHER
            # -------------------------------------------------

            if (
                isinstance(
                    product_pair_recommendations,
                    pd.DataFrame,
                )
                and not product_pair_recommendations.empty
            ):

                st.markdown(
                    "#### 🔗 Frequently Bought Together"
                )

                st.dataframe(
                    product_pair_recommendations,
                    hide_index=True,
                    width="stretch",
                )

            # -------------------------------------------------
            # PRODUCT STRATEGY
            # -------------------------------------------------

            if (
                isinstance(
                    product_strategy_results,
                    (list, tuple),
                )
                and len(product_strategy_results) > 0
            ):

                st.markdown(
                    "#### 📦 Product Strategy"
                )

                for recommendation in (
                    product_strategy_results
                ):

                    st.info(
                        f"💡 {recommendation}"
                    )

            # -------------------------------------------------
            # SUMMARY / EMPTY STATE
            # -------------------------------------------------

            if (
                total_customer_recommendations == 0
                and total_product_pairs == 0
                and total_business_recommendations == 0
            ):

                st.warning(
                    "No recommendation results were "
                    "generated for this dataset."
                )

            # ---------------------------------------------
            # RECOMMENDATION SUMMARY
            # ---------------------------------------------

            if isinstance(
                recommendation_results_summary,
                dict
            ):

                total_customer_recommendations = (
                    len(customer_recommendation_results)
                    if hasattr(
                        customer_recommendation_results,
                        "__len__"
                    )
                    else 0
                )

                total_product_pairs = (
                    len(product_pair_recommendations)
                    if hasattr(
                        product_pair_recommendations,
                        "__len__"
                    )
                    else 0
                )

                summary_col1, summary_col2 = (
                    st.columns(2)
                )


            
        # ====================================================
        # ANALYSIS PERFORMANCE
        # ====================================================

        if (
            st.session_state.analysis_seconds
            is not None
        ):

            st.caption(
                "⚡ Complete analysis processing time: "
                f"{st.session_state.analysis_seconds:.2f} seconds"
            )


# ============================================================
# ERROR HANDLING
# ============================================================


except Exception as exc:

    st.error(
        "❌ Unable to process the dataset."
    )


    with st.expander(
        "View Technical Details"
    ):

        st.exception(
            exc
        )