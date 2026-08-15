import pandas as pd


def filter_results(df):
    """
    Filter the dataset to keep only high-quality clinic leads.
    """

    print("\nStarting Lead Filtering...")

    rows_before = len(df)

    # -------------------------------
    # Required Fields
    # -------------------------------

    required_columns = [
        "Clinic Name",
        "Clinic Type",
        "Country",
        "City",
        "Full Address",
        "Phone Number"
    ]

    # Remove rows where required fields are empty
    df = df.dropna(subset=required_columns)

    # Remove blank strings
    for col in required_columns:
        df = df[df[col].astype(str).str.strip() != ""]

    # -------------------------------
    # Keep only valid phone numbers
    # -------------------------------

    if "Phone Valid" in df.columns:
        df = df[df["Phone Valid"] == True]

    rows_after = len(df)

    removed = rows_before - rows_after

    print(f"Rows Before Filtering : {rows_before}")
    print(f"Rows After Filtering  : {rows_after}")
    print(f"Rows Removed          : {removed}")

    return df