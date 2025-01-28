from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class TokenDataSchema(BaseModel):
    user_id: int
    email_address: str
    is_verified: bool
    # first_name: str
    # last_name: str
    # mobile_number: str = Field(..., pattern=r"^\+?[1-9]\d{1,14}$")
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# class TokenDataSchema(BaseModel):
#     user_id: int   
#     email: str
#     exp: datetime

#     class Config:
#         from_attributes = True