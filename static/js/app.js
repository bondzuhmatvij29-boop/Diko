/* ==========================================================================
   Diko Messenger & Data Center - Client Application Script
   ========================================================================== */

document.addEventListener('DOMContentLoaded', () => {
    // Инициализация элементов интерфейса
    initPostSystem();
    initChatSystem();
});

/* --- 1. Система публикации постов на главной странице --- */
function initPostSystem() {
    const postInput = document.getElementById('postInput');
    const publishBtn = document.getElementById('publishBtn');
    const postsContainer = document.getElementById('postsContainer');

    if (!publishBtn || !postInput || !postsContainer) return;

    publishBtn.addEventListener('click', async () => {
        const content = postInput.value.trim();
        if.content === "") {
            alert('Поле поста не може бути порожнім!');
            return;
        }

        // Данные нового поста
        const postData = {
            author: "nexustorvard", // Используем никнейм разработчика/пользователя
            content: content,
            category: "Спеціалізований пост"
        };

        try {
            // Имитация отправки на бэкенд (Flask / Database)
            // В реальном проекте здесь будет fetch('/api/posts', { method: 'POST', ... })
            
            // Добавляем пост в ленту динамически
            appendPostToDOM(postData, postsContainer);
            
            // Очищаем поле ввода
            postInput.value = '';
        } catch (error) {
            console.error('Помилка публікації поста:', error);
        }
    });
}

// Функция рендеринга поста в DOM
function appendPostToDOM(post, container) {
    const postCard = document.createElement('div');
    postCard.className = 'card post-card';
    
    const currentDate = new Date().toLocaleDateString('uk-UA', {
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

    // Вставляем новый пост в самое начало ленты
    container.prepend(postCard);
}


/* --- 2. Система обмена сообщениями в чате (Центр переписок) --- */
function initChatSystem() {
    const chatInput = document.getElementById('chatInput');
    const sendChatBtn = document.getElementById('sendChatBtn');
    const chatMessages = document.getElementById('chatMessages');

    if (!sendChatBtn || !chatInput || !chatMessages) return;

    const sendMessage = () => {
        const text = chatInput.value.trim();
        if (text === "") return;

        // 1. Добавляем исходящее сообщение пользователя
        appendMessageToChat(text, 'outgoing', chatMessages);
        chatInput.value = '';

        // Прокрутка чата вниз
        chatMessages.scrollTop = chatMessages.scrollHeight;

        // 2. Имитация ответа системы / базы данных (эмуляция сохранения)
        setTimeout(() => {
            const replyText = `[Архів бази даних]: Повідомлення успішно збережено у джерело.`;
            appendMessageToChat(replyText, 'incoming', chatMessages);
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }, 1000);
    };

    sendChatBtn.addEventListener('click', sendMessage);

    // Отправка по нажатию Enter
    chatInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });
}

// Функция добавления сообщения в окно чата
function appendMessageToChat(text, type, container) {
    const bubble = document.createElement('div');
    bubble.className = `message-bubble message-${type}`;
    bubble.textContent = text;
    container.appendChild(bubble);
}


/* --- Вспомогательная функция для защиты от XSS --- */
function escapeHtml(str) {
    return str
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}
