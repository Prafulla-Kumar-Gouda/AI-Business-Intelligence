"""
Universal Data Cleaner
----------------------
Optimized cleaning pipeline for the Universal AI
Business Intelligence platform.
"""

import pandas as pd


def clean_dataset(
    df: pd.DataFrame,
    detected_columns: dict,
):
    """
    Clean a business dataset efficiently.

    Returns:
        cleaned_df
        cleaning_report
    """

    if df is None or df.empty:
        raise ValueError(
            "The dataset is empty and cannot be cleaned."
        )

    # ========================================================
    # START
    # ========================================================

    original_rows = len(df)

    # Work on a copy so the uploaded DataFrame remains intact.
    data = df.copy()

    empty_rows_removed = 0
    empty_columns_removed = 0
    duplicate_rows_removed = 0
    invalid_date_rows = 0
    invalid_quantity_rows = 0
    invalid_price_rows = 0

    # ========================================================
    # REMOVE COMPLETELY EMPTY COLUMNS
    # ========================================================

    before_columns = data.shape[1]

    data = data.dropna(
        axis=1,
        how="all",
    )

    empty_columns_removed = (
        before_columns - data.shape[1]
    )

    # ========================================================
    # REMOVE COMPLETELY EMPTY ROWS
    # ========================================================

    before_rows = len(data)

    data = data.dropna(
        axis=0,
        how="all",
    )

    empty_rows_removed = (
        before_rows - len(data)
    )

    # ========================================================
    # NORMALIZE TEXT COLUMNS
    # ========================================================

    # Only process object/string columns.
    # This avoids unnecessary work on numeric columns.

    text_columns = data.select_dtypes(
        include=["object", "string"]
    ).columns

    for column in text_columns:

        data[column] = (
            data[column]
            .astype("string")
            .str.strip()
        )

        data[column] = data[column].replace(
            {
                "": pd.NA,
                "nan": pd.NA,
                "NaN": pd.NA,
                "NULL": pd.NA,
                "null": pd.NA,
                "None": pd.NA,
            }
        )

    # ========================================================
    # REMOVE DUPLICATES
    # ========================================================

    before_rows = len(data)

    data = data.drop_duplicates(
        ignore_index=True
    )

    duplicate_rows_removed = (
        before_rows - len(data)
    )

    # ========================================================
    # DATE CLEANING
    # ========================================================

    date_column = detected_columns.get(
        "date"
    )

    if (
        date_column
        and date_column in data.columns
    ):

        original_date = data[date_column]

        parsed_date = pd.to_datetime(
            original_date,
            errors="coerce",
        )

        invalid_date_mask = (
            parsed_date.isna()
            & original_date.notna()
        )

        invalid_date_rows = int(
            invalid_date_mask.sum()
        )

        # Only remove invalid dates when
        # at least some valid dates exist.

        if parsed_date.notna().any():

            data[date_column] = parsed_date

            valid_date_mask = (
                parsed_date.notna()
            )

            data = data.loc[
                valid_date_mask
            ].copy()

    # ========================================================
    # QUANTITY CLEANING
    # ========================================================

    quantity_column = detected_columns.get(
        "quantity"
    )

    if (
        quantity_column
        and quantity_column in data.columns
    ):

        numeric_quantity = pd.to_numeric(
            data[quantity_column],
            errors="coerce",
        )

        invalid_quantity_mask = (
            numeric_quantity.isna()
            & data[quantity_column].notna()
        )

        invalid_quantity_rows = int(
            invalid_quantity_mask.sum()
        )

        data[quantity_column] = (
            numeric_quantity
        )

        # Remove non-positive quantities
        # only if there are valid positive values.

        positive_quantity_mask = (
            numeric_quantity > 0
        )

        if positive_quantity_mask.any():

            data = data.loc[
                positive_quantity_mask
            ].copy()

    # ========================================================
    # PRICE CLEANING
    # ========================================================

    price_column = detected_columns.get(
        "price"
    )

    if (
        price_column
        and price_column in data.columns
    ):

        numeric_price = pd.to_numeric(
            data[price_column],
            errors="coerce",
        )

        invalid_price_mask = (
            numeric_price.isna()
            & data[price_column].notna()
        )

        invalid_price_rows = int(
            invalid_price_mask.sum()
        )

        data[price_column] = (
            numeric_price
        )

        # Remove non-positive prices
        # only if valid positive values exist.

        positive_price_mask = (
            numeric_price > 0
        )

        if positive_price_mask.any():

            data = data.loc[
                positive_price_mask
            ].copy()

    # ========================================================
    # FINAL RESET
    # ========================================================

    data = data.reset_index(
        drop=True
    )

    final_rows = len(data)

    rows_removed = (
        original_rows - final_rows
    )

    # ========================================================
    # REPORT
    # ========================================================

    cleaning_report = {

        "original_rows": int(
            original_rows
        ),

        "final_rows": int(
            final_rows
        ),

        "rows_removed": int(
            rows_removed
        ),

        "empty_rows_removed": int(
            empty_rows_removed
        ),

        "empty_columns_removed": int(
            empty_columns_removed
        ),

        "duplicate_rows_removed": int(
            duplicate_rows_removed
        ),

        "invalid_date_rows": int(
            invalid_date_rows
        ),

        "invalid_quantity_rows": int(
            invalid_quantity_rows
        ),

        "invalid_price_rows": int(
            invalid_price_rows
        ),

        "final_columns": int(
            data.shape[1]
        ),

        "missing_values_remaining": int(
            data.isna()
            .sum()
            .sum()
        ),
    }

    return data, cleaning_report