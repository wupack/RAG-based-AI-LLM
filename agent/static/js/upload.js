document.addEventListener('DOMContentLoaded', function() {
    const dropArea = document.getElementById('dropArea');
    const fileInput = document.getElementById('fileInput');
    const selectFilesBtn = document.getElementById('selectFilesBtn');
    const fileListContent = document.getElementById('fileListContent');
    const fileCount = document.getElementById('fileCount');
    const submitBtn = document.getElementById('submitBtn');
    const statusContainer = document.getElementById('status');
    const dbNameInput = document.getElementById('dbName');
    
    let files = [];
    
    // 选择文件按钮点击事件
    selectFilesBtn.addEventListener('click', function() {
        fileInput.click();
    });
    
    // 文件输入变化事件
    fileInput.addEventListener('change', function(e) {
        handleFiles(e.target.files);
        fileInput.value = ''; // 重置input，允许重复选择相同文件
    });
    
    // 拖放事件
    dropArea.addEventListener('dragover', function(e) {
        e.preventDefault();
        dropArea.classList.add('dragover');
    });
    
    dropArea.addEventListener('dragleave', function() {
        dropArea.classList.remove('dragover');
    });
    
    dropArea.addEventListener('drop', function(e) {
        e.preventDefault();
        dropArea.classList.remove('dragover');
        handleFiles(e.dataTransfer.files);
    });
    
    // 处理选择的文件
    function handleFiles(newFiles) {
        for (let i = 0; i < newFiles.length; i++) {
            const file = newFiles[i];
            
            // 检查文件类型是否支持
            if (!isFileTypeSupported(file.name)) {
                showStatus(`不支持的文件类型: ${file.name}`, 'error');
                continue;
            }
            
            // 检查是否已存在同名文件
            if (!files.some(f => f.name === file.name && f.size === file.size && f.lastModified === file.lastModified)) {
                files.push(file);
            }
        }
        
        updateFileList();
    }
    
    // 检查文件类型是否支持
    function isFileTypeSupported(filename) {
        const supportedExtensions = ['.txt', '.pdf', '.doc', '.docx', '.ppt', '.pptx', '.md', '.markdown'];
        const extension = filename.substring(filename.lastIndexOf('.')).toLowerCase();
        return supportedExtensions.includes(extension);
    }
    
    // 更新文件列表显示
    function updateFileList() {
        fileListContent.innerHTML = '';
        
        if (files.length === 0) {
            fileListContent.innerHTML = '<div class="empty-file-list">暂无文件，请拖放或选择文件</div>';
            fileCount.textContent = '0个文件';
            return;
        }
        
        files.forEach((file, index) => {
            const fileItem = document.createElement('div');
            fileItem.className = 'file-item';
            
            const fileIcon = document.createElement('div');
            fileIcon.className = 'file-icon';
            fileIcon.innerHTML = getFileIcon(file.name);
            
            const fileInfo = document.createElement('div');
            fileInfo.className = 'file-info';
            
            const fileName = document.createElement('div');
            fileName.className = 'file-name';
            fileName.textContent = file.name;
            
            const fileSize = document.createElement('div');
            fileSize.className = 'file-size';
            fileSize.textContent = formatFileSize(file.size);
            
            const fileRemove = document.createElement('div');
            fileRemove.className = 'file-remove';
            fileRemove.innerHTML = '<i class="mdi mdi-close"></i>';
            fileRemove.addEventListener('click', function(e) {
                e.stopPropagation();
                files.splice(index, 1);
                updateFileList();
            });
            
            fileInfo.appendChild(fileName);
            fileInfo.appendChild(fileSize);
            fileItem.appendChild(fileIcon);
            fileItem.appendChild(fileInfo);
            fileItem.appendChild(fileRemove);
            fileListContent.appendChild(fileItem);
        });
        
        fileCount.textContent = `${files.length}个文件`;
    }
    
    // 获取文件类型图标
    function getFileIcon(filename) {
        const extension = filename.substring(filename.lastIndexOf('.')).toLowerCase();
        switch(extension) {
            case '.pdf':
                return '<i class="mdi mdi-file-pdf"></i>';
            case '.doc':
            case '.docx':
                return '<i class="mdi mdi-file-word"></i>';
            case '.ppt':
            case '.pptx':
                return '<i class="mdi mdi-file-powerpoint"></i>';
            case '.txt':
                return '<i class="mdi mdi-file-document"></i>';
            case '.md':
            case '.markdown':
                return '<i class="mdi mdi-markdown"></i>';
            default:
                return '<i class="mdi mdi-file"></i>';
        }
    }
    
    // 格式化文件大小
    function formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }
    
    // 显示状态信息
    function showStatus(message, type = 'success') {
        statusContainer.className = `status-container ${type}`;
        statusContainer.innerHTML = message;
        statusContainer.style.display = 'block';
        
        // 5秒后自动隐藏
        setTimeout(() => {
            statusContainer.style.display = 'none';
        }, 5000);
    }
    
    // 表单提交事件
    submitBtn.addEventListener('click', async function() {
        const dbName = dbNameInput.value.trim();
        
        // 验证输入
        if (!dbName) {
            showStatus('请输入知识库名称', 'error');
            dbNameInput.focus();
            return;
        }
        
        if (files.length === 0) {
            showStatus('请至少选择一个文件', 'error');
            return;
        }
        
        try {
            // 准备表单数据
            const formData = new FormData();
            formData.append('db_name', dbName);
            
            // 添加所有文件
            for (let i = 0; i < files.length; i++) {
                formData.append('files', files[i]);
            }
            
            // 显示加载状态
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<i class="mdi mdi-loading mdi-spin"></i> 处理中...';
            
            // 发送请求
            const response = await fetch('/api/rebuild_vector_db', {
                method: 'POST',
                body: formData
            });
            
            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || '上传失败');
            }
            
            const result = await response.json();
            showStatus(`知识库创建成功: ${result.db_name} (${result.processed_files}个文件已处理)`, 'success');
            
            // 重置表单
            files = [];
            updateFileList();
            dbNameInput.value = '';
            
            // 3秒后刷新页面
            setTimeout(() => {
                location.reload();
            }, 3000);
            
        } catch (error) {
            console.error('上传失败:', error);
            showStatus('上传失败: ' + error.message, 'error');
        } finally {
            submitBtn.disabled = false;
            submitBtn.innerHTML = '<i class="mdi mdi-database-import"></i> 生成向量数据库';
        }
    });
    
    // 初始化文件列表
    updateFileList();
});