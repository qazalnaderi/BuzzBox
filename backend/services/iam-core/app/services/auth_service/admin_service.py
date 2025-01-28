import logging
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.repositories.admin_repository import get_admin_by_id
from app.core.db.database import get_db
from app.services.auth_service.auth_tokens import verify_access_token
from app.domain.models.admins import Admin


# HTTPBearer to handle Authorization header
bearer_scheme = HTTPBearer()

async def get_current_admin(
    token: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db)
) -> Admin:
    """
    Dependency to get current admin from token.
    Verifies both token validity and admin status.
    Raises HTTPException if token is invalid or user is not an admin.
    """
    try:
        # Extract and verify token
        token_string = token.credentials
        token_data = verify_access_token(token_string)
        
        # Get admin_id from token
        admin_id = token_data.get("admin_id")  # Changed from user_id to admin_id
        logging.info(f"Token data: {token_data}")
        logging.info(f"Admin ID from token: {admin_id}")

        if not admin_id:
            raise HTTPException(
                status_code=401,
                detail="Invalid token: missing admin ID"
            )

        # Check if admin exists
        admin = await get_admin_by_id(db, admin_id)
        if not admin:
            raise HTTPException(
                status_code=403,
                detail="Access forbidden: invalid admin ID"
            )

        return admin

    except Exception as e:
        logging.error(f"Error in get_current_admin: {e}")
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )



