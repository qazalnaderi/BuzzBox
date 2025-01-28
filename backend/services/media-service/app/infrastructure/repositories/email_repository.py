from typing import List, Optional, Dict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError
import logging
from typing import Annotated
from fastapi import Depends
from app.domain.models.email_models import Email, EmailRecipient, Attachment
from app.core.postgres_db.postgres_database import get_db


async def get_recipient_by_email_id(db: AsyncSession, email_id: int) -> EmailRecipient:

    result = await db.execute(
        select(EmailRecipient).filter(EmailRecipient.email_id == email_id)
    )
    recipient = result.scalars().first()
    return recipient

async def get_email_by_id(db: AsyncSession, email_id: int):
    stmt = select(Email).where(Email.email_id == email_id)
    result = await db.execute(stmt)
    return result.scalars().first()


async def get_email_attachments(db: AsyncSession, email_id: int) -> list[str]:
    results = await db.execute(
        select(Attachment.attachment_url).filter(Attachment.email_id == email_id)
    )
    return results.scalars().all()
