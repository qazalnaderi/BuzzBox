from pydantic import BaseModel
from datetime import datetime
from pydantic import ConfigDict


class CreateReportSchema(BaseModel):
    reported_email: str 
    reason: str 
  

class ReportSchema(BaseModel):
    reporter_id: int
    reported_user_id: int
    reason: str
    report_date: datetime

    model_config = ConfigDict(from_attributes=True)



class ReportResponse(BaseModel):
    reporter_email: str
    reported_user_email: str
    reason: str
    report_date: datetime

    model_config = ConfigDict(from_attributes=True)
 