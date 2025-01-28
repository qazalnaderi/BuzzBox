from typing import Optional
from fastapi import Depends, status, APIRouter
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.db.database import get_db
from app.services.auth_service.admin_service import get_current_admin
from app.infrastructure.repositories.account_repository import get_account_by_email
from app.domain.models.admins import Admin
from app.domain.schemas.admin_schema import AdminSchema
from app.domain.schemas.report_schema import ReportResponse
import logging
from fastapi import Depends, HTTPException
from app.domain.models.accounts import Account
from app.domain.models.report import Report
from app.services.admin_management_service import AdminManageService, BanUserService
admin_router = APIRouter()

@admin_router.get("/me", response_model=AdminSchema, status_code=status.HTTP_200_OK)
async def read_admin_me(
    admin: Admin = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
) -> AdminSchema:

    logging.info(f"...Getting admin profile with email address {admin.email_address}...")

    admin_schema = AdminSchema(
        admin_id=admin.admin_id,
        email_address=admin.email_address
    )

    return admin_schema


@admin_router.get("/reports", response_model=list[ReportResponse])
async def get_all_reports(
    admin: Admin = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
) -> list[ReportResponse]:

    try:
        admin_service = AdminManageService(db=db, admin=admin)
        reports = await admin_service.get_all_reports()
        
        return reports
        
    except Exception as e:
        logging.info(f"Error in get_all_reports endpoint: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error occurred while fetching reports"
        )    


@admin_router.post("/ban-user", status_code=200)
async def ban_user(
    reported_user_email_address: str,
    admin: Admin = Depends(get_current_admin),  
    db: AsyncSession = Depends(get_db)
):
    try:
        reported_account = await get_account_by_email(db, reported_user_email_address)
        
        if not reported_account:
            raise HTTPException(status_code=404, detail=f"User with email {reported_user_email_address} not found.")

        ban_user_service = BanUserService(db)

        await ban_user_service.ban_user(reported_account)
        return {"message": f"User with email {reported_account.email_address} has been banned successfully."}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")