document.getElementById("open-chat").addEventListener("click", function () {
    var chatModal = new bootstrap.Modal(document.getElementById('chat-modal'));
    chatModal.show();
});

document.getElementById("send-message").addEventListener("click", async function () {
    let userInput = document.getElementById("user-input").value;
    if (userInput.trim() === "") return;

    displayMessage(userInput, "user");

    document.getElementById("user-input").value = "";

    try {
        const response = await getChatGPTResponse(userInput);
        displayMessage(response, "ai");
    } catch (error) {
        displayMessage("Ошибка при обработке запроса.", "ai");
        console.error("Error:", error);
    }
});

function displayMessage(message, sender) {
    const messageElement = document.createElement("div");
    messageElement.classList.add("mb-3");
    messageElement.classList.add(sender === "user" ? "text-end" : "text-start");

    const messageBubble = document.createElement("div");
    messageBubble.classList.add("badge", sender === "user" ? "bg-light" : "bg-info");
    messageBubble.classList.add("p-2", "text-dark")
    messageBubble.textContent = message;

    messageElement.appendChild(messageBubble);
    document.getElementById("chat-window").appendChild(messageElement);

    document.getElementById("chat-window").scrollTop = document.getElementById("chat-window").scrollHeight;
}

async function getChatGPTResponse(userInput) {
    const response = await fetch("http://127.0.0.1:8000/accounts/chatgpt/", { // API URL
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ message: userInput })
    });

    if (!response.ok) {
        throw new Error("Ошибка сети");
    }

    const data = await response.json();
    if (data.error) {
        throw new Error(data.error);
    }

    return data.reply;
}
