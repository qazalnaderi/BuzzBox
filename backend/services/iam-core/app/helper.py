import random
import re
from datetime import date
from typing import Literal

MIN_PASSWORD_LENGTH = 8
VALID_GENDERS = ["male", "female", "other"]

def convert_date_to_string(data):
    if isinstance(data, dict):
        return {key: convert_date_to_string(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [convert_date_to_string(item) for item in data]
    elif isinstance(data, date):
        return data.isoformat()
    return data


async def suggest_email(first_name: str, last_name: str) -> str:
    random_number = random.randint(100, 999)
    return f"{first_name.lower()}{last_name.lower()}{random_number}@buzzbox.com"



async def validate_email(email: str):
        if not email.lower().endswith("@buzzbox.com"):
            return "Email address must end with @buzzbox.com"
        return None



async def validate_phone_number(phone_number: str) -> str:
    pattern = r"^\+[1-9]\d{7,14}$"
    if not re.match(pattern, phone_number):
        return "Invalid phone number format. It must be in international format (e.g., +123456789)."
    return None



async def validate_name(name: str) -> str:
    pattern = r"^[A-Za-z\s]+$"
    if not re.match(pattern, name):
        return "Name can only contain alphabetic characters and spaces."
    return None


async def check_password_strength(password: str) -> str:
    if len(password) < MIN_PASSWORD_LENGTH:
        return "Password must be at least 8 characters long."
    if not re.search(r"[A-Z]", password):
        return "Password must contain at least one uppercase letter."
    if not re.search(r"[a-z]", password):
        return "Password must contain at least one lowercase letter."
    if not re.search(r"[0-9]", password):
        return "Password must contain at least one digit."
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return "Password must contain at least one special character."
    return None



async def validate_gender(gender: str) -> str:
    if gender.lower() not in VALID_GENDERS:
        return "Gender should be one of: [female, male, other]"
    return None


class OTPVerificationFailedError(Exception):
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message

class MailboxCreationFailedError(Exception):
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message

class UserCreationFailedError(Exception):
    def __init__(self, message: str = "Failed to create user."):
        super().__init__(message)
        self.message = message

class AccountCreationFailedError(Exception):
    def __init__(self, message: str = "Failed to create account."):
        super().__init__(message)
        self.message = message

class SMTPCredentialCreationFailedError(Exception):
    def __init__(self, message: str = "Failed to create SMTP credentials."):
        super().__init__(message)
        self.message = message
class OTPResendFailedError(Exception):
    def __init__(self, message: str = "Failed to create send OTP."):
        super().__init__(message)
        self.message = message
