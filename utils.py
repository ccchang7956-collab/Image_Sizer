from PIL import Image
import io
from fastapi import UploadFile

def process_image(file: UploadFile, target_size_mb: float = 2.0, crop_box: tuple = None) -> io.BytesIO:
    """
    Process the uploaded image:
    1. Crop to 16:9 aspect ratio (using crop_box if provided, else center crop).
    2. Resize/Compress to be under target_size_mb.
    """
    image = Image.open(file.file)
    
    # Ensure image is in RGB mode (handle PNG/RGBA)
    if image.mode in ("RGBA", "P"):
        image = image.convert("RGB")

    # 1. Crop
    if crop_box:
        # crop_box is (x, y, width, height) from frontend
        # Pillow crop expects (left, top, right, bottom)
        x, y, w, h = crop_box
        image = image.crop((x, y, x + w, y + h))
    else:
        # Auto 16:9 Center Crop
        width, height = image.size
        target_ratio = 16 / 9
        current_ratio = width / height

        if current_ratio > target_ratio:
            # Too wide, crop width
            new_width = int(height * target_ratio)
            left = (width - new_width) // 2
            top = 0
            right = left + new_width
            bottom = height
        else:
            # Too tall, crop height
            new_height = int(width / target_ratio)
            left = 0
            top = (height - new_height) // 2
            right = width
            bottom = top + new_height

        image = image.crop((left, top, right, bottom))

    # 2. Compress/Resize to target size
    output = io.BytesIO()
    quality = 95
    target_size_bytes = target_size_mb * 1024 * 1024
    
    # Initial save to check size
    image.save(output, format="JPEG", quality=quality)
    
    while output.tell() > target_size_bytes and quality > 10:
        output.seek(0)
        output.truncate()
        quality -= 5
        image.save(output, format="JPEG", quality=quality)
    
    # If still too big after quality reduction, start resizing
    if output.tell() > target_size_bytes:
        scale_factor = 0.9
        while output.tell() > target_size_bytes:
            width, height = image.size
            new_size = (int(width * scale_factor), int(height * scale_factor))
            if new_size[0] < 100 or new_size[1] < 100: # Safety break
                break
            image = image.resize(new_size, Image.Resampling.LANCZOS)
            
            output.seek(0)
            output.truncate()
            image.save(output, format="JPEG", quality=quality) # Use last quality

    output.seek(0)
    return output
