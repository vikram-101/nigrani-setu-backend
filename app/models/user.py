from pydantic import BaseModel, Field
from typing import Literal, Optional

Role = Literal["inspector", "department", "admin"]


class SignupRequest(BaseModel):
    name: str
    login_id: str = Field(..., description="Chosen ID used to sign in, e.g. an inspector ID")
    password: str
    district: Optional[str] = None      # only meaningful for inspectors
    division: Optional[str] = None      # only meaningful for department officials


class LoginRequest(BaseModel):
    login_id: str
    password: str


class UserOut(BaseModel):
    id: str
    name: str
    login_id: str
    role: Role
    district: Optional[str] = None
    division: Optional[str] = None


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut
