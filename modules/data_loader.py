"""
Universal Data Loader
---------------------
Fast CSV / Excel loader for the Universal AI
Business Intelligence platform.

Supports:
- CSV
- XLSX
- XLS
- Fast Excel loading with python-calamine
- Automatic column detection
- Fast preview
- Dataset summary
"""

from pathlib import Path
import pandas as pd


SUPPORTED_EXTENSIONS = {".csv", ".xlsx", ".xls"}


# -------------------------------------------------------------------
# COLUMN ALIASES
# -------------------------------------------------------------------

COLUMN_ALIASES = {
    "customer_id": [
        "customer id",
        "customer_id",
        "customerid",
        "customer",
        "client id",
        "client_id",
        "clientid",
        "client number",
        "user id",
        "user_id",
    ],

    "product": [
        "description",
        "product description",
        "product_description",
        "product name",
        "product_name",
        "product",
        "item description",
        "item_description",
        "item name",
        "item_name",
        "item",
        "sku",
        "stockcode",
        "stock code",
    ],

    "quantity": [
        "quantity",
        "qty",
        "units",
        "units sold",
        "sales quantity",
    ],

    "price": [
        "price",
        "unit price",
        "unit_price",
        "selling price",
        "selling_price",
        "amount",
        "unit cost",
        "unit_cost",
    ],

    "date": [
        "date",
        "order date",
        "order_date",
        "invoice date",
        "invoice_date",
        "invoicedate",
        "transaction date",
        "transaction_date",
        "purchase date",
        "purchase_date",
    ],

    "country": [
        "country",
        "nation",
        "region",
        "market",
    ],

    "order_id": [
        "invoice",
        "invoice id",
        "invoice_id",
        "invoice number",
        "order id",
        "order_id",
        "order number",
        "transaction id",
        "transaction_id",
    ],
}


# -------------------------------------------------------------------
# PRODUCT PRIORITY
# -------------------------------------------------------------------
# Important:
# Description should be preferred over StockCode/SKU when both exist.

PRODUCT_PRIORITY = [
    "description",
    "product description",
    "product_description",
    "product name",
    "product_name",
    "product",
    "item description",
    "item_description",
    "item name",
    "item_name",
    "item",
    "sku",
    "stockcode",
    "stock code",
]


# -------------------------------------------------------------------
# COLUMN NORMALIZATION
# -------------------------------------------------------------------

def normalize_column_name(column_name: str) -> str:
    """
    Normalize a column name for reliable matching.
    """

    return (
        str(column_name)
        .strip()
        .lower()
        .replace("_", " ")
        .replace("-", " ")
        .replace("/", " ")
        .replace(".", " ")
    )


# -------------------------------------------------------------------
# EXACT MATCH
# -------------------------------------------------------------------

def _find_exact_match(normalized_columns, aliases):
    """
    Find the first column that exactly matches one of the aliases.
    """

    alias_set = {
        normalize_column_name(alias)
        for alias in aliases
    }

    for original_column, normalized_column in normalized_columns.items():

        if normalized_column in alias_set:
            return original_column

    return None


# -------------------------------------------------------------------
# PARTIAL MATCH
# -------------------------------------------------------------------

def _find_partial_match(normalized_columns, aliases):
    """
    Find a reasonable partial column-name match.
    """

    normalized_aliases = [
        normalize_column_name(alias)
        for alias in aliases
    ]

    for original_column, normalized_column in normalized_columns.items():

        for alias in normalized_aliases:

            if (
                alias in normalized_column
                or normalized_column in alias
            ):
                return original_column

    return None


# -------------------------------------------------------------------
# AUTOMATIC COLUMN DETECTION
# -------------------------------------------------------------------

def detect_columns(df: pd.DataFrame) -> dict:
    """
    Automatically detect important business columns.

    Product detection intentionally prioritizes:
    Description > Product Name > SKU > StockCode
    """

    detected = {}

    normalized_columns = {
        column: normalize_column_name(column)
        for column in df.columns
    }

    # ---------------------------------------------------------------
    # PRODUCT FIRST
    # ---------------------------------------------------------------
    # We explicitly walk through the priority list so that
    # Description wins over StockCode when both are present.

    product_aliases_normalized = [
        normalize_column_name(alias)
        for alias in PRODUCT_PRIORITY
    ]

    for alias in product_aliases_normalized:

        for original_column, normalized_column in normalized_columns.items():

            if normalized_column == alias:

                detected["product"] = original_column
                break

        if "product" in detected:
            break

    # ---------------------------------------------------------------
    # OTHER BUSINESS COLUMNS
    # ---------------------------------------------------------------

    for business_field, aliases in COLUMN_ALIASES.items():

        if business_field == "product":
            continue

        exact_match = _find_exact_match(
            normalized_columns,
            aliases
        )

        if exact_match is not None:

            detected[business_field] = exact_match
            continue

        partial_match = _find_partial_match(
            normalized_columns,
            aliases
        )

        if partial_match is not None:

            detected[business_field] = partial_match

    # ---------------------------------------------------------------
    # FALLBACK PRODUCT DETECTION
    # ---------------------------------------------------------------

    if "product" not in detected:

        sku_aliases = [
            "sku",
            "stockcode",
            "stock code",
        ]

        sku_match = _find_exact_match(
            normalized_columns,
            sku_aliases
        )

        if sku_match is not None:

            detected["product"] = sku_match

    return detected


# -------------------------------------------------------------------
# LOAD FULL FILE
# -------------------------------------------------------------------

def load_uploaded_file(uploaded_file) -> pd.DataFrame:
    """
    Load a CSV or Excel file.
    """

    if uploaded_file is None:
        raise ValueError("No file was uploaded.")

    filename = getattr(
        uploaded_file,
        "name",
        ""
    )

    if not filename:
        raise ValueError(
            "The uploaded file has no valid filename."
        )

    extension = Path(filename).suffix.lower()

    if extension not in SUPPORTED_EXTENSIONS:

        raise ValueError(
            "Unsupported file type. "
            "Please upload a CSV or Excel file."
        )

    try:

        # -----------------------------------------------------------
        # CSV
        # -----------------------------------------------------------

        if extension == ".csv":

            df = pd.read_csv(
                uploaded_file,
                low_memory=False
            )

        # -----------------------------------------------------------
        # EXCEL
        # -----------------------------------------------------------

        else:

            try:

                df = pd.read_excel(
                    uploaded_file,
                    engine="calamine"
                )

            except Exception:

                uploaded_file.seek(0)

                df = pd.read_excel(
                    uploaded_file
                )

    except Exception as exc:

        raise ValueError(
            f"Unable to read '{filename}'. "
            f"Please check that the file is valid. "
            f"Details: {exc}"
        ) from exc

    if df.empty:

        raise ValueError(
            "The uploaded file contains no data."
        )

    df.columns = (
        df.columns
        .astype(str)
        .str.strip()
    )

    return df


# -------------------------------------------------------------------
# FAST PREVIEW
# -------------------------------------------------------------------

def preview_uploaded_file(
    uploaded_file,
    preview_rows=1000
) -> dict:
    """
    Read only a small preview of the uploaded file.
    """

    if uploaded_file is None:
        raise ValueError("No file was uploaded.")

    filename = getattr(
        uploaded_file,
        "name",
        ""
    )

    if not filename:

        raise ValueError(
            "The uploaded file has no valid filename."
        )

    extension = Path(filename).suffix.lower()

    if extension not in SUPPORTED_EXTENSIONS:

        raise ValueError(
            "Unsupported file type. "
            "Please upload CSV or Excel."
        )

    try:

        # -----------------------------------------------------------
        # CSV PREVIEW
        # -----------------------------------------------------------

        if extension == ".csv":

            preview = pd.read_csv(
                uploaded_file,
                nrows=preview_rows,
                low_memory=False
            )

        # -----------------------------------------------------------
        # EXCEL PREVIEW
        # -----------------------------------------------------------

        else:

            try:

                preview = pd.read_excel(
                    uploaded_file,
                    engine="calamine",
                    nrows=preview_rows
                )

            except Exception:

                uploaded_file.seek(0)

                preview = pd.read_excel(
                    uploaded_file,
                    nrows=preview_rows
                )

    except Exception as exc:

        raise ValueError(
            f"Unable to preview '{filename}'. "
            f"Details: {exc}"
        ) from exc

    if preview.empty:

        raise ValueError(
            "The uploaded file contains no data."
        )

    preview.columns = (
        preview.columns
        .astype(str)
        .str.strip()
    )

    return {
        "preview": preview,
        "filename": filename,
        "extension": extension,
    }


# -------------------------------------------------------------------
# DATASET SUMMARY
# -------------------------------------------------------------------

def get_dataset_summary(df: pd.DataFrame) -> dict:
    """
    Return basic dataset statistics.
    """

    return {
        "rows": int(df.shape[0]),
        "columns": int(df.shape[1]),
        "column_names": df.columns.tolist(),
        "missing_values": int(
            df.isna().sum().sum()
        ),
        "duplicate_rows": int(
            df.duplicated().sum()
        ),
    }