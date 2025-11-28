from PIL import Image
import io
from fastapi import UploadFile

def process_image(file: UploadFile, target_size_mb: float = 2.0, crop_box: tuple = None, target_ratio: float = 16/9, min_size_mb: float = 0.0) -> io.BytesIO:
    """
    Process the uploaded image:
    1. Crop to target_ratio (using crop_box if provided, else center crop).
    2. Resize/Compress to be under target_size_mb.
    3. If min_size_mb > 0, ensure file size is at least min_size_mb (by upscaling if needed).
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
        # Auto Center Crop based on target_ratio
        width, height = image.size
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

    # 2. Compress/Resize to target size (Max Limit)
    output = io.BytesIO()
    quality = 95
    target_size_bytes = target_size_mb * 1024 * 1024
    min_size_bytes = min_size_mb * 1024 * 1024
    
    # Initial save to check size
    image.save(output, format="JPEG", quality=quality)
    
    # Logic for Max Size (Downscaling)
    while output.tell() > target_size_bytes and quality > 10:
        output.seek(0)
        output.truncate()
        quality -= 5
        image.save(output, format="JPEG", quality=quality)
    
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

    # 3. Logic for Min Size (Upscaling)
    # Only if we are below min size AND we haven't just downscaled to meet max size (conflict check)
    # If we downscaled to meet max size, we shouldn't upscale again unless max > min is valid.
    
    if min_size_bytes > 0 and output.tell() < min_size_bytes:
        # First try increasing quality to 100
        if quality < 100:
            quality = 100
            output.seek(0)
            output.truncate()
            image.save(output, format="JPEG", quality=quality)
            
        # If still too small, start upscaling
        scale_factor = 1.2
        max_iterations = 30 # Prevent infinite loops
        iteration = 0
        
        while output.tell() < min_size_bytes and iteration < max_iterations:
            # Check if upscaling would exceed max size
            # We can't easily predict exact size, but if we are already near max, stop.
            if output.tell() >= target_size_bytes: 
                break
                
            width, height = image.size
            new_size = (int(width * scale_factor), int(height * scale_factor))
            
            # Use BICUBIC for upscaling
            image_upscaled = image.resize(new_size, Image.Resampling.BICUBIC)
            
            temp_output = io.BytesIO()
            image_upscaled.save(temp_output, format="JPEG", quality=quality)
            
            # If upscaling exceeds max size, stop and keep previous
            if temp_output.tell() > target_size_bytes:
                break
                
            # Apply upscale
            image = image_upscaled
            output = temp_output
            iteration += 1

    output.seek(0)
    return output
