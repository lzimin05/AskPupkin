//check passwords 

document.addEventListener('DOMContentLoaded', function() {
    const password = document.getElementById('inputPassword');
    const confirmPassword = document.getElementById('inputPasswordRepeat');
    
    function validatePassword() {
        if (password.value !== confirmPassword.value) {
            confirmPassword.setCustomValidity("Passwords don't match");
        } else {
            confirmPassword.setCustomValidity('');
        }
    }
    
    password.addEventListener('change', validatePassword);
    confirmPassword.addEventListener('keyup', validatePassword);
});