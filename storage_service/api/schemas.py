from pydantic import BaseModel
from datetime import datetime

class VideoMetadata(BaseModel):
    name: str
    path: str
    type: str
    size: int
    updateDate: datetime
    previewUrl: str
    userId: int