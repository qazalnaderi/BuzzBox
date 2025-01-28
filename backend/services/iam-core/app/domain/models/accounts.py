from sqlalchemy import Column, Integer, String, ForeignKey, Text, TIMESTAMP, BigInteger, Date
from datetime import datetime, timezone
from sqlalchemy.orm import relationship, Mapped
from app.core.db.database import Base

class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    gender = Column(String(10), nullable=True)
    birthday = Column(Date, nullable=True)
    phone_number = Column(String(15), nullable=False)

    # Relationship declared as a string to avoid circular reference issues
    accounts = relationship("Account", back_populates="owner")


class Account(Base):
    __tablename__ = "accounts"

    account_id = Column(Integer, primary_key=True, index=True)
    email_address = Column(String(255), unique=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    created_at = Column(TIMESTAMP, default=datetime.now)
    updated_at = Column(TIMESTAMP, default=datetime.now, onupdate=datetime.now)
    password = Column(Text, nullable=False)
    status = Column(Text, nullable=True)
    recovery_email = Column(String(255), nullable=True)
    image_url = Column(String(255), nullable=True)  # Field for profile image path/URL

    owner = relationship("User", back_populates="accounts")

    smtp_credentials = relationship(
        "SmtpCredentials",  # Explicitly declare the relationship target as a string
        back_populates="account",
        uselist=False,
        lazy="select"
    )

    contacts = relationship(
        "Contact",  # Reference the Contact model
        back_populates="owner",  # Back-populate to the `owner` relationship in the Contact model
        cascade="all, delete-orphan",  # Handle deletions
        lazy="select"  # Optimize queries for this relationship
    )


    reports_made = relationship("Report", foreign_keys="[Report.reporter_id]", back_populates="reporter")
    reports_received = relationship("Report", foreign_keys="[Report.reported_user_id]", back_populates="reported_user")


class SmtpCredentials(Base):
    __tablename__ = "smtp_credentials"

    smtp_id = Column(BigInteger, primary_key=True, index=True)
    account_id = Column(BigInteger, ForeignKey("accounts.account_id", ondelete="CASCADE"), nullable=False)
    email_address = Column(String(255), nullable=False)
    smtp_password = Column(String, nullable=False)

    # Back-reference for Account
    account = relationship(
        "Account",  # Explicitly declare the relationship target as a string
        back_populates="smtp_credentials"
    )