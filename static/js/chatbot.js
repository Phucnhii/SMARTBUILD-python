document.addEventListener('DOMContentLoaded', function() {
  const chatbotIcon = document.getElementById('chatbot-icon');
  const chatbotPopup = document.getElementById('chatbot-popup');
  const chatbotClose = document.getElementById('chatbot-close');
  const chatbotForm = document.getElementById('chatbot-form');
  const chatbotInput = document.getElementById('chatbot-input');
  const chatbotMessages = document.getElementById('chatbot-messages');
  const newChatBtn = document.getElementById('new-chat-btn');

  
  let canChat = false; // ✅ Ràng buộc ban đầu: chưa được phép chat
  chatbotInput.disabled = true; // ✅ Khóa ô nhập lúc đầu

   function appendMessage(sender, text) {
      const msgDiv = document.createElement('div');
      msgDiv.classList.add('chat-message');

      if (sender === 'AI') {
        msgDiv.classList.add('ai-message');
        msgDiv.innerHTML = `
          <img src="/static/img/ava-robot.png" class="avatar">
          <div class="message-text">${text}</div>
        `;
      } else {
        msgDiv.classList.add('user-message');
        msgDiv.innerHTML = `
          <img src="/static/img/ava-user.jpeg" class="avatar-user">
          <div class="message-text">${text}</div>
        `;
      }

      chatbotMessages.appendChild(msgDiv);
      chatbotMessages.scrollTop = chatbotMessages.scrollHeight;

      saveChatHistory(); // Lưu mỗi khi append message
    }
      //  Hàm lưu history
    function saveChatHistory() {
      localStorage.setItem('chatHistory', chatbotMessages.innerHTML);
    }
  // Check history khi load trang
const savedHistory = localStorage.getItem('chatHistory');
if (savedHistory) {
  const reconnectDiv = document.getElementById('reconnect-confirm');
  reconnectDiv.style.display = 'block';
  document.getElementById('reconnect-yes').addEventListener('click', function() {
    chatbotMessages.innerHTML = savedHistory;
    chatbotMessages.scrollTop = chatbotMessages.scrollHeight;
    reconnectDiv.style.display = 'none';
    canChat = true;
    chatbotInput.disabled = false; 
  });

  document.getElementById('reconnect-no').addEventListener('click', function() {
    localStorage.removeItem('chatHistory');
    reconnectDiv.style.display = 'none';
    appendMessage('AI', 'Xin chào! Tôi có thể hỗ trợ gì cho bạn hôm nay?');
    canChat = true; // ✅ Cho phép chat
    chatbotInput.disabled = false;
  });
} else {
  appendMessage('AI', 'Xin chào! Tôi có thể hỗ trợ gì cho bạn hôm nay?');
  canChat = true;
  chatbotInput.disabled = false;
}


  if (chatbotIcon && chatbotPopup && chatbotClose) {
    // Hiện popup khi bấm icon
    chatbotIcon.addEventListener('click', function() {
      chatbotPopup.style.display = 'block';
      if (chatbotMessages.children.length === 0) {
        appendMessage('AI', 'Xin chào! Tôi có thể hỗ trợ gì cho bạn hôm nay?');
      }
    });

    // Đóng popup
    chatbotClose.addEventListener('click', function() {
      chatbotPopup.style.display = 'none';
    });
  }

  if (chatbotForm && chatbotInput && chatbotMessages) {
    chatbotForm.addEventListener('submit', async function(e) {
      e.preventDefault(); // Ngăn reload trang
      
      if (!canChat) {
        alert('Vui lòng chọn "Tiếp tục" hoặc "Bắt đầu mới" trước khi trò chuyện.');
        return;
      }
      const userMsg = chatbotInput.value.trim();
      if (!userMsg) return;

      appendMessage('Bạn', userMsg);
      chatbotInput.value = '';
      
      // Hiển thị loading
      const loadingDiv = document.createElement('div');
      loadingDiv.classList.add('chat-message', 'ai-message');
      loadingDiv.innerHTML = `
        <img src="/static/img/ava-robot.png" class="avatar">
        <div class="message-text">
          <div class="typing">
            <span></span>
            <span></span>
            <span></span>
          </div>
        </div>
      `;
      chatbotMessages.appendChild(loadingDiv);
      chatbotMessages.scrollTop = chatbotMessages.scrollHeight;

      try {
        const res = await fetch('/api/chatbot', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ message: userMsg })
        });

        const data = await res.json();
        if (data.error) throw new Error(data.error);
        // Xóa loading div
        chatbotMessages.removeChild(loadingDiv);
        appendMessage('AI', data.response);
      } catch (err) {
        appendMessage('AI', 'Lỗi: ' + err.message);
      }
    });

   

  
  }

  //  Nút New Chat xóa history
  if (newChatBtn) {
  newChatBtn.addEventListener('click', function() {
    document.getElementById('new-chat-confirm').style.display = 'block';
        chatbotInput.disabled = true;
    canChat = false;
  });

  document.getElementById('confirm-new-chat-yes').addEventListener('click', function() {
    chatbotMessages.innerHTML = '';
    localStorage.removeItem('chatHistory');
    appendMessage('AI', 'Xin chào! Tôi có thể hỗ trợ gì cho bạn hôm nay?');
    document.getElementById('new-chat-confirm').style.display = 'none';
    canChat = true;
    chatbotInput.disabled = false;
  });

  document.getElementById('confirm-new-chat-no').addEventListener('click', function() {
    document.getElementById('new-chat-confirm').style.display = 'none';
    canChat = true;
    chatbotInput.disabled = false;
  });
}
});
