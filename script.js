// DOM Elements
const messageInput = document.querySelector('.message-input');
const chatMessages = document.getElementById('chatMessages');

/**
 * Adds a new message to the chat
 * @param {string} text - Message content
 * @param {boolean} isBot - Whether message is from bot
 */
function addMessage(text, isBot = false) {
    const messageDiv = document.createElement('div');
    messageDiv.classList.add('message');
    if(isBot) messageDiv.style.background = 'rgba(255,215,0,0.2)';
    messageDiv.textContent = text;
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Event Listener for Message Input
messageInput.addEventListener('keypress', (e) => {
    if(e.key === 'Enter') {
        const message = messageInput.value.trim();
        if(message) {
            // Add user message
            addMessage(message);
            messageInput.value = '';
            
            // Simulate bot response after 1 second
            setTimeout(() => {
                addMessage(`I received your query about: "${message}"`, true);
            }, 1000);
        }
    }
});