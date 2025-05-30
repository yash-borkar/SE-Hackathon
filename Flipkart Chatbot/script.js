<script>
  const header = document.getElementById('chatbot-header');
  const body = document.getElementById('chatbot-body');
  const sendBtn = document.getElementById('send-btn');
  const chatInput = document.getElementById('chat-input');
  const chatMessages = document.getElementById('chat-messages');

  header.addEventListener('click', () => {
    body.style.display = body.style.display === 'flex' ? 'none' : 'flex';
  });

  sendBtn.addEventListener('click', sendMessage);
  chatInput.addEventListener('keypress', function (e) {
    if (e.key === 'Enter') sendMessage();
  });

  function sendMessage() {
    const msg = chatInput.value.trim();
    if (!msg) return;

    const userMsg = document.createElement('div');
    userMsg.textContent = "You: " + msg;
    chatMessages.appendChild(userMsg);

    const botMsg = document.createElement('div');
    botMsg.textContent = "Bot: Sorry, I'm just a demo!";
    chatMessages.appendChild(botMsg);

    chatMessages.scrollTop = chatMessages.scrollHeight;
    chatInput.value = '';
  }
</script>
