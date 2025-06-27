from sqlalchemy import Column, Integer, String, DateTime, BigInteger
from sqlalchemy.sql import func

from storage_service.api.database import Base


class Videos(Base):
    __tablename__ = "videos"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String)
    path = Column(String)
    type = Column(String)
    size = Column(Integer)
    update_date = Column(DateTime(timezone=True), default=func.now())
    preview_url = Column(String)
    user_id = Column(Integer)

    def __repr__(self):
        return f"<VideoMetadata(name='{self.name}', path='{self.path}')>"
