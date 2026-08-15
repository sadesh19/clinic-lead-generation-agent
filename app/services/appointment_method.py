import pandas as pd


def determine_appointment_method(df):
    """
    Determine the appointment method for each clinic.

    If the clinic already has a valid Appointment Method set (e.g. from the
    scraper or Google Maps enrichment), that value is preserved.
    Otherwise it is inferred from the available columns.
    """

    print("\nDetermining Appointment Method...")

    VALID_METHODS = {
        "website booking form", "online booking system",
        "whatsapp", "social media messages", "walk-in", "phone calls",
        "website contact",
    }

    methods = []

    for _, row in df.iterrows():

        # ── Keep existing value if already meaningful ─────────────────────────
        existing = str(row.get("Appointment Method", "")).strip()
        if existing and existing.lower() not in ("", "nan", "none"):
            methods.append(existing)
            continue

        # ── Infer from indicator columns (data-collection CSV format) ─────────
        phone = str(row.get("Phone + WhatsApp", "")).strip().lower()
        website_booking = str(row.get("Website Booking", "")).strip().lower()
        instagram = str(row.get("Instagram DM", "")).strip().lower()
        website = str(row.get("Website URL", "")).strip().lower()
        phone_number = str(row.get("Phone Number", "")).strip()

        if website_booking == "yes":
            method = "Website Booking Form"
        elif phone == "yes":
            method = "WhatsApp"
        elif instagram == "yes":
            method = "Social Media Messages"
        elif phone_number and phone_number not in ("", "nan", "none"):
            method = "Phone Calls"
        elif website and website not in ("", "nan", "none"):
            method = "Website Contact"
        else:
            method = "Unknown"

        methods.append(method)

    df["Appointment Method"] = methods

    print("Appointment Method Determined Successfully.")
    print("\nAppointment Method Distribution\n")
    print(df["Appointment Method"].value_counts())

    return df