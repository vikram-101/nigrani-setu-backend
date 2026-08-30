from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordRequestForm
from app.models.user import SignupRequest, LoginRequest, TokenResponse, UserOut
from app.database import users_collection, inspectors_collection
from app.security import hash_password, verify_password, create_access_token
from app.utils import generate_readable_id
from app.dependencies import get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])


async def _create_account(payload: SignupRequest, role: str) -> TokenResponse:
    existing = await users_collection.find_one({"login_id": payload.login_id})
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="This login ID is already taken")

    user_id = generate_readable_id("USR")
    user_doc = {
        "_id": user_id,
        "name": payload.name,
        "login_id": payload.login_id,
        "password_hash": hash_password(payload.password),
        # This is the field that actually tags the account by role — set once,
        # at signup, from whichever endpoint the request came through. A
        # department official's request can never end up with role=admin.
        "role": role,
        "district": payload.district,
        "division": payload.division,
    }
    await users_collection.insert_one(user_doc)

    # An inspector also gets a lightweight profile row for field-specific data
    if role == "inspector":
        await inspectors_collection.insert_one({
            "_id": generate_readable_id("INSP"),
            "user_id": user_id,
            "name": payload.name,
            "district": payload.district or "",
        })

    token = create_access_token({"sub": user_id, "role": role})
    user_out = UserOut(id=user_id, name=payload.name, login_id=payload.login_id, role=role,
                        district=payload.district, division=payload.division)
    return TokenResponse(access_token=token, user=user_out)


@router.post("/signup/inspector", response_model=TokenResponse)
async def signup_inspector(payload: SignupRequest):
    return await _create_account(payload, role="inspector")


@router.post("/signup/department", response_model=TokenResponse)
async def signup_department(payload: SignupRequest):
    return await _create_account(payload, role="department")


@router.post("/signup/admin", response_model=TokenResponse)
async def signup_admin(payload: SignupRequest):
    # In production this endpoint should not be publicly reachable at all —
    # gate it behind an internal-only network rule, a one-time setup script,
    # or an existing admin's approval. Kept open here only for prototype setup.
    return await _create_account(payload, role="admin")


@router.post("/login", response_model=TokenResponse)
async def login(payload: LoginRequest):
    user = await users_collection.find_one({"login_id": payload.login_id})
    if not user or not verify_password(payload.password, user["password_hash"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect login ID or password")

    token = create_access_token({"sub": user["_id"], "role": user["role"]})
    user_out = UserOut(id=user["_id"], name=user["name"], login_id=user["login_id"], role=user["role"],
                        district=user.get("district"), division=user.get("division"))
    return TokenResponse(access_token=token, user=user_out)


@router.get("/me", response_model=UserOut)
async def get_me(current_user: dict = Depends(get_current_user)):
    return UserOut(id=current_user["_id"], name=current_user["name"], login_id=current_user["login_id"],
                   role=current_user["role"], district=current_user.get("district"),
                   division=current_user.get("division"))
