const messageInput = document.getElementById('messageInput');
const sendButton = document.getElementById('sendButton');
const chatMessages = document.getElementById('chatMessages');
const welcomeSection = document.getElementById('welcomeSection');

let activeChatId = 'default';

const chatData = {
  'default': []
};

function addMessageToUI(text, isBot = false) {
  if(text == ""){
    return;
  }
  const messageDiv = document.createElement('div');
  messageDiv.classList.add('message');
  messageDiv.classList.add(isBot ? 'bot-message' : 'user-message');
  messageDiv.textContent = text;
  chatMessages.appendChild(messageDiv);
  chatMessages.scrollTop = chatMessages.scrollHeight;
  
  welcomeSection.style.display = 'none';
}

function addMessage(text, isBot = false) {
  if (!chatData[activeChatId]) {
    chatData[activeChatId] = [];
  }
  
  chatData[activeChatId].push({ text, isBot });
  
  addMessageToUI(text, isBot);
}

function loadChatMessages(chatId) {
  chatMessages.innerHTML = '';
  
  if (chatData[chatId] && chatData[chatId].length > 0) {
    welcomeSection.style.display = 'none';
    
    chatData[chatId].forEach(msg => {
      addMessageToUI(msg.text, msg.isBot);
    });
  } else {
    welcomeSection.style.display = 'block';
  }
}


function sendMessage() {
  let messageInput = document.getElementById('messageInput');
  let message = messageInput.value;

  // Append user message to the chat
  appendMessage(message, 'user-message');

  // Send the message to the backend (Flask)
  fetch('/get_response', {
      method: 'POST',
      headers: {
          'Content-Type': 'application/json',
      },
      body: JSON.stringify({ message: message }),
  })
  .then(response => response.json())
  .then(data => {
      let botResponse = data.response;
      
      // Append bot response to the chat
      appendMessage(botResponse, 'bot-message');
  })
  .catch(error => {
      console.error('Error:', error);
  });

  messageInput.value = ''; // Clear input field
}
messageInput.addEventListener('keypress', (e) => {
  if (e.key === 'Enter') {
    sendMessage();
  }
});

sendButton.addEventListener('click', sendMessage);

loadChatMessages('default');

window.chatApp = {
  loadChatMessages,
  activeChatId,
  chatData,
  setActiveChatId: (chatId) => {
    activeChatId = chatId;
    loadChatMessages(chatId);  // Ensure that messages are loaded when the chat is switched
  }
};


// JavaScript to handle sending and receiving messages
document.getElementById('sendButton').addEventListener('click', sendMessage);



// Function to append messages to chat
function appendMessage(message, sender) {
  let chatMessages = document.getElementById('chatMessages');
  let messageElement = document.createElement('div');
  messageElement.classList.add('message'); // Ensure the 'message' class is always added
  messageElement.classList.add(sender); // Add either 'user-message' or 'bot-message'
  messageElement.textContent = message;
  chatMessages.appendChild(messageElement);
}