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
        video_id: str,
        preview: UploadFile = File(..., description="Превью видео")
):
    try:
        preview_key = await upload_preview(preview, video_id)

        return {
            "preview_key": preview_key,
            "message": "Превью успешно загружено"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка загрузки превью: {str(e)}")


@app.get("/api/files/{video_id}/preview", summary="Получение превью видео", tags=["Превью"])
async def get_preview(video_id: str):
    try:
        preview_key = f"previews_{video_id}.png"

        response = minio_client.get_object(BUCKET_NAME, preview_key)
        return Response(
            content=response.data,
            media_type=response.headers["Content-Type"]
        )
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Превью не найдено: {str(e)}")