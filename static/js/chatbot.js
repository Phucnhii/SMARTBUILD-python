document.addEventListener('DOMContentLoaded', function() {
  const chatbotIcon = document.getElementById('chatbot-icon');
  const chatbotPopup = document.getElementById('chatbot-popup');
  const chatbotClose = document.getElementById('chatbot-close');
  const chatbotForm = document.getElementById('chatbot-form');
  const chatbotInput = document.getElementById('chatbot-input');
  const chatbotMessages = document.getElementById('chatbot-messages');

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

      const userMsg = chatbotInput.value.trim();
      if (!userMsg) return;

      appendMessage('Bạn', userMsg);
      chatbotInput.value = '';
      
      // Hiển thị loading
      const loadingDiv = document.createElement('div');
      loadingDiv.classList.add('chat-message', 'ai-message');
      loadingDiv.innerHTML = `
        <img src="/static/img/robot.png" class="avatar">
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
      <div class="message-text">${text}</div>
    `;
    // Nếu muốn avatar user, thêm dòng dưới và css .avatar-user
    msgDiv.innerHTML = `<img src="/static/img/ava-user.jpeg" class="avatar-user"><div class="message-text">${text}</div>`;
  }

  const chatbotMessages = document.getElementById('chatbot-messages');
  chatbotMessages.appendChild(msgDiv);
  chatbotMessages.scrollTop = chatbotMessages.scrollHeight;
}

  }
});
