// BARD/src/static/js/index.js
// Get DOM elements
const chatBox = document.getElementById('chatBox');
const messageInput = document.getElementById('messageInput');
const sendButton = document.getElementById('sendButton');
const loading = document.getElementById('loading');

/**
 * Add a message to the chat box
 * @param {string} content - The message content
 * @param {boolean} isUser - Whether the message is from the user
 */
function addMessage(content, isUser) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${isUser ? 'user' : 'bot'}`;
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    contentDiv.textContent = content;
    
    messageDiv.appendChild(contentDiv);
    chatBox.appendChild(messageDiv);
    chatBox.scrollTop = chatBox.scrollHeight;
}

/**
 * Send a message to the server and display the response
 */
async function sendMessage() {
    const message = messageInput.value.trim();
    if (!message) return;

    // Add user message to chat
    addMessage(message, true);
    messageInput.value = '';
    sendButton.disabled = true;
    loading.classList.add('active');

    try {
        const response = await fetch('/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ message: message }),
        });

        const data = await response.json();
        
        if (data.error) {
            addMessage(`Error: ${data.error}`, false);
        } else {
            addMessage(data.response, false);
        }
    } catch (error) {
        addMessage(`Error: ${error.message}`, false);
    } finally {
        sendButton.disabled = false;
        loading.classList.remove('active');
        messageInput.focus();
    }
}

// Event Listeners
sendButton.addEventListener('click', sendMessage);
messageInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        sendMessage();
    }
});

// Focus on input when page loads
messageInput.focus();