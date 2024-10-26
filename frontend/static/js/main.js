document.addEventListener("DOMContentLoaded", function() {
    const loginForm = document.getElementById('loginForm');
    const signupForm = document.getElementById('signupForm');

    if (loginForm) {
        loginForm.addEventListener('submit', function(event) {
            const username = document.getElementById('username').value;
            const password = document.getElementById('password').value;
            if (!username || !password) {
                event.preventDefault();
                alert("Please fill in all fields.");
            }
        });
    }

    if (signupForm) {
        signupForm.addEventListener('submit', function(event) {
            const username = document.getElementById('username').value;
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;

            if (!username || !email || !password) {
                event.preventDefault();
                alert("Please fill in all fields.");
            }
        });
    }
});