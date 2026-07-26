"""
clinic.py — Pydantic model representing one clinic lead.
Matches the Google Sheet structure from the requirements document.
"""
from typing import Optional, List
from pydantic import BaseModel, ConfigDict, Field
from app.utils.constants import AUTOMATION_STATUS, APPOINTMENT_METHODS, LEAD_PRIORITY


class ClinicLead(BaseModel):
    """A single verified clinic lead."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "lead_id": "LEAD-0001",
                "clinic_name": "Bright Smile Dental",
                "clinic_type": "Dental Clinic",
                "country": "United Kingdom",
                "city": "London",
                "address": "45 Baker Street, London, W1U 7AJ",
                "phone_number": "+442079460321",
                "email": "info@brightsmile.co.uk",
                "website_available": True,
                "website_url": "https://brightsmile.co.uk",
                "doctor_owner_name": "Dr. Sarah Ahmed",
                "social_media_links": [
                    "https://instagram.com/brightsmile",
                    "https://facebook.com/brightsmile",
                ],
                "appointment_method": "Online Booking System",
                "automation_status": "Automated",
                "google_rating": 4.7,
                "reviews_count": 312,
                "lead_priority": "High",
                "notes": "Uses Doctify booking platform",
                "call_status": "Not Called",
                "follow_up_date": None,
            }
        }
    )

    lead_id: str = Field(..., description="Unique identifier e.g. LEAD-0001")
    clinic_name: str
    clinic_type: str
    country: str
    city: str
    address: str
    phone_number: str = Field(..., description="Verified phone number with country code")
    email: Optional[str] = None
    website_available: bool = False
    website_url: Optional[str] = None
    doctor_owner_name: Optional[str] = None
    social_media_links: Optional[List[str]] = Field(
        default_factory=list,
        description="Instagram / Facebook profile URLs",
    )
    appointment_method: str = Field(
        ...,
        description=f"How the clinic handles bookings. Options: {APPOINTMENT_METHODS}",
    )
    automation_status: str = Field(
        ...,
        description=f"Level of booking automation. Options: {AUTOMATION_STATUS}",
    )
    google_rating: Optional[float] = Field(default=None, ge=1.0, le=5.0)
    reviews_count: Optional[int] = Field(default=None, ge=0)
    lead_priority: str = Field(
        default="Medium",
        description=f"Sales priority. Options: {LEAD_PRIORITY}",
    )
    notes: str = Field(default="", description="Any additional observations")
    call_status: str = Field(
        default="Not Called",
        description="Current outreach status e.g. Not Called | Called | Follow-up | Closed",
    )
    follow_up_date: Optional[str] = Field(
        default=None,
        description="ISO date string YYYY-MM-DD",
    )
