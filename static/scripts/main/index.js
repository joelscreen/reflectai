// Store User Details
async function store_user_details() {
    const response = await fetch("/fetch-user-details", {
        headers: {
            "session-token": localStorage.getItem("session_token")
        }
    });

    if (!response.ok) {
        return null;
    }

    const data = await response.json();

    localStorage.setItem("user_details", JSON.stringify(data));

    return data;
}

var user_details = {};

// Initialize Page
async function initialize() {
    if (localStorage.getItem("session_token") == null) {
        window.location.href = "/login";
        return;
    }

    user_details = await store_user_details();

    if (!user_details) {
        localStorage.clear();
        window.location.href = "/login";
        return;
    }

    document.getElementById("welcome-msg").textContent =
        `Welcome back, ${user_details.name}!!`;

    show_diary_entries();
}

initialize();

// Log Out
const log_out = document.getElementById("log-out");
log_out.addEventListener('click', async function() {
    await fetch("/logout", {
        method: "POST",
        headers: {
            "session-token": localStorage.getItem("session_token")
        }
    });

    localStorage.clear();

    window.location.href = "/login";
})

// Add Entries
const add_entries = document.getElementById("add-entries");
const entry_editor = document.getElementById("entry-editor");
const title = document.getElementById("title-editor");
const content = document.getElementById("content-editor");

add_entries.addEventListener("click", function() {
    entry_editor.style.top = "50%";
    entry_editor.style.left = "50%";
    title.value = "";
    content.value = "";
});

// Close Editor
const close_editor = document.getElementById("close-editor");

close_editor.addEventListener("click", function() {
    entry_editor.style.top = "200%";
    entry_editor.style.left = "200%";
    title.value = "";
    content.value = "";
});

// Create Diary from Editor
const create_editor = document.getElementById("create-editor");

create_editor.addEventListener("click", async function() {
    try {
        const response = await fetch("/insert-diary-entry", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                id: user_details.id,
                title: title.value,
                content: content.value
            })
        });

        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }

        entry_editor.style.top = "200%";
        entry_editor.style.left = "200%";
        title.value = "";
        content.value = "";
        show_diary_entries();
    }
    catch (error) {
        console.log(`Error ${error}`)
    }
})

// Delete Entry
async function delete_entry(id) {
    const response = await fetch("/delete-diary-entry", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "session-token": localStorage.getItem("session_token")
        },
        body: JSON.stringify({
            id: id,
            name: user_details.name
        })
    });

    if (!response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`);
    }
}

// Show Diary Entries
async function show_diary_entries() {
    const response = await fetch("/fetch-diary-entry", {
        method: "POST",
        headers: {
            "session-token": localStorage.getItem("session_token")
        }
    });
    const data = await response.json();

    if (!response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`);
    }

    const entry_container = document.getElementById("entry-container");
    entry_container.innerHTML = "";

    data.data.forEach(entry => {
        var created_date = entry.created_at
        created_date = created_date.split("T")[0]
        const diaryCard = document.createElement("div");
        diaryCard.className = "entries";

        diaryCard.innerHTML = `
            <button class="delete-entry"><i class="fa-regular fa-trash-can"></i></button>
            <h2 style="font-size:24px;">${entry.title}</h2>
            <p>${entry.content}</p>
            <p style="text-align:end; color:#898484;">${created_date}</p>
        `;

        const deleteButton = diaryCard.querySelector(".delete-entry");

        deleteButton.addEventListener("click", async function (e) {
            e.stopPropagation();

            await delete_entry(entry.id);
            show_diary_entries();
        });

        const entry_viewer = document.getElementById("entry-viewer");

        diaryCard.addEventListener("click", function () {
            entry_viewer.style.top = "50%";
            entry_viewer.style.left = "50%";
            document.getElementById("viewer-title").textContent = entry.title;
            document.getElementById("viewer-content").textContent = entry.content;
            document.getElementById("viewer-date").textContent = created_date;

            // Close Editor
            const close_editor = document.getElementById("close-editor-view");

            close_editor.addEventListener("click", function() {
                entry_viewer.style.top = "200%";
                entry_viewer.style.left = "200%";
                document.getElementById("viewer-title").textContent = "";
                document.getElementById("viewer-content").textContent = "";
                document.getElementById("viewer-date").textContent = "";
            });
        });

        entry_container.appendChild(diaryCard);
    });
    const addButton = document.createElement("div");
    addButton.className = "entries";
    addButton.id = "add-entries";
    addButton.style.fontSize = "120px";
    addButton.style.fontWeight = "100";
    addButton.style.backgroundColor = "#3f3d3d";
    addButton.style.display = "flex";
    addButton.style.justifyContent = "center";
    addButton.style.alignItems = "center";
    addButton.textContent = "+";

    addButton.addEventListener("click", function () {
        entry_editor.style.top = "50%";
        entry_editor.style.left = "50%";
        title.value = "";
        content.value = "";
    });

    entry_container.appendChild(addButton);

    const newAddButton = document.getElementById("add-entries");

    newAddButton.addEventListener("click", function () {
        entry_editor.style.top = "50%";
        entry_editor.style.left = "50%";
        title.value = "";
        content.value = "";
    });
}

show_diary_entries();
