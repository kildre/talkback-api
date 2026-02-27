from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

security = HTTPBearer()


def validate_jwt(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """
    Validate JWT token (dummy implementation for now).
    In production, decode and verify the JWT token properly.
    """
    token = credentials.credentials
    if not token or not token.startswith("fake-jwt-token-for-"):
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    # Extract user_id from fake token
    user_id = token.replace("fake-jwt-token-for-", "")
    return {"user_id": user_id}
