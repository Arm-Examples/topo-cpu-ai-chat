let conversationHistory = [];
let isGenerating = false;
const messagesContainer = document.getElementById('messages');
const userInput = document.getElementById('user-input');
const sendBtn = document.getElementById('send-btn');
const statusDot = document.getElementById('status-dot');
const statusText = document.getElementById('status-text');
const perfStats = document.getElementById('perf-stats');

document.addEventListener('DOMContentLoaded', () => {
    checkHealth();
    setInterval(checkHealth, 30000);

    userInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });

    addSystemMessage('Welcome! Start chatting with the LLM running on an Arm CPU!');
});

async function checkHealth() {
    try {
        const response = await fetch('/api/health');
        const data = await response.json();

        if (data.status === 'healthy') {
            statusDot.className = 'status-dot connected';
            statusText.textContent = 'Connected';
        } else {
            statusDot.className = 'status-dot error';
            statusText.textContent = 'Backend unavailable';
        }
    } catch (error) {
        statusDot.className = 'status-dot error';
        statusText.textContent = 'Connection error';
    }
}

async function sendMessage() {
    if (isGenerating) return;

    const message = userInput.value.trim();
    if (!message) return;

    userInput.value = '';
    sendBtn.disabled = true;
    isGenerating = true;

    addMessage('user', message);

    conversationHistory.push({
        role: 'user',
        content: message
    });

    const typingIndicator = addTypingIndicator();

    try {
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                message: message,
                history: conversationHistory
            })
        });

        if (!response.ok) {
            throw new Error(`HTTP error: ${response.status}`);
        }

        typingIndicator.remove();

        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let assistantMessage = '';
        let messageElement = null;

        while (true) {
            const { done, value } = await reader.read();
            if (done) break;

            const chunk = decoder.decode(value);
            const lines = chunk.split('\n');

            for (const line of lines) {
                if (line.startsWith('data: ')) {
                    const jsonStr = line.slice(6);
                    try {
                        const data = JSON.parse(jsonStr);

                        if (data.error) {
                            throw new Error(data.error);
                        }

                        if (data.content) {
                            assistantMessage += data.content;

                            if (!messageElement) {
                                messageElement = addMessage('assistant', assistantMessage);
                            } else {
                                updateMessage(messageElement, assistantMessage);
                            }
                        }

                        if(data.metrics && data.metrics.predicted_per_second) {
                            perfStats.textContent = `${data.metrics.predicted_per_second.toFixed(1)} tok/sec`;
                        }

                        if (data.done) {
                            break;
                        }
                    } catch (e) {
                        console.error('Parse error:', e);
                    }
                }
            }
        }

        if (assistantMessage) {
            conversationHistory.push({
                role: 'assistant',
                content: assistantMessage
            });
        }

    } catch (error) {
        typingIndicator.remove();
        addSystemMessage(`Error: ${error.message}`);
    } finally {
        isGenerating = false;
        sendBtn.disabled = false;
        userInput.focus();
    }
}

function addMessage(role, content) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${role}`;

    const avatar = document.createElement('div');
    avatar.className = 'message-avatar';
    avatar.textContent = role === 'user' ? 'U' : 'AI';

    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    contentDiv.textContent = content;

    messageDiv.appendChild(avatar);
    messageDiv.appendChild(contentDiv);
    messagesContainer.appendChild(messageDiv);

    scrollToBottom();
    return messageDiv;
}

function updateMessage(messageElement, content) {
    const contentDiv = messageElement.querySelector('.message-content');
    contentDiv.textContent = content;
    scrollToBottom();
}

function addSystemMessage(content) {
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message system';
    messageDiv.style.textAlign = 'center';
    messageDiv.style.color = '#6b7280';
    messageDiv.style.fontSize = '14px';
    messageDiv.style.fontStyle = 'italic';
    messageDiv.textContent = content;

    messagesContainer.appendChild(messageDiv);
    scrollToBottom();
}

function addTypingIndicator() {
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message assistant';

    const avatar = document.createElement('div');
    avatar.className = 'message-avatar';
    avatar.textContent = 'AI';

    const typingDiv = document.createElement('div');
    typingDiv.className = 'typing-indicator';
    typingDiv.innerHTML = '<span></span><span></span><span></span>';

    messageDiv.appendChild(avatar);
    messageDiv.appendChild(typingDiv);
    messagesContainer.appendChild(messageDiv);

    scrollToBottom();
    return messageDiv;
}

function scrollToBottom() {
    messagesContainer.parentElement.scrollTop = messagesContainer.parentElement.scrollHeight;
}
