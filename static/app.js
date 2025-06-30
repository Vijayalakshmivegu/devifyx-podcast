// Minimal placeholder JS for your frontend

console.log("app.js loaded");

// Example: Add your frontend logic here
// document.addEventListener("DOMContentLoaded", function() {
//     // Your code here
// });

// Example: static/app.js
async function uploadFile(file, language, summary_length) {
    const formData = new FormData();
    formData.append("file", file);
    formData.append("language", language);
    formData.append("summary_length", summary_length);

    const response = await fetch("/upload", {
        method: "POST",
        body: formData
    });

    if (!response.ok) {
        const error = await response.json();
        alert("Error: " + (error.detail || response.status));
        return;
    }

    const result = await response.json();
    console.log(result);

    // Display result in your HTML
    const outputDiv = document.getElementById("output");
    if (outputDiv) {
        outputDiv.textContent = JSON.stringify(result, null, 2);
    }
}

document.addEventListener("DOMContentLoaded", function () {
    // Handle file upload form
    const uploadForm = document.getElementById("uploadForm");
    if (uploadForm) {
        uploadForm.addEventListener("submit", async function (e) {
            e.preventDefault();
            const fileInput = uploadForm.querySelector('input[name="file"]');
            const languageInput = uploadForm.querySelector('input[name="language"]');
            const summaryLengthInput = uploadForm.querySelector('input[name="summary_length"]');
            const resultDiv = document.getElementById("result");
            resultDiv.style.display = "none";
            resultDiv.textContent = "";

            if (!fileInput.files.length) {
                alert("Please select a file.");
                return;
            }

            const formData = new FormData();
            formData.append("file", fileInput.files[0]);
            formData.append("language", languageInput.value);
            formData.append("summary_length", summaryLengthInput.value);

            try {
                const response = await fetch("/upload", {
                    method: "POST",
                    body: formData
                });
                const data = await response.json();
                if (response.ok) {
                    resultDiv.style.display = "block";
                    resultDiv.innerHTML = `
                        <strong>Summary:</strong><br>${data.summary || "N/A"}<br><br>
                        <strong>Themes:</strong><br>${Array.isArray(data.themes) ? data.themes.join(", ") : (data.themes || "N/A")}<br><br>
                        <strong>Tags:</strong><br>${Array.isArray(data.tags) ? data.tags.join(", ") : (data.tags || "N/A")}<br><br>
                        <strong>Speakers:</strong><br>${Array.isArray(data.speakers) ? data.speakers.join(", ") : (data.speakers || "N/A")}
                    `;
                } else {
                    resultDiv.style.display = "block";
                    resultDiv.textContent = data.detail || "An error occurred.";
                }
            } catch (err) {
                resultDiv.style.display = "block";
                resultDiv.textContent = "Network error.";
            }
        });
    }

    // Handle text form
    const textForm = document.getElementById("textForm");
    if (textForm) {
        textForm.addEventListener("submit", async function (e) {
            e.preventDefault();
            const contentInput = textForm.querySelector('textarea[name="content"]');
            const languageInput = textForm.querySelector('input[name="language"]');
            const summaryLengthInput = textForm.querySelector('input[name="summary_length"]');
            const resultDiv = document.getElementById("result");
            resultDiv.style.display = "none";
            resultDiv.textContent = "";

            const payload = {
                content: contentInput.value,
                language: languageInput.value,
                summary_length: summaryLengthInput.value
            };

            try {
                const response = await fetch("/process", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify(payload)
                });
                const data = await response.json();
                if (response.ok) {
                    resultDiv.style.display = "block";
                    resultDiv.innerHTML = `
                        <strong>Summary:</strong><br>${data.summary || "N/A"}<br><br>
                        <strong>Themes:</strong><br>${Array.isArray(data.themes) ? data.themes.join(", ") : (data.themes || "N/A")}<br><br>
                        <strong>Tags:</strong><br>${Array.isArray(data.tags) ? data.tags.join(", ") : (data.tags || "N/A")}<br><br>
                        <strong>Speakers:</strong><br>${Array.isArray(data.speakers) ? data.speakers.join(", ") : (data.speakers || "N/A")}
                    `;
                } else {
                    resultDiv.style.display = "block";
                    resultDiv.textContent = data.detail || "An error occurred.";
                }
            } catch (err) {
                resultDiv.style.display = "block";
                resultDiv.textContent = "Network error.";
            }
        });
    }
});