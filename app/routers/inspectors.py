from fastapi import APIRouter, Depends
from typing import List
from pydantic import BaseModel
from app.models.inspector import InspectorOut
from app.database import inspectors_collection
from app.utils import generate_readable_id
from app.dependencies import require_role, get_current_user

router = APIRouter(prefix="/inspectors", tags=["inspectors"])


class InspectorCreate(BaseModel):
    name: str
    district: str


def _to_out(doc: dict) -> InspectorOut:
    return InspectorOut(id=doc["_id"], user_id=doc.get("user_id", ""), name=doc["name"], district=doc["district"])


@router.post("", response_model=InspectorOut)
async def register_inspector_profile(payload: InspectorCreate, current_user: dict = Depends(require_role("admin"))):
    """
    For inspectors who don't yet have a login account (e.g. added by Admin
    ahead of time before they've signed up themselves). Once that person
    signs up through /auth/signup/inspector, their account is linked
    separately — this endpoint just seeds the directory Admin can assign against.
    """
    doc = {"_id": generate_readable_id("INSP"), "name": payload.name, "district": payload.district, "user_id": ""}
    await inspectors_collection.insert_one(doc)
    return _to_out(doc)


@router.get("", response_model=List[InspectorOut])
async def list_inspectors(current_user: dict = Depends(get_current_user)):
    docs = await inspectors_collection.find().to_list(length=500)
    return [_to_out(d) for d in docs]
