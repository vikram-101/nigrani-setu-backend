from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app.security import decode_access_token
from app.database import users_collection

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


async def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    """
    Every protected route depends on this. It decodes the JWT (issued at
    login), pulls the role that was baked into the token at signup time,
    and re-fetches the user document — this is the single source of truth
    for "who is this request coming from and what are they allowed to do".
    """
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")

    user_id = payload.get("sub")
    user = await users_collection.find_one({"_id": user_id})
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User no longer exists")
    return user


def require_role(*allowed_roles: str):
    """
    Usage: Depends(require_role("admin")) or Depends(require_role("inspector", "admin")).
    This is what actually enforces "only Admin can register an institute" —
    not the frontend hiding a button, but the backend refusing the request.
    """
    async def role_checker(current_user: dict = Depends(get_current_user)) -> dict:
        if current_user["role"] not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"This action requires one of these roles: {', '.join(allowed_roles)}",
            )
        return current_user
    return role_checker
