import pandas as pd


# ============================================================
# AI BUSINESS INSIGHT ENGINE
# ============================================================

def generate_insights(
    filtered_df,
    segments,
    exchange_rate=1.0,
    currency_symbol="£",
    currency_code="GBP"
):
    """
    Generate dynamic business insights from
    sales and customer intelligence data.
    """

    insights = []


    # ========================================================
    # BASIC DATA VALIDATION
    # ========================================================

    if filtered_df.empty:

        return [
            {
                "type": "warning",
                "title": "No Data Available",
                "message": "There is no data available for the selected filters."
            }
        ]


    # ========================================================
    # REVENUE ANALYSIS
    # ========================================================

    filtered_df = filtered_df.copy()

    filtered_df["DisplayRevenue"] = (
        filtered_df["Revenue"]
        * exchange_rate
    )


    total_revenue = (
        filtered_df["DisplayRevenue"].sum()
    )


    total_orders = (
        filtered_df["Invoice"].nunique()
    )


    total_customers = (
        filtered_df["Customer ID"].nunique()
    )


    # ========================================================
    # AVERAGE ORDER VALUE
    # ========================================================

    if total_orders > 0:

        average_order_value = (
            total_revenue / total_orders
        )

    else:

        average_order_value = 0


    # ========================================================
    # MONTHLY REVENUE
    # ========================================================

    monthly_revenue = (
        filtered_df
        .groupby(
            filtered_df["InvoiceDate"].dt.to_period("M")
        )["DisplayRevenue"]
        .sum()
        .sort_index()
    )


    # ========================================================
    # REVENUE TREND ANALYSIS
    # ========================================================

    if len(monthly_revenue) >= 2:

        latest_month = monthly_revenue.iloc[-1]

        previous_month = monthly_revenue.iloc[-2]


        if previous_month != 0:

            revenue_change = (
                (latest_month - previous_month)
                / previous_month
                * 100
            )

        else:

            revenue_change = 0


        if revenue_change > 10:

            insights.append(
                {
                    "type": "success",
                    "title": "📈 Strong Revenue Growth",
                    "message": (
                        f"Revenue increased by "
                        f"{revenue_change:.1f}% "
                        f"compared with the previous month. "
                        f"This indicates positive sales momentum."
                    )
                }
            )


        elif revenue_change < -10:

            insights.append(
                {
                    "type": "warning",
                    "title": "📉 Revenue Decline Detected",
                    "message": (
                        f"Revenue decreased by "
                        f"{abs(revenue_change):.1f}% "
                        f"compared with the previous month. "
                        f"Consider investigating product demand, "
                        f"customer activity and seasonal effects."
                    )
                }
            )


        else:

            insights.append(
                {
                    "type": "info",
                    "title": "📊 Revenue Relatively Stable",
                    "message": (
                        f"Revenue changed by "
                        f"{revenue_change:.1f}% "
                        f"compared with the previous month."
                    )
                }
            )


    # ========================================================
    # TOP COUNTRY
    # ========================================================

    country_revenue = (
        filtered_df
        .groupby("Country")["DisplayRevenue"]
        .sum()
        .sort_values(ascending=False)
    )


    if not country_revenue.empty:

        top_country = (
            country_revenue.index[0]
        )

        top_country_revenue = (
            country_revenue.iloc[0]
        )


        country_share = (
            top_country_revenue
            / total_revenue
            * 100
            if total_revenue > 0
            else 0
        )


        insights.append(
            {
                "type": "success",
                "title": "🌍 Top Revenue Market",
                "message": (
                    f"{top_country} is the strongest market, "
                    f"generating approximately "
                    f"{currency_symbol}"
                    f"{top_country_revenue:,.0f}, "
                    f"representing "
                    f"{country_share:.1f}% "
                    f"of total revenue."
                )
            }
        )


    # ========================================================
    # TOP PRODUCT
    # ========================================================

    product_revenue = (
        filtered_df
        .groupby("Description")["DisplayRevenue"]
        .sum()
        .sort_values(ascending=False)
    )


    if not product_revenue.empty:

        top_product = (
            product_revenue.index[0]
        )

        top_product_revenue = (
            product_revenue.iloc[0]
        )


        insights.append(
            {
                "type": "info",
                "title": "🛍️ Best Revenue Product",
                "message": (
                    f"{top_product} generated approximately "
                    f"{currency_symbol}"
                    f"{top_product_revenue:,.0f} "
                    f"in revenue."
                )
            }
        )


    # ========================================================
    # CUSTOMER SEGMENT ANALYSIS
    # ========================================================

    if not segments.empty:

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


        # ----------------------------------------------------
        # Largest Segment
        # ----------------------------------------------------

        largest_segment = (
            segment_summary
            .sort_values(
                "Customers",
                ascending=False
            )
            .iloc[0]
        )


        insights.append(
            {
                "type": "info",
                "title": "👥 Largest Customer Segment",
                "message": (
                    f"{largest_segment['Segment']} "
                    f"is the largest customer group with "
                    f"{int(largest_segment['Customers']):,} customers."
                )
            }
        )


        # ----------------------------------------------------
        # At-Risk Customers
        # ----------------------------------------------------

        at_risk = segment_summary[
            segment_summary["Segment"]
            .str.contains(
                "At Risk|Inactive",
                case=False,
                regex=True
            )
        ]


        if not at_risk.empty:

            at_risk_customers = int(
                at_risk["Customers"].sum()
            )


            total_segment_customers = int(
                segment_summary["Customers"].sum()
            )


            at_risk_percentage = (
                at_risk_customers
                / total_segment_customers
                * 100
                if total_segment_customers > 0
                else 0
            )


            if at_risk_percentage >= 25:

                insights.append(
                    {
                        "type": "warning",
                        "title": "⚠️ Customer Retention Alert",
                        "message": (
                            f"{at_risk_customers:,} customers "
                            f"({at_risk_percentage:.1f}%) "
                            f"are classified as At Risk / Inactive. "
                            f"Targeted re-engagement campaigns "
                            f"could help improve retention."
                        )
                    }
                )

            else:

                insights.append(
                    {
                        "type": "info",
                        "title": "👥 Customer Retention Status",
                        "message": (
                            f"{at_risk_customers:,} customers "
                            f"({at_risk_percentage:.1f}%) "
                            f"are currently At Risk / Inactive."
                        )
                    }
                )


        # ----------------------------------------------------
        # VIP Customers
        # ----------------------------------------------------

        vip = segment_summary[
            segment_summary["Segment"]
            .str.contains(
                "VIP|Loyal",
                case=False,
                regex=True
            )
        ]


        if not vip.empty:

            vip_customers = int(
                vip["Customers"].sum()
            )


            vip_value = (
                vip["Avg_Monetary"].mean()
                * exchange_rate
            )


            insights.append(
                {
                    "type": "success",
                    "title": "👑 High-Value Customers",
                    "message": (
                        f"{vip_customers:,} customers "
                        f"belong to the VIP / Loyal segment. "
                        f"Their average monetary value is approximately "
                        f"{currency_symbol}"
                        f"{vip_value:,.0f}."
                    )
                }
            )


    # ========================================================
    # AVERAGE ORDER VALUE INSIGHT
    # ========================================================

    if average_order_value > 0:

        insights.append(
            {
                "type": "info",
                "title": "💰 Average Order Value",
                "message": (
                    f"The average order value is approximately "
                    f"{currency_symbol}"
                    f"{average_order_value:,.2f} "
                    f"across {total_orders:,} orders."
                )
            }
        )


    # ========================================================
    # BUSINESS RECOMMENDATIONS
    # ========================================================

    recommendations = []


    # Revenue recommendation

    if len(monthly_revenue) >= 2:

        if revenue_change < -10:

            recommendations.append(
                "Investigate the recent revenue decline and identify "
                "products or markets contributing to the drop."
            )

        elif revenue_change > 10:

            recommendations.append(
                "Consider increasing inventory and marketing investment "
                "for products driving the current revenue growth."
            )


    # Customer recommendation

    if not segments.empty:

        at_risk = segment_summary[
            segment_summary["Segment"]
            .str.contains(
                "At Risk|Inactive",
                case=False,
                regex=True
            )
        ]


        if not at_risk.empty:

            at_risk_customers = int(
                at_risk["Customers"].sum()
            )


            if at_risk_customers > 1000:

                recommendations.append(
                    "Launch a targeted re-engagement campaign "
                    "for At Risk / Inactive customers."
                )


    # Market recommendation

    if not country_revenue.empty:

        top_country_share = (
            country_revenue.iloc[0]
            / total_revenue
            * 100
            if total_revenue > 0
            else 0
        )


        if top_country_share > 50:

            recommendations.append(
                "Revenue is highly concentrated in one market. "
                "Consider expanding into additional countries "
                "to reduce market dependency."
            )


    # Product recommendation

    if not product_revenue.empty:

        top_product_share = (
            product_revenue.iloc[0]
            / total_revenue
            * 100
            if total_revenue > 0
            else 0
        )


        if top_product_share > 20:

            recommendations.append(
                "The leading product contributes significantly "
                "to revenue. Maintain stock availability "
                "and monitor its demand closely."
            )


    # ========================================================
    # DEFAULT RECOMMENDATION
    # ========================================================

    if not recommendations:

        recommendations.append(
            "Continue monitoring revenue, customer segments "
            "and product performance to identify emerging trends."
        )


    return {
        "insights": insights,
        "recommendations": recommendations,
        "metrics": {
            "total_revenue": total_revenue,
            "total_orders": total_orders,
            "total_customers": total_customers,
            "average_order_value": average_order_value
        }
    }