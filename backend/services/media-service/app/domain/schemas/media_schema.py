from datetime import datetime
from typing import Annotated, Optional

from bson import ObjectId
from pydantic import BaseModel

from app.domain.models.media_model import MediaModel
from app.domain.models.object_id_model import ObjectIdPydanticAnnotation


class MediaSchema(MediaModel):
    message: str
    media_type: Optional[str] = None  # e.g., 'image', 'pdf', etc.
    file_size: Optional[int] = None  # Optional: Store file size in bytes
    media_url: Optional[str] = None  # If using external storage (like S3)
  

    class Config:
        from_attributes = True
        json_encoders = {ObjectId: str, datetime: lambda v: v.isoformat()}
        arbitrary_types_allowed = True


class MediaGetSchema(BaseModel):
    mongo_id: Annotated[ObjectId, ObjectIdPydanticAnnotation]