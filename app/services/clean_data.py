import pandas as pd


def clean_data(df):
    """
    Clean the clinic lead dataset.
    """

    # Remove completely empty rows
    df = df.dropna(how="all")

    # Convert list-type columns to strings so pandas can hash them for dedup
    for col in df.columns:
        if df[col].dtype == "object":
            df[col] = df[col].apply(
                lambda x: ", ".join(x) if isinstance(x, list) else x
            )

    # Remove duplicate rows
    df = df.drop_duplicates()

    # Remove leading/trailing spaces from all text columns
    for col in df.columns:
        if df[col].dtype == "object":
            df[col] = df[col].astype(str).str.strip()

    # Replace empty strings with NA
    df = df.replace("", pd.NA)

    # Standardize Website Available column (if it exists)
    if "Website Available" in df.columns:
        df["Website Available"] = (
            df["Website Available"]
            .astype(str)
            .str.strip()
            .str.lower()
            .replace({
                "yes": "Yes",
                "true": "Yes",
                "1": "Yes",
                "no": "No",
                "false": "No",
                "0": "No"
            })
        )

    print("\nData Cleaning Completed")
    print(f"Remaining Rows: {len(df)}")

    return df