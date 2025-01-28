from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from ...domain.models.accounts import SmtpCredentials


# Fetch SMTP credentials by account ID
async def get_smtp_credentials_by_account_id(db: AsyncSession, account_id: int):

    result = await db.execute(
        select(SmtpCredentials).filter(SmtpCredentials.account_id == account_id)
    )
    credentials = result.scalar_one_or_none()

    return credentials


async def create_smtp_credentials(
    db: AsyncSession, account_id: int, email_address: str, smtp_password: str
):
    smtp_credentials = SmtpCredentials(
        account_id=account_id,
        email_address=email_address,
        smtp_password=smtp_password,
    )
    db.add(smtp_credentials)
    await db.commit()
    await db.refresh(smtp_credentials)
    return smtp_credentials