from minio import Minio
from minio.error import S3Error
from fastapi import UploadFile
import hashlib
import io
import os

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

async def upload_video(video: UploadFile) -> str:
    try:
        #TODO uint поменять в ключе#
        object_key = f"{hashlib.md5(video.filename.encode()).hexdigest()}_{video.filename}"

        file_content = await video.read()
        content_type = video.content_type or "video/mp4"
        print(f"Content-Type перед загрузкой: {content_type}")
        minio_client.put_object(
            BUCKET_NAME,
            object_key,
            data=io.BytesIO(file_content),
            length=len(file_content),
            content_type=content_type,
            metadata={"Content-Type": content_type}
        )
        return object_key

    except S3Error as exc:
        print(f"Error uploading to MinIO: {exc}")
        raise