document.addEventListener("DOMContentLoaded", async function () {
    const urlParts = window.location.pathname.split("/");
    const mail = urlParts[2];  
    const queryParams = new URLSearchParams(window.location.search);
    const quiz_id = queryParams.get('quiz_id');  

    if (!mail || !quiz_id) {
        console.error("Missing mail or quiz_id in URL");
        return;
    }

    try {
        const response = await fetch(`/students/${mail}/${quiz_id}`);
        if (!response.ok) throw new Error(`HTTP error! Status: ${response.status}`);

        const data = await response.json();
        if (!data.questions || !Array.isArray(data.questions)) {
            console.error("Invalid API response format", data);
            return;
        }

        renderQuiz(data.questions);
        startCountdownTimer(data.time);
    } catch (error) {
        console.error("Failed to fetch quiz:", error);
    }
});

// Function to render quiz questions dynamically
function renderQuiz(questions) {
    const questionContainer = document.getElementById("question-container");
    questionContainer.innerHTML = ""; 

    questions.forEach((item, index) => {
        const questionDiv = document.createElement("div");
        questionDiv.classList.add("question-box", "p-3", "mb-3", "border", "rounded");

        questionDiv.innerHTML = `
            <h4>${index + 1}. ${item.question}</h4>
            <div class="options">
                ${item.options.map((option, i) => `
                    <div class="form-check">
                        <input class="form-check-input" type="radio" name="q${index}" id="q${index}o${i}" value="${option}">
                        <label class="form-check-label" for="q${index}o${i}">${option}</label>
                    </div>
                `).join('')}
            </div>
        `;

        questionContainer.appendChild(questionDiv);
    });
}

// Function to start the countdown timer
function startCountdownTimer(timeInMinutes) {
    let timerDisplay = document.getElementById('timer');
    let timeLeft = timeInMinutes * 60; 

    function updateTimer() {
        let minutes = Math.floor(timeLeft / 60);
        let seconds = timeLeft % 60;
        timerDisplay.textContent = `${minutes}:${seconds < 10 ? '0' : ''}${seconds}`;

        if (timeLeft <= 0) {
            clearInterval(timerInterval);
            alert("Time's up! Submitting quiz...");
            submitQuizForm();
        } else {
            timeLeft--; 
        }
    }

    updateTimer();
    let timerInterval = setInterval(updateTimer, 1000);
}

// Function to submit the form automatically
function submitQuizForm() {
    let quizForm = document.getElementById('quiz-results');
    if (quizForm) {
        quizForm.submit();
    } else {
        console.error("Quiz form not found!");
    }
}
document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("quiz-results");

    form.addEventListener("submit", async function (event) {
        event.preventDefault(); 

        const formData = new FormData(form);
        const urlParts = window.location.pathname.split("/");
        const mail = urlParts[2];  
        const queryParams = new URLSearchParams(window.location.search);
        const quiz_id = queryParams.get('quiz_id'); 
        console.log(mail)

        try {
            const response = await fetch(`/students/${mail}/${quiz_id}`, {
                method: "POST",
                body: formData
            });

            const result = await response.json();
            console.log(result);
            setTimeout(() => {
                window.location.href = `/students/${mail}`;  
            });  

        } catch (error) {
            console.error("Error submitting quiz:", error);
        }
    });
});
