# 圖片裁切壓縮工具 (Image Sizer)

一個基於 FastAPI 的圖片處理 Web 應用程式，提供自動裁切與智慧壓縮功能。

## ✨ 功能特色

- 🖼️ **智慧裁切** - 支援多種預設比例 (16:9, 7:9) 與自訂比例
- 📦 **智慧壓縮** - 自動調整品質與尺寸以符合目標檔案大小
- 📏 **大小範圍** - 可設定最小與最大檔案大小限制
- 🎯 **互動式裁切** - 使用 Cropper.js 提供視覺化裁切介面
- ♿ **無障礙設計** - 完整的 ARIA 標籤與鍵盤導航支援

## 🛠️ 技術架構

- **後端**: Python 3.10+, FastAPI, Pillow
- **前端**: HTML5, TailwindCSS, Cropper.js
- **配置**: Pydantic Settings, python-dotenv

## 📦 安裝步驟

### 1. 複製專案

```bash
git clone <repository-url>
cd Image_Sizer
```

### 2. 建立虛擬環境

```bash
python -m venv venv
source venv/bin/activate  # macOS/Linux
# 或
.\venv\Scripts\activate  # Windows
```

### 3. 安裝依賴

```bash
pip install -r requirements.txt
```

### 4. 設定環境變數 (選用)

```bash
cp .env.example .env
# 編輯 .env 檔案以自訂設定
```

## 🚀 執行方式

### 開發環境

```bash
python main.py
# 或
uvicorn main:app --reload
```

### 生產環境

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

啟動後訪問 http://localhost:8000

## 📖 API 文件

啟動應用程式後，可透過以下網址查看自動生成的 API 文件：

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### 主要端點

| 方法 | 路徑 | 說明 |
|------|------|------|
| GET | `/` | 首頁 (Web UI) |
| POST | `/upload` | 上傳並處理圖片 |

### POST /upload 參數

| 參數 | 類型 | 必填 | 預設值 | 說明 |
|------|------|------|--------|------|
| file | File | ✅ | - | 圖片檔案 (支援 PNG, JPG, GIF) |
| target_size_mb | float | ❌ | 2.0 | 目標最大檔案大小 (MB) |
| min_size_mb | float | ❌ | 0.0 | 目標最小檔案大小 (MB) |
| x, y, width, height | float | ❌ | - | 裁切框座標 |
| target_ratio | float | ❌ | 16/9 | 目標長寬比 |

## ⚙️ 環境變數

| 變數 | 說明 | 預設值 |
|------|------|--------|
| HOST | 伺服器主機 | 0.0.0.0 |
| PORT | 伺服器埠號 | 8000 |
| DEBUG | 除錯模式 | false |
| MAX_UPLOAD_SIZE_MB | 最大上傳檔案大小 | 10.0 |
| CORS_ORIGINS | 允許的跨域來源 | ["*"] |

## 📁 專案結構

```
Image_Sizer/
├── main.py              # FastAPI 應用程式入口
├── utils.py             # 圖片處理工具函數
├── config.py            # 配置管理
├── requirements.txt     # Python 依賴
├── .env.example         # 環境變數範本
├── .gitignore
├── README.md
├── static/
│   ├── css/
│   │   └── style.css    # 自訂樣式
│   └── js/
│       └── main.js      # 前端主程式
└── templates/
    └── index.html       # 首頁模板
```

## 📄 授權

MIT License
