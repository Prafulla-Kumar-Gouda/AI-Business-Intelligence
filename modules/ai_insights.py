"""
Universal AI Business Insights
------------------------------
Generates deterministic, explainable business insights
from analytics, segmentation, forecasting and
recommendation outputs.
"""

import pandas as pd


def generate_revenue_insights(
    df: pd.DataFrame,
    detected_columns: dict
) -> list:
    """Generate insights from revenue performance."""

    insights = []

    quantity_column = detected_columns.get("quantity")
    price_column = detected_columns.get("price")
    date_column = detected_columns.get("date")

    if quantity_column and price_column:
        revenue = (
            pd.to_numeric(
                df[quantity_column],
                errors="coerce"
            )
            * pd.to_numeric(
                df[price_column],
                errors="coerce"
            )
        )
    elif price_column:
        revenue = pd.to_numeric(
            df[price_column],
            errors="coerce"
        )
    elif "Revenue" in df.columns:
        revenue = pd.to_numeric(
            df["Revenue"],
            errors="coerce"
        )
    else:
        revenue = pd.Series(
            0,
            index=df.index
        )

    revenue = revenue.fillna(0)

    total_revenue = float(
        revenue.sum()
    )

    if total_revenue > 0:
        insights.append(
            f"Total analyzed revenue is "
            f"{total_revenue:,.2f}."
        )

    if date_column and date_column in df.columns:
        dates = pd.to_datetime(
            df[date_column],
            errors="coerce"
        )

        if dates.notna().any():
            monthly = (
                pd.DataFrame(
                    {
                        "Date": dates,
                        "Revenue": revenue
                    }
                )
                .dropna(subset=["Date"])
            )

            monthly = (
                monthly
                .groupby(
                    monthly["Date"].dt.to_period("M")
                )["Revenue"]
                .sum()
            )

            if len(monthly) >= 2:
                latest = float(
                    monthly.iloc[-1]
                )

                previous = float(
                    monthly.iloc[-2]
                )

                if previous != 0:
                    change = (
                        (latest - previous)
                        / abs(previous)
                    ) * 100

                    direction = (
                        "increased"
                        if change >= 0
                        else "decreased"
                    )

                    insights.append(
                        f"Revenue {direction} by "
                        f"{abs(change):.1f}% compared "
                        f"with the previous month."
                    )

    return insights


def generate_product_insights(
    df: pd.DataFrame,
    detected_columns: dict
) -> list:
    """Generate product performance insights."""

    product_column = detected_columns.get(
        "product"
    )

    if not product_column or product_column not in df.columns:
        return []

    quantity_column = detected_columns.get(
        "quantity"
    )

    price_column = detected_columns.get(
        "price"
    )

    if quantity_column and price_column:
        revenue = (
            pd.to_numeric(
                df[quantity_column],
                errors="coerce"
            )
            * pd.to_numeric(
                df[price_column],
                errors="coerce"
            )
        )
    elif price_column:
        revenue = pd.to_numeric(
            df[price_column],
            errors="coerce"
        )
    else:
        revenue = pd.Series(
            0,
            index=df.index
        )

    data = pd.DataFrame(
        {
            "Product": df[product_column],
            "Revenue": revenue.fillna(0)
        }
    )

    data = data.dropna(
        subset=["Product"]
    )

    if data.empty:
        return []

    product_revenue = (
        data.groupby("Product")["Revenue"]
        .sum()
        .sort_values(
            ascending=False
        )
    )

    if product_revenue.empty:
        return []

    top_product = str(
        product_revenue.index[0]
    )

    top_revenue = float(
        product_revenue.iloc[0]
    )

    return [
        f"'{top_product}' is the highest-revenue "
        f"product, generating {top_revenue:,.2f}."
    ]


def generate_customer_insights(
    segmented_customers: pd.DataFrame
) -> list:
    """Generate insights from customer segments."""

    if (
        segmented_customers is None
        or segmented_customers.empty
        or "Segment" not in segmented_customers.columns
    ):
        return []

    counts = (
        segmented_customers["Segment"]
        .value_counts()
    )

    if counts.empty:
        return []

    largest_segment = str(
        counts.index[0]
    )

    largest_count = int(
        counts.iloc[0]
    )

    insights = [
        f"The largest customer segment is "
        f"'{largest_segment}' with "
        f"{largest_count:,} customers."
    ]

    if "VIP / Loyal Customers" in counts.index:
        insights.append(
            f"There are "
            f"{int(counts['VIP / Loyal Customers']):,} "
            f"VIP / Loyal Customers who can be targeted "
            f"with retention and cross-selling campaigns."
        )

    if "At Risk / Inactive" in counts.index:
        insights.append(
            f"There are "
            f"{int(counts['At Risk / Inactive']):,} "
            f"At Risk / Inactive customers who may benefit "
            f"from win-back campaigns."
        )

    return insights


def generate_forecast_insights(
    forecast: pd.DataFrame
) -> list:
    """Generate insights from forecast results."""

    if (
        forecast is None
        or forecast.empty
        or "Forecast Revenue" not in forecast.columns
    ):
        return []

    values = pd.to_numeric(
        forecast["Forecast Revenue"],
        errors="coerce"
    ).dropna()

    if values.empty:
        return []

    total = float(
        values.sum()
    )

    average = float(
        values.mean()
    )

    insights = [
        f"Forecast revenue for the next "
        f"{len(values)} period(s) is approximately "
        f"{total:,.2f}.",
        f"Average forecast revenue per period is "
        f"{average:,.2f}."
    ]

    if len(values) >= 2:
        first = float(values.iloc[0])
        last = float(values.iloc[-1])

        if first != 0:
            change = (
                (last - first)
                / abs(first)
            ) * 100

            if change > 5:
                insights.append(
                    f"The forecast indicates an upward "
                    f"trend of approximately {change:.1f}% "
                    f"from the first to the last forecast period."
                )

            elif change < -5:
                insights.append(
                    f"The forecast indicates a downward "
                    f"trend of approximately {abs(change):.1f}% "
                    f"from the first to the last forecast period."
                )

            else:
                insights.append(
                    "The forecast is relatively stable "
                    "across the projected periods."
                )

    return insights


def generate_business_actions(
    segmented_customers: pd.DataFrame = None,
    recommendations: list = None
) -> list:
    """Generate actionable business suggestions."""

    actions = []

    if (
        segmented_customers is not None
        and not segmented_customers.empty
    ):
        segments = (
            segmented_customers["Segment"]
            .value_counts()
        )

        if "At Risk / Inactive" in segments.index:
            actions.append(
                "Launch targeted win-back campaigns "
                "for At Risk / Inactive customers."
            )

        if "VIP / Loyal Customers" in segments.index:
            actions.append(
                "Prioritize retention, loyalty rewards "
                "and cross-selling for VIP / Loyal Customers."
            )

        if "Potential High Value" in segments.index:
            actions.append(
                "Use personalized offers to move "
                "Potential High Value customers toward loyalty."
            )

    if recommendations is not None:

        if isinstance(recommendations, pd.DataFrame):

            if not recommendations.empty:
                recommendation_rows = (
                    recommendations
                    .head(3)
                    .astype(str)
                    .apply(" | ".join, axis=1)
                    .tolist()
                )

                actions.extend(recommendation_rows)

        elif recommendations:

            actions.extend(
                recommendations[:3]
            )

    return actions


def generate_ai_insights(
    df: pd.DataFrame,
    detected_columns: dict,
    segmented_customers: pd.DataFrame = None,
    forecast: pd.DataFrame = None,
    recommendations: list = None
) -> dict:
    """
    Generate the complete business insight package.
    """

    revenue_insights = generate_revenue_insights(
        df,
        detected_columns
    )

    product_insights = generate_product_insights(
        df,
        detected_columns
    )

    customer_insights = generate_customer_insights(
        segmented_customers
    )

    forecast_insights = generate_forecast_insights(
        forecast
    )

    actions = generate_business_actions(
        segmented_customers,
        recommendations
    )

    all_insights = (
        revenue_insights
        + product_insights
        + customer_insights
        + forecast_insights
    )

    return {
        "revenue_insights": revenue_insights,
        "product_insights": product_insights,
        "customer_insights": customer_insights,
        "forecast_insights": forecast_insights,
        "business_actions": actions,
        "all_insights": all_insights
    }