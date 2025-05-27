from fastapi import FastAPI, HTTPException, Response
from fastapi import File, UploadFile
from storage_service.api.storage import minio_client, BUCKET_NAME, upload_video

app = FastAPI()

@app.get("/", summary="Main root",tags=["Main"])
async def index():
    return {"message": "Video Storage Service"}

@app.post("/api/files/upload",summary="Загрузка в хранилище",tags=["Видео"] )
async def upload(file: UploadFile = File(...)):
    try:
        object_key = await upload_video(file)
        return {"object_key": object_key, "message": "Video uploaded successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload video: {str(e)}")


@app.get("/api/files/{object_key}",summary="Получение из хранилища",tags=["Видео"])
async def get_file(object_key: str):
    try:
        response = minio_client.get_object(BUCKET_NAME, object_key)
        return Response(content=response.data, media_type=response.headers["Content-Type"])
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"File not found: {str(e)}")
