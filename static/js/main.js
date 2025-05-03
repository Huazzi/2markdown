document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('upload-form');
    const fileInput = document.getElementById('file-upload');
    const selectFileBtn = document.getElementById('select-file-btn');
    const convertBtn = document.getElementById('convert-btn');
    const fileInfo = document.getElementById('file-info');
    const filename = document.getElementById('filename');
    const removeFileBtn = document.getElementById('remove-file');
    const processing = document.getElementById('processing');
    const errorMessage = document.getElementById('error-message');
    const uploadArea = document.querySelector('.upload-area');

    // 打开文件选择器
    selectFileBtn.addEventListener('click', function(e) {
        e.preventDefault();
        fileInput.click();
    });

    // 监听文件选择
    fileInput.addEventListener('change', function() {
        if (fileInput.files.length > 0) {
            showFileInfo(fileInput.files[0]);
        }
    });

    // 移除已选择的文件
    removeFileBtn.addEventListener('click', function(e) {
        e.preventDefault();
        resetForm();
    });

    // 拖拽上传功能
    uploadArea.addEventListener('dragover', function(e) {
        e.preventDefault();
        uploadArea.classList.add('dragover');
    });

    uploadArea.addEventListener('dragleave', function() {
        uploadArea.classList.remove('dragover');
    });

    uploadArea.addEventListener('drop', function(e) {
        e.preventDefault();
        uploadArea.classList.remove('dragover');
        
        if (e.dataTransfer.files.length > 0) {
            fileInput.files = e.dataTransfer.files;
            showFileInfo(e.dataTransfer.files[0]);
        }
    });

    // 表单提交处理
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        
        if (fileInput.files.length === 0) {
            showError('请选择要转换的文件');
            return;
        }

        // 准备表单数据
        const formData = new FormData();
        formData.append('file', fileInput.files[0]);

        // 显示处理中状态
        processing.classList.remove('d-none');
        convertBtn.disabled = true;
        hideError();

        // 发送转换请求
        fetch('/upload', {
            method: 'POST',
            body: formData
        })
        .then(response => {
            // 检查响应类型
            const contentType = response.headers.get('content-type');
            
            if (contentType && contentType.includes('application/json')) {
                // 如果是JSON（可能是错误信息），解析为JSON
                return response.json().then(data => {
                    throw new Error(data.error || '转换失败');
                });
            } else if (response.ok) {
                // 如果不是JSON且响应成功，处理文件下载
                return response.blob();
            } else {
                // 其他错误情况
                throw new Error('转换失败，请稍后重试');
            }
        })
        .then(blob => {
            // 创建下载链接
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.style.display = 'none';
            a.href = url;
            a.download = fileInput.files[0].name.replace(/\.[^/.]+$/, '') + '.md';
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            
            // 重置表单
            resetForm();
        })
        .catch(error => {
            showError(error.message);
        })
        .finally(() => {
            // 隐藏处理中状态
            processing.classList.add('d-none');
            convertBtn.disabled = false;
        });
    });

    // 显示已选择文件的信息
    function showFileInfo(file) {
        filename.textContent = file.name;
        fileInfo.classList.remove('d-none');
        convertBtn.disabled = false;
    }

    // 重置表单
    function resetForm() {
        form.reset();
        fileInfo.classList.add('d-none');
        convertBtn.disabled = true;
        hideError();
    }

    // 显示错误信息
    function showError(message) {
        errorMessage.textContent = message;
        errorMessage.classList.remove('d-none');
    }

    // 隐藏错误信息
    function hideError() {
        errorMessage.textContent = '';
        errorMessage.classList.add('d-none');
    }
}); 