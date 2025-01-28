from sqlalchemy import Column, Integer, String, ForeignKey, Text, TIMESTAMP, BigInteger, Date
from datetime import datetime, timezone
from sqlalchemy.orm import relationship, Mapped
from app.core.postgres_db.postgres_database import Base

class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    gender = Column(String(10), nullable=True)
    birthday = Column(Date, nullable=False)
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