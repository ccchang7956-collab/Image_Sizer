from fastapi.testclient import TestClient
from main import app
import io
from PIL import Image

client = TestClient(app)

def create_dummy_image(width, height, color):
    img = Image.new('RGB', (width, height), color)
    # Add a different color patch to verify cropping
    # Top-left 100x100 is white
    for x in range(100):
        for y in range(100):
            img.putpixel((x, y), (255, 255, 255))
            
    buf = io.BytesIO()
    img.save(buf, format='JPEG')
    buf.seek(0)
    return buf

def test_manual_crop():
    # Create 1000x1000 red image with white top-left corner
    img_buf = create_dummy_image(1000, 1000, (255, 0, 0))
    
    # Define crop box: Top-left 100x100 (which is white)
    # x=0, y=0, width=100, height=100
    
    response = client.post(
        "/upload",
        files={"file": ("test.jpg", img_buf, "image/jpeg")},
        data={
            "target_size_mb": 2.0,
            "x": 0,
            "y": 0,
            "width": 100,
            "height": 100
        }
    )
    
    assert response.status_code == 200
    
    # Verify the output image
    processed_img = Image.open(io.BytesIO(response.content))
    width, height = processed_img.size
    
    print(f"Processed Size: {width}x{height}")
    
    # Check if it's white (mean color)
    # Since we cropped the white part, the average color should be close to white
    # Note: JPEG compression might introduce slight artifacts, so we check if it's "bright"
    r, g, b = processed_img.resize((1, 1)).getpixel((0, 0))
    print(f"Average Color: ({r}, {g}, {b})")
    
    assert r > 240 and g > 240 and b > 240, "Image should be white (cropped area)"
    assert abs(width - 100) < 5 and abs(height - 100) < 5, "Size should be approx 100x100 (before resizing logic kicks in if needed)"
    
    print("Manual Crop Test Passed!")

if __name__ == "__main__":
    test_manual_crop()
