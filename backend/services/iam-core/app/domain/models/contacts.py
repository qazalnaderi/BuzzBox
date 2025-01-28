from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from app.core.db.database import Base



class Contact(Base):
    __tablename__ = "contacts"

    contact_id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("accounts.account_id"), nullable=False)
    contact_email = Column(String, unique=True, nullable=False)

    # Relationship to Account (no direct relationship with User)
    owner = relationship("Account", back_populates="contacts")