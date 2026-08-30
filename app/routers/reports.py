from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from typing import List, Optional
from app.models.report import ReportOut
from app.database import reports_collection, institutes_collection, assignments_collection, alerts_collection
from app.utils import generate_readable_id, now_iso, save_upload
from app.dependencies import require_role, get_current_user
from app.ws_manager import manager

router = APIRouter(prefix="/reports", tags=["reports"])


def _to_out(doc: dict) -> ReportOut:
    return ReportOut(
        id=doc["_id"], institute_id=doc["institute_id"], institute_name=doc["institute_name"],
        inspector_user_id=doc["inspector_user_id"], inspector_name=doc["inspector_name"],
        beneficiaries_present=doc["beneficiaries_present"], beneficiaries_claimed=doc["beneficiaries_claimed"],
        attendance_status=doc["attendance_status"], hygiene=doc["hygiene"], notes=doc.get("notes"),
        photo_url=doc.get("photo_url"), latitude=doc.get("latitude"), longitude=doc.get("longitude"),
        submitted_at=doc["submitted_at"], status=doc["status"],
    )


@router.post("", response_model=ReportOut, status_code=status.HTTP_201_CREATED)
async def submit_report(
    institute_id: str = Form(...),
    beneficiaries_present: int = Form(...),
    attendance_status: str = Form(...),   # "matches" | "discrepancy"
    hygiene: str = Form(...),
    notes: Optional[str] = Form(None),
    latitude: Optional[float] = Form(None),
    longitude: Optional[float] = Form(None),
    photo: UploadFile = File(...),
    current_user: dict = Depends(require_role("inspector")),
):
    institute = await institutes_collection.find_one({"_id": institute_id})
    if not institute:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Institute not found")

    report_id = generate_readable_id("RPT")
    photo_url = save_upload(photo, report_id)

    # --- Core flagging logic ---
    # A discrepancy the inspector themself noted, OR a beneficiary count
    # significantly below what's registered, gets auto-flagged. This is the
    # same rule that lived in the frontend prototype — now it's enforced
    # server-side, so it can't be bypassed by editing the client.
    is_mismatch = beneficiaries_present < institute["beneficiaries"] * 0.7
    is_flagged = attendance_status == "discrepancy" or is_mismatch
    report_status = "flagged" if is_flagged else "verified"

    doc = {
        "_id": report_id,
        "institute_id": institute_id,
        "institute_name": institute["name"],
        "inspector_user_id": current_user["_id"],
        "inspector_name": current_user["name"],
        "beneficiaries_present": beneficiaries_present,
        "beneficiaries_claimed": institute["beneficiaries"],
        "attendance_status": attendance_status,
        "hygiene": hygiene,
        "notes": notes,
        "photo_url": photo_url,
        "latitude": latitude,
        "longitude": longitude,
        "submitted_at": now_iso(),
        "status": report_status,
    }
    await reports_collection.insert_one(doc)

    # Close out the assignment this report was filed against, if one exists
    await assignments_collection.update_one(
        {"institute_id": institute_id, "inspector_user_id": current_user["_id"], "status": "pending"},
        {"$set": {"status": "completed"}},
    )

    if is_flagged:
        alert_doc = {
            "_id": generate_readable_id("ALT"),
            "type": "Attendance discrepancy" if attendance_status == "discrepancy" else "Beneficiary count mismatch",
            "institute_id": institute_id,
            "institute_name": institute["name"],
            "report_id": report_id,
            "detail": f"Reported {beneficiaries_present} of {institute['beneficiaries']} claimed beneficiaries present.",
            "severity": "high",
            "created_at": now_iso(),
        }
        await alerts_collection.insert_one(alert_doc)
        await manager.broadcast("new_alert", alert_doc)

    report_out = _to_out(doc)
    await manager.broadcast("new_report", report_out.model_dump())
    return report_out


@router.get("", response_model=List[ReportOut])
async def list_reports(current_user: dict = Depends(require_role("admin", "department"))):
    docs = await reports_collection.find().sort("submitted_at", -1).to_list(length=1000)
    return [_to_out(d) for d in docs]


@router.get("/mine", response_model=List[ReportOut])
async def list_my_reports(current_user: dict = Depends(require_role("inspector"))):
    docs = await reports_collection.find({"inspector_user_id": current_user["_id"]}).sort("submitted_at", -1).to_list(length=500)
    return [_to_out(d) for d in docs]


@router.get("/institute/{institute_id}", response_model=List[ReportOut])
async def list_reports_for_institute(institute_id: str, current_user: dict = Depends(get_current_user)):
    docs = await reports_collection.find({"institute_id": institute_id}).sort("submitted_at", -1).to_list(length=500)
    return [_to_out(d) for d in docs]
