import pandas as pd


def remove_duplicate_leads(df):
    """
    Remove duplicate clinic leads based on
    Clinic Name + Phone Number + Website URL.
    """

    print("\nStarting Duplicate Detection...")

    rows_before = len(df)

    # Normalize text columns
    df["Clinic Name"] = (
        df["Clinic Name"]
        .astype(str)
        .str.lower()
        .str.strip()
    )

    df["Phone Number"] = (
        df["Phone Number"]
        .astype(str)
        .str.replace(" ", "", regex=False)
        .str.replace("-", "", regex=False)
        .str.replace("(", "", regex=False)
        .str.replace(")", "", regex=False)
    )

    df["Website URL"] = (
        df["Website URL"]
        .astype(str)
        .str.lower()
        .str.replace("https://", "", regex=False)
        .str.replace("http://", "", regex=False)
        .str.replace("www.", "", regex=False)
        .str.strip()
    )

    # Remove business duplicates
    df = df.drop_duplicates(
        subset=[
            "Clinic Name",
            "Phone Number",
            "Website URL"
        ],
        keep="first"
    )

    rows_after = len(df)

    duplicates_removed = rows_before - rows_after

    print(f"Rows Before : {rows_before}")
    print(f"Rows After  : {rows_after}")
    print(f"Duplicates Removed : {duplicates_removed}")

    return df