// Redirect if not logged in
if (localStorage.getItem("session_token") != null) {
    window.location.href = "/";
}

// Register code
const name = document.getElementById("name");
const loginid = document.getElementById("loginid");
const email = document.getElementById("email");
const password = document.getElementById("password");
const confirm_password = document.getElementById("confirm-password");
const submit = document.getElementById("submit");

submit.addEventListener('click', async function() {
    if (password.value != confirm_password.value) {
        return;
    }

    try {
        const response = await fetch("/register-user", {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                name: name.value,
                loginid: loginid.value,
                email: email.value,
                password: password.value
            })
        });

        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }

        name.value = "";
        loginid.value = "";
        email.value = "";
        password.value = "";
        confirm_password.value = "";

        const data = await response.json();

        if (data.success == false) {
            return;
        }

        localStorage.setItem("session_token", data.session_token)

        window.location.href = "/";
    }
    catch (error) {
        console.error('Error sending POST request:', error);
    }
});
