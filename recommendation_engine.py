import pandas as pd
import numpy as np


# ============================================================
# RECOMMENDATION ENGINE
# ============================================================

def build_recommendation_engine(
    retail_data,
    customer_segments,
    top_n=10
):
    """
    Business recommendation engine.

    Generates:
        1. Overall popular products
        2. Segment-specific products
        3. Product pair relationships
        4. Customer-level recommendations
        5. Business recommendations
    """

    # ========================================================
    # VALIDATION
    # ========================================================

    if retail_data is None or retail_data.empty:

        return {
            "popular_products": pd.DataFrame(),
            "segment_recommendations": pd.DataFrame(),
            "product_pairs": pd.DataFrame(),
            "customer_recommendations": pd.DataFrame(),
            "business_recommendations": []
        }


    # ========================================================
    # COPY DATA
    # ========================================================

    df = retail_data.copy()

    segments = customer_segments.copy()


    # ========================================================
    # STANDARDIZE CUSTOMER ID
    # ========================================================

    df["Customer ID"] = pd.to_numeric(
        df["Customer ID"],
        errors="coerce"
    )

    segments["Customer ID"] = pd.to_numeric(
        segments["Customer ID"],
        errors="coerce"
    )


    # ========================================================
    # REMOVE INVALID PRODUCTS
    # ========================================================

    df["Description"] = (
        df["Description"]
        .fillna("Unknown Product")
        .astype(str)
        .str.strip()
    )


    df = df[
        (df["Description"] != "")
        &
        (df["Description"] != "nan")
    ].copy()


    # ========================================================
    # POPULAR PRODUCTS
    # ========================================================

    popular_products = (
        df
        .groupby("Description")
        .agg(
            Quantity=("Quantity", "sum"),
            Orders=("Invoice", "nunique"),
            Revenue=("Revenue", "sum")
        )
        .reset_index()
        .sort_values(
            "Quantity",
            ascending=False
        )
        .head(top_n)
    )


    popular_products["Rank"] = (
        np.arange(len(popular_products)) + 1
    )


    popular_products = popular_products[
        [
            "Rank",
            "Description",
            "Quantity",
            "Orders",
            "Revenue"
        ]
    ]


    # ========================================================
    # CUSTOMER + SEGMENT DATA
    # ========================================================

    customer_purchase_data = df[
        df["Customer ID"].notna()
    ].copy()


    customer_purchase_data = (
        customer_purchase_data.merge(
            segments[
                [
                    "Customer ID",
                    "Segment"
                ]
            ],
            on="Customer ID",
            how="left"
        )
    )


    customer_purchase_data["Segment"] = (
        customer_purchase_data["Segment"]
        .fillna("Unknown")
    )


    # ========================================================
    # SEGMENT-SPECIFIC PRODUCT RECOMMENDATIONS
    # ========================================================

    segment_products = (
        customer_purchase_data
        .groupby(
            [
                "Segment",
                "Description"
            ]
        )
        .agg(
            Quantity=("Quantity", "sum"),
            Orders=("Invoice", "nunique"),
            Revenue=("Revenue", "sum")
        )
        .reset_index()
    )


    segment_products["Rank"] = (
        segment_products
        .groupby("Segment")["Quantity"]
        .rank(
            method="first",
            ascending=False
        )
    )


    segment_recommendations = (
        segment_products[
            segment_products["Rank"] <= top_n
        ]
        .sort_values(
            [
                "Segment",
                "Rank"
            ]
        )
        .copy()
    )


    # ========================================================
    # PRODUCT PAIR ANALYSIS
    # ========================================================

    # Find products appearing together in the same invoice.

    invoice_products = (
        customer_purchase_data[
            [
                "Invoice",
                "Description"
            ]
        ]
        .drop_duplicates()
    )


    # Limit extremely large invoices to avoid
    # unnecessary combinations.

    invoice_product_counts = (
        invoice_products
        .groupby("Invoice")
        .size()
    )


    valid_invoices = (
        invoice_product_counts[
            invoice_product_counts <= 50
        ]
        .index
    )


    invoice_products = invoice_products[
        invoice_products["Invoice"]
        .isin(valid_invoices)
    ]


    pair_rows = []


    for invoice, group in invoice_products.groupby(
        "Invoice"
    ):

        products = sorted(
            group["Description"]
            .unique()
        )


        if len(products) < 2:

            continue


        # Maximum combinations per invoice

        for i in range(len(products)):

            for j in range(
                i + 1,
                len(products)
            ):

                pair_rows.append(
                    (
                        products[i],
                        products[j]
                    )
                )


    if pair_rows:

        product_pairs = pd.DataFrame(
            pair_rows,
            columns=[
                "Product_A",
                "Product_B"
            ]
        )


        product_pairs = (
            product_pairs
            .value_counts()
            .reset_index(
                name="Co_Purchase_Count"
            )
            .sort_values(
                "Co_Purchase_Count",
                ascending=False
            )
            .head(20)
        )

    else:

        product_pairs = pd.DataFrame(
            columns=[
                "Product_A",
                "Product_B",
                "Co_Purchase_Count"
            ]
        )


    # ========================================================
    # CUSTOMER LEVEL RECOMMENDATIONS
    # ========================================================

    # Find each customer's previously purchased products.

    customer_history = (
        customer_purchase_data
        .groupby("Customer ID")[
            "Description"
        ]
        .apply(
            lambda x: set(x)
        )
        .to_dict()
    )


    # Product popularity by segment.

    segment_product_lookup = {}


    for segment_name, group in (
        segment_recommendations
        .groupby("Segment")
    ):

        segment_product_lookup[
            segment_name
        ] = group.sort_values(
            "Rank"
        )["Description"].tolist()


    customer_recommendation_rows = []


    # Work through customers in the segmentation file.

    for _, customer in segments.iterrows():

        customer_id = customer["Customer ID"]

        segment = customer["Segment"]


        purchased_products = (
            customer_history.get(
                customer_id,
                set()
            )
        )


        candidate_products = (
            segment_product_lookup.get(
                segment,
                []
            )
        )


        recommendations = []


        for product in candidate_products:

            if product not in purchased_products:

                recommendations.append(
                    product
                )


            if len(recommendations) >= 5:

                break


        # If all segment products were purchased,
        # fall back to overall popular products.

        if len(recommendations) < 5:

            for product in (
                popular_products[
                    "Description"
                ].tolist()
            ):

                if product not in purchased_products:

                    if product not in recommendations:

                        recommendations.append(
                            product
                        )


                if len(recommendations) >= 5:

                    break


        customer_recommendation_rows.append(
            {
                "Customer ID": customer_id,
                "Segment": segment,
                "Recommendation 1":
                    recommendations[0]
                    if len(recommendations) > 0
                    else "No recommendation",
                "Recommendation 2":
                    recommendations[1]
                    if len(recommendations) > 1
                    else "No recommendation",
                "Recommendation 3":
                    recommendations[2]
                    if len(recommendations) > 2
                    else "No recommendation",
                "Recommendation 4":
                    recommendations[3]
                    if len(recommendations) > 3
                    else "No recommendation",
                "Recommendation 5":
                    recommendations[4]
                    if len(recommendations) > 4
                    else "No recommendation"
            }
        )


    customer_recommendations = pd.DataFrame(
        customer_recommendation_rows
    )


    # ========================================================
    # BUSINESS RECOMMENDATIONS
    # ========================================================

    business_recommendations = []


    # --------------------------------------------------------
    # POPULAR PRODUCTS
    # --------------------------------------------------------

    if not popular_products.empty:

        top_product = (
            popular_products.iloc[0]["Description"]
        )

        business_recommendations.append(
            f"Prioritize inventory and visibility for "
            f"'{top_product}', the highest-volume product."
        )


    # --------------------------------------------------------
    # SEGMENT STRATEGIES
    # --------------------------------------------------------

    for segment_name, group in (
        segment_recommendations
        .groupby("Segment")
    ):

        if group.empty:

            continue


        best_product = (
            group.sort_values(
                "Rank"
            ).iloc[0]["Description"]
        )


        if "VIP" in segment_name:

            business_recommendations.append(
                f"Promote '{best_product}' to VIP / Loyal "
                f"customers using premium or exclusive offers."
            )


        elif "Potential High Value" in segment_name:

            business_recommendations.append(
                f"Use '{best_product}' in targeted campaigns "
                f"to convert Potential High Value customers "
                f"into VIP customers."
            )


        elif "Regular" in segment_name:

            business_recommendations.append(
                f"Use '{best_product}' for cross-selling "
                f"and increasing purchase frequency among "
                f"Regular customers."
            )


        elif (
            "At Risk" in segment_name
            or "Inactive" in segment_name
        ):

            business_recommendations.append(
                f"Consider '{best_product}' as part of a "
                f"win-back campaign for At Risk / Inactive customers."
            )


    # --------------------------------------------------------
    # PRODUCT PAIRING
    # --------------------------------------------------------

    if not product_pairs.empty:

        pair = product_pairs.iloc[0]


        business_recommendations.append(
            f"Consider bundling '{pair['Product_A']}' "
            f"with '{pair['Product_B']}', which appear "
            f"together frequently in customer orders."
        )


    # --------------------------------------------------------
    # DEFAULT
    # --------------------------------------------------------

    if not business_recommendations:

        business_recommendations.append(
            "Continue monitoring product demand and "
            "customer purchasing behavior."
        )


    # ========================================================
    # RETURN RESULTS
    # ========================================================

    return {

        "popular_products":
            popular_products,

        "segment_recommendations":
            segment_recommendations,

        "product_pairs":
            product_pairs,

        "customer_recommendations":
            customer_recommendations,

        "business_recommendations":
            business_recommendations
    }


# ============================================================
# TEST MODE
# ============================================================

if __name__ == "__main__":

    print("=" * 60)

    print(
        "RECOMMENDATION ENGINE TEST"
    )

    print("=" * 60)


    print(
        "\nLoading data..."
    )


    retail = pd.read_csv(
        "data/processed/retail_features.csv",
        low_memory=False
    )


    segments = pd.read_csv(
        "data/processed/customer_segments.csv",
        low_memory=False
    )


    print(
        f"Retail rows: {len(retail):,}"
    )

    print(
        f"Customers: {len(segments):,}"
    )


    print(
        "\nBuilding recommendations..."
    )


    results = build_recommendation_engine(
        retail_data=retail,
        customer_segments=segments,
        top_n=10
    )


    print(
        "\n" + "-" * 60
    )

    print(
        "TOP PRODUCTS"
    )

    print(
        "-" * 60
    )


    print(
        results[
            "popular_products"
        ].to_string(
            index=False
        )
    )


    print(
        "\n" + "-" * 60
    )

    print(
        "TOP PRODUCT PAIRS"
    )

    print(
        "-" * 60
    )


    print(
        results[
            "product_pairs"
        ].head(10).to_string(
            index=False
        )
    )


    print(
        "\n" + "-" * 60
    )

    print(
        "BUSINESS RECOMMENDATIONS"
    )

    print(
        "-" * 60
    )


    for index, recommendation in enumerate(
        results[
            "business_recommendations"
        ],
        start=1
    ):

        print(
            f"{index}. {recommendation}"
        )


    print(
        "\n" + "=" * 60
    )

    print(
        "RECOMMENDATION ENGINE COMPLETED"
    )

    print(
        "=" * 60
    )