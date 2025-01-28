from sqlalchemy import Column, BigInteger, Text, TIMESTAMP, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.db.database import Base


class Report(Base):
    __tablename__ = "reports"

    reporter_id = Column(BigInteger, ForeignKey("accounts.account_id", ondelete="CASCADE"), primary_key=True)
    reported_user_id = Column(BigInteger, ForeignKey("accounts.account_id", ondelete="CASCADE"), primary_key=True)
    reason = Column(Text, nullable=False)
    report_date = Column(TIMESTAMP, default=datetime.utcnow)

    # Relationships
    reporter = relationship("Account", foreign_keys=[reporter_id], back_populates="reports_made")
    reported_user = relationship("Account", foreign_keys=[reported_user_id], back_populates="reports_received")
