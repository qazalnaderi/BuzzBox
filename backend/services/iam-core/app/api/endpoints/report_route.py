from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from app.domain.schemas.report_schema import CreateReportSchema, ReportSchema
from app.services.report_service import ReportService
from app.services.auth_service.user_service import get_current_user  
from app.core.db.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession

report_router = APIRouter()

@report_router.post("/reports", response_model=ReportSchema, status_code=status.HTTP_201_CREATED)
async def create_report(
    report_data: CreateReportSchema,
    current_user_id: int = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    report_service = ReportService(session)
    return await report_service.create_report(report_data, current_user_id)