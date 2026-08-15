"""
process.py — Standalone data processing pipeline.

Can be run directly after data collection to process leads_output.csv
and produce cleaned, validated, deduped, and exported outputs.

Usage:
    python -m app.services.process
    python -m app.services.process --input "data collection/leads_output.csv"
"""
import os
import sys
import argparse
import pandas as pd

from app.services.save_to_db import save_dataframe_to_mongo
from app.services.export_data import export_all_formats
from app.services.clean_data import clean_data
from app.services.validate import (
    validate_email,
    validate_phone,
    validate_website,
)
from app.services.remove_duplicates import remove_duplicate_leads
from app.services.filter_results import filter_results
from app.services.appointment_method import determine_appointment_method
from app.services.automation_status import determine_automation_status


# ─── File Paths ────────────────────────────────────────────────────────────────

DEFAULT_INPUT  = os.path.join("data collection", "leads_output.csv")
DEFAULT_OUTPUT = "outputs"


# ─── Load Dataset ──────────────────────────────────────────────────────────────

def load_data(file_path: str) -> pd.DataFrame | None:
    """Load clinic lead CSV file."""
    try:
        df = pd.read_csv(file_path)
        print("=" * 60)
        print("CLINIC LEAD DATASET LOADED SUCCESSFULLY")
        print("=" * 60)
        print(f"Total Rows    : {df.shape[0]}")
        print(f"Total Columns : {df.shape[1]}")
        print("\nColumn Names:")
        print(df.columns.tolist())
        return df
    except FileNotFoundError:
        print(f"\nError: File not found\n{file_path}")
        return None
    except Exception as e:
        print(f"\nUnexpected Error: {e}")
        return None


# ─── Save Dataset ──────────────────────────────────────────────────────────────

def save_data(df: pd.DataFrame, output_path: str) -> None:
    """Save dataframe to CSV."""
    os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"\nDataset saved: {output_path}")


# ─── Main Function ─────────────────────────────────────────────────────────────

def main(input_file: str = DEFAULT_INPUT, output_dir: str = DEFAULT_OUTPUT) -> None:

    # Phase 1 — Load Dataset
    print("\nPHASE 1 : LOAD DATASET\n")
    df = load_data(input_file)
    if df is None:
        return
    print("\nFirst 5 Records\n")
    print(df.head())

    # Phase 2 — Clean Data
    print("\nPHASE 2 : CLEAN DATA\n")
    df = clean_data(df)
    save_data(df, os.path.join(output_dir, "cleaned_leads.csv"))

    # Phase 3 — Validate Data
    print("\nPHASE 3 : VALIDATE DATA\n")
    df["Email Valid"]   = df["Email"].apply(validate_email)
    df["Phone Valid"]   = df["Phone Number"].apply(validate_phone)
    df["Website Valid"] = df["Website URL"].apply(validate_website)

    print("\nValidation Summary")
    print("-" * 40)
    print(f"Valid Emails   : {df['Email Valid'].sum()}")
    print(f"Valid Phones   : {df['Phone Valid'].sum()}")
    print(f"Valid Websites : {df['Website Valid'].sum()}")
    save_data(df, os.path.join(output_dir, "validated_leads.csv"))

    # Phase 4 — Remove Duplicates
    print("\nPHASE 4 : REMOVE DUPLICATES\n")
    df = remove_duplicate_leads(df)
    save_data(df, os.path.join(output_dir, "deduplicated_leads.csv"))

    # Phase 5 — Filter Results
    print("\nPHASE 5 : FILTER RESULTS\n")
    df = filter_results(df)
    save_data(df, os.path.join(output_dir, "filtered_leads.csv"))

    # Phase 6 — Appointment Method
    print("\nPHASE 6 : DETERMINE APPOINTMENT METHOD\n")
    df = determine_appointment_method(df)
    print("\nAppointment Method Preview\n")
    if "Appointment Method" in df.columns:
        print(df[["Clinic Name", "Appointment Method"]].head())
    save_data(df, os.path.join(output_dir, "appointment_method_leads.csv"))

    # Phase 7 — Automation Status
    print("\nPHASE 7 : DETERMINE AUTOMATION STATUS\n")
    df = determine_automation_status(df)
    print("\nAutomation Status Preview\n")
    if "Automation Status" in df.columns:
        print(df[["Clinic Name", "Appointment Method", "Automation Status"]].head())
    save_data(df, os.path.join(output_dir, "automation_status_leads.csv"))

    # Phase 8 — Save to MongoDB & Export
    print("\nPHASE 8 : SAVE TO DATABASE & EXPORT\n")
    db_summary = save_dataframe_to_mongo(df)
    print(f"  MongoDB  : {db_summary.get('inserted',0)} inserted, "
          f"{db_summary.get('updated',0)} updated, "
          f"{db_summary.get('skipped',0)} skipped")

    export_all_formats(df, output_dir, base_name="final_leads")

    # Completed
    print("\n" + "=" * 60)
    for i in range(1, 9):
        print(f"PHASE {i} COMPLETED")
    print("=" * 60)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Clinic Lead Data Processing Pipeline")
    parser.add_argument("--input", default=DEFAULT_INPUT, help="Path to leads CSV file")
    parser.add_argument("--output", default=DEFAULT_OUTPUT, help="Output directory")
    args = parser.parse_args()
    main(input_file=args.input, output_dir=args.output)