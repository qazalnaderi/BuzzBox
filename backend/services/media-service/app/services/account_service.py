from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from typing import Annotated
from loguru import logger
from app.infrastructure.clients.iam_client import IAMClient
from app.domain.schemas.token_schema import TokenDataSchema
from app.core.config.config import get_settings
from typing import Annotated
from loguru import logger
from fastapi import Depends
from app.infrastructure.repositories.user_repository import UserRepository
from sqlalchemy.ext.asyncio import AsyncSession


class AccountService:
    def __init__(self, account_repo: Annotated[UserRepository, Depends()]) -> None:
        self.account_repo = account_repo

    async def get_account_profile(self, email_address: str):
        logger.info(f"Fetching profile for account: {email_address}")
        account = await self.account_repo.get_account_by_email(email_address)
        if not account:
            raise HTTPException(status_code=404, detail="Account not found")
        return account

    async def update_profile_picture(self, email_address: str, media_url: str):
        logger.info(f"Updating profile picture for account: {email_address}")
        update_fields = {"profile_picture_id": media_url}
        return await self.account_repo.update_profile_picture(email_address, media_url)
        logger.info(f"Account With Email: {email_address} Updated")

    async def get_account_by_id(self, account_id:int):
        acc = await self.account_repo.get_account_by_id(account_id)
        return acc     