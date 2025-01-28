from fastapi import HTTPException, status
from typing import List
from app.domain.models.report import Report
from app.infrastructure.repositories import report_repository, account_repository
from app.domain.schemas.report_schema import CreateReportSchema, ReportSchema
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

class ReportService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_report(self, report_data: CreateReportSchema, reporter_id: int) -> ReportSchema:
        # Find reported user by email
        reported_user = await account_repository.get_account_by_email(self.session, report_data.reported_email)
        if not reported_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User with this email not found"
            )

        if report_data.reason == "" :
               raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You cannot report someone for no reason"
            )
        reporter_account = await account_repository.get_account_by_user_id(self.session, reporter_id)
        # Check self-reporting
        if reporter_account.account_id == reported_user.account_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You cannot report yourself"
            )

        try:
            report = Report(
                reporter_id=reporter_account.account_id,
                reported_user_id=reported_user.account_id,
                reason=report_data.reason,
            )
            logger.info(f"Creating report by {reporter_id} against {reported_user.account_id}")
            created_report = await report_repository.create_report(self.session, report)
            return ReportSchema.from_orm(created_report)
        except IntegrityError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unable to create report"
            )
        except Exception as e:
            logger.error(f"Error creating report: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while creating the report"
            )
            
