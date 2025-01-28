from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.login_service import LoginService
from app.core.db.database import get_db
from app.domain.schemas.accounts_schema import AdminLogin, UserLogin, LoginResponse, ErrorResponse
from typing import Annotated
from fastapi.security import OAuth2PasswordRequestForm
import logging
from fastapi import HTTPException

login_router = APIRouter()


@login_router.post("/admin/login", response_model=LoginResponse, responses={400: {"model": ErrorResponse}})
async def admin_login(login_data: AdminLogin, db: AsyncSession = Depends(get_db)):
    login_service = LoginService(db)
    response = await login_service.admin_login(login_data)

    if isinstance(response, dict) and response.get("status_code") != 200:
        return JSONResponse(
            content=ErrorResponse(message=response["message"]).dict(),
            status_code=response["status_code"]
        )

    return response


@login_router.post("/user/login", response_model=LoginResponse, status_code=status.HTTP_200_OK)
async def user_login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: AsyncSession = Depends(get_db)
) -> LoginResponse:
    logging.info(f"Received login request for user: {form_data.username}")

    login_service = LoginService(db)
    response = await login_service.user_login(
        UserLogin(
            email_address=form_data.username,  
            password=form_data.password
        )
    )

    if isinstance(response, dict) and response.get("status_code") != 200:
        raise HTTPException(
            status_code=response["status_code"],
            detail=response["message"]
        )

    return response
