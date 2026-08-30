from fastapi import APIRouter, Depends
from typing import List
from app.models.alert import AlertOut
from app.database import alerts_collection
from app.dependencies import require_role

router = APIRouter(prefix="/alerts", tags=["alerts"])


def _to_out(doc: dict) -> AlertOut:
    return AlertOut(id=doc["_id"], type=doc["type"], institute_id=doc["institute_id"],
                     institute_name=doc["institute_name"], report_id=doc["report_id"],
                     detail=doc["detail"], severity=doc["severity"], created_at=doc["created_at"])


@router.get("", response_model=List[AlertOut])
async def list_alerts(current_user: dict = Depends(require_role("admin", "department"))):
    docs = await alerts_collection.find().sort("created_at", -1).to_list(length=1000)
    return [_to_out(d) for d in docs]
