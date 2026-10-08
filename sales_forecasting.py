import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error


# ============================================================
# CONFIGURATION
# ============================================================

INPUT_FILE = "data/processed/retail_features.csv"

OUTPUT_DIR = "data/processed"

OUTPUT_FILE = os.path.join(
    OUTPUT_DIR,
    "sales_forecast.csv"
)

CHART_FILE = os.path.join(
    OUTPUT_DIR,
    "sales_forecast.png"
)


# ============================================================
# CREATE OUTPUT DIRECTORY
# ============================================================

os.makedirs(
    OUTPUT_DIR,
    exist_ok=True
)


# ============================================================
# LOAD DATA
# ============================================================

print("\n" + "=" * 60)
print("SALES FORECASTING ENGINE")
print("=" * 60)

print("\nLoading retail data...")

df = pd.read_csv(
    INPUT_FILE,
    usecols=[
        "InvoiceDate",
        "Revenue"
    ],
    low_memory=False
)

df["InvoiceDate"] = pd.to_datetime(
    df["InvoiceDate"],
    errors="coerce"
)

df = df.dropna(
    subset=[
        "InvoiceDate",
        "Revenue"
    ]
)

print(
    f"Rows loaded: {len(df):,}"
)


# ============================================================
# MONTHLY REVENUE
# ============================================================

print("\nAggregating monthly revenue...")

monthly = (
    df
    .set_index("InvoiceDate")
    .resample("MS")["Revenue"]
    .sum()
    .reset_index()
)


monthly.columns = [
    "Month",
    "Revenue"
]


print(
    f"Historical months: {len(monthly)}"
)


print("\nHistorical revenue:")

print(
    monthly.to_string(index=False)
)


# ============================================================
# FEATURE ENGINEERING
# ============================================================

monthly["Time_Index"] = np.arange(
    len(monthly)
)

monthly["Month_Number"] = (
    monthly["Month"].dt.month
)


# Cyclical seasonal features

monthly["Month_Sin"] = np.sin(
    2 * np.pi
    * monthly["Month_Number"]
    / 12
)

monthly["Month_Cos"] = np.cos(
    2 * np.pi
    * monthly["Month_Number"]
    / 12
)


# ============================================================
# MODEL FEATURES
# ============================================================

features = [
    "Time_Index",
    "Month_Sin",
    "Month_Cos"
]


X = monthly[features]

y = monthly["Revenue"]


# ============================================================
# TRAINING
# ============================================================

print("\nTraining forecasting model...")

model = LinearRegression()

model.fit(
    X,
    y
)


# ============================================================
# HISTORICAL PREDICTIONS
# ============================================================

monthly["Predicted_Revenue"] = model.predict(
    X
)


# ============================================================
# MODEL EVALUATION
# ============================================================

mae = mean_absolute_error(
    y,
    monthly["Predicted_Revenue"]
)

rmse = np.sqrt(
    mean_squared_error(
        y,
        monthly["Predicted_Revenue"]
    )
)


print("\n" + "-" * 60)

print("MODEL PERFORMANCE")

print("-" * 60)

print(
    f"Mean Absolute Error : £{mae:,.2f}"
)

print(
    f"Root Mean Square Error : £{rmse:,.2f}"
)


# ============================================================
# FORECAST NEXT 3 MONTHS
# ============================================================

FORECAST_MONTHS = 3


last_month = monthly["Month"].max()


future_dates = pd.date_range(
    start=last_month + pd.DateOffset(months=1),
    periods=FORECAST_MONTHS,
    freq="MS"
)


future = pd.DataFrame(
    {
        "Month": future_dates
    }
)


future["Time_Index"] = np.arange(
    len(monthly),
    len(monthly) + FORECAST_MONTHS
)


future["Month_Number"] = (
    future["Month"].dt.month
)


future["Month_Sin"] = np.sin(
    2 * np.pi
    * future["Month_Number"]
    / 12
)


future["Month_Cos"] = np.cos(
    2 * np.pi
    * future["Month_Number"]
    / 12
)


# ============================================================
# GENERATE FORECAST
# ============================================================

future["Forecast_Revenue"] = model.predict(
    future[features]
)


# Prevent negative forecast values

future["Forecast_Revenue"] = (
    future["Forecast_Revenue"]
    .clip(lower=0)
)


# ============================================================
# FORECAST OUTPUT
# ============================================================

forecast_output = future[
    [
        "Month",
        "Forecast_Revenue"
    ]
].copy()


forecast_output["Month"] = (
    forecast_output["Month"]
    .dt.strftime("%Y-%m-%d")
)


# ============================================================
# SAVE FORECAST
# ============================================================

forecast_output.to_csv(
    OUTPUT_FILE,
    index=False
)


print("\n" + "-" * 60)

print("NEXT 3 MONTH FORECAST")

print("-" * 60)

print(
    forecast_output.to_string(
        index=False
    )
)


# ============================================================
# FORECAST SUMMARY
# ============================================================

total_forecast = (
    future["Forecast_Revenue"]
    .sum()
)

average_forecast = (
    future["Forecast_Revenue"]
    .mean()
)


print("\n" + "-" * 60)

print("FORECAST SUMMARY")

print("-" * 60)

print(
    f"Expected revenue over next "
    f"{FORECAST_MONTHS} months: "
    f"£{total_forecast:,.2f}"
)

print(
    f"Average monthly forecast: "
    f"£{average_forecast:,.2f}"
)


# ============================================================
# VISUALIZATION
# ============================================================

print("\nCreating forecast chart...")


plt.figure(
    figsize=(12, 6)
)


# Historical revenue

plt.plot(
    monthly["Month"],
    monthly["Revenue"],
    marker="o",
    label="Historical Revenue"
)


# Forecast revenue

plt.plot(
    future["Month"],
    future["Forecast_Revenue"],
    marker="o",
    linestyle="--",
    label="Forecast Revenue"
)


# Forecast boundary

plt.axvline(
    x=last_month,
    linestyle=":"
)


plt.title(
    "Retail Revenue Forecast"
)

plt.xlabel(
    "Month"
)

plt.ylabel(
    "Revenue (£)"
)


plt.legend()

plt.grid(
    alpha=0.3
)


plt.tight_layout()


plt.savefig(
    CHART_FILE,
    dpi=150
)


plt.close()


# ============================================================
# FINAL OUTPUT
# ============================================================

print("\n" + "=" * 60)

print("SALES FORECASTING COMPLETED SUCCESSFULLY")

print("=" * 60)

print(
    f"\nForecast file:"
    f"\n{OUTPUT_FILE}"
)

print(
    f"\nForecast chart:"
    f"\n{CHART_FILE}"
)

print(
    "\nForecast period:"
)

print(
    f"{future_dates.min().date()} "
    f"→ "
    f"{future_dates.max().date()}"
)

print("\n")