"""
constants.py — Project-wide constants matching the requirements document.
"""

# ── Target locations ────────────────────────────────────────────────────────
TARGET_LOCATIONS = {
    "United Kingdom": ["London", "Manchester", "Birmingham", "Leeds", "Bristol"],
    "UAE": ["Dubai", "Abu Dhabi", "Sharjah"],
    "Pakistan": ["Islamabad", "Rawalpindi", "Lahore", "Karachi"],
    "Australia": ["Sydney", "Melbourne", "Brisbane"],
}

# ── Clinic types ─────────────────────────────────────────────────────────────
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

# ── Appointment methods ───────────────────────────────────────────────────────
APPOINTMENT_METHODS = [
    "Phone Calls",
    "WhatsApp",
    "Website Booking Form",
    "Online Booking System",
    "Social Media Messages",
    "Walk-in",
]

# ── Automation status levels ──────────────────────────────────────────────────
AUTOMATION_STATUS = ["Manual", "Semi Automated", "Automated"]

# ── Lead priority tiers ───────────────────────────────────────────────────────
LEAD_PRIORITY = ["High", "Medium", "Low"]

# ── Minimum leads per week ────────────────────────────────────────────────────
MIN_LEADS_PER_WEEK = 100

# ── Google Maps search radius (metres) ───────────────────────────────────────
DEFAULT_SEARCH_RADIUS = 10000   # 10 km
