// Redirect if not logged in
if (localStorage.getItem("session_token") != null) {
    window.location.href = "/";
}

// Login code
const loginid = document.getElementById("loginid");
const password = document.getElementById("password");
const submit = document.getElementById("submit");

submit.addEventListener('click', async function() {

    try {
        const response = await fetch("/check-user-login", {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                loginid: loginid.value,
                password: password.value
            })
        });

        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }

        loginid.value = "";
        password.value = "";

        const data = await response.json();

        localStorage.setItem("session_token", data.session_token)

        window.location.href = "/";
    }
    catch (error) {
        console.error('Error sending POST request:', error);
    }
});
