from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime


class EmailCreate(BaseModel):
    sender_id: int
    subject: str
    body: str


class EmailResponse(BaseModel):
    email_id: int
    subject: str
    body: str
    created_at: datetime
    is_important: bool

    model_config = ConfigDict(from_attributes=True)


class EmailRecipientCreate(BaseModel):
    email_id: int
    recipient_email: str


class EmailRecipientResponse(BaseModel):
    recipient_id: int
    email_id: int
    recipient_email: str
    is_muted: bool

    model_config = ConfigDict(from_attributes=True)


class EmailSendRequest(BaseModel):
    recipient: str 
    subject: str 
    body: str 


class EmailModel(BaseModel):
    email_id: int
    sender_id: int
    subject: str
    body: str
    created_at: datetime
    is_important: bool
    recipient: str    

    model_config = ConfigDict(from_attributes=True)



class InboxResponse(BaseModel):
    email_id: int
    subject: str
    body: str
    sender_email: str
    received_at: datetime
    created_at: datetime
    is_important: bool
    
    model_config = ConfigDict(from_attributes=True)
