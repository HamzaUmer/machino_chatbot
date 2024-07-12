document.getElementById('send-btn').addEventListener('click', sendMessage);
document.getElementById('chat-input').addEventListener('keydown', function(event) {
    if (event.key === 'Enter') {
        sendMessage();
    }
});

function sendMessage() {
    const chatInput = document.getElementById('chat-input');
    const chatBody = document.getElementById('chat-body');

    if (chatInput.value.trim() !== "") {
        const userMessage = document.createElement('div');
        userMessage.classList.add('message', 'user-message');
        userMessage.textContent = chatInput.value;
        chatBody.appendChild(userMessage);

        // Show typing indicator
        const typingIndicator = document.createElement('div');
        typingIndicator.classList.add('message', 'bot-message', 'typing-indicator');
        typingIndicator.innerHTML = '<span></span><span></span><span></span>';
        chatBody.appendChild(typingIndicator);
        chatBody.scrollTop = chatBody.scrollHeight;

        // Send the user's message to the API
        fetch('https://machino-web-chatbot-f2ce8dd78424.herokuapp.com/qna/chatbot', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ query: chatInput.value }),
        })
        .then(response => response.json())
        .then(data => {
            // Remove typing indicator
            chatBody.removeChild(typingIndicator);

            // Show bot response
            const botMessage = document.createElement('div');
            botMessage.classList.add('message', 'bot-message');
            botMessage.textContent = data.answer;
            chatBody.appendChild(botMessage);

            // const botUrl = document.createElement('div');
            // botUrl.classList.add('message', 'bot-message');
            // // botUrl.innerHTML = `<a href="${data.url}" target="_blank">Source</a>`;
            // chatBody.appendChild(botUrl);

            chatBody.scrollTop = chatBody.scrollHeight;
        })
        .catch(error => {
            // Remove typing indicator
            chatBody.removeChild(typingIndicator);

            const botMessage = document.createElement('div');
            botMessage.classList.add('message', 'bot-message');
            botMessage.textContent = "Sorry, there was an error. Please try again.";
            chatBody.appendChild(botMessage);
            chatBody.scrollTop = chatBody.scrollHeight;
        });

        chatInput.value = "";
    }
}
