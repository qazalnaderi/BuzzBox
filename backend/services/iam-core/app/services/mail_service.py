import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import smtplib
from email.mime.text import MIMEText
from loguru import logger
from typing import List, Dict
import requests
from fastapi import HTTPException, status
from bs4 import BeautifulSoup
import asyncio
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import httpx
import ssl
import http.client as http_client
from typing import Optional
from requests.adapters import HTTPAdapter
from urllib3.poolmanager import PoolManager
from datetime import datetime
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder




class SSLAdapter(HTTPAdapter):
    """Custom SSL adapter for requests to relax SSL settings."""
    def __init__(self, ssl_context=None, **kwargs):
        self.ssl_context = ssl_context
        super().__init__(**kwargs)

    def init_poolmanager(self, *args, **kwargs):
        kwargs['ssl_context'] = self.ssl_context
        return super().init_poolmanager(*args, **kwargs)

class MailService:
    POSTE_IO_API_URL = "https://poste/admin/api/v1/boxes"
    ADMIN_EMAIL = "admin@buzzbox.com"
    ADMIN_PASSWORD = "@Qazal1234"

    last_request_time = None
    request_interval = 4.0  # Minimum time between requests
    lock = asyncio.Lock()  # Lock to ensure only one request is sent at a time

    @staticmethod
    async def create_mailbox(username: str, password: str):

        """
            Create a mailbox for the user using Poste.io API.
        """
        email_address = f"{username}@buzzbox.com"
        payload = {
            "name": username,
            "email": email_address,
            "passwordPlaintext": password,
            "disabled": False,
            "superAdmin": False,
            "redirectTo": [],
            "referenceId": ""
        }
        logging.info(f"Payload: {payload}")
        logging.info(f"POST URL: {MailService.POSTE_IO_API_URL}")

        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE

        # Configure session with the custom SSL adapter
        session = requests.Session()
        session.mount("https://", SSLAdapter(ssl_context))

        # Use the lock to ensure only one request is sent at a time
        async with MailService.lock:
            if MailService.last_request_time is not None:
                elapsed_time = asyncio.get_event_loop().time() - MailService.last_request_time
                if elapsed_time < MailService.request_interval:
                    delay = MailService.request_interval - elapsed_time
                    logging.debug(f"Throttling: Waiting {delay} seconds before next request.")
                    await asyncio.sleep(delay)

            try:
                response = requests.post(
                    MailService.POSTE_IO_API_URL,
                    auth=(MailService.ADMIN_EMAIL, MailService.ADMIN_PASSWORD),
                    json=payload,
                    verify=False
                )

                logging.info(f"Response Status Code: {response.status_code}")
                logging.info(f"Response Content: {response.text}")

                MailService.last_request_time = asyncio.get_event_loop().time()

                if response.status_code in [200, 201]:
                    logging.info(f"Mailbox created successfully for {email_address}")
                    return {"status": "success", "message": "Mailbox created successfully"}
                else:
                    logging.error(f"Failed to create mailbox for {email_address}: {response.text}")
                    return {"status": "error", "message": f"Failed to create mailbox: {response.text}"}

            except requests.RequestException as e:
                logging.error(f"Network error occurred while creating mailbox for {email_address}: {str(e)}")
                return {"status": "error", "message": f"Network error: {str(e)}"}
            except Exception as e:
                logging.error(f"Unexpected error occurred while creating mailbox for {email_address}: {str(e)}")
                return {"status": "error", "message": f"Unexpected error: {str(e)}"}

    @staticmethod
    async def send_email_via_smtp(
        sender_email: str,
        recipient_email: str,
        subject: str,
        body: str,
        smtp_user: str,
        smtp_pass: str,
    ):
        """
        Send an email via Poste.io SMTP server.

        Args:
            sender_email (str): Email address of the sender.
            recipient_emails (List[str]): List of recipient email addresses.
            subject (str): Subject of the email.
            body (str): Body of the email.
            smtp_user (str): SMTP username (email address of the sender).
            smtp_pass (str): SMTP password for authentication.

        Returns:
            dict: A dictionary indicating success or raises an HTTPException.
        """
        smtp_host = "poste"  # Updated to use localhost
        smtp_port = 587  # Default port for STARTTLS

        try:
            # Create the email message
            msg = MIMEText(body, "plain")
            msg["From"] = sender_email
            msg["To"] = recipient_email
            msg["Subject"] = subject

            # Connect to the SMTP server and send the email
            with smtplib.SMTP(smtp_host, smtp_port, timeout=10) as server:
                server.starttls()  # Upgrade the connection to secure
                server.login(smtp_user, smtp_pass)  # Authenticate with the SMTP server
                server.sendmail(sender_email, recipient_email, msg.as_string())  # Send the email

                

            logging.info(f"Email sent successfully from {sender_email} to {recipient_email}")
            return {
                "status": "success",
                "message": "Email sent successfully"
            }

        except smtplib.SMTPAuthenticationError as e:
            logging.error(f"SMTP Authentication error: {str(e)}")
            raise HTTPException(status_code=401, detail="SMTP authentication failed. Check your credentials.")

        except smtplib.SMTPConnectError as e:
            logging.error(f"SMTP Connection error: {str(e)}")
            raise HTTPException(status_code=503, detail="Failed to connect to the SMTP server.")

        except smtplib.SMTPException as e:
            logging.error(f"SMTP error occurred: {str(e)}")
            raise HTTPException(status_code=500, detail=f"SMTP error: {str(e)}")

        except Exception as e:
            logging.error(f"Unexpected error sending email: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
