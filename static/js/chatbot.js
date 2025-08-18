document.addEventListener('DOMContentLoaded', function () {
  const chatbotIcon = document.getElementById('chatbot-icon');
  const chatbotPopup = document.getElementById('chatbot-popup');
  const chatbotClose = document.getElementById('chatbot-close');
  const chatbotForm = document.getElementById('chatbot-form');
  const chatbotInput = document.getElementById('chatbot-input');
  const chatbotMessages = document.getElementById('chatbot-messages');
  const newChatBtn = document.getElementById('new-chat-btn');


  let canChat = false; // Ràng buộc ban đầu: chưa được phép chat
  chatbotInput.disabled = true; //  Khóa ô nhập lúc đầu

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
  //  Hàm lưu history với timestamp và session tracking
  function saveChatHistory() {
    const chatData = {
      content: chatbotMessages.innerHTML,
      timestamp: Date.now(),
      sessionId: getOrCreateSessionId(),
      page: window.location.pathname
    };
    localStorage.setItem('smartbuild_chatHistory', JSON.stringify(chatData));
  }

  // Tạo session ID duy nhất cho phiên chatbot
  function getOrCreateSessionId() {
    let sessionId = localStorage.getItem('smartbuild_sessionId');
    if (!sessionId) {
      sessionId = 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
      localStorage.setItem('smartbuild_sessionId', sessionId);
    }
    return sessionId;
  }

  // Check history khi load trang với cải thiện
  const savedHistoryData = localStorage.getItem('smartbuild_chatHistory');
  let savedHistory = null;
  if (savedHistoryData) {
    try {
      const historyObj = JSON.parse(savedHistoryData);
      // Kiểm tra nếu lịch sử còn hiệu lực (trong vòng 24 giờ)
      const isValidHistory = historyObj &&
        historyObj.timestamp &&
        (Date.now() - historyObj.timestamp) < 24 * 60 * 60 * 1000;
      if (isValidHistory) {
        savedHistory = historyObj.content;
      } else {
        // Xóa lịch sử cũ nếu quá hạn
        localStorage.removeItem('smartbuild_chatHistory');
      }
    } catch (e) {
      console.log('Lỗi đọc lịch sử chat:', e);
      localStorage.removeItem('smartbuild_chatHistory');
    }
  }
  if (savedHistory) {
    const reconnectDiv = document.getElementById('reconnect-confirm');
    reconnectDiv.style.display = 'block';
    document.getElementById('reconnect-yes').addEventListener('click', function () {
      chatbotMessages.innerHTML = savedHistory;
      chatbotMessages.scrollTop = chatbotMessages.scrollHeight;
      reconnectDiv.style.display = 'none';
      canChat = true;
      chatbotInput.disabled = false;
    });

    document.getElementById('reconnect-no').addEventListener('click', function () {
      localStorage.removeItem('smartbuild_chatHistory');
      reconnectDiv.style.display = 'none';
      appendMessage('AI', 'Xin chào! Tôi có thể hỗ trợ gì cho bạn hôm nay?');
      canChat = true; // Cho phép chat
      chatbotInput.disabled = false;
    });
  } else {
    appendMessage('AI', 'Xin chào! Tôi có thể hỗ trợ gì cho bạn hôm nay?');
    canChat = true;
    chatbotInput.disabled = false;
  }


  if (chatbotIcon && chatbotPopup && chatbotClose) {
    // Hiện popup khi bấm icon
    chatbotIcon.addEventListener('click', function () {
      chatbotPopup.style.display = 'block';
      if (chatbotMessages.children.length === 0) {
        appendMessage('AI', 'Xin chào! Tôi có thể hỗ trợ gì cho bạn hôm nay?');
      }
    });

    // Đóng popup
    chatbotClose.addEventListener('click', function () {
      chatbotPopup.style.display = 'none';
    });
  }

  if (chatbotForm && chatbotInput && chatbotMessages) {
    chatbotForm.addEventListener('submit', async function (e) {
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
    newChatBtn.addEventListener('click', function () {
        const reconnectDiv = document.getElementById('reconnect-confirm');
  if (reconnectDiv && reconnectDiv.style.display === 'block') {
    // Nếu popup reconnect đang hiển thị thì không cho mở new chat confirm
    return;
  }
      document.getElementById('new-chat-confirm').style.display = 'block';
      chatbotInput.disabled = true;
      canChat = false;
    });

    document.getElementById('confirm-new-chat-yes').addEventListener('click', function () {
      chatbotMessages.innerHTML = '';
      localStorage.removeItem('smartbuild_chatHistory');
      localStorage.removeItem('smartbuild_sessionId'); // Reset session
      appendMessage('AI', 'Xin chào! Tôi có thể hỗ trợ gì cho bạn hôm nay?');
      document.getElementById('new-chat-confirm').style.display = 'none';
      canChat = true;
      chatbotInput.disabled = false;
    });

    document.getElementById('confirm-new-chat-no').addEventListener('click', function () {
      document.getElementById('new-chat-confirm').style.display = 'none';
      canChat = true;
      chatbotInput.disabled = false;
    });
  }

  // Lưu lịch sử khi người dùng rời khỏi trang
  window.addEventListener('beforeunload', function () {
    if (chatbotMessages && chatbotMessages.innerHTML.trim()) {
      saveChatHistory();
    }
  });

  // Lưu lịch sử định kỳ mỗi 10 giây nếu có hoạt động chat
  setInterval(function () {
    if (chatbotMessages && chatbotMessages.children.length > 1) { // Có ít nhất 1 tin nhắn ngoài tin chào
      saveChatHistory();
    }
  }, 10000); // 10 giây
});