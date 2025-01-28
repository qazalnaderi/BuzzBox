from sqlalchemy.future import select
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from app.infrastructure.repositories.account_repository import get_user_by_id
from app.domain.models.accounts import Account, User
from app.infrastructure.repositories.account_repository import get_account_by_email
from app.domain.schemas.profile_management_schema import UpdateProfile


async def update_user_and_account(db: AsyncSession, user: User, account: Account, profile_data: dict):
    try:
        if not isinstance(user, User):
            raise ValueError("The 'user' parameter is not a valid User object")
        if not isinstance(account, Account):
            raise ValueError("The 'account' parameter is not a valid Account object")
        # Update user fields
        if profile_data.get("profile_picture_id"):
            user.profile_picture_id = profile_data["profile_picture_id"]
        if profile_data.get("first_name"):
            user.first_name = profile_data["first_name"]
        if profile_data.get("last_name"):
            user.last_name = profile_data["last_name"]
        if profile_data.get("phone_number"):
            user.phone_number = profile_data["phone_number"]
        if profile_data.get("gender"):
            user.gender = profile_data["gender"]
        if profile_data.get("birthday"):
            user.birthday = profile_data["birthday"]

        # Update account fields
        if profile_data.get("new_email_address"):
            account.email_address = profile_data["new_email_address"]

        # Commit changes
        await db.commit()
        await db.refresh(user)
        await db.refresh(account)

        logging.info(f"Updated user {user.user_id} and account {account.account_id}")
        return user, account
    except IntegrityError as e:
        logging.error(f"Integrity error during update: {e}")
        await db.rollback()
        raise e
    except Exception as e:
        logging.error(f"Unexpected error during update: {e}")
        await db.rollback()
        raise e



async def update_account_password(db: AsyncSession, account, hashed_new_password: str):
    account.password = hashed_new_password
    db.add(account)
    await db.commit()
    await db.refresh(account)
    return account