const newChatBtn = document.getElementById('newChatBtn');
const newchatid = document.getElementById('newchatid');
const cancelBtn = document.getElementById('cancelBtn');
const createChatBtn = document.getElementById('createChatBtn');
const newChatTitle = document.getElementById('newChatTitle');
const chatList = document.getElementById('chatList');

function setupChatItemListeners() {
  const chatItems = document.querySelectorAll('.chat-item');
  
  chatItems.forEach(item => {
    item.addEventListener('click', function() {
      chatItems.forEach(i => i.classList.remove('active'));
      
      this.classList.add('active');
      
      const chatId = this.dataset.chatId || 'default';
      
      window.chatApp.setActiveChatId(chatId);
      
      window.chatApp.loadChatMessages(chatId);
    });
  });
}

newChatBtn.addEventListener('click', function() {
  newchatid.style.display = 'block';
  newChatTitle.value = '';
  newChatTitle.focus();
});

cancelBtn.addEventListener('click', function() {
  newchatid.style.display = 'none';
});

createChatBtn.addEventListener('click', createNewChat);

newChatTitle.addEventListener('keyup', function(event) {
  if (event.key === 'Enter') {
    createNewChat();
  }
});

window.addEventListener('click', function(event) {
  if (event.target === newchatid) {
    newchatid.style.display = 'none';
  }
});

function createNewChat() {
  const title = newChatTitle.value.trim();
  if (title) {
    const chatId = 'chat_' + Date.now();
    
    const newChat = document.createElement('div');
    newChat.className = 'chat-item';
    newChat.dataset.chatId = chatId;
    newChat.innerHTML = `
      <div class="chat-icon"><i class="fas fa-comments"></i></div>
      <div class="chat-content">
        <div class="chat-title">${title}</div>
      </div>
    `;
    
    window.chatApp.chatData[chatId] = [];
    
    chatList.insertBefore(newChat, chatList.firstChild);
    document.querySelectorAll('.chat-item').forEach(i => i.classList.remove('active'));
    newChat.classList.add('active');
    
    window.chatApp.setActiveChatId(chatId);
    
    window.chatApp.loadChatMessages(chatId);
    
    newchatid.style.display = 'none';
    
    setupChatItemListeners();
  } else {
    alert('Please enter a chat title');
  }
}

document.addEventListener('DOMContentLoaded', function() {
  setupChatItemListeners();
});