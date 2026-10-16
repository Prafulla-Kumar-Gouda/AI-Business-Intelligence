import pandas as pd

from modules.data_loader import detect_columns
from modules.segmentation import segment_customers
from modules.forecasting import forecast_sales
from modules.recommendations import product_strategy_recommendations
from modules.ai_insights import generate_ai_insights


df = pd.DataFrame({
    "Customer ID": [1001, 1001, 1002, 1002, 1002, 1003, 1003, 1004],
    "Product": ["A", "B", "A", "B", "C", "A", "C", "D"],
    "Quantity": [2, 1, 3, 2, 1, 4, 2, 5],
    "Price": [10, 20, 10, 20, 30, 10, 30, 15],
    "Date": [
        "2026-01-01",
        "2026-01-01",
        "2026-01-02",
        "2026-01-02",
        "2026-01-02",
        "2026-02-01",
        "2026-02-01",
        "2026-02-10"
    ],
    "Country": [
        "India",
        "India",
        "India",
        "India",
        "India",
        "USA",
        "USA",
        "UK"
    ],
    "Order ID": [
        "O1", "O1", "O2", "O2",
        "O2", "O3", "O3", "O4"
    ]
})


detected = detect_columns(df)

segmented = segment_customers(
    df,
    detected,
    n_clusters=3
)

forecast = forecast_sales(
    df,
    detected,
    periods=3
)

recommendations = product_strategy_recommendations(
    df,
    detected,
    segmented
)

insights = generate_ai_insights(
    df=df,
    detected_columns=detected,
    segmented_customers=segmented,
    forecast=forecast,
    recommendations=recommendations
)


print("\nAI BUSINESS INSIGHTS")
print("=" * 60)

for section, items in insights.items():
    print(f"\n{section.upper()}")
    print("-" * 60)

    if items:
        for item in items:
            print(f"• {item}")
    else:
        print("No insights generated.")


print("\n" + "=" * 60)
print("AI INSIGHTS TEST COMPLETED SUCCESSFULLY")
print("=" * 60)