# In report_repository.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload
from typing import List

from app.domain.models.report import Report
import logging

async def create_report(session: AsyncSession, report: Report) -> Report:
    session.add(report)
    try:
        await session.commit()
        await session.refresh(report)
        return report
    except IntegrityError as e:
        await session.rollback()
        logging.error(f"Error creating report: {str(e)}")
        raise

async def get_reports(session: AsyncSession) -> List[Report]:
    result = await session.execute(
        select(Report).options(
            joinedload(Report.reporter),
            joinedload(Report.reported_user),
        )
    )
    return result.unique().scalars().all()

async def get_reports_for_account(db: AsyncSession, account_id: int):
    stmt = select(Report).filter(Report.reported_user_id == account_id)
    result = await db.execute(stmt)
    return result.scalars().all()
