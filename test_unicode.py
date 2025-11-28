from fastapi.testclient import TestClient
from main import app
import io
from PIL import Image

client = TestClient(app)

def create_dummy_image():
    img = Image.new('RGB', (100, 100), 'red')
    buf = io.BytesIO()
    img.save(buf, format='JPEG')
    buf.seek(0)
    return buf

def test_unicode_filename_upload():
    # Test with Chinese characters
    filename = "測試圖片.jpg"
    img_buf = create_dummy_image()
    
    response = client.post(
        "/upload",
        files={"file": (filename, img_buf, "image/jpeg")},
        data={"target_size_mb": 2.0}
    )
    
    assert response.status_code == 200
    assert "content-disposition" in response.headers
    # Check if filename is correctly encoded in the header
    # It should contain the URL encoded version of "processed_測試圖片"
    # "測試圖片" url encoded is "%E6%B8%AC%E8%A9%A6%E5%9C%96%E7%89%87"
    assert "filename*=UTF-8''processed_%E6%B8%AC%E8%A9%A6%E5%9C%96%E7%89%87.jpg" in response.headers["content-disposition"]
    print("Unicode Filename Test Passed!")

if __name__ == "__main__":
    test_unicode_filename_upload()
