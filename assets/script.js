// ==========================================
// ILM Generator JavaScript
// ==========================================

// ----------------------------
// Flashcards
// ----------------------------
function toggleFlashcard(id) {

    let answer = document.getElementById(id);

    if (answer.style.display === "none") {
        answer.style.display = "block";
    } else {
        answer.style.display = "none";
    }
}

// ----------------------------
// MCQ Answer Checking
// ----------------------------
function checkAnswer(questionId, correctAnswer) {

    let options = document.getElementsByName(questionId);

    let selected = "";

    for (let i = 0; i < options.length; i++) {

        if (options[i].checked) {
            selected = options[i].value;
        }

    }

    let result = document.getElementById(questionId + "_result");

    if (selected === "") {

        result.innerHTML = "Please select an answer.";

        return;
    }

    if (selected === correctAnswer) {

        result.innerHTML = "✅ Correct Answer";

        result.style.color = "green";

    } else {

        result.innerHTML = "❌ Incorrect Answer";

        result.style.color = "red";

    }

}

// ----------------------------
// Print Page
// ----------------------------
function printPage() {

    window.print();

}

// ----------------------------
// Expand All Sections
// ----------------------------
function expandAll() {

    let sections = document.getElementsByClassName("content");

    for (let i = 0; i < sections.length; i++) {

        sections[i].style.display = "block";

    }

}
