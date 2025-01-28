from sqlalchemy.ext.asyncio import AsyncSession
from app.domain.models.email_models import Attachment
from typing import List
from app.core.postgres_db.postgres_database import get_db

async def create_attachment(db: AsyncSession, email_id: int, attachment_urls: list[str]):
    if isinstance(attachment_urls, dict):
        urls = attachment_urls.get('attachment_urls', [])
    else:
        urls = attachment_urls

    
    for url in urls:        
        attachment = Attachment(email_id=email_id, attachment_url=url)
        db.add(attachment)
    
    await db.commit()
    return True


async def get_attachment_by_id(db: AsyncSession, attachment_id: int):
    stmt = select(Attachment).filter(Attachment.id == attachment_id)
    result = await db.execute(stmt)
    attachment = result.scalars().first()
    return attachment
