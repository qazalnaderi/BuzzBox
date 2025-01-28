from sqlalchemy import Column, Integer, String


from app.core.db.database import Base

class Admin(Base):
    __tablename__ = "admins"

    admin_id = Column(Integer, primary_key=True, index=True)
    email_address = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)