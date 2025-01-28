from pydantic import BaseModel, ConfigDict
from datetime import date, datetime
from typing import Optional

class UserBase(BaseModel):
    first_name: str 
    last_name: str 
    gender: Optional[str] = "other"
    birthday: date
    phone_number: str 

class UserCreate(UserBase):
    pass

class UserResponse(BaseModel):
    email_address: str
    first_name: Optional[str] = None
    last_name : Optional[str] = None
    model_config = ConfigDict(from_attributes=True)

class AccountBase(BaseModel):
    email_address: str 
    password: str 
    status: Optional[str] 
    recovery_email: Optional[str] 

class AccountCreate(AccountBase):
    pass

class AccountResponse(AccountBase):
    account_id: int
    user_id: int
    created_at: datetime
    updated_at: datetime


    model_config = ConfigDict(from_attributes=True)

class UserLogin(BaseModel):
    email_address: str 
    password: str

class OTPCreate(BaseModel):
    email_address: str 
    otp: str

class AdminLogin(BaseModel):
    email_address: str 
    password: str

class UserInfo(BaseModel):
    email_address: str
    first_name: str
    last_name: str

class VerifyOTPSchema(BaseModel):
    email_address: str
    otp: str


    model_config = ConfigDict(from_attributes=True)

class VerifyOTPResponseSchema(BaseModel):
    email_address: str
    otp_valid: bool
    message: str

    model_config = ConfigDict(from_attributes=True)

class ResendOTPSchema(BaseModel):
    email_address: str

    model_config = ConfigDict(from_attributes=True)

class ResendOTPResponseSchema(BaseModel):
    email_address: str
    otp_sent: bool
    message: str

    model_config = ConfigDict(from_attributes=True)


class LoginResponse(BaseModel):
    access_token: str
    token_type: str

class ErrorResponse(BaseModel):
    message: str


class AccountSchema(BaseModel):
    account_id: int
    email_address: str
    status: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

    
class UserSchema(BaseModel):
    user_id: int
    first_name: str
    last_name: str
    gender: Optional[str] = "other"
    birthday: date
    phone_number: str
    accounts: list[AccountSchema]  

    
    model_config = ConfigDict(from_attributes=True)


class RegistrationResponse(BaseModel):
    message: str

    model_config = ConfigDict(from_attributes=True)
