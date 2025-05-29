from fastapi import FastAPI, HTTPException, Response
from fastapi import File
from fastapi.params import Depends

from storage_service.api.database import get_db
from storage_service.api.storage import *

app = FastAPI()

@app.get("/", summary="Main root",tags=["Main"])
async def index():
    return {"message": "Video Storage Service"}

@app.post("/api/files/upload",summary="Загрузка в хранилище",tags=["Видео"] )
async def upload(
        file: UploadFile = File(...),
        db: Session = Depends(get_db)
):
    try:
        object_key = await upload_video(file, db)
        return {
            "object_key": object_key,
            "message": "Видео загружено, данные сохранены"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка загрузки видео: {str(e)}")


@app.get("/api/files/{object_key}",summary="Получение из хранилища",tags=["Видео"])
async def get_file(object_key: str):
    try:
        response = minio_client.get_object(BUCKET_NAME, object_key)
        return Response(content=response.data, media_type=response.headers["Content-Type"])
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"File not found: {str(e)}")

@app.post("/api/files/{video_id}/preview", summary="Загрузка превью для видео", tags=["Превью"])
async def upload_preview_for_video(
        video_id: int,
        preview: UploadFile = File(..., description="Превью видео"),
        db: Session = Depends(get_db)
):
    try:
        db_video = db.query(Videos).filter(Videos.id == video_id).first()
        if not db_video:
            raise HTTPException(status_code=404, detail="Видео не найдено")

        preview_key = await upload_preview(preview, video_id)

        db_video.preview_url = preview_key
        db.commit()


        return {
            "preview_url": preview_key,
            "message": "Превью успешно загружено"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка в загрузке превью: {str(e)}")


@app.get("/api/files/{video_id}/preview", summary="Получение превью видео", tags=["Превью"])
async def get_preview(
        video_id: str,
        db: Session = Depends(get_db)
):
    try:
        db_video = db.query(Videos).filter(Videos.id == video_id).first()
        if not db_video:
            raise HTTPException(status_code=404, detail="Видео не найдено")

        response = minio_client.get_object(BUCKET_NAME, db_video.preview_url)
        return Response(
            content=response.data,
            media_type=response.headers["Content-Type"]
        )

    except S3Error as e:
        if e.code == "NoSuchKey":
            raise HTTPException(status_code=404, detail="Превью не найдено в хранилище")
        raise HTTPException(status_code=500, detail=f"Ошибка хранилища: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Ошибка получения превью: {str(e)}")