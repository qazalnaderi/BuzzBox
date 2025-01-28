import logging
from fastapi import Depends, HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.db.database import get_db
from app.infrastructure.repositories.account_repository import get_user_by_id
from app.services.auth_service.auth_tokens import verify_access_token
from fastapi.security import OAuth2PasswordBearer
from typing import Annotated
import jwt
from app.core.configs.config import get_settings 
from loguru import logger
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login/user/login")

settings = get_settings()
JWT_SECRET_KEY = settings.JWT_SECRET_KEY
JWT_ALGORITHM = settings.JWT_ALGORITHM

async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: AsyncSession = Depends(get_db)
) -> str:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    logger.info(f"Validating token {token}")
    
    try:
        payload = jwt.decode(
            token,
            JWT_SECRET_KEY,  # Make sure this matches your config structure
            algorithms=[JWT_ALGORITHM]
        )
        user_id: str = payload.get("user_id")  # Changed from "sub" to match your token structure
        
        if user_id is None:
            logger.error("Could not validate credentials")
            raise credentials_exception
            
    except jwt.PyJWTError:
        logger.error("Error decoding token")
        raise credentials_exception
        
    logger.info(f"User with id {user_id} validated successfully")
    return user_id