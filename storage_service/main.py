import sys

import uvicorn
from fastapi import FastAPI, HTTPException, Response
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import File
from fastapi.params import Depends , Header
import jwt
from jwt.exceptions import PyJWTError
from starlette.responses import StreamingResponse

from storage_service.api.database import get_db
from storage_service.api.storage import *

app = FastAPI()
security = HTTPBearer()

PUBLIC_KEY = """-----BEGIN PUBLIC KEY-----\n
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAqpdeHjpybq+EhruVGJSz
31sY+rXsgv9bKkWhq1aJ1rhROICmt/dj1ELDsMLHmsGoLz56nLvWiCzmHwWUV9hM
24GiidHyyx+QwBnaiJyDwE+E9rJUAi5KGtB51YTpDGZbUw8+S8YUJamJpb7c6JD9
2bzZOaBkffMU1vcMFC4pILNS0jpVF5LHeEQYzd9I5/tl4F+xSIUdq5MdaNatDAzb
UGQBuy3pyjKS1WSZrZhSFtiY6/CfLxWe7LBoZzcC0sm6gxPbAtroJnBUMSIcvoRW
CbLnsuf6eMI7dx5q8WjA4G9KwsiXB8ER7YPNEbfbaeszQHj4m/ercU/pu09NuTv4
SQIDAQAB\n-----END PUBLIC KEY-----\n
"""

async def get_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:

        token = credentials.credentials
        print(token)
        payload = jwt.decode(token, PUBLIC_KEY, algorithms=["RS256"])
        userId = payload.get("sub") or payload.get("user_id")
        if not id:
            raise HTTPException(status_code=401, detail="Неверный токен загрузки")
        return int(userId)
    except PyJWTError as e:
        raise HTTPException(status_code=401, detail="Недействительный токен")

@app.post("/api/files/upload",summary="Загрузка в хранилище",tags=["Видео"] )
async def upload(
        file: UploadFile = File(..., description="Видео"),
        preview: UploadFile = File(..., description="Превью видео"),
        db: Session = Depends(get_db),
        userId: int = Depends(get_user)
):
    try:
        video_id = await upload_video(file, db, userId)

        db_video = db.query(Videos).filter(Videos.id == video_id).first()
        if not db_video:
            raise HTTPException(status_code=404, detail="Видео не найдено")

        preview_key = await upload_preview(preview, video_id)
        db_video.preview_url = preview_key
        db.commit()

        return {
            "videoId": video_id
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка загрузки видео и превью: {str(e)}")


@app.get("/api/files/{videoId}", summary="Получение ссылки на видео из хранилища", tags=["Видео"])
async def get_file(
        videoId: int,
        db: Session = Depends(get_db),
        userId: int = Depends(get_user)
):
    try:
        db_video = await get_video_db(db, videoId, userId)
        url = generate_presigned_url(db_video.path)
        return {"urlVideo": url}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при получении ссылки на видео: {str(e)}")

@app.get("/api/files/preview/{videoId}", summary="Получение ссылки на превью из хранилища", tags=["Превью"])
async def get_preview(
        videoId: int,
        db: Session = Depends(get_db),
        userId: int = Depends(get_user)
):
    try:
        db_video = await get_video_db(db, videoId, userId)
        if not db_video.preview_url:
            raise HTTPException(status_code=404, detail="Превью не найдено")
        url = generate_presigned_url(db_video.preview_url)
        return {"urlPreview": url}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при получении ссылки на превью: {str(e)}")

if __name__ == "__main__":
    FAST_API_PORT = os.getenv("FAST_API_PORT", "8001")
    try:
        port = int(FAST_API_PORT)
    except ValueError:
        sys.exit(1)
    else:
        uvicorn.run("storage_service.main:app", host="0.0.0.0",port=port)

