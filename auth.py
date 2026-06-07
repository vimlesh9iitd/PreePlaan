# ══════════════════════════════════════════════════════════════════
#  auth.py  —  Supabase JWT verification
#
#  Flutter Supabase se milta hai access_token.
#  Wo Bearer token header mein bhejta hai.
#  Hum yahan verify karte hain aur user_id (sub) nikalte hain.
# ══════════════════════════════════════════════════════════════════

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from jwt.exceptions import InvalidTokenError
from config import settings

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> str:
    """
    Returns the user_id (UUID string) from the Supabase JWT.
    Raises 401 if token is invalid or expired.
    """
    token = credentials.credentials

    try:
        payload = jwt.decode(
            token,
            settings.supabase_jwt_secret,
            algorithms=["HS256"],
            options={"verify_aud": False},   # Supabase sets aud="authenticated"
        )
        user_id: str = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: sub claim missing",
            )
        return user_id

    except InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token invalid ya expire ho gaya: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )
