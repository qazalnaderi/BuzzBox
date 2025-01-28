from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.domain.models.emails import Email, EmailRecipient


async def create_email(db: AsyncSession, sender_id: int, subject: str, body: str):
    new_email = Email(sender_id=sender_id, subject=subject, body=body)
    db.add(new_email)
    await db.commit()
    await db.refresh(new_email)
    return new_email


async def get_email_by_id(db: AsyncSession, email_id: int):
    stmt = select(Email).where(Email.email_id == email_id)
    result = await db.execute(stmt)
    return result.scalars().first()


async def create_email_recipient(db: AsyncSession, email_id: int, recipient_email: str, is_muted: bool = False):
    new_recipient = EmailRecipient(email_id=email_id, recipient_email=recipient_email, is_muted=is_muted)
    db.add(new_recipient)
    await db.commit()
    await db.refresh(new_recipient)
    return new_recipient




async def get_emails_by_sender(db: AsyncSession, sender_id: int) -> list[Email]:
    """
    Fetch all emails sent by a specific sender.
    """
    stmt = select(Email).filter(Email.sender_id == sender_id)
    result = await db.execute(stmt)
    return result.scalars().all()

async def get_emails_for_recipient(db: AsyncSession, recipient_email: str) -> list[Email]:
    """
    Fetch all emails for a specific recipient.
    """
    stmt = select(Email).join(EmailRecipient).filter(EmailRecipient.recipient_email == recipient_email)
    result = await db.execute(stmt)
    return result.scalars().all()

async def update_recipient_muted_status(db: AsyncSession, email_id: int, recipient_email: str, is_muted: bool) -> bool:
    """
    Update the muted status of a recipient for a specific email.
    """
    stmt = update(EmailRecipient).filter(
        EmailRecipient.email_id == email_id,
        EmailRecipient.recipient_email == recipient_email
    ).values(is_muted=is_muted).execution_options(synchronize_session="fetch")
    result = await db.execute(stmt)
    await db.commit()
    return result.rowcount > 0  # Return True if rows were affected


async def get_recipient_by_email_id(db: AsyncSession, email_id: int) -> list[EmailRecipient]:
    """
    Fetch all recipients for a specific email based on its email_id.
    """
    result = await db.execute(
        select(EmailRecipient).filter(EmailRecipient.email_id == email_id)
    )
    recipient = result.scalars().first()
    return recipient