"""
export_data.py — Export final leads to CSV, Excel, and JSON.
"""

import os


def export_all_formats(df, output_dir, base_name="final_leads"):
    """
    Save df as CSV, Excel, and JSON in output_dir.
    Returns dict of file paths.
    """
    os.makedirs(output_dir, exist_ok=True)

    csv_path = os.path.join(output_dir, f"{base_name}.csv")
    xlsx_path = os.path.join(output_dir, f"{base_name}.xlsx")
    json_path = os.path.join(output_dir, f"{base_name}.json")

    df.to_csv(csv_path, index=False)
    df.to_excel(xlsx_path, index=False, engine="openpyxl")
    df.to_json(json_path, orient="records", indent=2, force_ascii=False)

    print(f"\nExported files:")
    print(f"  CSV   : {csv_path}")
    print(f"  Excel : {xlsx_path}")
    print(f"  JSON  : {json_path}")

    return {"csv": csv_path, "xlsx": xlsx_path, "json": json_path}
