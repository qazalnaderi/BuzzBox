from typing import List, Optional, Dict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError
import logging
from typing import Annotated
from fastapi import Depends
from app.domain.models.account_models import User, Account
from app.core.postgres_db.postgres_database import get_db


class UserRepository:
    def __init__(self, db: Annotated[AsyncSession, Depends(get_db)]):
        self.db = db

    # async def update_user_and_account(
    #     self, user: User, account: Account, profile_data: dict
    # ) -> tuple[User, Account]:
    #     try:
    #         if not isinstance(user, User):
    #             raise ValueError("The 'user' parameter is not a valid User object")
    #         if not isinstance(account, Account):
    #             raise ValueError("The 'account' parameter is not a valid Account object")

    #         # Update user fields
    #         if profile_data.get("profile_picture_id"):
    #             account.image_url = profile_data["profile_picture_id"]
    #         if profile_data.get("first_name"):
    #             user.first_name = profile_data["first_name"]
    #         if profile_data.get("last_name"):
    #             user.last_name = profile_data["last_name"]
    #         if profile_data.get("phone_number"):
    #             user.phone_number = profile_data["phone_number"]
    #         if profile_data.get("gender"):
    #             user.gender = profile_data["gender"]
    #         if profile_data.get("birthday"):
    #             user.birthday = profile_data["birthday"]

    #         # Update account fields
    #         if profile_data.get("new_email_address"):
    #             account.email_address = profile_data["new_email_address"]

    #         # Commit changes
    #         await self.db.commit()
    #         await self.db.refresh(user)
    #         await self.db.refresh(account)

    #         logging.info(f"Updated user {user.user_id} and account {account.account_id}")
    #         return user, account

    #     except IntegrityError as e:
    #         logging.error(f"Integrity error during update: {e}")
    #         await self.db.rollback()
    #         raise e
    #     except Exception as e:
    #         logging.error(f"Unexpected error during update: {e}")
    #         await self.db.rollback()
    #         raise e

    async def get_account_by_email(self, email: str) -> Optional[Account]:
        stmt = select(Account).filter(Account.email_address == email)
        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def get_user_by_phone(self, phone_number: str) -> Optional[User]:
        stmt = select(User).filter(User.phone_number == phone_number)
        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        query = select(User).where(User.user_id == user_id)
        result = await self.db.execute(query)
        return result.scalars().first()

    async def get_account_by_id(self, account_id: int) -> Optional[Account]:
        stmt = select(Account).where(Account.account_id == account_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_account_by_user_id(self, user_id: int) -> Optional[Account]:
        stmt = select(Account).filter(Account.user_id == user_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all_accounts_belonging_to_user_id(self, user_id: int) -> List[Account]:
        stmt = select(Account).filter(Account.user_id == user_id)
        result = await self.db.execute(stmt)
        accounts = result.scalars().all()
        logging.info(f"Accounts found: {accounts}")
        if not accounts:
            logging.info(f"No accounts found for user_id {user_id}")
            return []
        return accounts

    async def update_profile_picture(self, email_address: int, new_profile_picture_url: str) -> Optional[Account]:
        stmt = select(Account).filter(Account.email_address == email_address)
        result = await self.db.execute(stmt)
        account = result.scalars().first()

        if account:
            account.image_url = new_profile_picture_url
            await self.db.commit()
            await self.db.refresh(account)
            return account
        return None
    # async def update_account_by_email(self, email_address: str, updated_user: Dict):
    #     query = self.db.query(Account).filter(Account.email_address == email_address)
    #     db = query.first()
    #     query.filter(Account.email_address == email_address).update(
    #         updated_user, synchronize_session=False
    #     )
    #     self.db.commit()
    #     self.db.refresh(db)

    #     return db