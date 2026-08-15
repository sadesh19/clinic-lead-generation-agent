import pandas as pd


def determine_automation_status(df):
    """
    Determine automation status for each clinic.

    If the clinic already has a valid Automation Status set (e.g. from the
    scraper), that value is preserved.
    Otherwise it is inferred from available columns.
    """

    print("\nDetermining Automation Status...")

    VALID_STATUSES = {"manual", "semi automated", "automated"}

    automation = []

    for _, row in df.iterrows():

        # ── Keep existing value if already meaningful ─────────────────────────
        existing = str(row.get("Automation Status", "")).strip()
        if existing.lower() in VALID_STATUSES:
            automation.append(existing)
            continue

        # ── Infer from indicator columns (data-collection CSV format) ─────────
        appointment = str(row.get("Appointment Method", "")).strip().lower()
        website_booking = str(row.get("Website Booking", "")).strip().lower()
        website_available = str(row.get("Website Availability", "")).strip().lower()
        instagram = str(row.get("Instagram DM", "")).strip().lower()
        whatsapp = str(row.get("Phone + WhatsApp", "")).strip().lower()

        if appointment in ("website booking form", "online booking system"):
            status = "Automated"
        elif (
            website_available in ("yes", "true")
            or instagram == "yes"
            or whatsapp == "yes"
            or website_booking == "yes"
        ):
            status = "Semi Automated"
        else:
            status = "Manual"

        automation.append(status)

    df["Automation Status"] = automation

    print("\nAutomation Status Determined Successfully.")
    print("\nAutomation Status Distribution\n")
    print(df["Automation Status"].value_counts())

    return df