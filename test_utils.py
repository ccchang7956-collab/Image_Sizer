import io
from PIL import Image
from utils import process_image
from fastapi import UploadFile

def create_dummy_image(width, height, color):
    img = Image.new('RGB', (width, height), color)
    buf = io.BytesIO()
    img.save(buf, format='JPEG')
    buf.seek(0)
    return buf

def test_process_image():
    # 1. Test Aspect Ratio (16:9)
    # Create a square image (1000x1000)
    print("Testing Aspect Ratio...")
    img_buf = create_dummy_image(1000, 1000, 'red')
    upload_file = UploadFile(filename="test.jpg", file=img_buf)
    
    processed_buf = process_image(upload_file, target_size_mb=2.0)
    processed_img = Image.open(processed_buf)
    
    width, height = processed_img.size
    ratio = width / height
    expected_ratio = 16 / 9
    
    print(f"Original: 1000x1000, Processed: {width}x{height}, Ratio: {ratio:.2f}")
    assert abs(ratio - expected_ratio) < 0.05, f"Aspect ratio mismatch: {ratio}"
    print("Aspect Ratio Test Passed!")

    # 2. Test File Size Limit
    # Create a large image (should be > 1MB)
    print("\nTesting File Size Limit (0.1MB)...")
    # Make a very large image to ensure it exceeds 0.1MB initially
    img_buf_large = create_dummy_image(3000, 3000, 'blue')
    upload_file_large = UploadFile(filename="large.jpg", file=img_buf_large)
    
    target_mb = 0.1
    processed_buf_large = process_image(upload_file_large, target_size_mb=target_mb)
    
    size_mb = processed_buf_large.getbuffer().nbytes / (1024 * 1024)
    print(f"Target: {target_mb}MB, Result: {size_mb:.4f}MB")
    assert size_mb <= target_mb, f"File size too large: {size_mb}MB"
    print("File Size Test Passed!")

if __name__ == "__main__":
    test_process_image()
