document.addEventListener('DOMContentLoaded', function() {
    var userDropdown = document.getElementById('userName');
    var accessDropdown = document.getElementById('role');
    var submitButton = document.getElementById('submitButton');

    // Function to toggle the button state based on the selected value
    function toggleSubmitButton() {
        if (userDropdown.value === '' || accessDropdown.value === '' ) {
            submitButton.disabled = true;  // Disable if no stock selected
        } else {
            submitButton.disabled = false;  // Enable if stock selected
        }
    }

    // Initially disable the button if no stock is selected
    toggleSubmitButton();

    // Add event listener for changes in the dropdown selection
    userDropdown.addEventListener('change', toggleSubmitButton);
    accessDropdown.addEventListener('change', toggleSubmitButton);
});
