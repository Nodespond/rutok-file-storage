from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import func

DATABASE_URL = "postgresql://rutok:rutok@postgres-db:5432/rutok"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


class Videos(Base):
    __tablename__ = "videos"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String)
    path = Column(String)
    type = Column(String)
    size = Column(Integer)
    update_date = Column(DateTime(timezone=True), default=func.now())
    preview = Column(String)

    def __repr__(self):
        return f"<VideoMetadata(name='{self.name}', path='{self.path}')>"

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()