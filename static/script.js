

async function logout() {
    const username = document.getElementById("username").value;

    const response = await fetch('/logout', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username })
    });

    const data = await response.json();
    document.getElementById("message").innerText = data.message || data.error;
}

async function getProfile() {
    const username = document.getElementById("username").value;

    const response = await fetch(`/profile?username=${username}`);
    const data = await response.json();

    document.getElementById("message").innerText = data.message || data.error;
}
