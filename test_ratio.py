from fastapi.testclient import TestClient
from main import app
import io
from PIL import Image

client = TestClient(app)

def create_dummy_image(width, height, color='red'):
    img = Image.new('RGB', (width, height), color)
    buf = io.BytesIO()
    img.save(buf, format='JPEG')
    buf.seek(0)
    return buf

def test_aspect_ratios():
    # 1. Test 9:7 Ratio (approx 1.2857)
    print("Testing 9:7 Ratio...")
    img_buf = create_dummy_image(1000, 1000)
    
    response = client.post(
        "/upload",
        files={"file": ("test.jpg", img_buf, "image/jpeg")},
        data={
            "target_size_mb": 2.0,
            "target_ratio": 9/7
        }
    )
    
    assert response.status_code == 200
    processed_img = Image.open(io.BytesIO(response.content))
    width, height = processed_img.size
    ratio = width / height
    expected_ratio = 9 / 7
    
    print(f"Original: 1000x1000, Processed: {width}x{height}, Ratio: {ratio:.4f}")
    assert abs(ratio - expected_ratio) < 0.05, f"Aspect ratio mismatch: {ratio}"
    print("9:7 Ratio Test Passed!")

    # 2. Test Custom Ratio (e.g., 1:1)
    print("\nTesting 1:1 Ratio...")
    img_buf_2 = create_dummy_image(1000, 500) # Landscape input
    
    response = client.post(
        "/upload",
        files={"file": ("test.jpg", img_buf_2, "image/jpeg")},
        data={
            "target_size_mb": 2.0,
            "target_ratio": 1.0
        }
    )
    
    assert response.status_code == 200
    processed_img_2 = Image.open(io.BytesIO(response.content))
    width, height = processed_img_2.size
    ratio = width / height
    
    print(f"Original: 1000x500, Processed: {width}x{height}, Ratio: {ratio:.4f}")
    assert abs(ratio - 1.0) < 0.05, f"Aspect ratio mismatch: {ratio}"
    print("1:1 Ratio Test Passed!")

if __name__ == "__main__":
    test_aspect_ratios()
