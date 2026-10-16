"""
Universal Business Analytics
----------------------------
Optimized analytics engine for the Universal AI Business
Intelligence platform.
"""

import pandas as pd


# ============================================================
# REVENUE CALCULATION
# ============================================================

def calculate_revenue(
    df: pd.DataFrame,
    detected_columns: dict,
) -> pd.DataFrame:
    """
    Calculate revenue once and attach it to the DataFrame.

    Revenue priority:
    1. Quantity × Price
    2. Price
    3. Existing Revenue column
    4. Zero
    """

    # Avoid unnecessary copy when revenue already exists.
    data = df.copy()

    quantity_column = detected_columns.get(
        "quantity"
    )

    price_column = detected_columns.get(
        "price"
    )

    # ========================================================
    # QUANTITY × PRICE
    # ========================================================

    if (
        quantity_column
        and price_column
        and quantity_column in data.columns
        and price_column in data.columns
    ):

        quantity = pd.to_numeric(
            data[quantity_column],
            errors="coerce",
        )

        price = pd.to_numeric(
            data[price_column],
            errors="coerce",
        )

        data["__Revenue"] = (
            quantity * price
        )

    # ========================================================
    # PRICE ONLY
    # ========================================================

    elif (
        price_column
        and price_column in data.columns
    ):

        data["__Revenue"] = pd.to_numeric(
            data[price_column],
            errors="coerce",
        )

    # ========================================================
    # EXISTING REVENUE COLUMN
    # ========================================================

    elif "Revenue" in data.columns:

        data["__Revenue"] = pd.to_numeric(
            data["Revenue"],
            errors="coerce",
        )

    # ========================================================
    # NO REVENUE INFORMATION
    # ========================================================

    else:

        data["__Revenue"] = 0.0

    data["__Revenue"] = (
        data["__Revenue"]
        .fillna(0)
    )

    return data


# ============================================================
# KPI CALCULATION
# ============================================================

def calculate_kpis(
    df: pd.DataFrame,
    detected_columns: dict,
) -> dict:
    """
    Calculate the main business KPIs.
    """

    data = calculate_revenue(
        df,
        detected_columns,
    )

    revenue = float(
        data["__Revenue"].sum()
    )

    # ========================================================
    # ORDERS
    # ========================================================

    order_column = detected_columns.get(
        "order_id"
    )

    if (
        order_column
        and order_column in data.columns
    ):

        orders = int(
            data[order_column]
            .dropna()
            .nunique()
        )

    else:

        orders = len(data)

    # ========================================================
    # CUSTOMERS
    # ========================================================

    customer_column = detected_columns.get(
        "customer_id"
    )

    if (
        customer_column
        and customer_column in data.columns
    ):

        customers = int(
            data[customer_column]
            .dropna()
            .nunique()
        )

    else:

        customers = 0

    # ========================================================
    # PRODUCTS
    # ========================================================

    product_column = detected_columns.get(
        "product"
    )

    if (
        product_column
        and product_column in data.columns
    ):

        products = int(
            data[product_column]
            .dropna()
            .nunique()
        )

    else:

        products = 0

    # ========================================================
    # QUANTITY
    # ========================================================

    quantity_column = detected_columns.get(
        "quantity"
    )

    if (
        quantity_column
        and quantity_column in data.columns
    ):

        total_quantity = float(
            pd.to_numeric(
                data[quantity_column],
                errors="coerce",
            )
            .fillna(0)
            .sum()
        )

    else:

        total_quantity = 0.0

    # ========================================================
    # AVERAGES
    # ========================================================

    average_order_value = (
        revenue / orders
        if orders > 0
        else 0.0
    )

    average_customer_value = (
        revenue / customers
        if customers > 0
        else 0.0
    )

    return {

        "revenue": revenue,

        "orders": orders,

        "customers": customers,

        "products": products,

        "quantity": total_quantity,

        "average_order_value": (
            average_order_value
        ),

        "average_customer_value": (
            average_customer_value
        ),
    }


# ============================================================
# MONTHLY REVENUE
# ============================================================

def monthly_revenue(
    df: pd.DataFrame,
    detected_columns: dict,
) -> pd.DataFrame:
    """
    Calculate revenue by month.
    """

    date_column = detected_columns.get(
        "date"
    )

    if (
        not date_column
        or date_column not in df.columns
    ):

        return pd.DataFrame(
            columns=[
                "Month",
                "Revenue",
            ]
        )

    data = calculate_revenue(
        df,
        detected_columns,
    )

    # If cleaning already converted the date,
    # avoid unnecessary conversion.

    if pd.api.types.is_datetime64_any_dtype(
        data[date_column]
    ):

        data["__Date"] = data[
            date_column
        ]

    else:

        data["__Date"] = pd.to_datetime(
            data[date_column],
            errors="coerce",
        )

    data = data.dropna(
        subset=[
            "__Date"
        ]
    )

    if data.empty:

        return pd.DataFrame(
            columns=[
                "Month",
                "Revenue",
            ]
        )

    result = (
        data.groupby(
            data["__Date"].dt.to_period(
                "M"
            )
        )["__Revenue"]
        .sum()
        .reset_index()
    )

    result["Month"] = (
        result["__Date"]
        .dt.to_timestamp()
    )

    result = result[
        [
            "Month",
            "__Revenue",
        ]
    ]

    result = result.rename(
        columns={
            "__Revenue": "Revenue"
        }
    )

    return result


# ============================================================
# TOP PRODUCTS
# ============================================================

def top_products(
    df: pd.DataFrame,
    detected_columns: dict,
    limit: int = 10,
) -> pd.DataFrame:
    """
    Calculate the highest-revenue products.
    """

    product_column = detected_columns.get(
        "product"
    )

    if (
        not product_column
        or product_column not in df.columns
    ):

        return pd.DataFrame()

    data = calculate_revenue(
        df,
        detected_columns,
    )

    result = (
        data.groupby(
            product_column,
            dropna=True,
        )
        .agg(
            Revenue=(
                "__Revenue",
                "sum",
            ),
            Orders=(
                "__Revenue",
                "count",
            ),
        )
        .reset_index()
    )

    result = (
        result
        .sort_values(
            "Revenue",
            ascending=False,
        )
        .head(limit)
    )

    return result.rename(
        columns={
            product_column: "Product"
        }
    )


# ============================================================
# TOP CUSTOMERS
# ============================================================

def top_customers(
    df: pd.DataFrame,
    detected_columns: dict,
    limit: int = 10,
) -> pd.DataFrame:
    """
    Calculate the highest-value customers.
    """

    customer_column = detected_columns.get(
        "customer_id"
    )

    if (
        not customer_column
        or customer_column not in df.columns
    ):

        return pd.DataFrame()

    data = calculate_revenue(
        df,
        detected_columns,
    )

    result = (
        data.groupby(
            customer_column,
            dropna=True,
        )
        .agg(
            Revenue=(
                "__Revenue",
                "sum",
            ),
            Orders=(
                "__Revenue",
                "count",
            ),
        )
        .reset_index()
    )

    result = (
        result
        .sort_values(
            "Revenue",
            ascending=False,
        )
        .head(limit)
    )

    return result.rename(
        columns={
            customer_column: "Customer ID"
        }
    )


# ============================================================
# REVENUE BY COUNTRY
# ============================================================

def revenue_by_country(
    df: pd.DataFrame,
    detected_columns: dict,
    limit: int = 10,
) -> pd.DataFrame:
    """
    Calculate revenue by country/market.
    """

    country_column = detected_columns.get(
        "country"
    )

    if (
        not country_column
        or country_column not in df.columns
    ):

        return pd.DataFrame()

    data = calculate_revenue(
        df,
        detected_columns,
    )

    result = (
        data.groupby(
            country_column,
            dropna=True,
        )["__Revenue"]
        .sum()
        .reset_index()
    )

    result = (
        result
        .sort_values(
            "__Revenue",
            ascending=False,
        )
        .head(limit)
    )

    return result.rename(
        columns={
            country_column: "Country",
            "__Revenue": "Revenue",
        }
    )