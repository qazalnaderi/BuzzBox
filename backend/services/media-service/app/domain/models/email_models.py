from sqlalchemy import Column, BigInteger, Text, Boolean, ForeignKey, TIMESTAMP, String
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.postgres_db.postgres_database import Base


class Email(Base):
    __tablename__ = "emails"

    email_id = Column(BigInteger, primary_key=True, index=True)
    sender_id = Column(BigInteger, ForeignKey("accounts.account_id", ondelete="CASCADE"), nullable=False)
    subject = Column(Text, nullable=False)
    body = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    is_important = Column(Boolean, default=False)
    attachments = Column(Text, nullable=True)

    recipients = relationship("EmailRecipient", back_populates="email")
    attachments = relationship("Attachment", back_populates="email")

class EmailRecipient(Base):
    __tablename__ = "email_recipients"

    recipient_id = Column(BigInteger, primary_key=True, index=True)
    email_id = Column(BigInteger, ForeignKey("emails.email_id", ondelete="CASCADE"), nullable=False)
    recipient_email = Column(String(255), ForeignKey("accounts.email_address", ondelete="CASCADE"), nullable=False)
    is_muted = Column(Boolean, default=False)

    email = relationship("Email", back_populates="recipients")



class Attachment(Base):
    __tablename__ = "attachments"

    attachment_id = Column(BigInteger, primary_key=True, index=True)
    email_id = Column(BigInteger, ForeignKey("emails.email_id", ondelete="CASCADE"), nullable=False)
    attachment_url = Column(Text, nullable=False)

    email = relationship("Email", back_populates="attachments")
