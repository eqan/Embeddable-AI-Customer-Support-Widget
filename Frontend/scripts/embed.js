// Insert full embed script implementing chatbot injection and logic
(function () {
  // -------------------------------
  // 1. Styles (CSS)
  // -------------------------------
  // Read color config from script tag if present
  let userColors = {};
  try {
    // Find the script tag that loaded this file
    let scriptTag = document.currentScript;
    if (!scriptTag) {
      // Fallback for browsers that don't support document.currentScript
      const scripts = document.querySelectorAll('script[src]');
      scriptTag = Array.from(scripts).find(s => s.src && s.src.includes('embed.js'));
    }
    if (scriptTag && scriptTag.dataset.colors) {
      userColors = JSON.parse(scriptTag.dataset.colors);
    } else if (window.ChatbotWidgetConfig?.colors) {
      userColors = window.ChatbotWidgetConfig.colors;
    }
  } catch (e) {
    console.warn('Invalid data-colors JSON for chatbot:', e);
  }

  const defaultColors = {
    primary: "#5350c4",
    primaryDark: "#3d39ac",
    accent: "#ccccf5"
  };
  const colors = { ...defaultColors, ...userColors };

  const css = `@import url("https://fonts.googleapis.com/css2?family=Inter:opsz,wght@14..32,100..900&display=swap");

* {
  margin: 0;
  padding: 0;
  font-family: "Inter", sans-serif;
  box-sizing: border-box;
}

#chatbot-toggler {
  position: fixed;
  bottom: 30px;
  right: 35px;
  height: 50px;
  width: 50px;
  border: none;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  border-radius: 50%;
  background: ${colors.primary};
  transition: all 0.2s ease;
}

body.show-chatbot #chatbot-toggler {
  transform: rotate(90deg);
}

#chatbot-toggler span {
  color: #fff;
  position: absolute;
}

body.show-chatbot #chatbot-toggler span:first-child, #chatbot-toggler span:last-child{
  opacity: 0;
}

body.show-chatbot #chatbot-toggler span:last-child{
  opacity: 1;
}

.chatbot-popup {
  position: fixed;
  right: 25px;
  bottom: 90px;
  width: 420px;
  background: #fff;
  overflow: hidden;
  border-radius: 15px;
  opacity: 0;
  transform: scale(0.2);
  transform-origin: bottom right;
  pointer-events: none;
  box-shadow: 0 0 128px rgba(0, 0, 0, 0.1), 0 32px 64px -48px rgba(0, 0, 0, 0.5);
  transition: all 0.1s ease;
}

body.show-chatbot .chatbot-popup {
  opacity: 1;
  pointer-events: auto;
  transform: scale(1);
}

.chat-header {
  display: flex;
  align-items: center;
  background: ${colors.primary};
  padding: 15px 22px;
  justify-content: space-between;
}

.chat-header .header-info {
  display: flex;
  gap: 10px;
  align-items: center;
}

.header-info .chatbot-logo {
  height: 35px;
  width: 35px;
  padding: 6px;
  fill: ${colors.primary};
  flex-shrink: 0;
  background: #fff;
  border-radius: 50%;
}

.header-info .logo-text {
  color: #fff;
  font-size: 1.31rem;
  font-weight: 600;
}

.chat-header #close-chatbot {
  border: none;
  color: #fff;
  height: 40px;
  width: 40px;
  font-size: 1.9rem;
  margin-right: -10px;
  padding-top: 2px;
  cursor: pointer;
  border-radius: 50%;
  background: none;
  transition: 0.2s ease;
}

.chat-header #close-chatbot:hover {
  background: ${colors.primaryDark};
}

.chat-body {
  padding: 25px 22px;
  display: flex;
  gap: 20px;
  height: 460px;
  margin-bottom: 82px;
  overflow-y: auto;
  flex-direction: column;
  scrollbar-width: thin;
  scrollbar-color: ${colors.accent} transparent;
}

.chat-body .message {
  display: flex;
  gap: 11px;
  align-items: center;
}

.chat-body .bot-message .bot-avatar {
  height: 35px;
  width: 35px;
  padding: 6px;
  fill: #fff;
  flex-shrink: 0;
  margin-bottom: 2px;
  align-self: flex-end;
  background: ${colors.primary};
  border-radius: 50%;
}

.chat-body .user-message {
  flex-direction: column;
  align-items: flex-end;
}

.chat-body .message .message-text {
  padding: 12px 16px;
  max-width: 75%;
  font-size: 0.95rem;
  background: #f2f2ff;
}

.chat-body .bot-message.thinking .message-text {
  padding: 2px 16px;
}

.chat-body .bot-message .message-text {
  background-color: #f2f2ff;
  border-radius: 13px 13px 13px 3px;
}

.chat-body .user-message .message-text {
  color: #fff;
  background-color: ${colors.primary};
  border-radius: 13px 13px 3px 13px;
}

.chat-body .bot-message .thinking-indicator {
  display: flex;
  gap: 4px;
  padding-block: 15px;
}

.chat-body .bot-message .thinking-indicator .dot:nth-child(1) {
  animation-delay: 0.2s;
}

.chat-body .bot-message .thinking-indicator .dot:nth-child(2) {
  animation-delay: 0.3s;
}

.chat-body .bot-message .thinking-indicator .dot:nth-child(3) {
  animation-delay: 0.4s;
}

.chat-body .bot-message .thinking-indicator .dot {
  height: 7px;
  width: 7px;
  opacity: 0.7;
  border-radius: 50%;
  background: ${colors.accent};
  animation: dotPulse 1.8s ease-in-out infinite;
}

@keyframes dotPulse {
  0%,
  44% {
    transform: translateY(0);
  }

  28% {
    opacity: 0.4;
    transform: translateY(-4px);
  }

  44% {
    opacity: 0.2;
  }
}

.chat-footer {
  position: absolute;
  bottom: 0;
  width: 100%;
  background: white;
  padding: 15px 22px 20px;
}

.chat-footer .chat-form {
  display: flex;
  align-items: center;
  background: white;
  border-radius: 32px;
  outline: 1px solid ${colors.accent};
}

.chat-footer .chat-form:focus-within {
  outline: 2px solid ${colors.primary};
}

.chat-form .message-input {
  border: none;
  outline: none;
  height: 47px;
  width: 100%;
  resize: none;
  max-height: 180px;
  white-space: pre-line;
  font-size: 1rem;
  padding: 13px;
  border-radius: inherit;
  scrollbar-width: thin;
  scrollbar-color: transparent transparent;
}

.chat-form .message-input::hover {
  scrollbar-color: ${colors.accent} transparent;
}

.chat-form .chat-controls {
  display: flex;
  height: 47px;
  gap: 3px;
  align-items: center;
  align-self: flex-end;
  padding-right: 6px;
}

.chat-form .chat-controls button {
  height: 35px;
  width: 35px;
  border: none;
  font-size: 1.15rem;
  cursor: pointer;
  color: #706db0;
  background: none;
  border-radius: 50%;
  transition: 0.2s ease;
}

.chat-form .chat-controls #send-message {
  color: #fff;
  display: none;
  background: ${colors.primary};
}

.chat-form .message-input:valid ~ .chat-controls #send-message {
  display: block;
}

.chat-form .chat-controls #send-message:hover {
  background: ${colors.primaryDark};
}

.chat-form .chat-controls button:hover {
  background: #f1f1f1;
}

.chat-body .user-message .attachment {
  width: 50%;
  margin-top: -7px;
  border-radius: 13px 3px 13px 3px;
}

/* Support ticket form */
.support-form-wrapper {
  width: 100%;
}
.support-form {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-top: 10px;
}
.support-form label {
  font-size: 0.9rem;
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.support-form input,
.support-form textarea,
.support-form select {
  padding: 10px;
  border: 1px solid #ccc;
  border-radius: 6px;
  font-size: 0.95rem;
  font-family: "Inter", sans-serif;
}
.support-form button[type="submit"] {
  align-self: flex-start;
  background: ${colors.primary};
  color: #fff;
  border: none;
  padding: 10px 18px;
  border-radius: 6px;
  cursor: pointer;
  transition: background 0.2s;
}
.support-form button[type="submit"]:hover {
  background: ${colors.primaryDark};
}

em-emoji-picker {
  position: absolute;
  left: 50%;
  top: -337px;
  width: 100%;
  max-width: 350px;
  max-height: 330px;
  visibility: hidden;
  transform: translateX(-50%);
}

 body.show-emoji-picker em-emoji-picker {
  visibility: visible;
 }
/* Responsive for mobile screen */
@media screen and (max-width: 600px) {
  .chatbot-popup {
    width: 100%;
    right: 0;
    bottom: 0;
    border-radius: 0;
    height: 100%;
  }

  .chat-header .header-info .logo-text {
    font-size: 1.1rem;
  }

  .chat-body {
    height: 100%;
    margin-bottom: 0;
  }

  .chat-body .message .message-text {
    max-width: 85%;
  }

  .chat-footer .chat-form {
    border-radius: 0;
    border-radius: 25px;
  }

  .chat-footer .chat-form .message-input {
    border-radius: 0;
  }

  .chat-footer .chat-form .chat-controls {
    padding-right: 10px;
  }

  .chat-footer .chat-form .chat-controls button {
    height: 40px;
    width: 40px;
  }
}

/* Auth overlay */
.chatbot-auth-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 100000;
}
.chatbot-auth-overlay .auth-modal {
  background: #ffffff;
  padding: 30px 35px;
  border-radius: 8px;
  text-align: center;
  box-shadow: 0 2px 8px rgba(0,0,0,0.15);
}
.chatbot-auth-overlay .auth-modal h3 {
  margin-bottom: 25px;
  font-size: 1.15rem;
  color: #333;
}
`;

  // -------------------------------
  // 2. HTML Markup
  // -------------------------------
  const markup = `
    <button id="chatbot-toggler">
      <span class="material-symbols-outlined">mode_comment</span>
      <span class="material-symbols-rounded">close</span>
    </button>

    <div class="chatbot-popup">
      <div class="chat-header">
        <div class="header-info">
          <svg class="chatbot-logo" xmlns="http://www.w3.org/2000/svg" width="50" height="50" viewBox="0 0 1024 1024"><path d="M738.3 287.6H285.7c-59 0-106.8 47.8-106.8 106.8v303.1c0 59 47.8 106.8 106.8 106.8h81.5v111.1c0 .7.8 1.1 1.4.7l166.9-110.6 41.8-.8h117.4l43.6-.4c59 0 106.8-47.8 106.8-106.8V394.5c0-59-47.8-106.9-106.8-106.9zM351.7 448.2c0-29.5 23.9-53.5 53.5-53.5s53.5 23.9 53.5 53.5-23.9 53.5-53.5 53.5-53.5-23.9-53.5-53.5zm157.9 267.1c-67.8 0-123.8-47.5-132.3-109h264.6c-8.6 61.5-64.5 109-132.3 109zm110-213.7c-29.5 0-53.5-23.9-53.5-53.5s23.9-53.5 53.5-53.5 53.5 23.9 53.5 53.5-23.9 53.5-53.5 53.5zM867.2 644.5V453.1h26.5c19.4 0 35.1 15.7 35.1 35.1v121.1c0 19.4-15.7 35.1-35.1 35.1h-26.5zM95.2 609.4V488.2c0-19.4 15.7-35.1 35.1-35.1h26.5v191.3h-26.5c-19.4 0-35.1-15.7-35.1-35.1zM561.5 149.6c0 23.4-15.6 43.3-36.9 49.7v44.9h-30v-44.9c-21.4-6.5-36.9-26.3-36.9-49.7 0-28.6 23.3-51.9 51.9-51.9s51.9 23.3 51.9 51.9z"></path></svg>
          <h2 class="logo-text">${window.ChatbotWidgetConfig.title || 'Chatbot'}</h2>
        </div>
        <button id="close-chatbot" class="material-symbols-rounded">keyboard_arrow_down</button>
      </div>
      <div class="chat-body">
        <div class="message bot-message">
          <svg class="bot-avatar" xmlns="http://www.w3.org/2000/svg" width="50" height="50" viewBox="0 0 1024 1024"><path d="M738.3 287.6H285.7c-59 0-106.8 47.8-106.8 106.8v303.1c0 59 47.8 106.8 106.8 106.8h81.5v111.1c0 .7.8 1.1 1.4.7l166.9-110.6 41.8-.8h117.4l43.6-.4c59 0 106.8-47.8 106.8-106.8V394.5c0-59-47.8-106.9-106.8-106.9zM351.7 448.2c0-29.5 23.9-53.5 53.5-53.5s53.5 23.9 53.5 53.5-23.9 53.5-53.5 53.5-53.5-23.9-53.5-53.5zm157.9 267.1c-67.8 0-123.8-47.5-132.3-109h264.6c-8.6 61.5-64.5 109-132.3 109zm110-213.7c-29.5 0-53.5-23.9-53.5-53.5s23.9-53.5 53.5-53.5 53.5 23.9 53.5 53.5-23.9 53.5-53.5 53.5zM867.2 644.5V453.1h26.5c19.4 0 35.1 15.7 35.1 35.1v121.1c0 19.4-15.7 35.1-35.1 35.1h-26.5zM95.2 609.4V488.2c0-19.4 15.7-35.1 35.1-35.1h26.5v191.3h-26.5c-19.4 0-35.1-15.7-35.1-35.1zM561.5 149.6c0 23.4-15.6 43.3-36.9 49.7v44.9h-30v-44.9c-21.4-6.5-36.9-26.3-36.9-49.7 0-28.6 23.3-51.9 51.9-51.9s51.9 23.3 51.9 51.9z"></path></svg>
          <div class="message-text">Hey there 👋 <br/>How can i help you today?</div>
        </div>
      </div>
      <div class="chat-footer">
        <form action="#" class="chat-form">
          <textarea placeholder="Message..." class="message-input" required></textarea>
          <div class="chat-controls">
            <button type="button" id="emoji-picker" class="material-symbols-rounded">sentiment_satisfied</button>
            <button type="submit" id="send-message" class="material-symbols-rounded">arrow_upward</button>
          </div>
        </form>
      </div>
    </div>`;

  // -------------------------------
  // 3. Helper injection functions
  // -------------------------------
  function injectStyle() {
    if (document.getElementById("embedded-chatbot-style")) return;
    const style = document.createElement("style");
    style.id = "embedded-chatbot-style";
    style.textContent = css;
    document.head.appendChild(style);
  }

  function injectFontLinks() {
    if (!document.getElementById("material-symbol-font")) {
      const link = document.createElement("link");
      link.id = "material-symbol-font";
      link.rel = "stylesheet";
      link.href = "https://fonts.googleapis.com/css2?family=Material+Symbols+Rounded:opsz,wght,FILL,GRAD@48,400,0,0&family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@48,400,1,0";
      document.head.appendChild(link);
    }
  }

  function injectMarkup() {
    if (document.getElementById("chatbot-toggler")) return; // Already injected
    const container = document.createElement("div");
    container.id = "embedded-chatbot-container";
    container.innerHTML = markup;
    document.body.appendChild(container);
  }

  function loadEmojiMart() {
    return new Promise((resolve) => {
      if (window.EmojiMart) return resolve();
      const script = document.createElement("script");
      script.src = "https://cdn.jsdelivr.net/npm/emoji-mart@latest/dist/browser.js";
      script.async = true;
      script.onload = () => resolve();
      document.head.appendChild(script);
    });
  }

  function loadMarkdownLib() {
    return new Promise(res => {
      if (window.marked) return res();
      const s = document.createElement('script');
      s.src = 'https://cdn.jsdelivr.net/npm/marked@15.0.12/lib/marked.umd.min.js';
      s.onload = res;
      document.head.appendChild(s);
    });
  }

  // EmailJS loader
  function loadEmailJS() {
    return new Promise(res => {
      if (window.emailjs) return res();
      const s = document.createElement('script');
      s.src = 'https://cdn.jsdelivr.net/npm/emailjs-com@3/dist/email.min.js';
      s.onload = () => {
        if (window.emailjs?.init) {
          const publicKey = window.ChatbotWidgetConfig?.emailJsUserId || 'YOUR_PUBLIC_KEY';
          window.emailjs.init(publicKey);
        }
        res();
      };
      document.head.appendChild(s);
    });
  }

  // Google Identity Services loader
  function loadGoogleAuth() {
    return new Promise(res => {
      if (window.google?.accounts?.id) return res();
      const s = document.createElement('script');
      s.src = 'https://accounts.google.com/gsi/client';
      s.onload = res;
      document.head.appendChild(s);
    });
  }

  // Ensure the user is authenticated before using the chatbot
  function ensureAuthenticated() {
    return new Promise(async (resolve) => {
      const stored = localStorage.getItem('chatbotAuthToken');
      if (stored) return resolve(stored);

      // Build overlay markup
      const overlay = document.createElement('div');
      overlay.className = 'chatbot-auth-overlay';
      overlay.innerHTML = `
        <div class="auth-modal">
          <h3>Sign in to continue</h3>
          <div id="g_id_signin"></div>
        </div>`;
      document.body.appendChild(overlay);

      const clientId = window.ChatbotWidgetConfig?.googleClientId || 'YOUR_GOOGLE_CLIENT_ID';
      const backendBase = window.ChatbotWidgetConfig?.backendBaseUrl || '';

      // Initialize Google identity
      window.google.accounts.id.initialize({
        client_id: clientId,
        callback: async (response) => {
          try {
            // Exchange credential with backend
            const res = await fetch(`${backendBase}/google-login`, {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ code: response.credential })
            });
            const data = await res.json();
            if (!res.ok) throw new Error(data.detail || data.message || 'Authentication failed');

            const token = data.token || data.result?.token;
            if (!token) throw new Error('Token missing in server response');

            localStorage.setItem('chatbotAuthToken', token);
            overlay.remove();
            resolve(token);
          } catch (err) {
            console.error(err);
            overlay.querySelector('h3').textContent = err.message || 'Login failed, please try again';
          }
        }
      });

      // Render the sign-in button
      window.google.accounts.id.renderButton(document.getElementById('g_id_signin'), {
        theme: 'outline',
        size: 'large'
      });

      window.google.accounts.id.prompt();
    });
  }

  // Helper: check stored JWT validity
  function getStoredToken() {
    const token = localStorage.getItem('chatbotAuthToken');
    if (!token) return null;
    try {
      const payloadBase64 = token.split('.')[1];
      const payload = JSON.parse(atob(payloadBase64));
      if (!payload.exp || payload.exp * 1000 < Date.now()) {
        localStorage.removeItem('chatbotAuthToken');
        return null;
      }
      return token;
    } catch (e) {
      localStorage.removeItem('chatbotAuthToken');
      return null;
    }
  }

  // -------------------------------
  // 4. Main chatbot logic
  // -------------------------------
  function initLogic() {
    const chatBody = document.querySelector(".chat-body");
    const messageInput = document.querySelector(".message-input");
    const sendMessageButton = document.querySelector("#send-message");
    const chatbotToggler = document.querySelector("#chatbot-toggler");
    const closeChatbot = document.querySelector("#close-chatbot");
    const chatForm = document.querySelector(".chat-form");

    // API setup
    const API_KEY = "AIzaSyAvtlgLMG9QaPKEsvBomeh84cooqKkst9I";
    const API_URL = `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=${API_KEY}`;

    const userData = {
      message: null,
      file: {
        data: null,
        mime_type: null,
      },
    };

    const chatHistory = [];
    const initialInputHeight = messageInput.scrollHeight;

    // Create message element
    const createMessageElement = (content, ...classes) => {
      const div = document.createElement("div");
      div.classList.add("message", ...classes);
      div.innerHTML = content;
      return div;
    };

    // Generate bot response using API
    const generateBotResponse = async (incomingMessageDiv) => {
      const messageElement = incomingMessageDiv.querySelector(".message-text");

      chatHistory.push({
        role: "user",
        parts: [
          { text: userData.message },
          ...(userData.file.data ? [{ inline_data: userData.file }] : []),
        ],
      });

      const requestOptions = {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          contents: chatHistory,
        }),
      };

      try {
        const response = await fetch(API_URL, requestOptions);
        const data = await response.json();
        if (!response.ok) throw new Error(data.error?.message || "Error");

        const apiResponseText = data.candidates[0].content.parts[0].text
          .replace(/\*\*(.*?)\*\*/g, "$1")
          .trim();

        if (apiResponseText.toLowerCase() === "calendly") {
          // Insert Calendly iframe JUST ABOVE this bot message so that it is not treated as a chat bubble
          const iframeWrapper = document.createElement("div");
          iframeWrapper.classList.add("calendly-embed-wrapper");
          iframeWrapper.innerHTML =
            '<iframe src="https://calendly.com/eqan-ahmad123/customer-agent" style="width: 100%; min-width: 400px; height: 600px; border:none;" frameborder="0"></iframe>';

          // Place iframe immediately before the incoming bot message element
          chatBody.insertBefore(iframeWrapper, incomingMessageDiv);

          // Update the bot message text to guide the user
          messageElement.textContent = "Select schedule from above";
        } else if (apiResponseText.toLowerCase() === "human-message") {
          // Show support ticket form
          const wrapper = document.createElement("div");
          wrapper.classList.add("support-form-wrapper");
          wrapper.innerHTML = `
            <form class="support-form" style="background-color: #f9f9f9; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);">
              <label style="display: block; margin-bottom: 10px;">Name*<input type="text" name="name" required style="width: 100%; padding: 8px; margin-top: 5px; border: 1px solid #ccc; border-radius: 4px;" /></label>
              <label style="display: block; margin-bottom: 10px;">Email*<input type="email" name="email" required style="width: 100%; padding: 8px; margin-top: 5px; border: 1px solid #ccc; border-radius: 4px;" /></label>
              <label style="display: block; margin-bottom: 10px;">Phone<input type="tel" name="phone" style="width: 100%; padding: 8px; margin-top: 5px; border: 1px solid #ccc; border-radius: 4px;" /></label>
              <label style="display: block; margin-bottom: 10px;">Message / Issue*<textarea name="message" rows="3" required style="width: 100%; padding: 8px; margin-top: 5px; border: 1px solid #ccc; border-radius: 4px;"></textarea></label>
              <label style="display: block; margin-bottom: 10px;">Priority<select name="priority" style="width: 100%; padding: 8px; margin-top: 5px; border: 1px solid #ccc; border-radius: 4px;">
                  <option value="Low">Low</option>
                  <option value="Medium" selected>Medium</option>
                  <option value="High">High</option>
                  <option value="Urgent">Urgent</option>
              </select></label>
              <button type="submit" style="background-color: ${colors.primary}; color: white; padding: 10px 15px; border: none; border-radius: 4px; cursor: pointer;">Submit</button>
            </form>`;

          // Insert form just above bot bubble
          chatBody.insertBefore(wrapper, incomingMessageDiv);
          messageElement.textContent = "Please fill out the form above to talk to a human agent.";

          const form = wrapper.querySelector(".support-form");
          form.addEventListener("submit", async (e) => {
            e.preventDefault();
            const fd = new FormData(form);
            const ticketId = "TICKET-" + Date.now().toString(36).toUpperCase();

            const payload = {
              name: fd.get("name"),
              email: fd.get("email"),
              phone: fd.get("phone") || "N/A",
              message: fd.get("message"),
              priority: fd.get("priority"),
              ticketId,
            };

            try {
              // Send email to support team
              await emailjs.send(
                window.ChatbotWidgetConfig?.emailJsServiceId || 'YOUR_SERVICE_ID',
                window.ChatbotWidgetConfig?.emailJsSupportTemplateId || 'SUPPORT_TEMPLATE_ID',
                payload
              );

              // Send auto-confirmation email to user
              await emailjs.send(
                window.ChatbotWidgetConfig?.emailJsServiceId || 'YOUR_SERVICE_ID',
                window.ChatbotWidgetConfig?.emailJsUserTemplateId || 'USER_CONFIRM_TEMPLATE_ID',
                payload
              );

              // Acknowledge in chat
              messageElement.textContent = `Thank you! Your ticket (${ticketId}) has been created. Our support team will reach out to you at ${payload.email}.`;
              wrapper.remove();
            } catch (err) {
              console.error(err);
              messageElement.textContent = "Failed to submit your request. Please try again later.";
              messageElement.style.color = "#ff0000";
            }
          });
        } else {
          messageElement.innerHTML = marked.parse(apiResponseText);
        }

        chatHistory.push({
          role: "model",
          parts: [{ text: apiResponseText }],
        });
      } catch (error) {
        console.error(error);
        messageElement.innerText = error.message || "Something went wrong";
        messageElement.style.color = "#ff0000";
      } finally {
        incomingMessageDiv.classList.remove("thinking");
        chatBody.scrollTo({ top: chatBody.scrollHeight, behavior: "smooth" });
      }
    };

    // Handle outgoing message
    const handleOutgoingMessage = (e) => {
      e.preventDefault();
      userData.message = messageInput.value.trim();
      if (!userData.message) return;
      messageInput.value = "";
      messageInput.dispatchEvent(new Event("input"));

      const messageContent = `<div class="message-text"></div>`;
      const outgoingMessageDiv = createMessageElement(messageContent, "user-message");
      outgoingMessageDiv.querySelector(".message-text").textContent = userData.message;
      chatBody.appendChild(outgoingMessageDiv);
      chatBody.scrollTo({ top: chatBody.scrollHeight, behavior: "smooth" });

      setTimeout(() => {
        const thinkingContent = `<svg class="bot-avatar" xmlns="http://www.w3.org/2000/svg" width="50" height="50" viewBox="0 0 1024 1024"><path d="M738.3 287.6H285.7c-59 0-106.8 47.8-106.8 106.8v303.1c0 59 47.8 106.8 106.8 106.8h81.5v111.1c0 .7.8 1.1 1.4.7l166.9-110.6 41.8-.8h117.4l43.6-.4c59 0 106.8-47.8 106.8-106.8V394.5c0-59-47.8-106.9-106.8-106.9zM351.7 448.2c0-29.5 23.9-53.5 53.5-53.5s53.5 23.9 53.5 53.5-23.9 53.5-53.5 53.5-53.5-23.9-53.5-53.5zm157.9 267.1c-67.8 0-123.8-47.5-132.3-109h264.6c-8.6 61.5-64.5 109-132.3 109zm110-213.7c-29.5 0-53.5-23.9-53.5-53.5s23.9-53.5 53.5-53.5 53.5 23.9 53.5 53.5-23.9 53.5-53.5 53.5zM867.2 644.5V453.1h26.5c19.4 0 35.1 15.7 35.1 35.1v121.1c0 19.4-15.7 35.1-35.1 35.1h-26.5zM95.2 609.4V488.2c0-19.4 15.7-35.1 35.1-35.1h26.5v191.3h-26.5c-19.4 0-35.1-15.7-35.1-35.1zM561.5 149.6c0 23.4-15.6 43.3-36.9 49.7v44.9h-30v-44.9c-21.4-6.5-36.9-26.3-36.9-49.7 0-28.6 23.3-51.9 51.9-51.9s51.9 23.3 51.9 51.9z"></path></svg><div class="message-text"><div class="thinking-indicator"><div class="dot"></div><div class="dot"></div><div class="dot"></div></div></div>`;
        const incomingMessageDiv = createMessageElement(thinkingContent, "bot-message", "thinking");
        chatBody.appendChild(incomingMessageDiv);
        chatBody.scrollTo({ top: chatBody.scrollHeight, behavior: "smooth" });
        generateBotResponse(incomingMessageDiv);
      }, 600);
    };

    // Listeners
    messageInput.addEventListener("keydown", (e) => {
      const userMessage = e.target.value.trim();
      if (e.key === "Enter" && userMessage && !e.shiftKey && window.innerWidth > 768) {
        handleOutgoingMessage(e);
      }
    });

    messageInput.addEventListener("input", () => {
      messageInput.style.height = `${initialInputHeight}px`;
      messageInput.style.height = `${messageInput.scrollHeight}px`;
      chatForm.style.borderRadius = messageInput.scrollHeight > initialInputHeight ? "15px" : "32px";
    });

    chatForm.addEventListener("submit", handleOutgoingMessage);
    sendMessageButton.addEventListener("click", handleOutgoingMessage);

    chatbotToggler.addEventListener("click", async () => {
      if (!getStoredToken()) {
        await loadGoogleAuth();
        const token = await ensureAuthenticated();
        if (!token) return; // user cancelled or failed
      }
      document.body.classList.toggle("show-chatbot");
    });

    closeChatbot.addEventListener("click", () => {
      document.body.classList.remove("show-chatbot");
    });

    // Emoji picker
    const picker = new EmojiMart.Picker({
      theme: "light",
      skinTonePosition: "none",
      preview: "none",
      onEmojiSelect: (emoji) => {
        const { selectionStart: start, selectionEnd: end } = messageInput;
        messageInput.setRangeText(emoji.native, start, end, "end");
        messageInput.focus();
      },
      onClickOutside: (e) => {
        if (e.target.id === "emoji-picker") {
          document.body.classList.toggle("show-emoji-picker");
        } else {
          document.body.classList.remove("show-emoji-picker");
        }
      },
    });

    document.querySelector(".chat-form").appendChild(picker);
  }

  // -------------------------------
  // 5. Bootstrap sequence
  // -------------------------------
  async function bootstrap() {
    injectStyle();
    injectFontLinks();
    injectMarkup();
    // Load core libraries (Google auth will be loaded on demand)
    await Promise.all([loadEmojiMart(), loadMarkdownLib(), loadEmailJS()]);
    initLogic();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", bootstrap);
  } else {
    bootstrap();
  }
})();