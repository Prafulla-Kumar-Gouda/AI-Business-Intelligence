import pandas as pd
import numpy as np


# ============================================================
# ADVANCED CUSTOMER INTELLIGENCE ENGINE
# ============================================================


def analyze_customers(
    segments,
    retail_data,
    exchange_rate=1.0,
    currency_symbol="£",
    currency_code="GBP"
):
    """
    Advanced customer intelligence engine.

    Uses:
        - RFM segmentation
        - Customer monetary value
        - Customer frequency
        - Customer recency
        - Segment distribution
        - Retention analysis
    """

    # ========================================================
    # VALIDATION
    # ========================================================

    if segments is None or segments.empty:

        return {
            "summary": {},
            "segments": pd.DataFrame(),
            "top_customers": pd.DataFrame(),
            "strategies": [],
            "recommendations": []
        }


    # ========================================================
    # COPY DATA
    # ========================================================

    customer_segments = segments.copy()

    sales_data = retail_data.copy()


    # ========================================================
    # STANDARDIZE CUSTOMER ID
    # ========================================================

    customer_segments["Customer ID"] = (
        pd.to_numeric(
            customer_segments["Customer ID"],
            errors="coerce"
        )
    )


    sales_data["Customer ID"] = (
        pd.to_numeric(
            sales_data["Customer ID"],
            errors="coerce"
        )
    )


    # ========================================================
    # SEGMENT SUMMARY
    # ========================================================

    segment_summary = (
        customer_segments
        .groupby("Segment")
        .agg(
            Customers=("Customer ID", "count"),
            Avg_Recency=("Recency", "mean"),
            Avg_Frequency=("Frequency", "mean"),
            Avg_Monetary=("Monetary", "mean")
        )
        .reset_index()
    )


    # ========================================================
    # TOTAL CUSTOMERS
    # ========================================================

    total_customers = int(
        segment_summary["Customers"].sum()
    )


    # ========================================================
    # SEGMENT PERCENTAGE
    # ========================================================

    if total_customers > 0:

        segment_summary["Customer_Percentage"] = (
            segment_summary["Customers"]
            / total_customers
            * 100
        )

    else:

        segment_summary["Customer_Percentage"] = 0


    # ========================================================
    # DISPLAY CURRENCY
    # ========================================================

    segment_summary["Avg_Monetary_Display"] = (
        segment_summary["Avg_Monetary"]
        * exchange_rate
    )


    # ========================================================
    # SEGMENT VALUE CONTRIBUTION
    # ========================================================

    segment_summary["Estimated_Value"] = (
        segment_summary["Customers"]
        * segment_summary["Avg_Monetary"]
    )


    segment_summary["Estimated_Value_Display"] = (
        segment_summary["Estimated_Value"]
        * exchange_rate
    )


    total_segment_value = (
        segment_summary["Estimated_Value"].sum()
    )


    if total_segment_value > 0:

        segment_summary["Value_Percentage"] = (
            segment_summary["Estimated_Value"]
            / total_segment_value
            * 100
        )

    else:

        segment_summary["Value_Percentage"] = 0


    # ========================================================
    # IDENTIFY SEGMENTS
    # ========================================================

    def get_segment(pattern):

        result = customer_segments[
            customer_segments["Segment"]
            .str.contains(
                pattern,
                case=False,
                regex=True,
                na=False
            )
        ]

        return result


    vip_customers = get_segment(
        "VIP|Loyal"
    )


    high_value_customers = get_segment(
        "Potential High Value"
    )


    regular_customers = get_segment(
        "Regular"
    )


    at_risk_customers = get_segment(
        "At Risk|Inactive"
    )


    # ========================================================
    # SEGMENT COUNTS
    # ========================================================

    vip_count = len(vip_customers)

    high_value_count = len(
        high_value_customers
    )

    regular_count = len(
        regular_customers
    )

    at_risk_count = len(
        at_risk_customers
    )


    # ========================================================
    # RETENTION OPPORTUNITY
    # ========================================================

    retention_opportunity = (
        at_risk_count
        + high_value_count
    )


    retention_percentage = (
        retention_opportunity
        / total_customers
        * 100
        if total_customers > 0
        else 0
    )


    # ========================================================
    # AT-RISK VALUE
    # ========================================================

    if not at_risk_customers.empty:

        at_risk_value = (
            at_risk_customers["Monetary"]
            .sum()
            * exchange_rate
        )

    else:

        at_risk_value = 0


    # ========================================================
    # VIP VALUE
    # ========================================================

    if not vip_customers.empty:

        vip_value = (
            vip_customers["Monetary"]
            .sum()
            * exchange_rate
        )

    else:

        vip_value = 0


    # ========================================================
    # POTENTIAL HIGH VALUE
    # ========================================================

    if not high_value_customers.empty:

        potential_value = (
            high_value_customers["Monetary"]
            .sum()
            * exchange_rate
        )

    else:

        potential_value = 0


    # ========================================================
    # TOP CUSTOMERS
    # ========================================================

    top_customers = (
        customer_segments
        .sort_values(
            "Monetary",
            ascending=False
        )
        .head(20)
        .copy()
    )


    top_customers["Monetary_Display"] = (
        top_customers["Monetary"]
        * exchange_rate
    )


    top_customers["Customer ID"] = (
        top_customers["Customer ID"]
        .astype("Int64")
    )


    # ========================================================
    # CUSTOMER STRATEGIES
    # ========================================================

    strategies = []


    # --------------------------------------------------------
    # VIP STRATEGY
    # --------------------------------------------------------

    if vip_count > 0:

        strategies.append({
            "segment": "VIP / Loyal",
            "customers": vip_count,
            "priority": "HIGH",
            "strategy": (
                "Reward and retain these customers using "
                "loyalty benefits, exclusive offers, "
                "early product access and personalized communication."
            )
        })


    # --------------------------------------------------------
    # HIGH VALUE STRATEGY
    # --------------------------------------------------------

    if high_value_count > 0:

        strategies.append({
            "segment": "Potential High Value",
            "customers": high_value_count,
            "priority": "HIGH",
            "strategy": (
                "Convert these customers into VIP customers "
                "using personalized promotions, cross-selling "
                "and loyalty incentives."
            )
        })


    # --------------------------------------------------------
    # REGULAR STRATEGY
    # --------------------------------------------------------

    if regular_count > 0:

        strategies.append({
            "segment": "Regular Customers",
            "customers": regular_count,
            "priority": "MEDIUM",
            "strategy": (
                "Increase purchase frequency through "
                "cross-selling, product recommendations "
                "and limited-time promotions."
            )
        })


    # --------------------------------------------------------
    # AT-RISK STRATEGY
    # --------------------------------------------------------

    if at_risk_count > 0:

        strategies.append({
            "segment": "At Risk / Inactive",
            "customers": at_risk_count,
            "priority": "CRITICAL",
            "strategy": (
                "Launch targeted re-engagement campaigns "
                "using personalized discounts, reminders "
                "and win-back offers."
            )
        })


    # ========================================================
    # BUSINESS RECOMMENDATIONS
    # ========================================================

    recommendations = []


    # --------------------------------------------------------
    # RETENTION RECOMMENDATION
    # --------------------------------------------------------

    if at_risk_count > 1000:

        recommendations.append(
            f"Prioritize customer retention: "
            f"{at_risk_count:,} customers are "
            f"At Risk / Inactive."
        )


    # --------------------------------------------------------
    # HIGH-VALUE CONVERSION
    # --------------------------------------------------------

    if high_value_count > 500:

        recommendations.append(
            f"Create a VIP conversion campaign for "
            f"{high_value_count:,} Potential High Value customers."
        )


    # --------------------------------------------------------
    # VIP PROTECTION
    # --------------------------------------------------------

    if vip_count > 0:

        recommendations.append(
            f"Protect the VIP customer base of "
            f"{vip_count:,} customers through loyalty "
            f"and personalized engagement."
        )


    # --------------------------------------------------------
    # AT-RISK VALUE
    # --------------------------------------------------------

    if at_risk_value > 0:

        recommendations.append(
            f"Approximately "
            f"{currency_symbol}"
            f"{at_risk_value:,.0f} "
            f"is associated with At Risk / Inactive customers. "
            f"Retention campaigns may recover part of this value."
        )


    # --------------------------------------------------------
    # CUSTOMER CONCENTRATION
    # --------------------------------------------------------

    if not top_customers.empty:

        top_20_value = (
            top_customers["Monetary"].sum()
        )


        if total_segment_value > 0:

            top_20_share = (
                top_20_value
                / total_segment_value
                * 100
            )


            if top_20_share > 20:

                recommendations.append(
                    f"The top 20 customers represent approximately "
                    f"{top_20_share:.1f}% of estimated customer value. "
                    f"Maintaining these relationships should be a priority."
                )


    # ========================================================
    # DEFAULT RECOMMENDATION
    # ========================================================

    if not recommendations:

        recommendations.append(
            "Continue monitoring customer segments and "
            "retention indicators to identify opportunities."
        )


    # ========================================================
    # SUMMARY
    # ========================================================

    summary = {

        "total_customers":
            total_customers,

        "vip_customers":
            vip_count,

        "high_value_customers":
            high_value_count,

        "regular_customers":
            regular_count,

        "at_risk_customers":
            at_risk_count,

        "retention_opportunity":
            retention_opportunity,

        "retention_percentage":
            retention_percentage,

        "vip_value":
            vip_value,

        "potential_value":
            potential_value,

        "at_risk_value":
            at_risk_value,

        "currency_code":
            currency_code,

        "currency_symbol":
            currency_symbol
    }


    # ========================================================
    # RETURN
    # ========================================================

    return {

        "summary":
            summary,

        "segments":
            segment_summary,

        "top_customers":
            top_customers,

        "strategies":
            strategies,

        "recommendations":
            recommendations
    }