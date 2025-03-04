const messageInput = document.getElementById('messageInput');
const sendButton = document.getElementById('sendButton');
const chatMessages = document.getElementById('chatMessages');
const welcomeSection = document.getElementById('welcomeSection');

let activeChatId = 'default';

const chatData = {
  'default': []
};

function addMessageToUI(text, isBot = false) {
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
  const message = messageInput.value.trim();
  if (message) {
    addMessage(message);
    messageInput.value = '';
    
    setTimeout(() => {
      addMessage(`I received your query about: "${message}"`, true);
    }, 1000);
  }
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
  }
};