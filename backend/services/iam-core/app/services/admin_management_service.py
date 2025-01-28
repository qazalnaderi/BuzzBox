import logging
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.repositories.admin_repository import get_admin_by_id
from app.core.db.database import get_db
from app.services.auth_service.auth_tokens import verify_access_token
from app.domain.models.admins import Admin
from app.domain.models.report import Report
from app.domain.models.accounts import Account
from app.domain.schemas.report_schema import ReportResponse
from app.infrastructure.repositories.report_repository import get_reports, get_reports_for_account
from app.infrastructure.repositories.account_repository import (
    get_account_by_user_id,
    get_all_account_belongsto_user_id,
    delete_reports_by_account,
    delete_emails_by_account,
    delete_account,
    delete_user,
    get_account_by_id,
    get_user_by_id
)


class AdminManageService:
    def __init__(self, db: AsyncSession, admin: Admin):
        self.db = db
        self.admin = admin

    async def get_all_reports(self) -> list[ReportResponse]:
        """
        Get all reports with eager loaded relationships.
        Access controlled by admin authentication.
        """
        try:
            logging.info(f"Admin {self.admin.email_address} requesting all reports")
            reports = await get_reports(self.db)  
            logging.info(f"Retrieved {len(reports)} reports")

            result = []
            for report in reports:
                reporter = await get_account_by_id(self.db, report.reporter_id)
                reported = await get_account_by_id(self.db, report.reported_user_id)
                result.append(
                    ReportResponse(
                        reporter_email=reporter.email_address,     
                        reported_user_email=reported.email_address,
                        reason=report.reason,
                        report_date=report.report_date       
                    )
                )
            return result
            
        except Exception as e:
            logging.error(f"Error in fetching errors: {str(e)}")
            raise



class BanUserService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def ban_user(self, reported_account: Account):
        
        reports = await get_reports_for_account(self.db, reported_account.account_id)
        if not reports:
            raise HTTPException(status_code=400, detail=f"No reports found for email {reported_account.email_address}.")
        
        # Step 3: Delete related reports
        await delete_reports_by_account(self.db, reported_account.account_id)
        
        # Step 4: Delete related emails
        await delete_emails_by_account(self.db, reported_account.account_id)
        
        # Step 5: Delete the user account
        await delete_account(self.db, reported_account)

        # Step 6: Check if the user has any other accounts
        other_accounts = await get_all_account_belongsto_user_id(self.db, reported_account.user_id)

        # Step 7: If no other accounts exist for the user, delete the user
        if len(other_accounts) == 0:
            user = await get_user_by_id(self.db, reported_account.user_id)
            if user:
                await delete_user(self.db, user)

        # Commit changes
        await self.db.commit()