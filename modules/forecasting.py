"""
Universal Sales Forecasting
---------------------------
Creates monthly revenue forecasts using Linear Regression.
"""

import pandas as pd
from sklearn.linear_model import LinearRegression


def prepare_monthly_sales(
    df: pd.DataFrame,
    detected_columns: dict
) -> pd.DataFrame:
    """
    Convert transaction-level data into monthly revenue.
    """

    if df is None or df.empty:
        return pd.DataFrame(columns=["Month", "Revenue"])

    date_column = detected_columns.get("date")
    quantity_column = detected_columns.get("quantity")
    price_column = detected_columns.get("price")

    if not date_column or date_column not in df.columns:
        return pd.DataFrame(columns=["Month", "Revenue"])

    data = df.copy()

    # ---------------------------------------------------------
    # Create revenue
    # ---------------------------------------------------------
    if (
        quantity_column
        and price_column
        and quantity_column in data.columns
        and price_column in data.columns
    ):
        quantity = pd.to_numeric(
            data[quantity_column],
            errors="coerce"
        )

        price = pd.to_numeric(
            data[price_column],
            errors="coerce"
        )

        data["__Revenue"] = quantity * price

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
        return pd.DataFrame(columns=["Month", "Revenue"])

    # ---------------------------------------------------------
    # Convert date
    # ---------------------------------------------------------
    data["__Date"] = pd.to_datetime(
        data[date_column],
        errors="coerce"
    )

    data["__Revenue"] = data["__Revenue"].fillna(0)

    # Remove invalid dates
    data = data.dropna(
        subset=["__Date"]
    )

    if data.empty:
        return pd.DataFrame(columns=["Month", "Revenue"])

    # ---------------------------------------------------------
    # Monthly aggregation
    # ---------------------------------------------------------
    monthly = (
        data.groupby(
            data["__Date"].dt.to_period("M")
        )["__Revenue"]
        .sum()
        .reset_index()
    )

    monthly["Month"] = (
        monthly["__Date"]
        .dt.to_timestamp()
    )

    monthly = (
        monthly[
            ["Month", "__Revenue"]
        ]
        .rename(
            columns={
                "__Revenue": "Revenue"
            }
        )
        .sort_values("Month")
        .reset_index(drop=True)
    )

    return monthly


def forecast_sales(
    df: pd.DataFrame,
    detected_columns: dict,
    periods: int = 3
) -> pd.DataFrame:
    """
    Forecast future monthly revenue.

    Parameters
    ----------
    df : DataFrame
        Cleaned transaction data.

    detected_columns : dict
        Automatically detected business columns.

    periods : int
        Number of future months to forecast.

    Returns
    -------
    DataFrame
        Future months with forecast revenue.
    """

    # ---------------------------------------------------------
    # Validate forecast period
    # ---------------------------------------------------------
    if periods <= 0:
        return pd.DataFrame(
            columns=[
                "Month",
                "Forecast Revenue"
            ]
        )

    monthly = prepare_monthly_sales(
        df,
        detected_columns
    )

    if monthly.empty:
        return pd.DataFrame(
            columns=[
                "Month",
                "Forecast Revenue"
            ]
        )

    # At least two historical months required
    if len(monthly) < 2:
        return pd.DataFrame(
            columns=[
                "Month",
                "Forecast Revenue"
            ]
        )

    monthly = monthly.copy()

    # ---------------------------------------------------------
    # Numeric time index
    # ---------------------------------------------------------
    monthly["Time_Index"] = range(
        len(monthly)
    )

    X = monthly[
        ["Time_Index"]
    ]

    y = monthly[
        "Revenue"
    ]

    # ---------------------------------------------------------
    # Train Linear Regression model
    # ---------------------------------------------------------
    model = LinearRegression()

    model.fit(
        X,
        y
    )

    # ---------------------------------------------------------
    # Future time indexes
    # ---------------------------------------------------------
    future_indexes = list(
        range(
            len(monthly),
            len(monthly) + periods
        )
    )

    # ---------------------------------------------------------
    # Future dates
    # ---------------------------------------------------------
    last_month = monthly["Month"].max()

    future_dates = pd.date_range(
        start=last_month
        + pd.offsets.MonthBegin(1),
        periods=periods,
        freq="MS"
    )

    # ---------------------------------------------------------
    # Generate predictions
    # ---------------------------------------------------------
    predictions = model.predict(
        pd.DataFrame(
            {
                "Time_Index": future_indexes
            }
        )
    )

    # Revenue cannot be negative
    predictions = predictions.clip(
        min=0
    )

    forecast = pd.DataFrame(
        {
            "Month": future_dates,
            "Forecast Revenue": predictions
        }
    )

    return forecast


def forecast_summary(
    forecast: pd.DataFrame
) -> dict:
    """
    Generate summary statistics for the forecast.
    """

    if (
        forecast is None
        or forecast.empty
    ):
        return {
            "forecast_periods": 0,
            "total_forecast": 0.0,
            "average_monthly_forecast": 0.0
        }

    total_forecast = float(
        forecast["Forecast Revenue"]
        .sum()
    )

    average_forecast = float(
        forecast["Forecast Revenue"]
        .mean()
    )

    return {
        "forecast_periods": int(
            len(forecast)
        ),
        "total_forecast": total_forecast,
        "average_monthly_forecast": average_forecast
    }


def forecast_accuracy(
    df: pd.DataFrame,
    detected_columns: dict
) -> dict:
    """
    Evaluate the forecasting model using
    a simple holdout approach.

    The model is trained on earlier months
    and tested against the final available month.
    """

    monthly = prepare_monthly_sales(
        df,
        detected_columns
    )

    # Need enough historical data
    if len(monthly) < 4:
        return {
            "mae": None,
            "rmse": None
        }

    # ---------------------------------------------------------
    # Train / test split
    # ---------------------------------------------------------
    train = monthly.iloc[:-1].copy()
    test = monthly.iloc[-1:].copy()

    train["Time_Index"] = range(
        len(train)
    )

    test["Time_Index"] = [
        len(train)
    ]

    # ---------------------------------------------------------
    # Train model
    # ---------------------------------------------------------
    model = LinearRegression()

    model.fit(
        train[["Time_Index"]],
        train["Revenue"]
    )

    # ---------------------------------------------------------
    # Prediction
    # ---------------------------------------------------------
    prediction = float(
        model.predict(
            test[["Time_Index"]]
        )[0]
    )

    actual = float(
        test["Revenue"].iloc[0]
    )

    error = prediction - actual

    # Mean Absolute Error
    mae = abs(error)

    # Root Mean Squared Error
    rmse = (error ** 2) ** 0.5

    return {
        "mae": float(mae),
        "rmse": float(rmse)
    }


def forecast_insights(
    forecast: pd.DataFrame
) -> dict:
    """
    Generate simple business insights from
    forecasted revenue.
    """

    if (
        forecast is None
        or forecast.empty
        or len(forecast) < 2
    ):
        return {
            "trend": "Insufficient Data",
            "change_percentage": 0.0,
            "message": (
                "There is not enough forecast data "
                "to determine a future revenue trend."
            )
        }

    first_value = float(
        forecast["Forecast Revenue"].iloc[0]
    )

    last_value = float(
        forecast["Forecast Revenue"].iloc[-1]
    )

    if first_value == 0:
        change_percentage = (
            100.0
            if last_value > 0
            else 0.0
        )
    else:
        change_percentage = (
            (last_value - first_value)
            / abs(first_value)
        ) * 100

    # ---------------------------------------------------------
    # Determine trend
    # ---------------------------------------------------------
    if change_percentage > 5:
        trend = "Increasing"

        message = (
            f"Forecast revenue shows an increasing trend "
            f"of approximately {change_percentage:.1f}% "
            f"across the forecast period."
        )

    elif change_percentage < -5:
        trend = "Decreasing"

        message = (
            f"Forecast revenue shows a decreasing trend "
            f"of approximately {abs(change_percentage):.1f}% "
            f"across the forecast period."
        )

    else:
        trend = "Stable"

        message = (
            "Forecast revenue remains relatively stable "
            "across the forecast period."
        )

    return {
        "trend": trend,
        "change_percentage": float(
            change_percentage
        ),
        "message": message
    }