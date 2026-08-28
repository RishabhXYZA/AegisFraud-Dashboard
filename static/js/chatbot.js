**
 * AegisFraud Analytics - Virtual Avatar Chatbot
 * Manages phone-ratio drawer, prompt suggestion chips, and AI conversation.
 */

document.addEventListener("DOMContentLoaded", function () {
    const toggleBtn = document.getElementById("avatarChatToggle");
    const chatWindow = document.getElementById("avatarChatWindow");
    const closeBtn = document.getElementById("closeChatBtn");
    const chatForm = document.getElementById("chatForm");
    const chatInput = document.getElementById("chatInput");
    const chatMessages = document.getElementById("chatMessages");
    const promptChips = document.querySelectorAll(".prompt-chip");

    if (toggleBtn && chatWindow) {
        toggleBtn.addEventListener("click", () => {
            chatWindow.classList.toggle("open");
            if (chatWindow.classList.contains("open")) {
                chatInput.focus();
            }
        });
    }

    if (closeBtn && chatWindow) {
        closeBtn.addEventListener("click", () => {
            chatWindow.classList.remove("open");
        });
    }

    // Quick prompt suggestion chips
    promptChips.forEach(chip => {
        chip.addEventListener("click", function () {
            const prompt = this.getAttribute("data-prompt");
            if (prompt) {
                chatInput.value = prompt;
                sendMessage(prompt);
            }
        });
    });

    if (chatForm) {
        chatForm.addEventListener("submit", function (e) {
            e.preventDefault();
            const message = chatInput.value.trim();
            if (!message) return;
            sendMessage(message);
        });
    }

    async function sendMessage(text) {
        appendMessage("user", text);
        chatInput.value = "";

        // Typing indicator
        const typingId = "typing_" + Date.now();
        appendTypingIndicator(typingId);

        try {
            const res = await fetch("/api/chat", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ message: text })
            });
            const json = await res.json();
            removeTypingIndicator(typingId);

            if (json.success && json.reply) {
                appendMessage("bot", json.reply);
            } else {
                appendMessage("bot", "⚠️ " + (json.reply || "Unable to generate response."));
            }
        } catch (err) {
            removeTypingIndicator(typingId);
            appendMessage("bot", `❌ Error connecting to AI Avatar: ${err.message}`);
        }
    }

    function appendMessage(sender, content) {
        const bubble = document.createElement("div");
        bubble.className = `message-bubble ${sender}-bubble`;

        const contentDiv = document.createElement("div");
        contentDiv.className = "message-content";

        if (sender === "bot" && typeof marked !== "undefined") {
            contentDiv.innerHTML = marked.parse(content);
        } else {
            contentDiv.textContent = content;
        }

        bubble.appendChild(contentDiv);
        chatMessages.appendChild(bubble);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    function appendTypingIndicator(id) {
        const bubble = document.createElement("div");
        bubble.className = "message-bubble bot-bubble";
        bubble.id = id;
        bubble.innerHTML = `
            <div class="d-flex align-items-center gap-1 py-1">
                <span class="spinner-grow spinner-grow-sm text-primary" style="width: 0.5rem; height: 0.5rem;"></span>
                <span class="spinner-grow spinner-grow-sm text-info" style="width: 0.5rem; height: 0.5rem;"></span>
                <span class="spinner-grow spinner-grow-sm text-secondary" style="width: 0.5rem; height: 0.5rem;"></span>
            </div>
        `;
        chatMessages.appendChild(bubble);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    function removeTypingIndicator(id) {
        const el = document.getElementById(id);
        if (el) el.remove();
    }
});
