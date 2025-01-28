from pydantic import BaseModel
from pydantic import ConfigDict

class ContactCreate(BaseModel):
    contact_email: str 

class ContactUpdate(BaseModel):
    contact_email: str 


