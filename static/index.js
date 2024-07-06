function sendMessage() {
    var userInput = document.getElementById("user-input").value;
    if (userInput.trim() === "") return;

    var chatMessages = document.getElementById("chat-messages");
    var userMessage = `<div class="message user-message">${userInput}</div>`;
    chatMessages.innerHTML += userMessage;

    // Clear input field
    document.getElementById("user-input").value = "";

    // Send user input to the backend and fetch the bot response
    fetch("/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({ user_input: userInput }),
    })
    .then(response => response.json())
    .then(data => {
        var botMessage = `<div class="message bot-message">${data.bot_response}</div>`;
        chatMessages.innerHTML += botMessage;
        chatMessages.scrollTop = chatMessages.scrollHeight; // Scroll to bottom
    })
    .catch(error => {
        console.error("Error:", error);
    });
}

function handleEnter(event) {
    if (event.key === "Enter") {
        event.preventDefault(); // Prevent default behavior (form submission)
        sendMessage(); // Call sendMessage function
    }
}
