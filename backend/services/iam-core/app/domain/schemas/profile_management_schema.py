from pydantic import BaseModel, EmailStr, Field
from datetime import date
from pydantic import ConfigDict
from typing import Optional

class UpdateProfile(BaseModel):
    previous_email_address: str 
    new_email_address: Optional[str] = None
    first_name: Optional[str] 
    last_name: Optional[str] 
    gender: Optional[str] 
    birthday: Optional[date] 
    phone_number: Optional[str] 

    model_config = ConfigDict(from_attributes=True)


class UpdatedProfileResponse(BaseModel):
    email_address: str
    message: str

    model_config = ConfigDict(from_attributes=True)

class ChangePasswordRequest(BaseModel):
        current_password: str
        new_password: str
        confirm_new_password: str

class ChangePasswordResponse(BaseModel):
        message: str

class PasswordResetRequest(BaseModel):
    email_address: str 
    otp: str 
    new_password: str 
    confirm_password: str 

class PasswordResetResponse(BaseModel):
    status_code: int
    message: str



class DeleteAccountRequest(BaseModel):
    password: str 
    confirm_password: str