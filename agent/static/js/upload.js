document.getElementById('uploadForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const files = document.getElementById('fileInput').files;
    if (files.length === 0) {
        alert('请选择文件');
        return;
    }

    const formData = new FormData();
    for (let i = 0; i < files.length; i++) {
        formData.append('files', files[i]);
    }

    try {
        document.getElementById('status').textContent = '处理中...';
        const response = await fetch('/api/rebuild_vector_db', {
            method: 'POST',
            body: formData
        });
        const result = await response.json();
        document.getElementById('status').textContent = `成功处理 ${result.processed_files} 个文件`;
    } catch (error) {
        document.getElementById('status').textContent = '处理失败: ' + error.message;
    }
});