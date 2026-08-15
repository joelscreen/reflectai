// Declare User Details
const user_details = JSON.parse(localStorage.getItem("user_details"));

// Redirect if not logged in
if (localStorage.getItem("session_token") == null) {
    window.location.href = "/login";
}

// Store User Details
async function store_user_details() {
    const response = await fetch("/fetch-user-details", {
        headers: {
            "session-token": localStorage.getItem("session_token")
        }
    });

    if (!response.ok) {
        return;
    }

    const data = await response.json();

    localStorage.setItem("user_details", JSON.stringify(data));
}

store_user_details();

document.getElementById("welcome-msg").textContent = `Welcome back, ${user_details.name}!!`

// Log Out
const log_out = document.getElementById("log-out");
log_out.addEventListener('click', async function() {
    await fetch("/logout", {
        method: "POST",
        headers: {
            "session-token": localStorage.getItem("session_token")
        }
    });

    localStorage.removeItem("session_token");

    window.location.href = "/login";
})

// Personality Report
const personality_p = document.getElementById("personality-p")

async function get_personality(new_report) {
    const e_response = await fetch("/fetch-diary-entry", {
        method: "POST",
        headers: {
            "session-token": localStorage.getItem("session_token")
        }
    });
    const e_data = await e_response.json();

    if (!e_response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`);
    }

    const response = await fetch("/personality-check", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            id: user_details.id,
            name: user_details.name,
            entries: e_data,
            new_report: new_report
        })
    })
    const data = await response.json()

    personality_p.innerHTML = marked.parse(data.reply);
}

get_personality("false");

// Advice
const advice_p = document.getElementById("advice-p")

async function get_advice(new_report) {
    const e_response = await fetch("/fetch-diary-entry", {
        method: "POST",
        headers: {
            "session-token": localStorage.getItem("session_token")
        }
    });
    const e_data = await e_response.json();

    if (!e_response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`);
    }

    const response = await fetch("/advice", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            id: user_details.id,
            name: user_details.name,
            entries: e_data,
            new_report: new_report
        })
    })
    const data = await response.json()

    advice_p.innerHTML = marked.parse(data.reply);
}

get_advice("false");

// Generate new report
const generate_new_report = document.getElementById("generate-new-report");

generate_new_report.addEventListener("click", async function() {
    await get_personality("true");
});

// Generate new advice
const generate_new_advice = document.getElementById("generate-new-advice");

generate_new_advice.addEventListener("click", async function() {
    await get_advice("true");
});

// Reflect Companion
const reflect_comp_input = document.getElementById("reflect-comp-input");
const reflect_comp_send = document.getElementById("reflect-comp-send");
const reflect_comp_p = document.getElementById("reflect-comp-p")

reflect_comp_send.addEventListener("click", async function () {
    if (reflect_comp_input.value == "") {
        return;
    }
    const e_response = await fetch("/fetch-diary-entry", {
        method: "POST",
        headers: {
            "session-token": localStorage.getItem("session_token")
        }
    });
    const e_data = await e_response.json();

    if (!e_response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`);
    }

    const response = await fetch("/reflect-companion", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            user_id: user_details.id,
            name: user_details.name,
            entries: e_data,
            message: reflect_comp_input.value,
            chat_history: reflect_comp_p.innerHTML,
            chat_id: currentChatId
        })
    })
    const data = await response.json()

    if (currentChatId == null) {
        currentChatId = data.chat_id;
    }
    await get_chat_history();

    reflect_comp_p.innerHTML += `
        <p style="margin-left: auto;
                  width: fit-content;
                  background-color: #4d4a4a;
                  padding: 10px;
                  border-radius: 8px;">${reflect_comp_input.value}</p>
    `
   reflect_comp_p.innerHTML += `
        <div class="ai-message">
            ${marked.parse(data.reply)}
        </div>
    `;

    reflect_comp_input.value = "";
});

// Chat History
let currentChatId = null;
const chat_history_div = document.getElementById("chat-history");

async function get_chat_history() {
    chat_history_div.innerHTML = "";

    const response = await fetch("/get-chat-history", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            user_id: user_details.id
        })
    });
    const data = await response.json();

    data.data.forEach(chat => {
        chat_history_div.innerHTML += `
            <button class="chat-btn" data-chat-id="${chat.id}">
                ${chat.name}
            </button>
        `;
    });
    document.querySelectorAll(".chat-btn").forEach(button => {
        button.addEventListener("click", async function () {
            const chatId = this.dataset.chatId;

            const response = await fetch("/load-chat", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    user_id: user_details.id,
                    chat_id: chatId
                })
            });

            const data = await response.json();

            currentChatId = Number(chatId);
            reflect_comp_p.innerHTML = data.conversation;

            const aiMessages = reflect_comp_p.querySelectorAll(".ai-message");

            aiMessages.forEach(message => {
                message.innerHTML = marked.parse(message.textContent);
            });
        });
    });
}

get_chat_history()

// Core Traits
const core_traits_p = document.getElementById("core-traits")

async function get_core_traits(new_report) {
    const e_response = await fetch("/fetch-diary-entry", {
        method: "POST",
        headers: {
            "session-token": localStorage.getItem("session_token")
        }
    });
    const e_data = await e_response.json();

    if (!e_response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`);
    }

    const h_response = await fetch("/get-chat-history", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            user_id: user_details.id
        })
    });
    const h_data = await h_response.json();

    const response = await fetch("/core-traits", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            user_id: user_details.id,
            name: user_details.name,
            entries: e_data,
            chat_history: h_data,
            new_report: new_report
        })
    })
    const data = await response.json()

    core_traits_p.innerHTML = ""
    core_traits_p.innerHTML += "<h2>Core Traits</h2>"
    core_traits_p.innerHTML += marked.parse(data.core_traits);
    core_traits_p.innerHTML += "<h2>Frequent Emotions</h2>"
    core_traits_p.innerHTML += marked.parse(data.frequent_emotions);
}

get_core_traits("false");

const generate_new_list = document.getElementById("generate-new-list");

generate_new_list.addEventListener("click", async function() {
    await get_core_traits("true");
});

// Strenghts and Weaknesses
const strenghts_weaknesses_p = document.getElementById("strenghts-weaknesses")

async function get_sw_traits(new_report) {
    const e_response = await fetch("/fetch-diary-entry", {
        method: "POST",
        headers: {
            "session-token": localStorage.getItem("session_token")
        }
    });
    const e_data = await e_response.json();

    if (!e_response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`);
    }

    const h_response = await fetch("/get-chat-history", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            user_id: user_details.id
        })
    });
    const h_data = await h_response.json();

    const response = await fetch("/strenghts-weaknesses", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            user_id: user_details.id,
            name: user_details.name,
            entries: e_data,
            chat_history: h_data,
            new_report: new_report
        })
    })
    const data = await response.json()

    strenghts_weaknesses_p.innerHTML = ""
    strenghts_weaknesses_p.innerHTML += "<h2>Strenghts</h2>"
    strenghts_weaknesses_p.innerHTML += marked.parse(data.strenghts);
    strenghts_weaknesses_p.innerHTML += "<h2>Weaknesses</h2>"
    strenghts_weaknesses_p.innerHTML += marked.parse(data.weaknesses);
}

get_sw_traits("false");

const generate_new_list_sw = document.getElementById("generate-new-list-sw");

generate_new_list_sw.addEventListener("click", async function() {
    await get_sw_traits("true");
});
