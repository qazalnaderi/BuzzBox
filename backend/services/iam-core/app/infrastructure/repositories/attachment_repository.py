# from sqlalchemy.ext.asyncio import AsyncSession
# from app.domain.models.emails import Attachment


# async def create_attachment(db: AsyncSession, email_id: int, attachment_url: str):
#     attachment = Attachment(email_id=email_id, attachment_url=attachment_url)
#     db.add(attachment)
#     await db.commit()
#     await db.refresh(attachment)
#     return attachment
