async function submitForm() {
    const username = document.getElementById("username").value;
    const password = document.getElementById("password").value;
    const errorMessage = document.getElementById("errorMessage");

    // Clear previous error message
    errorMessage.textContent = "";

    // Make an asynchronous request to your FastAPI /token endpoint
    try {
        const response = await fetch('https://apiintegrated.niceflower-b877fcb8.australiaeast.azurecontainerapps.io/token', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: new URLSearchParams({
                'username': username,
                'password': password,
                'grant_type': 'password',
                'scope': '',
                'client_id': '',
                'client_secret': '',
            }),
        });

        if (!response.ok) {
            // Handle authentication error
            const errorData = await response.json();
            throw new Error(errorData.detail);
            
        }

        const responseData = await response.json();
        const accessToken = responseData.access_token;

        // Redirect to the desired page or perform other actions on successful login
        alert("Login successful!");
        window.location.href = 'https://apiintegrated.niceflower-b877fcb8.australiaeast.azurecontainerapps.io/docs';

        // Optionally, you can store the token in a secure way (e.g., in a cookie or local storage)
        // localStorage.setItem('access_token', accessToken);

    } catch (error) {
        errorMessage.textContent = error.message || "An error occurred during login.";
    }
}
