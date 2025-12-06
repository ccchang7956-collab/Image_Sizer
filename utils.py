"""
圖片處理工具模組

提供圖片裁切、壓縮和縮放功能。
"""
from PIL import Image
import io
from typing import BinaryIO, Optional

# ============ 處理常數 ============
INITIAL_QUALITY = 95
MIN_QUALITY = 10
QUALITY_STEP = 5
DOWNSCALE_FACTOR = 0.9
UPSCALE_FACTOR = 1.2
MAX_UPSCALE_ITERATIONS = 30
MIN_DIMENSION = 100
DEFAULT_TARGET_RATIO = 16 / 9


class ImageProcessingError(Exception):
    """圖片處理相關的例外"""
    pass


class InvalidImageError(ImageProcessingError):
    """無效圖片格式的例外"""
    pass


def validate_image(file: BinaryIO) -> Image.Image:
    """
    驗證並開啟圖片檔案
    
    Args:
        file: 檔案物件
        
    Returns:
        PIL Image 物件
        
    Raises:
        InvalidImageError: 當檔案不是有效圖片時
    """
    try:
        image = Image.open(file)
        image.verify()  # 驗證圖片完整性
        file.seek(0)    # 重置檔案指標
        image = Image.open(file)  # 重新開啟（verify 後需重開）
        return image
    except Exception as e:
        raise InvalidImageError(f"無效的圖片格式: {str(e)}")


def convert_to_rgb(image: Image.Image) -> Image.Image:
    """將圖片轉換為 RGB 模式"""
    if image.mode in ("RGBA", "P"):
        return image.convert("RGB")
    return image


def crop_to_ratio(
    image: Image.Image,
    crop_box: Optional[tuple[float, float, float, float]] = None,
    target_ratio: float = DEFAULT_TARGET_RATIO
) -> Image.Image:
    """
    根據裁切框或目標比例裁切圖片
    
    Args:
        image: PIL Image 物件
        crop_box: (x, y, width, height) 裁切框，若為 None 則自動置中裁切
        target_ratio: 目標長寬比
        
    Returns:
        裁切後的 Image 物件
    """
    if crop_box:
        x, y, w, h = crop_box
        return image.crop((x, y, x + w, y + h))
    
    # 自動置中裁切
    width, height = image.size
    current_ratio = width / height

    if current_ratio > target_ratio:
        # 太寬，裁切寬度
        new_width = int(height * target_ratio)
        left = (width - new_width) // 2
        return image.crop((left, 0, left + new_width, height))
    else:
        # 太高，裁切高度
        new_height = int(width / target_ratio)
        top = (height - new_height) // 2
        return image.crop((0, top, width, top + new_height))


def compress_to_max_size(
    image: Image.Image,
    target_size_bytes: int
) -> tuple[io.BytesIO, int, Image.Image]:
    """
    壓縮圖片至目標大小以下
    
    Args:
        image: PIL Image 物件
        target_size_bytes: 目標最大檔案大小（bytes）
        
    Returns:
        (BytesIO 輸出, 最終品質, 處理後的 Image)
    """
    output = io.BytesIO()
    quality = INITIAL_QUALITY
    
    # 初始儲存
    image.save(output, format="JPEG", quality=quality)
    
    # 降低品質
    while output.tell() > target_size_bytes and quality > MIN_QUALITY:
        output.seek(0)
        output.truncate()
        quality -= QUALITY_STEP
        image.save(output, format="JPEG", quality=quality)
    
    # 如仍過大，縮小尺寸
    if output.tell() > target_size_bytes:
        while output.tell() > target_size_bytes:
            width, height = image.size
            new_size = (int(width * DOWNSCALE_FACTOR), int(height * DOWNSCALE_FACTOR))
            
            if new_size[0] < MIN_DIMENSION or new_size[1] < MIN_DIMENSION:
                break
                
            image = image.resize(new_size, Image.Resampling.LANCZOS)
            output.seek(0)
            output.truncate()
            image.save(output, format="JPEG", quality=quality)
    
    return output, quality, image


def upscale_to_min_size(
    image: Image.Image,
    output: io.BytesIO,
    quality: int,
    min_size_bytes: int,
    max_size_bytes: int
) -> io.BytesIO:
    """
    放大圖片至最小檔案大小
    
    Args:
        image: PIL Image 物件
        output: 當前輸出 BytesIO
        quality: 當前品質
        min_size_bytes: 目標最小檔案大小（bytes）
        max_size_bytes: 目標最大檔案大小（bytes）
        
    Returns:
        處理後的 BytesIO 輸出
    """
    if min_size_bytes <= 0 or output.tell() >= min_size_bytes:
        return output
    
    # 先嘗試提高品質
    if quality < 100:
        quality = 100
        output.seek(0)
        output.truncate()
        image.save(output, format="JPEG", quality=quality)
    
    # 如仍太小，放大尺寸
    iteration = 0
    while output.tell() < min_size_bytes and iteration < MAX_UPSCALE_ITERATIONS:
        if output.tell() >= max_size_bytes:
            break
        
        width, height = image.size
        new_size = (int(width * UPSCALE_FACTOR), int(height * UPSCALE_FACTOR))
        
        image_upscaled = image.resize(new_size, Image.Resampling.BICUBIC)
        temp_output = io.BytesIO()
        image_upscaled.save(temp_output, format="JPEG", quality=quality)
        
        if temp_output.tell() > max_size_bytes:
            break
        
        image = image_upscaled
        output = temp_output
        iteration += 1
    
    return output


def process_image(
    file: BinaryIO,
    target_size_mb: float = 2.0,
    crop_box: Optional[tuple[float, float, float, float]] = None,
    target_ratio: float = DEFAULT_TARGET_RATIO,
    min_size_mb: float = 0.0
) -> io.BytesIO:
    """
    處理上傳的圖片：裁切、壓縮、調整大小
    
    Args:
        file: 上傳的檔案物件
        target_size_mb: 目標最大檔案大小 (MB)
        crop_box: 裁切框 (x, y, width, height)，若為 None 則自動置中裁切
        target_ratio: 目標長寬比
        min_size_mb: 目標最小檔案大小 (MB)
        
    Returns:
        處理後的圖片 BytesIO 物件
        
    Raises:
        InvalidImageError: 當檔案不是有效圖片時
    """
    # 1. 驗證並開啟圖片
    image = validate_image(file)
    
    # 2. 轉換為 RGB
    image = convert_to_rgb(image)
    
    # 3. 裁切
    image = crop_to_ratio(image, crop_box, target_ratio)
    
    # 4. 壓縮至最大大小限制
    target_size_bytes = int(target_size_mb * 1024 * 1024)
    min_size_bytes = int(min_size_mb * 1024 * 1024)
    
    output, quality, image = compress_to_max_size(image, target_size_bytes)
    
    # 5. 放大至最小大小（如需要）
    output = upscale_to_min_size(image, output, quality, min_size_bytes, target_size_bytes)
    
    output.seek(0)
    return output
