/* ==========================================================================
   Diko Messenger & Data Center - Client Application Script
   ========================================================================== */

document.addEventListener('DOMContentLoaded', () => {
    initPostSystem();
    initChatSystem();
});

/* --- 1. Система публикации постов --- */
function initPostSystem() {
    const postInput = document.getElementById('postInput');
    const publishBtn = document.getElementById('publishBtn');
    const postsContainer = document.getElementById('postsContainer');

    if (!publishBtn || !postInput || !postsContainer) return;

    publishBtn.addEventListener('click', async () => {
        const content = postInput.value.trim();
        if (content === "") {
            alert('Поле поста не может быть пустым!');
            return;
        }

        try {
            const response = await fetch('/api/posts', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ content: content })
            });

            const result = await response.json();

            if (response.ok) {
                appendPostToDOM({
                    author: "nexustorvard",
                    content: content,
                    category: "Специализированный пост"
                }, postsContainer);
                postInput.value = '';
            } else {
                alert(result.error || 'Ошибка при сохранении поста');
            }
        } catch (error) {
            console.error('Ошибка публикации поста:', error);
        }
    });
}

function appendPostToDOM(post, container) {
    const postCard = document.createElement('div');
    postCard.className = 'card post-card';
    
    const currentDate = new Date().toLocaleDateString('ru-RU', {
        day: 'numeric',
        month: 'short',
        hour: '2-digit',
        minute: '2-digit'
    });

    postCard.innerHTML = `
        <div class="post-header">
            <span class="post-author">@${post.author}</span>
            <span class="post-date">${currentDate}</span>
        </div>
        <div class="post-content">${escapeHtml(post.content)}</div>
        <span class="post-badge">${post.category}</span>
    `;

    container.prepend(postCard);
}

/* --- 2. Система чата и переписок --- */
function initChatSystem() {
    const chatInput = document.getElementById('chatInput');
    const sendChatBtn = document.getElementById('sendChatBtn');
    const chatMessages = document.getElementById('chatMessages');

    if (!sendChatBtn || !chatInput || !chatMessages) return;

    const sendMessage = () => {
        const text = chatInput.value.trim();
        if (text === "") return;

        appendMessageToChat(text, 'outgoing', chatMessages);
        chatInput.value = '';
        chatMessages.scrollTop = chatMessages.scrollHeight;

        setTimeout(() => {
            const replyText = `[Архив базы данных]: Сообщение успешно сохранено в реестр.`;
            appendMessageToChat(replyText, 'incoming', chatMessages);
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }, 800);
    };

    sendChatBtn.addEventListener('click', sendMessage);
    chatInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') sendMessage();
    });
}

function appendMessageToChat(text, type, container) {
    const bubble = document.createElement('div');
    bubble.className = `message-bubble message-${type}`;
    bubble.textContent = text;
    container.appendChild(bubble);
}

function escapeHtml(str) {
    return str
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}
