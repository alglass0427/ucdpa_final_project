document.addEventListener("DOMContentLoaded", () => {
    const spinner = document.getElementById("loading-spinner");
  
    // Attach click event to all delete buttons
    document.querySelectorAll(".spin-link").forEach((link) => {
      link.addEventListener("click", (e) => {
        e.preventDefault(); // Prevent the default action immediately
  
        // Show the spinner
        spinner.style.display = "flex";
  
        // Disable all delete buttons to prevent multiple clicks
        document.querySelectorAll(".spin-button").forEach((btn) => {
          btn.disabled = true;
        });
  
        // Redirect after a small delay (to ensure spinner is visible)
        setTimeout(() => {
          window.location.href = link.getAttribute("href");
        }, 300);
      });
    });
  });