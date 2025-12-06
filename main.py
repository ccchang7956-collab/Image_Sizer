"""
Image Sizer - 圖片裁切壓縮工具 API

FastAPI 應用程式主入口點
"""
import asyncio
from urllib.parse import quote

from fastapi import FastAPI, UploadFile, File, Form, Request, HTTPException
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from config import settings
from utils import process_image, InvalidImageError

# 建立 FastAPI 應用
app = FastAPI(
    title="Image Sizer",
    description="圖片裁切壓縮工具 API",
    version="1.0.0"
)

# CORS 中介軟體
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=settings.CORS_ALLOW_METHODS,
    allow_headers=settings.CORS_ALLOW_HEADERS,
)

# 設定模板與靜態檔案目錄
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# 常數
MAX_UPLOAD_BYTES = int(settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024)


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """渲染首頁"""
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/upload")
async def upload_image(
    file: UploadFile = File(...),
    target_size_mb: float = Form(settings.DEFAULT_TARGET_SIZE_MB),
    min_size_mb: float = Form(settings.DEFAULT_MIN_SIZE_MB),
    x: float = Form(None),
    y: float = Form(None),
    width: float = Form(None),
    height: float = Form(None),
    target_ratio: float = Form(settings.DEFAULT_TARGET_RATIO)
):
    """
    上傳並處理圖片
    
    - 裁切至指定比例
    - 壓縮至目標大小範圍
    
    Args:
        file: 上傳的圖片檔案
        target_size_mb: 目標最大檔案大小 (MB)
        min_size_mb: 目標最小檔案大小 (MB)
        x, y, width, height: 裁切框座標
        target_ratio: 目標長寬比
        
    Returns:
        處理後的圖片檔案
    """
    # 驗證檔案大小
    content = await file.read()
    if len(content) > MAX_UPLOAD_BYTES:
        raise HTTPException(
            status_code=413,
            detail=f"檔案大小超過限制 ({settings.MAX_UPLOAD_SIZE_MB}MB)"
        )
    
    # 重置檔案指標
    await file.seek(0)
    
    # 驗證大小範圍
    if min_size_mb >= target_size_mb:
        raise HTTPException(
            status_code=400,
            detail="最小檔案大小必須小於最大檔案大小"
        )
    
    # 建立裁切框
    crop_box = None
    if all(v is not None for v in [x, y, width, height]):
        crop_box = (x, y, width, height)
    
    try:
        # 使用 asyncio.to_thread 避免阻塞事件循環
        processed_image_io = await asyncio.to_thread(
            process_image,
            file.file,
            target_size_mb,
            crop_box,
            target_ratio,
            min_size_mb
        )
    except InvalidImageError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"處理圖片時發生錯誤: {str(e)}")
    
    # 處理非 ASCII 檔名 (RFC 5987)
    original_name = file.filename.rsplit('.', 1)[0] if '.' in file.filename else file.filename
    filename = f"processed_{original_name}.jpg"
    encoded_filename = quote(filename)
    
    return StreamingResponse(
        processed_image_io,
        media_type="image/jpeg",
        headers={
            "Content-Disposition": f"attachment; filename*=UTF-8''{encoded_filename}"
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
