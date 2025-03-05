// Chat Integration Script
const API_ENDPOINT = '/chat'; // This will be the backend endpoint

async function sendMessageToChatbot(message) {
  try {
    const response = await fetch(API_ENDPOINT, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ 
        message: message,
        context: '', // You can modify this to pass context if needed
        tone: 'friendly' 
      })
    });

    if (!response.ok) {
      throw new Error('Network response was not ok');
    }

    const data = await response.json();
    return data.response;
  } catch (error) {
    console.error('Error:', error);
    return "I'm sorry, there was an error processing your message. Please try again.";
  }
}

// Modify the existing sendMessage function in chat.js
function sendMessage() {
  const messageInput = document.getElementById('messageInput');
  const message = messageInput.value.trim();
  
  if (message) {
    // Add user message
    addMessage(message);
    messageInput.value = '';
    
    // Show typing indicator
    addMessage('...', true);
    
    // Send message to chatbot
    sendMessageToChatbot(message)
      .then(response => {
        // Remove typing indicator
        const messages = document.getElementById('chatMessages');
        messages.removeChild(messages.lastChild);
        
        // Add chatbot response
        addMessage(response, true);
      })
      .catch(error => {
        // Remove typing indicator
        const messages = document.getElementById('chatMessages');
        messages.removeChild(messages.lastChild);
        
        // Show error message
        addMessage("Sorry, I couldn't process your message.", true);
      });
  }
}

// Ensure the event listeners are set up
document.addEventListener('DOMContentLoaded', () => {
  const messageInput = document.getElementById('messageInput');
  const sendButton = document.getElementById('sendButton');

  messageInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
      sendMessage();
    }
  });

  sendButton.addEventListener('click', sendMessage);
});