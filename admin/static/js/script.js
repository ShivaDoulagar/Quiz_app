async function loadSubjects() {
    try {
        const response = await fetch("/admin/list_of_subjects");
        const data = await response.json();

        const subjectsContainer = document.getElementById("subjects-container");

        // Clear container
        subjectsContainer.innerHTML = "";

        // Loop through subjects and create cards
        data.subjects.forEach(subject => {
            const card = document.createElement("div");
            card.classList.add("col-md-4");

            card.innerHTML = `
                <div class="card h-100">
                    <div class="card-body">
                        <h5 class="card-title">${subject.name}</h5>
                        <p class="card-text">${subject.description}</p>
                    </div>
                </div>
            `;
            subjectsContainer.appendChild(card);
        });
    } catch (error) {
        console.error("Error loading subjects:", error);
    }
}

// Load subjects when the page loads
document.addEventListener("DOMContentLoaded", loadSubjects);



const modal = document.getElementById('show_details');
modal.addEventListener('show.bs.modal', function (event) {
  const button = event.relatedTarget;

  document.getElementById('quiz-id').textContent = button.getAttribute('data-id');
  document.getElementById('quiz-title').textContent = button.getAttribute('data-title');
  document.getElementById('quiz-chapter').textContent = button.getAttribute('data-chapter');
  document.getElementById('quiz-date').textContent = button.getAttribute('data-date');
  document.getElementById('quiz-duration').textContent = button.getAttribute('data-duration');
});