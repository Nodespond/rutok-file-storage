from minio import Minio
from minio.error import S3Error
from fastapi import HTTPException

from fastapi import UploadFile

import io , os

from datetime import datetime
from sqlalchemy.orm import Session

from storage_service.api.models import Videos

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

MINIO_HOST = os.environ.get("MINIO_HOST", "localhost:9000")
MINIO_ACCESS_KEY = os.environ.get("MINIO_ACCESS_KEY")
MINIO_SECRET_KEY = os.environ.get("MINIO_SECRET_KEY")
BUCKET_NAME = os.environ.get("BUCKET_NAME", "videos")


def create_bucket(minio_client, bucket_name):
    try:
        found = minio_client.bucket_exists(bucket_name)
        if not found:
            minio_client.make_bucket(bucket_name)
        else:
            print("Bucket " + bucket_name + " already exists")
    except Exception as e:
        print(f"Error creating bucket: {e}")

minio_client = Minio(
    MINIO_HOST,
    access_key=MINIO_ACCESS_KEY,
    secret_key=MINIO_SECRET_KEY,
    secure=False
)
create_bucket(minio_client, BUCKET_NAME)

async def upload_video(video: UploadFile , db:Session, userId:int ) -> int:
    try:

        record = Videos(
            name=video.filename,
            path="",
            type=video.content_type,
            size=0,
            update_date=datetime.now(),
            user_id=userId
        )

        db.add(record)
        db.commit()
        db.refresh(record)

        object_id = f"{record.id}"

        file_content = await video.read()
        size = len(file_content)

        minio_client.put_object(
            BUCKET_NAME,
            object_id,
            data=io.BytesIO(file_content),
            length=size,
            content_type=video.content_type,
            metadata={"Content-Type": video.content_type}
        )

        record.path = object_id
        record.size = size
        db.commit()

        return record.id

    except S3Error as exc:
        print(f"Ошибка загрузки в MinIO: {exc}")
        if record and record.id:
            db.delete(record)
            db.commit()
        raise
    except Exception as db_exc:
        print(f"Ошибка загрузки в БД: {db_exc}")
        raise HTTPException(status_code=500, detail="Ошибка загрузки видео в хранилище")


async def upload_preview(preview: UploadFile, videoId: int):
    try:
        preview_key = f"preview_{videoId}.png"

        if not preview.content_type.startswith('image/'):
            raise ValueError("Превью должно быть изображением")

        file_content = await preview.read()

        minio_client.put_object(
            BUCKET_NAME,
            preview_key,
            io.BytesIO(file_content),
            length=len(file_content),
            content_type=preview.content_type
        )

        return preview_key

    except S3Error as e:
        raise HTTPException(status_code=500, detail=f"Ошибка загрузки превью: {str(e)}")

async def get_video_path(db: Session, video_id: int, user_id: int):
    db_video = db.query(Videos).filter(Videos.id == video_id, Videos.user_id == user_id).first()
    if not db_video:
        return None
    return db_video.path

async def get_video_preview(db: Session, video_id: int, user_id: int):
    try:
        db_video = db.query(Videos).filter(Videos.id == video_id, Videos.user_id == user_id).first()
        if not db_video:
            return None
        return db_video.preview_url

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при запросе к базе данных: {str(e)}")
