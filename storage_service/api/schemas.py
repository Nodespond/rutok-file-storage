from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class VideoMetadata(BaseModel):
    name: str
    path: str
    type: str
    size: int
    update_date: datetime
    object_preview: Optional[str] = None