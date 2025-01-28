from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from loguru import logger
from fastapi.responses import JSONResponse
from app.services.auth_service.otp_service import OTPService
from app.domain.schemas.accounts_schema import OTPCreate, UserSchema, AccountSchema
from app.services.auth_service.user_service import get_current_user
from app.domain.models.accounts import User, Account
import logging
from app.infrastructure.repositories import account_repository
from app.domain.schemas.accounts_schema import (
    UserCreate,
    AccountCreate,
)
from app.core.db.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
auth_router = APIRouter()


@auth_router.get("/Me", response_model=UserSchema, status_code=status.HTTP_200_OK)
async def read_users_me(user_id: int = Depends(get_current_user), db: AsyncSession = Depends(get_db)) -> UserSchema:

    accounts = await account_repository.get_all_account_belongsto_user_id(db, user_id)

    account_schemas = [AccountSchema.from_orm(acc) for acc in accounts]
    user = await account_repository.get_user_by_id(db, user_id)
    user_schema = UserSchema(
        user_id=user_id,
        first_name=user.first_name,
        last_name=user.last_name,
        gender=user.gender,
        birthday=user.birthday,
        phone_number=user.phone_number,
        accounts=account_schemas,
    )

    logger.info(f"Getting user with email address {accounts[0].email_address}...")

    return user_schema
