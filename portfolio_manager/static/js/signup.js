//////////////////////////////////
/////////////////////////////////////////////////
setTimeout(function() {
    let flashMessages = document.getElementsByClassName('flash-message');
    for (var i = 0; i < flashMessages.length; i++) {
        flashMessages[i].style.display = 'none';
    }
}, 3000); // 3000 milliseconds = 3 seconds


document.addEventListener('DOMContentLoaded', () => {
    const usernameEl = document.querySelector('#fullname');
    const emailEl = document.querySelector('#email');
    const passwordEl = document.querySelector('#password');
    const confirmpasswordEl = document.querySelector('#confirm_password');
    const dobEl = document.querySelector('#dob');
    const genderEl = document.querySelector('#gender');
    const form_1 = document.querySelector('#signUpForm');
    

    form_1.addEventListener('submit', function (e) {
        let isValid = true;


        const inputs = [usernameEl, genderEl, emailEl, passwordEl,confirmpasswordEl, dobEl];

        // Iterate over each input and run validation based on ID
        inputs.forEach(input => {
            switch (input.id) {
                case 'fullname':
                    if (!checkUsername()) isValid = false;
                    break;
                case 'email':
                    if (!checkEmail()) isValid = false;
                    break;
                case 'password':
                    if (!checkPassword()) isValid = false;
                    break;
                case 'confirm_password':
                    if (!checkPassword()) isValid = false;
                    // if (!checkPassword()) isValid = false;
                    break;
                case 'dob':
                    if (!checkDOB()) isValid = false;
                    break;
                default:
                    if (input.name === 'gender') {
                        if (!checkGender()) isValid = false;
                    }
                    break;
            }



        // Prevent form submission if invalid
        if (!isValid) {
            e.preventDefault(); // Prevent default form submission
        }
    })
    });

    form_1.addEventListener('input', function (e) {
        switch (e.target.id) {
            case 'fullname':
                checkUsername();
                break;
            case 'email':
                checkEmail();
                break;
            case 'password':
                checkPassword();
                break;
                case 'confirm_password':
                    checkPassword();
                    break;
       
        }
    });

    const isRequired = value => value.trim() !== '';
    const isBetween = (length, min, max) => length >= min && length <= max;
    const isEmailValid = email => /^(.+@.+\..+)$/.test(email);
    const isPasswordSecure = password => /^(?=.*[a-z])(?=.*[A-Z])(?=.*[0-9])(?=.*[!@#\$%\^&\*])(?=.{8,})/.test(password);

    const showError = (input, message) => {
        const formField = input.parentElement;
        formField.classList.remove('success');
        formField.classList.add('error');
        const error = formField.querySelector('small');
        error.textContent = message;
    };

    const showSuccess = (input) => {
        const formField = input.parentElement;
        formField.classList.remove('error');
        formField.classList.add('success');
        const error = formField.querySelector('small');
        error.textContent = '';
    };

    const checkUsername = () => {
        const username = usernameEl.value.trim();
        if (!isRequired(username)) {
            showError(usernameEl, 'Username cannot be blank.');
            return false;
        } else if (!isBetween(username.length, 3, 25)) {
            showError(usernameEl, 'Username must be between 3 and 25 characters.');
            return false;
        } else {
            showSuccess(usernameEl);
            return true;
        }
    };

    const checkEmail = () => {
        const email = emailEl.value.trim();
        if (!isRequired(email)) {
            showError(emailEl, 'Email cannot be blank.');
            return false;
        } else if (!isEmailValid(email)) {
            showError(emailEl, 'Email is not valid.');
            return false;
        } else {
            showSuccess(emailEl);
            return true;
        }
    };

    const checkPassword = () => {
        const password = passwordEl.value.trim();
        const conf_password = confirmpasswordEl.value.trim();
        if (!isRequired(password)) {
            showError(passwordEl, 'Password cannot be blank.');
            return false;
        } else if (!isPasswordSecure(password)) {
            showError(passwordEl, 'Password must be at least 8 characters long, with at least one lowercase, one uppercase, one number, and one special character.');
            return false;
        } else if (password!==conf_password) {
            showError(passwordEl, 'Passwords do not match.');
            showError(confirmpasswordEl, 'Passwords do not match.');
            return false;
        } else {
            showSuccess(passwordEl);
            showSuccess(confirmpasswordEl);
            return true;
        }
    };


    const checkDOB = () => {

        const dob = dobEl.value.trim();
        console.log(dob)
        if (!isRequired(dob)) {
            showError(dobEl, 'Date of Birth cannot be blank.');
            return false;
        } else {
            showSuccess(dobEl);
            return true;
        }
    };

    const checkGender = () => {
        const gender = genderEl.value;
        console.log(gender)
        if (gender == 'Gender') {
            showError(genderEl, 'Please Select Gender.');
            return false;
        } else {
            showSuccess(genderEl);
            return true;
        }
    };
});

