/**
 * Image Sizer - 圖片裁切壓縮工具
 * 前端主程式
 */

// ============ DOM 元素 ============
const fileInput = document.getElementById('file-upload');
const fileNameDisplay = document.getElementById('file-name');
const ratioDisplay = document.getElementById('ratio-display');
const ratioContainer = document.getElementById('ratio-container');
const reCropBtn = document.getElementById('reCropBtn');
const form = document.getElementById('uploadForm');
const loading = document.getElementById('loading');
const submitBtn = document.getElementById('submitBtn');
const errorMessage = document.getElementById('error-message');

// Crop Modal 元素
const cropModal = document.getElementById('cropModal');
const imageToCrop = document.getElementById('image-to-crop');
const confirmCropBtn = document.getElementById('confirmCropBtn');
const cancelCropBtn = document.getElementById('cancelCropBtn');
const cropX = document.getElementById('crop-x');
const cropY = document.getElementById('crop-y');
const cropWidth = document.getElementById('crop-width');
const cropHeight = document.getElementById('crop-height');
const targetRatioInput = document.getElementById('target-ratio');
const ratioBtns = document.querySelectorAll('.ratio-btn');
const customWInput = document.getElementById('custom-w');
const customHInput = document.getElementById('custom-h');
const applyCustomRatioBtn = document.getElementById('applyCustomRatioBtn');

// ============ 狀態變數 ============
let cropper = null;
let currentFileSrc = null;

// ============ 比例設定函數 ============
/**
 * 設定裁切比例
 * @param {number} ratio - 目標比例
 */
function setRatio(ratio) {
    if (cropper) {
        cropper.setAspectRatio(ratio);
    }

    let ratioText = "自由調整";
    if (!isNaN(ratio)) {
        if (Math.abs(ratio - 16 / 9) < 0.01) {
            ratioText = "16:9";
        } else if (Math.abs(ratio - 7 / 9) < 0.01) {
            ratioText = "7:9";
        } else {
            const w = parseFloat(customWInput.value);
            const h = parseFloat(customHInput.value);
            if (w && h && Math.abs(ratio - w / h) < 0.001) {
                ratioText = `自訂 (${w}:${h})`;
            } else {
                ratioText = `自訂 (${ratio.toFixed(2)})`;
            }
        }
    }

    ratioDisplay.textContent = `目前比例: ${ratioText}`;

    // 更新按鈕樣式
    ratioBtns.forEach(btn => {
        const btnRatio = parseFloat(btn.dataset.ratio);
        const isSelected = (isNaN(btnRatio) && isNaN(ratio)) || (Math.abs(btnRatio - ratio) < 0.01);

        if (isSelected) {
            btn.classList.add('bg-blue-100', 'border-primary', 'text-primary');
        } else {
            btn.classList.remove('bg-blue-100', 'border-primary', 'text-primary');
        }
    });

    // 更新隱藏輸入
    if (!isNaN(ratio)) {
        targetRatioInput.value = ratio;
    }
}

// 將 setRatio 設為全域函數供 HTML onclick 使用
window.setRatio = setRatio;

// ============ Modal 函數 ============
/**
 * 開啟裁切 Modal
 * @param {string} imageSrc - 圖片來源
 */
function openCropModal(imageSrc) {
    imageToCrop.src = imageSrc;
    cropModal.classList.remove('hidden');

    // 初始化 Cropper（預設 16:9）
    if (cropper) {
        cropper.destroy();
    }
    cropper = new Cropper(imageToCrop, {
        aspectRatio: 16 / 9,
        viewMode: 1,
        autoCropArea: 1,
    });

    // 重設按鈕為 16:9
    setRatio(16 / 9);
}

/**
 * 關閉裁切 Modal
 */
function closeCropModal() {
    cropModal.classList.add('hidden');
}

// ============ UI 狀態函數 ============
/**
 * 顯示載入狀態
 */
function showLoading() {
    loading.classList.remove('hidden');
    submitBtn.disabled = true;
    submitBtn.classList.add('opacity-50', 'cursor-not-allowed');
    submitBtn.setAttribute('aria-busy', 'true');
    errorMessage.classList.add('hidden');
}

/**
 * 隱藏載入狀態
 */
function hideLoading() {
    loading.classList.add('hidden');
    submitBtn.disabled = false;
    submitBtn.classList.remove('opacity-50', 'cursor-not-allowed');
    submitBtn.setAttribute('aria-busy', 'false');
}

/**
 * 顯示錯誤訊息
 * @param {string} message - 錯誤訊息
 */
function showError(message) {
    errorMessage.textContent = message;
    errorMessage.classList.remove('hidden');
}

// ============ 事件處理 ============
// 自訂比例套用
applyCustomRatioBtn.addEventListener('click', () => {
    const w = parseFloat(customWInput.value);
    const h = parseFloat(customHInput.value);
    if (w > 0 && h > 0) {
        setRatio(w / h);
    } else {
        alert("請輸入有效的寬度和高度");
    }
});

// 檔案選擇
fileInput.addEventListener('change', (e) => {
    const file = e.target.files[0];
    if (file) {
        fileNameDisplay.textContent = `已選擇: ${file.name}`;
        fileNameDisplay.classList.remove('hidden');
        ratioContainer.classList.remove('hidden');

        // 開啟裁切 Modal
        const reader = new FileReader();
        reader.onload = (e) => {
            currentFileSrc = e.target.result;
            openCropModal(currentFileSrc);
        };
        reader.readAsDataURL(file);
    } else {
        fileNameDisplay.classList.add('hidden');
        ratioContainer.classList.add('hidden');
        currentFileSrc = null;
    }
});

// 重新裁切
reCropBtn.addEventListener('click', () => {
    if (currentFileSrc) {
        openCropModal(currentFileSrc);
    }
});

// 確認裁切
confirmCropBtn.addEventListener('click', () => {
    if (cropper) {
        const data = cropper.getData();
        cropX.value = data.x;
        cropY.value = data.y;
        cropWidth.value = data.width;
        cropHeight.value = data.height;

        closeCropModal();
    }
});

// 取消裁切
cancelCropBtn.addEventListener('click', () => {
    closeCropModal();
    fileInput.value = '';
    fileNameDisplay.classList.add('hidden');
    ratioContainer.classList.add('hidden');
    if (cropper) {
        cropper.destroy();
        cropper = null;
    }
});

// 表單提交
form.addEventListener('submit', async (e) => {
    e.preventDefault();

    const file = fileInput.files[0];
    if (!file) return;

    // 驗證 Min < Max
    const minSize = parseFloat(document.getElementById('min_size_mb').value);
    const maxSize = parseFloat(document.getElementById('target_size_mb').value);

    if (minSize >= maxSize) {
        showError("最小檔案大小必須小於最大檔案大小。");
        return;
    }

    showLoading();

    const formData = new FormData(form);

    try {
        const response = await fetch('/upload', {
            method: 'POST',
            body: formData
        });

        if (response.ok) {
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;

            // 從 header 取得檔名
            const contentDisposition = response.headers.get('Content-Disposition');
            let filename = 'processed_image.jpg';
            if (contentDisposition) {
                const filenameMatch = contentDisposition.match(/filename\*=UTF-8''([^;]+)/);
                if (filenameMatch && filenameMatch.length === 2) {
                    filename = decodeURIComponent(filenameMatch[1]);
                } else {
                    const filenameMatchSimple = contentDisposition.match(/filename="?([^"]+)"?/);
                    if (filenameMatchSimple && filenameMatchSimple.length === 2) {
                        filename = filenameMatchSimple[1];
                    }
                }
            }
            a.download = filename;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            a.remove();
        } else {
            const errorData = await response.json().catch(() => null);
            throw new Error(errorData?.detail || 'Upload failed');
        }
    } catch (error) {
        console.error('Error:', error);
        showError(error.message || "處理圖片時發生錯誤。");
    } finally {
        hideLoading();
    }
});
