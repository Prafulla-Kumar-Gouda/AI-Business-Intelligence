"""
Universal Recommendation Engine
--------------------------------
Generates product and customer recommendations
from uploaded business datasets.

Optimized for large datasets.
"""

import pandas as pd
from itertools import combinations
from collections import Counter


# ============================================================
# REVENUE PREPARATION
# ============================================================

def _prepare_revenue(
    df: pd.DataFrame,
    detected_columns: dict
) -> pd.DataFrame:
    """
    Create a temporary revenue column.

    Revenue is calculated from:
        Quantity × Price

    If Quantity is unavailable, Price is used.
    If an existing Revenue column exists, it is used
    as a fallback.
    """

    if df is None or df.empty:
        return pd.DataFrame()

    data = df.copy()

    quantity_column = detected_columns.get("quantity")
    price_column = detected_columns.get("price")

    if (
        quantity_column
        and price_column
        and quantity_column in data.columns
        and price_column in data.columns
    ):

        data["__Revenue"] = (
            pd.to_numeric(
                data[quantity_column],
                errors="coerce"
            )
            *
            pd.to_numeric(
                data[price_column],
                errors="coerce"
            )
        )

    elif (
        price_column
        and price_column in data.columns
    ):

        data["__Revenue"] = pd.to_numeric(
            data[price_column],
            errors="coerce"
        )

    elif "Revenue" in data.columns:

        data["__Revenue"] = pd.to_numeric(
            data["Revenue"],
            errors="coerce"
        )

    else:

        data["__Revenue"] = 0.0

    data["__Revenue"] = (
        data["__Revenue"]
        .fillna(0)
    )

    return data


# ============================================================
# FREQUENTLY BOUGHT TOGETHER
# ============================================================

def frequently_bought_together(
    df: pd.DataFrame,
    detected_columns: dict,
    limit: int = 10
) -> pd.DataFrame:
    """
    Find products that are frequently purchased together.

    Optimized approach:
    - Keeps only required columns.
    - Removes duplicate products within an order.
    - Limits extremely large baskets.
    - Counts pairs using Counter.
    """

    if df is None or df.empty:
        return pd.DataFrame(
            columns=[
                "Product_A",
                "Product_B",
                "Co_Purchase_Count",
            ]
        )

    order_column = detected_columns.get("order_id")
    product_column = detected_columns.get("product")

    if (
        not order_column
        or not product_column
        or order_column not in df.columns
        or product_column not in df.columns
    ):
        return pd.DataFrame(
            columns=[
                "Product_A",
                "Product_B",
                "Co_Purchase_Count",
            ]
        )

    data = df[
        [
            order_column,
            product_column,
        ]
    ].copy()

    data = data.dropna(
        subset=[
            order_column,
            product_column,
        ]
    )

    if data.empty:
        return pd.DataFrame(
            columns=[
                "Product_A",
                "Product_B",
                "Co_Purchase_Count",
            ]
        )

    data[product_column] = (
        data[product_column]
        .astype(str)
        .str.strip()
    )

    data = data[
        data[product_column] != ""
    ]

    if data.empty:
        return pd.DataFrame(
            columns=[
                "Product_A",
                "Product_B",
                "Co_Purchase_Count",
            ]
        )

    # --------------------------------------------------------
    # Keep only reasonably sized baskets
    # --------------------------------------------------------

    basket_sizes = (
        data.groupby(order_column)[product_column]
        .nunique()
    )

    valid_orders = basket_sizes[
        basket_sizes <= 30
    ].index

    data = data[
        data[order_column].isin(valid_orders)
    ]

    if data.empty:
        return pd.DataFrame(
            columns=[
                "Product_A",
                "Product_B",
                "Co_Purchase_Count",
            ]
        )

    # --------------------------------------------------------
    # Remove duplicate product entries within each order
    # --------------------------------------------------------

    data = data.drop_duplicates(
        subset=[
            order_column,
            product_column,
        ]
    )

    # --------------------------------------------------------
    # Build product baskets
    # --------------------------------------------------------

    baskets = (
        data.groupby(order_column)[product_column]
        .agg(list)
    )

    pair_counter = Counter()

    for products in baskets:

        if len(products) < 2:
            continue

        products = sorted(
            set(products)
        )

        if len(products) > 30:
            products = products[:30]

        for pair in combinations(
            products,
            2
        ):
            pair_counter[pair] += 1

    if not pair_counter:
        return pd.DataFrame(
            columns=[
                "Product_A",
                "Product_B",
                "Co_Purchase_Count",
            ]
        )

    result = pd.DataFrame(
        [
            {
                "Product_A": pair[0],
                "Product_B": pair[1],
                "Co_Purchase_Count": count,
            }
            for pair, count
            in pair_counter.items()
        ]
    )

    result = (
        result
        .sort_values(
            "Co_Purchase_Count",
            ascending=False
        )
        .head(limit)
        .reset_index(drop=True)
    )

    return result


# ============================================================
# CUSTOMER RECOMMENDATIONS
# ============================================================

def customer_recommendations(
    df: pd.DataFrame,
    detected_columns: dict,
    limit: int = 5
) -> pd.DataFrame:
    """
    Generate personalized product recommendations.

    Recommendations are based on:
    - Products already purchased by customers.
    - Popular products.
    - Frequently bought-together relationships.
    """

    if df is None or df.empty:
        return pd.DataFrame()

    customer_column = detected_columns.get(
        "customer_id"
    )

    product_column = detected_columns.get(
        "product"
    )

    order_column = detected_columns.get(
        "order_id"
    )

    if (
        not customer_column
        or not product_column
        or customer_column not in df.columns
        or product_column not in df.columns
    ):
        return pd.DataFrame()

    data = df[
        [
            customer_column,
            product_column,
        ]
        +
        (
            [order_column]
            if order_column
            and order_column in df.columns
            else []
        )
    ].copy()

    data = data.dropna(
        subset=[
            customer_column,
            product_column,
        ]
    )

    if data.empty:
        return pd.DataFrame()

    data[product_column] = (
        data[product_column]
        .astype(str)
        .str.strip()
    )

    data = data[
        data[product_column] != ""
    ]

    if data.empty:
        return pd.DataFrame()

    # --------------------------------------------------------
    # Popular products
    # --------------------------------------------------------

    popular_products = (
        data[product_column]
        .value_counts()
        .head(50)
        .index
        .tolist()
    )

    if not popular_products:
        return pd.DataFrame()

    # --------------------------------------------------------
    # Customer purchase history
    # --------------------------------------------------------

    customer_products = (
        data.groupby(customer_column)[product_column]
        .apply(
            lambda x: set(x)
        )
    )

    # --------------------------------------------------------
    # Frequently bought together
    # --------------------------------------------------------

    pair_df = frequently_bought_together(
        df,
        detected_columns,
        limit=100,
    )

    pair_map = {}

    if not pair_df.empty:

        for _, row in pair_df.iterrows():

            product_a = row["Product_A"]
            product_b = row["Product_B"]

            pair_map.setdefault(
                product_a,
                []
            ).append(product_b)

            pair_map.setdefault(
                product_b,
                []
            ).append(product_a)

    results = []

    for customer_id, purchased in customer_products.items():

        recommendations = []

        # ----------------------------------------------------
        # First: recommendations from purchased products
        # ----------------------------------------------------

        for product in purchased:

            related_products = pair_map.get(
                product,
                []
            )

            for recommendation in related_products:

                if recommendation not in purchased:
                    if recommendation not in recommendations:
                        recommendations.append(
                            recommendation
                        )

                if len(recommendations) >= limit:
                    break

            if len(recommendations) >= limit:
                break

        # ----------------------------------------------------
        # Second: fill with popular products
        # ----------------------------------------------------

        if len(recommendations) < limit:

            for product in popular_products:

                if product not in purchased:
                    if product not in recommendations:
                        recommendations.append(
                            product
                        )

                if len(recommendations) >= limit:
                    break

        # ----------------------------------------------------
        # Build customer record
        # ----------------------------------------------------

        record = {
            "Customer ID": customer_id
        }

        for index in range(limit):

            column_name = (
                f"Recommendation {index + 1}"
            )

            if index < len(recommendations):

                record[column_name] = (
                    recommendations[index]
                )

            else:

                record[column_name] = (
                    "No recommendation"
                )

        results.append(record)

    return pd.DataFrame(results)


# ============================================================
# PRODUCT STRATEGY RECOMMENDATIONS
# ============================================================

def product_strategy_recommendations(
    df: pd.DataFrame,
    detected_columns: dict,
    segmented_customers: pd.DataFrame = None,
    limit: int = 6
) -> list:
    """
    Generate business-level product strategy
    recommendations.
    """

    if df is None or df.empty:
        return []

    product_column = detected_columns.get(
        "product"
    )

    if (
        not product_column
        or product_column not in df.columns
    ):
        return []

    data = _prepare_revenue(
        df,
        detected_columns
    )

    if data.empty:
        return []

    # --------------------------------------------------------
    # Top products by revenue
    # --------------------------------------------------------

    product_revenue = (
        data.groupby(
            product_column,
            dropna=True
        )["__Revenue"]
        .sum()
        .sort_values(
            ascending=False
        )
    )

    product_revenue = (
        product_revenue
        .head(10)
    )

    # --------------------------------------------------------
    # Frequently bought products
    # --------------------------------------------------------

    pairs = frequently_bought_together(
        df,
        detected_columns,
        limit=limit,
    )

    recommendations = []

    # --------------------------------------------------------
    # Inventory / visibility recommendation
    # --------------------------------------------------------

    if not product_revenue.empty:

        top_product = (
            product_revenue.index[0]
        )

        recommendations.append(
            "Prioritize inventory and visibility "
            f"for '{top_product}', which is among "
            "the highest-revenue products."
        )

    # --------------------------------------------------------
    # Cross-selling recommendation
    # --------------------------------------------------------

    if not pairs.empty:

        strongest_pair = pairs.iloc[0]

        recommendations.append(
            "Create a cross-selling or bundle "
            f"strategy for '{strongest_pair['Product_A']}' "
            f"and '{strongest_pair['Product_B']}', "
            "which are frequently purchased together."
        )

    # --------------------------------------------------------
    # Segment-based recommendations
    # --------------------------------------------------------

    if (
        segmented_customers is not None
        and not segmented_customers.empty
        and "Segment" in segmented_customers.columns
    ):

        segments = (
            segmented_customers[
                "Segment"
            ]
            .dropna()
            .astype(str)
            .str.lower()
            .value_counts()
        )

        for segment_name, count in segments.items():

            if (
                "at risk" in segment_name
                or "inactive" in segment_name
            ):

                recommendations.append(
                    f"Consider a win-back campaign "
                    f"for approximately {count:,} "
                    "At Risk / Inactive customers."
                )

            elif (
                "potential high" in segment_name
            ):

                recommendations.append(
                    f"Use personalized cross-selling "
                    f"for approximately {count:,} "
                    "Potential High Value customers."
                )

    # --------------------------------------------------------
    # Top-product promotion
    # --------------------------------------------------------

    if len(product_revenue) >= 2:

        second_product = (
            product_revenue.index[1]
        )

        recommendations.append(
            f"Consider promoting '{second_product}' "
            "alongside other high-performing products "
            "to increase basket value."
        )

    # --------------------------------------------------------
    # Limit recommendations
    # --------------------------------------------------------

    return recommendations[:limit]


# ============================================================
# RECOMMENDATION SUMMARY
# ============================================================

def recommendation_summary(
    df: pd.DataFrame,
    detected_columns: dict,
    segmented_customers: pd.DataFrame = None
) -> dict:
    """
    Generate a compact summary of the recommendation engine.
    """

    if df is None or df.empty:
        return {
            "frequently_bought_pairs": 0,
            "popular_products": 0,
            "business_recommendations": 0,
        }

    product_column = detected_columns.get(
        "product"
    )

    popular_products_count = 0

    if (
        product_column
        and product_column in df.columns
    ):

        popular_products_count = (
            df[product_column]
            .dropna()
            .astype(str)
            .str.strip()
            .replace("", pd.NA)
            .dropna()
            .value_counts()
            .head(5)
            .shape[0]
        )

    pair_results = frequently_bought_together(
        df,
        detected_columns,
        limit=10,
    )

    business_results = (
        product_strategy_recommendations(
            df,
            detected_columns,
            segmented_customers=segmented_customers,
            limit=6,
        )
    )

    return {
        "frequently_bought_pairs": int(
            len(pair_results)
        ),
        "popular_products": int(
            popular_products_count
        ),
        "business_recommendations": int(
            len(business_results)
        ),
    }