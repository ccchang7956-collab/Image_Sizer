from fastapi import FastAPI, UploadFile, File, Form, Request
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import io
from utils import process_image

app = FastAPI()

templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

from urllib.parse import quote

@app.post("/upload")
async def upload_image(
    file: UploadFile = File(...),
    target_size_mb: float = Form(2.0),
    x: float = Form(None),
    y: float = Form(None),
    width: float = Form(None),
    height: float = Form(None)
):
    crop_box = None
    if x is not None and y is not None and width is not None and height is not None:
        crop_box = (x, y, width, height)
        
    processed_image_io = process_image(file, target_size_mb, crop_box)
    
    # Handle non-ASCII filenames using RFC 5987
    filename = f"processed_{file.filename.rsplit('.', 1)[0]}.jpg"
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
    uvicorn.run(app, host="0.0.0.0", port=8000)
