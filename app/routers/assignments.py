import random
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from app.models.assignment import AssignmentOut
from app.database import assignments_collection, institutes_collection, inspectors_collection
from app.utils import generate_readable_id
from app.dependencies import require_role, get_current_user
from app.ws_manager import manager

router = APIRouter(prefix="/assignments", tags=["assignments"])


def _to_out(doc: dict) -> AssignmentOut:
    return AssignmentOut(id=doc["_id"], institute_id=doc["institute_id"], institute_name=doc["institute_name"],
                          inspector_user_id=doc["inspector_user_id"], inspector_name=doc["inspector_name"],
                          window=doc["window"], status=doc["status"])


@router.post("/draw", response_model=AssignmentOut)
async def run_random_draw(current_user: dict = Depends(require_role("admin"))):
    institutes = await institutes_collection.find().to_list(length=500)
    # Only draw from inspectors who have actually signed up (their profile
    # got linked to a real login account at /auth/signup/inspector). An
    # inspector added manually by Admin with no account yet would never be
    # able to see this assignment, so they're excluded from the pool.
    inspectors = await inspectors_collection.find({"user_id": {"$nin": ["", None]}}).to_list(length=500)

    if not institutes or not inspectors:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Need at least one institute, and at least one inspector who has signed up (not just been pre-registered by Admin), before running a draw",
        )

    # The actual "no one can predict who inspects whom" logic. random.choice
    # is enough for a prototype; a production version could weight it to
    # avoid the same pairing repeating too often.
    institute = random.choice(institutes)
    inspector = random.choice(inspectors)

    doc = {
        "_id": generate_readable_id("AS"),
        "institute_id": institute["_id"],
        "institute_name": institute["name"],
        "inspector_user_id": inspector.get("user_id", ""),
        "inspector_name": inspector["name"],
        "window": "Today, before 6:00 PM",
        "status": "pending",
    }
    await assignments_collection.insert_one(doc)
    await manager.broadcast("new_assignment", _to_out(doc).model_dump())
    return _to_out(doc)


@router.get("/mine", response_model=Optional[AssignmentOut])
async def get_my_assignment(current_user: dict = Depends(require_role("inspector"))):
    doc = await assignments_collection.find_one({
        "inspector_user_id": current_user["_id"],
        "status": "pending",
    })
    if not doc:
        return None
    return _to_out(doc)


@router.get("", response_model=List[AssignmentOut])
async def list_assignments(current_user: dict = Depends(require_role("admin", "department"))):
    docs = await assignments_collection.find().to_list(length=500)
    return [_to_out(d) for d in docs]