import logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    force=True,
)

logger = logging.getLogger(__name__)
logger.info("Custom logging is configured.")
import smtplib
from fastapi.middleware.cors import CORSMiddleware
from app.api.endpoints.account_route import user_router
from app.api.endpoints.login_route import login_router
from app.api.endpoints.profile_management_route import profile_router
from app.api.endpoints.contacts_route import contact_router
from app.api.endpoints.email_route import email_router
from app.api.endpoints.report_route import report_router
from app.api.endpoints.admin_route import admin_router
from app.api.endpoints.auth_route import auth_router

from fastapi import FastAPI
from fastapi.security import OAuth2PasswordBearer

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(user_router, prefix="/account", tags=["account"])
app.include_router(login_router,prefix="/login", tags=["login"])
app.include_router(profile_router, prefix="/profile", tags=["manage-profile"])
app.include_router(contact_router, prefix="/contacts", tags=["manage-contacts"])
app.include_router(email_router, prefix="/emails", tags=["emails"])
app.include_router(report_router, prefix="/reports", tags=["reports"])
app.include_router(admin_router, prefix="/admin", tags=["admin"])
app.include_router(auth_router,prefix="/auth", tags=["auth"])



logging.info("IAM Service Started")

@app.get("/")
async def root():
    return {"message": "Hello Dear! Welcome to the IAM service."}




# smtp_host = "poste"
# smtp_port = 587
# smtp_user = "admin@buzzbox.com"
# smtp_pass = "@Qazal1234"

# try:
#     with smtplib.SMTP(smtp_host, smtp_port) as server:
#         server.set_debuglevel(1)  # Enable verbose logs
#         server.starttls()         # Upgrade connection to secure
#         server.login(smtp_user, smtp_pass)  # Authenticate
#         print("SMTP connected and authenticated successfully.")
# except smtplib.SMTPConnectError as e:
#     print("SMTP Connection error:", e)
# except smtplib.SMTPAuthenticationError as e:
#     print("SMTP Authentication error:", e)
# except Exception as e:
#     print("Unexpected error:", e)
