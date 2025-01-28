from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime

class AdminSchema(BaseModel):
    admin_id: int
    email_address: str 
    model_config = ConfigDict(from_attributes=True)
