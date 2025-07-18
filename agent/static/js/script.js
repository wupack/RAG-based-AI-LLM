document.addEventListener('DOMContentLoaded', function() {
    // 消息发送功能
    const userInput = document.getElementById('user-input');
    const sendBtn = document.getElementById('send-btn');
    const messagesContainer = document.getElementById('messages');
    
    // 发送消息函数
    async function sendMessage() {
        const message = userInput.value.trim();
        if (!message) return;
        
        // 添加用户消息到聊天界面
        addMessage('user', message);
        userInput.value = '';
        
        try {
            // 获取当前选择的知识库
            const currentDb = document.getElementById('vector-db-select').value;
            
            // 发送请求到后端
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: message,
                    db_name: currentDb
                })
            });
            
            if (!response.ok) {
                throw new Error('获取回复失败');
            }
            
            const data = await response.json();
            // 添加AI回复到聊天界面
            addMessage('ai', data.response);
        } catch (error) {
            console.error('Error:', error);
            addMessage('ai', '抱歉，发生错误: ' + error.message);
        }
    }
    
    // 添加消息到聊天界面
    function addMessage(sender, text) {
        const messageElement = document.createElement('div');
        messageElement.className = `message ${sender}`;
        
        const avatar = document.createElement('div');
        avatar.className = 'avatar';
        
        const content = document.createElement('div');
        content.className = 'content';
        content.textContent = text;
        
        if (sender === 'user') {
            avatar.innerHTML = '<i class="mdi mdi-account"></i>';
            messageElement.appendChild(avatar);
            messageElement.appendChild(content);
        } else {
            avatar.innerHTML = '<i class="mdi mdi-robot"></i>';
            messageElement.appendChild(avatar);
            messageElement.appendChild(content);
        }
        
        messagesContainer.appendChild(messageElement);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }
    
    // 事件监听
    sendBtn.addEventListener('click', sendMessage);
    
    userInput.addEventListener('keydown', function(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });
    
    // 初始化聊天界面
    function initChat() {
        // 这里可以添加初始化聊天记录的逻辑
        // 例如从本地存储加载历史消息
    }
    
    initChat();
});