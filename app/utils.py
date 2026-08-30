import secrets
import os
import shutil
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
