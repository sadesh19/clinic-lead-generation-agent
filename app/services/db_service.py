"""
db_service.py — MongoDB storage for clinic leads.
Handles connection, dedupe-safe insert/update, and retrieval.
"""
import os
import ssl
from datetime import datetime, timezone
from dotenv import load_dotenv
from pymongo import MongoClient, ASCENDING
import certifi
from config import config

load_dotenv()

MONGODB_URI = config.MONGODB_URI
MONGODB_DB  = config.MONGODB_DB
MONGODB_TLS = os.getenv("MONGODB_TLS", "").lower()
MONGODB_TLS_ALLOW_INVALID_CERTS = os.getenv("MONGODB_TLS_ALLOW_INVALID_CERTS", "false").lower() == "true"
MONGODB_TLS_VERSION = os.getenv("MONGODB_TLS_VERSION", "").strip()

mongo_client_kwargs = {}

# Only apply TLS for Atlas (mongodb+srv://) or explicitly enabled
if MONGODB_TLS == "true" or (not MONGODB_TLS and MONGODB_URI.startswith("mongodb+srv://")):
    mongo_client_kwargs["tls"] = True
    mongo_client_kwargs["tlsCAFile"] = certifi.where()
elif MONGODB_TLS == "false":
    pass  # no TLS at all

if MONGODB_TLS_ALLOW_INVALID_CERTS and mongo_client_kwargs.get("tls"):
    mongo_client_kwargs["tlsAllowInvalidCertificates"] = True
    mongo_client_kwargs["tlsAllowInvalidHostnames"]     = True

if MONGODB_TLS_VERSION and mongo_client_kwargs.get("tls"):
    mongo_client_kwargs["tlsVersion"] = getattr(ssl, MONGODB_TLS_VERSION)

try:
    _client = MongoClient(MONGODB_URI, **mongo_client_kwargs)
    _db = _client[MONGODB_DB]
    leads_collection = _db["leads"]

    # Create indexes (idempotent)
    leads_collection.create_index(
        [("phone_number", ASCENDING)],
        unique=True,
        partialFilterExpression={"phone_number": {"$type": "string"}},
        name="uniq_phone",
    )
    leads_collection.create_index([("clinic_name", ASCENDING), ("city", ASCENDING)])
    _mongo_available = True

except Exception as _e:
    leads_collection = None
    _mongo_available = False
    import logging
    logging.getLogger(__name__).warning(
        "MongoDB not available (%s) — DB operations will be skipped.", _e
    )


def save_lead(lead) -> str:
    """
    Insert a new lead, or update it if it already exists (by phone, or by clinic_name+city).
    Returns 'inserted', 'updated', or 'skipped' (if MongoDB not available).
    """
    if not _mongo_available:
        return "skipped"

    lead = lead.model_dump() if hasattr(lead, "model_dump") else dict(lead)
    lead["updated_at"] = datetime.now(timezone.utc)

    query = None
    if lead.get("phone_number"):
        query = {"phone_number": lead["phone_number"]}
    elif lead.get("clinic_name") and lead.get("city"):
        query = {"clinic_name": lead["clinic_name"], "city": lead["city"]}

    if query:
        existing = leads_collection.find_one(query)
        if existing:
            leads_collection.update_one({"_id": existing["_id"]}, {"$set": lead})
            return "updated"

    lead["created_at"] = lead["updated_at"]
    leads_collection.insert_one(lead)
    return "inserted"


def get_all_leads(query: dict = None) -> list:
    """Return all leads from the collection, or empty list if MongoDB unavailable."""
    if not _mongo_available:
        return []
    return list(leads_collection.find(query or {}))