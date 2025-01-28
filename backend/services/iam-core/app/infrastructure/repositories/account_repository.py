from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select 
from sqlalchemy import delete
from app.domain.models.accounts import Account, User
from app.domain.models.report import Report
from app.domain.models.emails import Email
from app.domain.schemas.accounts_schema import UserCreate, AccountCreate
from app.services.auth_service.hash_service import HashService
import logging

hash_service = HashService()

async def get_account_by_email(db: AsyncSession, email: str):
    stmt = select(Account).filter(Account.email_address == email)
    result = await db.execute(stmt)
    account = result.scalars().first()
    return account


async def get_user_by_phone(db: AsyncSession, phone_number: str):
    stmt = select(User).filter(User.phone_number == phone_number)
    result = await db.execute(stmt)
    return result.scalars().first()

async def get_user_by_id(db: AsyncSession,user_id: int):
    query = select(User).where(User.user_id == user_id)
    result = await db.execute(query)
    return result.scalars().first()


async def get_account_by_id(db: AsyncSession, account_id: int):

    stmt = select(Account).where(Account.account_id == account_id)
    result = await db.execute(stmt)
    account = result.scalar_one_or_none()
    return account

    
async def get_account_by_user_id(db: AsyncSession, user_id: int):
    result = await db.execute(
        select(Account).filter(Account.user_id == user_id)
    )
    account = result.scalar_one_or_none()

    return account

async def get_all_account_belongsto_user_id(db: AsyncSession, user_id: int):
    result = await db.execute(
        select(Account).filter(Account.user_id == user_id)
    )
    accs = result.scalars().all()
    logging.info(f"Accounts found: {accs}")  # Add this line
    if not accs:
        logging.info(f"No accounts found for user_id {user_id}")
        return [] 

    return accs


async def verify_user_credentials(db: AsyncSession, email: str, password: str):
    account = await get_account_by_email(db, email)
    if not account or not hash_service.verify_password(password, account.password):
        return None
    return account

# Create a new user
async def create_user(db: AsyncSession, user: UserCreate):
    db_user = User(
        first_name=user.first_name,
        last_name=user.last_name,
        gender=user.gender,
        birthday=user.birthday,
        phone_number=user.phone_number,
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user

# Create a new account
async def create_account(db: AsyncSession, account: AccountCreate, user_id: int):
    hashed_password = hash_service.hash_password(account.password)
    db_account = Account(
        email_address=account.email_address,
        password=hashed_password,
        status=account.status,
        recovery_email=account.recovery_email,
        user_id=user_id,
        image_url="",
    )
    db.add(db_account)
    await db.commit()
    await db.refresh(db_account)
    return db_account



async def delete_reports_by_account(db: AsyncSession, account_id: int):
    await db.execute(delete(Report).where(Report.reporter_id == account_id))
    await db.execute(delete(Report).where(Report.reported_user_id == account_id))

async def delete_emails_by_account(db: AsyncSession, account_id: int):
    await db.execute(delete(Email).where(Email.sender_id == account_id))

async def delete_account(db: AsyncSession, account):
    await db.delete(account)


async def delete_user(db: AsyncSession, user):
    await db.delete(user)