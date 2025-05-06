// Copy your JavaScript from paste.txt here
const chatBox = document.getElementById('chat-box');
const chatForm = document.getElementById('chat-form');
const userInput = document.getElementById('user-input');
const typingIndicator = document.getElementById('typing-indicator');
const clearBtn = document.getElementById('clear-chat');

// Handle form submission
chatForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const message = userInput.value.trim();
    if (!message) return;

    appendMessage('user', message);
    userInput.value = '';
    typingIndicator.style.display = 'block';

    try {
        console.log("Sending chat request...");
        const res = await fetch('/chatbot/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: message })
        });

        if (!res.ok) {
            throw new Error(`Server responded with ${res.status}: ${res.statusText}`);
        }

        const data = await res.json();
        console.log("Received response:", data);
        
        typingIndicator.style.display = 'none';
        
        // Handle different response types
        if (data.type === 'quiz') {
            appendQuiz(data);
        } else {
            appendMessage('bot', data.response);
        }
    } catch (error) {
        console.error("Error:", error);
        typingIndicator.style.display = 'none';
        appendMessage('bot', 'Sorry, something went wrong! Please try again.');
    }
});

// Handle quiz responses
function appendQuiz(quizData) {
    const msgWrapper = document.createElement('div');
    msgWrapper.classList.add('message', 'bot-msg');

    const avatar = document.createElement('div');
    avatar.classList.add('avatar');
    avatar.textContent = "🤖";

    const msgContent = document.createElement('div');
    msgContent.classList.add('message-content', 'quiz-content');
    
    // Create quiz question
    const questionElement = document.createElement('p');
    questionElement.classList.add('quiz-question');
    questionElement.innerHTML = `<strong>Quiz Question:</strong> ${quizData.question}`;
    msgContent.appendChild(questionElement);
    
    // Create options with radio buttons
    const optionsDiv = document.createElement('div');
    optionsDiv.classList.add('quiz-options');
    
    quizData.options.forEach((option, index) => {
        const optionLabel = document.createElement('label');
        optionLabel.classList.add('quiz-option');
        
        const radioInput = document.createElement('input');
        radioInput.type = 'radio';
        radioInput.name = 'quiz-option';
        radioInput.value = option;
        radioInput.id = `option-${index}`;
        
        const optionText = document.createElement('span');
        optionText.textContent = option;
        
        optionLabel.appendChild(radioInput);
        optionLabel.appendChild(optionText);
        optionsDiv.appendChild(optionLabel);
    });
    
    msgContent.appendChild(optionsDiv);
    
    // Create submit button
    const submitBtn = document.createElement('button');
    submitBtn.classList.add('btn', 'btn-primary', 'btn-sm', 'quiz-submit');
    submitBtn.textContent = 'Submit Answer';
    submitBtn.addEventListener('click', () => {
        const selectedOption = document.querySelector('input[name="quiz-option"]:checked');
        if (!selectedOption) {
            alert('Please select an answer');
            return;
        }
        
        // Check answer
        const correctAnswer = quizData.answer;
        const userAnswer = selectedOption.value;
        
        // Disable options after submission
        document.querySelectorAll('input[name="quiz-option"]').forEach(input => {
            input.disabled = true;
        });
        submitBtn.disabled = true;
        
        // Show result
        const resultDiv = document.createElement('div');
        resultDiv.classList.add('quiz-result');
        
        if (userAnswer === correctAnswer) {
            resultDiv.innerHTML = `<span class="correct-answer">✓ Correct!</span>`;
        } else {
            resultDiv.innerHTML = `<span class="wrong-answer">✗ Incorrect! The correct answer is: ${correctAnswer}</span>`;
        }
        
        // Add explanation
        resultDiv.innerHTML += `<p class="explanation"><strong>Explanation:</strong> ${quizData.explanation}</p>`;
        
        // Add "Try another quiz" button
        const tryAnotherBtn = document.createElement('button');
        tryAnotherBtn.classList.add('btn', 'btn-primary', 'btn-sm', 'quiz-try-another');
        tryAnotherBtn.textContent = 'Try Another Quiz';
        tryAnotherBtn.style.marginTop = '10px';
        tryAnotherBtn.addEventListener('click', () => {
            // Simulate user sending a quiz request
            userInput.value = 'quiz me';
            chatForm.dispatchEvent(new Event('submit'));
        });
        
        resultDiv.appendChild(tryAnotherBtn);
        msgContent.appendChild(resultDiv);
        
        // Save this interaction to storage
        saveMessageToStorage('bot', 'quiz', quizData);
        saveMessageToStorage('user', 'answer', userAnswer);
    });
    
    msgContent.appendChild(submitBtn);
    
    msgWrapper.appendChild(avatar);
    msgWrapper.appendChild(msgContent);
    chatBox.appendChild(msgWrapper);
    chatBox.scrollTop = chatBox.scrollHeight;
}

// Append regular message
function appendMessage(sender, text) {
    const msgWrapper = document.createElement('div');
    msgWrapper.classList.add('message', sender === 'bot' ? 'bot-msg' : 'user-msg');

    const avatar = document.createElement('div');
    avatar.classList.add('avatar');
    avatar.textContent = sender === 'bot' ? "🤖" : "👤";

    const msgContent = document.createElement('div');
    msgContent.classList.add('message-content');
    
    // Convert URLs to clickable links
    const linkedText = text.replace(
        /(https?:\/\/[^\s]+)/g, 
        '<a href="$1" target="_blank" rel="noopener noreferrer">$1</a>'
    );
    
    msgContent.innerHTML = linkedText;

    if (sender === 'bot') {
        msgWrapper.appendChild(avatar);
        msgWrapper.appendChild(msgContent);
    } else {
        msgWrapper.appendChild(msgContent);
        msgWrapper.appendChild(avatar);
    }

    chatBox.appendChild(msgWrapper);
    chatBox.scrollTop = chatBox.scrollHeight;

    // Save message to storage
    saveMessageToStorage(sender, 'message', text);
}

// Save message to local storage
function saveMessageToStorage(sender, type, content) {
    try {
        const chats = JSON.parse(localStorage.getItem('chatHistory')) || [];
        chats.push({ sender, type, content, timestamp: new Date().toISOString() });
        // Limit history to 100 messages to prevent storage issues
        if (chats.length > 100) {
            chats.shift(); // Remove oldest message
        }
        localStorage.setItem('chatHistory', JSON.stringify(chats));
    } catch (error) {
        console.error("Error saving to local storage:", error);
    }
}

// Load chat history
function loadChatHistory() {
    try {
        const chats = JSON.parse(localStorage.getItem('chatHistory')) || [];
        
        // Only load the last 50 messages to prevent UI overload
        const recentChats = chats.slice(-50);
        
        recentChats.forEach(chat => {
            if (chat.type === 'quiz' && typeof chat.content === 'object') {
                appendQuiz(chat.content);
            } else if (chat.type === 'message') {
                appendMessage(chat.sender, chat.content);
            }
        });
    } catch (error) {
        console.error("Error loading chat history:", error);
        // If error loading, clear the history
        localStorage.removeItem('chatHistory');
    }
}

// Clear chat history
function clearChatHistory() {
    localStorage.removeItem('chatHistory');
    chatBox.innerHTML = '';
    
    // Add typing indicator back (it gets cleared)
    chatBox.appendChild(typingIndicator);
    
    // Add welcome message
    setTimeout(() => {
        appendMessage('bot', 'Hi there! I\'m your Quiz Master. Ask me for a quiz or any educational question!');
    }, 300);
}

// Add welcome message
function addWelcomeMessage() {
    const chats = JSON.parse(localStorage.getItem('chatHistory')) || [];
    if (chats.length === 0) {
        appendMessage('bot', 'Hi there! I\'m your Quiz Master. Ask me for a quiz or any educational question!');
    }
}

// Event listeners
if (clearBtn) {
    clearBtn.addEventListener('click', clearChatHistory);
}

// Add some helpful preset buttons
function addPresetButtons() {
    const presets = [
        {text: "Quiz me", action: () => { userInput.value = "quiz me"; chatForm.dispatchEvent(new Event('submit')); }},
        {text: "Science quiz", action: () => { userInput.value = "science quiz"; chatForm.dispatchEvent(new Event('submit')); }},
        {text: "Math quiz", action: () => { userInput.value = "math quiz"; chatForm.dispatchEvent(new Event('submit')); }},
        {text: "History quiz", action: () => { userInput.value = "history quiz"; chatForm.dispatchEvent(new Event('submit')); }}
    ];
    
    const presetContainer = document.createElement('div');
    presetContainer.classList.add('preset-buttons');
    presetContainer.style.display = 'flex';
    presetContainer.style.justifyContent = 'center';
    presetContainer.style.gap = '10px';
    presetContainer.style.marginTop = '15px';
    
    presets.forEach(preset => {
        const btn = document.createElement('button');
        btn.classList.add('btn', 'btn-primary');
        btn.textContent = preset.text;
        btn.style.fontSize = '14px';
        btn.style.padding = '8px 12px';
        btn.addEventListener('click', preset.action);
        presetContainer.appendChild(btn);
    });
    
    // Add after chat form
    chatForm.parentNode.insertBefore(presetContainer, chatForm.nextSibling);
}

// Detect errors and provide recovery
function detectAndFixErrors() {
    // Check if we can access localStorage
    try {
        localStorage.setItem('test', 'test');
        localStorage.removeItem('test');
    } catch (e) {
        console.error("LocalStorage not available:", e);
        // Alert user and disable storage features
        alert("Warning: Local storage is not available. Chat history will not be saved between sessions.");
        // Create dummy functions to prevent errors
        window.saveMessageToStorage = () => {};
        window.loadChatHistory = () => {
            appendMessage('bot', 'Hi there! I\'m your Quiz Master. Ask me for a quiz or any educational question!');
        };
    }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    detectAndFixErrors();
    loadChatHistory();
    addWelcomeMessage();
    addPresetButtons();
    
    // Debug info
    console.log("Chat application initialized");
});