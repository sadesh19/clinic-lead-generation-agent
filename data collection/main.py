import os
import time
import requests
import pandas as pd
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import re
import json

# Load environment variables
load_dotenv()
API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")

# New Places API endpoints
PLACES_TEXT_SEARCH_URL = "https://places.googleapis.com/v1/places:searchText"

# ─── Target Configuration ─────────────────────────────────────────────────────

TARGET_LOCATIONS = {
    "United Kingdom": ["London", "Manchester", "Birmingham", "Leeds", "Bristol"],
}

CLINIC_TYPES = [
    "Dental Clinic",
    "Aesthetic Clinic",
    "Skin Clinic",
    "Cosmetic Clinic",
    "Physiotherapy Clinic",
    "Hair Transplant Clinic",
    "Eye Clinic",
    "Private Medical Clinic",
    "Wellness & Health Center",
]

PROGRESS_FILE = "progress.json"
OUTPUT_FILE   = "leads_output.csv"


# ─── Progress Tracker ─────────────────────────────────────────────────────────

def load_progress():
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, "r") as f:
            return json.load(f)
    return {"completed": []}


def save_progress(progress):
    with open(PROGRESS_FILE, "w") as f:
        json.dump(progress, f, indent=2)


# ─── Lead Generator ───────────────────────────────────────────────────────────

class ClinicLeadGenerator:
    def __init__(self, api_key):
        if not api_key:
            raise ValueError("Google Maps API Key is required.")
        self.api_key = api_key
        self.leads = []
        self.seen = set()  # Deduplicate by (name, address)

    def load_existing_leads(self, filename):
        """Load any previously saved leads to avoid duplicates on resume."""
        if os.path.exists(filename):
            df = pd.read_csv(filename)
            self.leads = df.to_dict("records")
            for lead in self.leads:
                key = (str(lead.get("Clinic Name", "")).lower(),
                       str(lead.get("Full Address", "")).lower())
                self.seen.add(key)
            print(f"Loaded {len(self.leads)} existing leads from '{filename}'")

    def search_clinics(self, city, country, clinic_type):
        query = f"{clinic_type} in {city}, {country}"
        print(f"\n  Searching: {query}")

        headers = {
            "Content-Type": "application/json",
            "X-Goog-Api-Key": self.api_key,
            "X-Goog-FieldMask": (
                "places.id,places.displayName,places.formattedAddress,"
                "places.nationalPhoneNumber,places.websiteUri,"
                "places.rating,places.userRatingCount,"
                "places.addressComponents,nextPageToken"
            ),
        }

        payload = {"textQuery": query, "languageCode": "en"}
        page_token = None
        page = 1
        new_leads = 0

        while True:
            if page_token:
                payload["pageToken"] = page_token

            try:
                resp = requests.post(
                    PLACES_TEXT_SEARCH_URL, json=payload,
                    headers=headers, timeout=15
                )
                resp.raise_for_status()
                data = resp.json()
            except Exception as e:
                print(f"    [!] API error (page {page}): {e}")
                break

            places = data.get("places", [])
            print(f"    Page {page}: {len(places)} places found")

            for place in places:
                lead = self._process_place(place, city, country, clinic_type)
                if lead:
                    key = (lead["Clinic Name"].lower(), lead["Full Address"].lower())
                    if key not in self.seen:
                        self.seen.add(key)
                        self.leads.append(lead)
                        new_leads += 1
                time.sleep(0.25)

            page_token = data.get("nextPageToken")
            if not page_token:
                break

            page += 1
            time.sleep(2)

        print(f"    +{new_leads} new leads (total so far: {len(self.leads)})")
        return new_leads

    def _process_place(self, place, city, country, clinic_type):
        try:
            name    = place.get("displayName", {}).get("text", "")
            address = place.get("formattedAddress", "")
            phone   = place.get("nationalPhoneNumber", "")
            website = place.get("websiteUri", "")
            rating  = place.get("rating", "")
            reviews = place.get("userRatingCount", "")

            # Extract city & country from address components
            extracted_city    = ""
            extracted_country = ""
            for comp in place.get("addressComponents", []):
                types = comp.get("types", [])
                if "locality" in types:
                    extracted_city = comp.get("longText", "")
                if "country" in types:
                    extracted_country = comp.get("longText", "")

            lead = {
                "Clinic Name":        name,
                "Clinic Type":        clinic_type,
                "Country":            extracted_country or country,
                "City":               extracted_city or city,
                "Full Address":       address,
                "Phone Number":       phone,
                "Email":              "",
                "Website Availability": "Yes" if website else "No",
                "Website URL":        website,
                "Doctor/Owner Name":  "",
                "Social Media Links": "",
                "Appointment Method": "",
                "Automation Status":  "",
                "Google Rating":      rating,
                "Reviews Count":      reviews,
                "Notes":              "",
                "Lead ID":            "",
                "Phone + WhatsApp":   phone,
                "Instagram DM":       "",
                "Website Booking":    "",
                "Call Status":        "",
                "Follow-up Date":     "",
                "Lead Priority":      "",
            }

            if website:
                self._scrape_website_info(lead, website)

            return lead

        except Exception as e:
            print(f"    [!] Error processing place: {e}")
            return None

    def _scrape_website_info(self, lead, url):
        try:
            headers = {
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/120.0.0.0 Safari/537.36"
                )
            }
            resp = requests.get(url, headers=headers, timeout=10)
            resp.raise_for_status()

            soup = BeautifulSoup(resp.content, "html.parser")
            text = soup.get_text().lower()

            # Emails
            emails = set(re.findall(r"[a-z0-9\.\-+_]+@[a-z0-9\.\-+_]+\.[a-z]+", text))
            noise  = {"example", "sentry", "wix", "schema", "wordpress", "jquery",
                      "privacy", "support", "test", "noreply"}
            emails = {e for e in emails if not any(n in e for n in noise)}
            if emails:
                lead["Email"] = ", ".join(list(emails)[:2])

            # Social media links
            social = []
            for tag in soup.find_all("a", href=True):
                href = tag["href"]
                low  = href.lower()
                if ("instagram.com" in low or "facebook.com" in low) and href not in social:
                    social.append(href)
            if social:
                lead["Social Media Links"] = ", ".join(social)

            # Instagram DM
            insta = [l for l in social if "instagram.com" in l.lower()]
            if insta:
                lead["Instagram DM"] = insta[0]

            # Appointment methods
            methods = []
            if any(kw in text for kw in ["book online", "book appointment", "book now", "booking"]):
                methods.append("Website Booking Form")
                lead["Website Booking"]   = "Yes"
                lead["Automation Status"] = "Semi Automated / Automated"

            if "whatsapp" in text or "wa.me" in text:
                methods.append("WhatsApp")
                if not lead["Automation Status"]:
                    lead["Automation Status"] = "Semi Automated"

            if any(kw in text for kw in ["chatbot", "automated reminder", "crm system", "online booking system"]):
                lead["Automation Status"] = "Automated"

            if not lead["Automation Status"]:
                lead["Automation Status"] = "Manual"

            lead["Appointment Method"] = ", ".join(methods) if methods else "Phone Calls"

        except Exception as e:
            print(f"      [scrape] {url[:60]}... -> {type(e).__name__}")
            if not lead["Automation Status"]:
                lead["Automation Status"] = "Manual"
            if not lead["Appointment Method"]:
                lead["Appointment Method"] = "Phone Calls"

    def export_to_csv(self, filename=OUTPUT_FILE):
        if not self.leads:
            print("No leads to export.")
            return

        # Assign Lead IDs
        for i, lead in enumerate(self.leads, start=1):
            lead["Lead ID"] = f"L{i:04d}"

        columns = [
            "Lead ID", "Clinic Name", "Clinic Type", "Country", "City",
            "Full Address", "Phone Number", "Email", "Website Availability",
            "Website URL", "Doctor/Owner Name", "Social Media Links",
            "Appointment Method", "Automation Status", "Google Rating",
            "Reviews Count", "Lead Priority", "Notes", "Call Status",
            "Follow-up Date", "Phone + WhatsApp", "Instagram DM", "Website Booking",
        ]

        df = pd.DataFrame(self.leads)
        export_cols = [c for c in columns if c in df.columns]
        df[export_cols].to_csv(filename, index=False, encoding="utf-8-sig")
        print(f"\nExported {len(self.leads)} leads to '{filename}'")


# ─── Main ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 60)
    print("  Clinic Lead Generation — Full Run")
    print("=" * 60)

    if not API_KEY:
        print("ERROR: GOOGLE_MAPS_API_KEY not set in .env file.")
        exit(1)

    generator = ClinicLeadGenerator(API_KEY)
    generator.load_existing_leads(OUTPUT_FILE)

    progress = load_progress()
    completed = set(progress["completed"])

    total_countries = len(TARGET_LOCATIONS)
    total_cities    = sum(len(v) for v in TARGET_LOCATIONS.values())
    total_searches  = total_cities * len(CLINIC_TYPES)

    print(f"\nTargets: {total_countries} countries | {total_cities} cities | "
          f"{len(CLINIC_TYPES)} clinic types")
    print(f"Total searches planned: {total_searches}")
    print(f"Searches already done:  {len(completed)}")
    print(f"Remaining:              {total_searches - len(completed)}\n")

    search_num = 0
    for country, cities in TARGET_LOCATIONS.items():
        for city in cities:
            for clinic_type in CLINIC_TYPES:
                search_key = f"{country}|{city}|{clinic_type}"
                search_num += 1

                if search_key in completed:
                    print(f"[{search_num}/{total_searches}] SKIP (done): "
                          f"{clinic_type} in {city}, {country}")
                    continue

                print(f"[{search_num}/{total_searches}] {clinic_type} | "
                      f"{city}, {country}")

                try:
                    generator.search_clinics(city, country, clinic_type)
                except Exception as e:
                    print(f"  [!] Unexpected error: {e}")

                # Mark as done and save progress
                completed.add(search_key)
                progress["completed"] = list(completed)
                save_progress(progress)

                # Save CSV after every city+type combo
                generator.export_to_csv(OUTPUT_FILE)

                # Polite delay between searches
                time.sleep(1.5)

    print("\n" + "=" * 60)
    print(f"  DONE! Total leads collected: {len(generator.leads)}")
    print("=" * 60)
