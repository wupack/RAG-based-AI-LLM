document.addEventListener('DOMContentLoaded', () => {
    const messagesContainer = document.getElementById('messages');
    const userInput = document.getElementById('user-input');
    const sendBtn = document.getElementById('send-btn');
    const originalBtnText = sendBtn.textContent;
    
    function addMessage(text, isUser) {
        const msgDiv = document.createElement('div');
        msgDiv.className = `message ${isUser ? 'user-message' : 'bot-message'}`;
        msgDiv.textContent = text;

        if (!isUser) {
            const copyBtn = document.createElement('button');
            copyBtn.className = 'copy-btn';
            copyBtn.textContent = '复制';
            copyBtn.addEventListener('click', () => {
                navigator.clipboard.writeText(text).then(() => {
                    const originalCopyBtnText = copyBtn.textContent;
                    copyBtn.textContent = '已复制';
                    setTimeout(() => {
                        copyBtn.textContent = originalCopyBtnText;
                    }, 1000);
                }).catch(err => {
                    console.error('复制失败: ', err);
                });
            });
            msgDiv.appendChild(copyBtn);
        }

        messagesContainer.appendChild(msgDiv);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }
    
    async function sendMessage() {
        const message = userInput.value.trim();
        if (!message) return;

        sendBtn.textContent = '提问中';
        sendBtn.disabled = true;

        addMessage(message, true);
        userInput.value = '';
        
        try {
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ message })
            });
            
            if (!response.ok) {
                throw new Error('请求失败');
            }
            
            const data = await response.json();
            addMessage(data.response, false);
        } catch (error) {
            addMessage(`错误: ${error.message}`, false);
            console.error(error);
        } finally {
            sendBtn.textContent = originalBtnText;
            sendBtn.disabled = false;
        }
    }
    
    sendBtn.addEventListener('click', sendMessage);
    userInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });
});