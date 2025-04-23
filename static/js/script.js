// script.js
document.addEventListener("DOMContentLoaded", () => {
  console.log("Custom script loaded.");

  // Optional: Dark/Light mode toggle
  const toggleBtn = document.getElementById("theme-toggle");
  if (toggleBtn) {
    toggleBtn.addEventListener("click", () => {
      document.body.classList.toggle("light-mode");
    });
  }

  // Placeholder for showing dynamic messages or alerts
  window.showAlert = (message) => {
    const alertBox = document.getElementById("alert-box");
    if (alertBox) {
      alertBox.innerText = message;
      alertBox.style.display = "block";
      setTimeout(() => (alertBox.style.display = "none"), 3000);
    }
  };
});
