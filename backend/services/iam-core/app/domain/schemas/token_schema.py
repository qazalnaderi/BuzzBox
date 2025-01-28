from typing import Optional
from pydantic import BaseModel
from datetime import datetime

# Access Token Response Schema
class Token(BaseModel):
    access_token: str
    token_type: str
    expires_in: Optional[datetime] = 3600  

    class Config:
        from_attributes = True


