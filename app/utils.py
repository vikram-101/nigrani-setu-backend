import secrets
import os
import shutil
from math import radians, sin, cos, sqrt, atan2
from datetime import datetime, timezone
from fastapi import UploadFile

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


def generate_readable_id(prefix: str) -> str:
    """
    Produces IDs like INST-4F9A2C, RPT-88C1A0 — short, unique enough for a
    prototype, and easy to read out loud during a demo (unlike a raw ObjectId).
    """
    return f"{prefix}-{secrets.token_hex(3).upper()}"


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def save_upload(file: UploadFile, report_id: str) -> str:
    """
    Saves an uploaded photo to disk and returns the relative path stored on
    the report document. For the hackathon prototype this is local disk;
    swapping to S3/Cloudinary later only means changing this one function.
    """
    extension = os.path.splitext(file.filename)[1] or ".jpg"
    filename = f"{report_id}{extension}"
    destination = os.path.join(UPLOAD_DIR, filename)
    with open(destination, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return f"/{UPLOAD_DIR}/{filename}"


def distance_meters(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Haversine formula — real-world distance in meters between two GPS points
    on Earth's surface. This is the core of geo-tag verification: it tells
    us how far the inspector's phone actually was from the institute's
    registered coordinates when the evidence photo was captured.
    """
    R = 6371000  # Earth's radius in meters
    phi1, phi2 = radians(lat1), radians(lat2)
    d_phi = radians(lat2 - lat1)
    d_lambda = radians(lon2 - lon1)

    a = sin(d_phi / 2) ** 2 + cos(phi1) * cos(phi2) * sin(d_lambda / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c