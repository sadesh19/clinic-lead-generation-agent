"""
save_to_db.py — Store final processed leads DataFrame into MongoDB.
"""
import os
import ssl
from datetime import datetime, timezone
from dotenv import load_dotenv
from pymongo import MongoClient, ASCENDING
import certifi

load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
MONGODB_DB  = os.getenv("MONGODB_DB",  "clinic_leads")
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
    # FIX: pass mongo_client_kwargs so TLS config is actually applied
    client = MongoClient(MONGODB_URI, **mongo_client_kwargs)
    db = client[MONGODB_DB]
    leads_collection = db["leads"]

    leads_collection.create_index(
        [("Phone Number", ASCENDING)],
        unique=True,
        partialFilterExpression={"Phone Number": {"$type": "string"}},
        name="uniq_phone_df",
    )
    leads_collection.create_index([("Clinic Name", ASCENDING), ("City", ASCENDING)])
    _mongo_available = True

except Exception as _e:
    leads_collection = None
    _mongo_available = False
    import logging
    logging.getLogger(__name__).warning(
        "MongoDB not available (%s) — DB save will be skipped.", _e
    )


def save_dataframe_to_mongo(df):
    """
    Save every row of the final DataFrame to MongoDB.
    Dedupe by Phone Number, fallback to Clinic Name + City.
    Returns a summary dict: {'inserted': X, 'updated': Y, 'skipped': Z}
    """
    summary = {"inserted": 0, "updated": 0, "skipped": 0}

    if not _mongo_available:
        print("  [MongoDB] Not available — skipping DB save.")
        summary["skipped"] = len(df)
        return summary

    records = df.to_dict(orient="records")

    for record in records:
        record["updated_at"] = datetime.now(timezone.utc)

        query = None
        if record.get("Phone Number"):
            query = {"Phone Number": record["Phone Number"]}
        elif record.get("Clinic Name") and record.get("City"):
            query = {"Clinic Name": record["Clinic Name"], "City": record["City"]}

        if query:
            existing = leads_collection.find_one(query)
            if existing:
                leads_collection.update_one({"_id": existing["_id"]}, {"$set": record})
                summary["updated"] += 1
                continue

        record["created_at"] = record["updated_at"]
        leads_collection.insert_one(record)
        summary["inserted"] += 1

    return summary


def get_all_leads_df():
    """Fetch all leads from MongoDB as a DataFrame (for re-export anytime)."""
    import pandas as pd
    if not _mongo_available:
        return pd.DataFrame()
    records = list(leads_collection.find({}, {"_id": 0}))
    return pd.DataFrame(records)