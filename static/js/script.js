// script.js

// Wait for DOM to be ready
document.addEventListener('DOMContentLoaded', function () {
    console.log("🔧 JS Loaded: Handsign Detection Script Active");

    // Add hover effects to video
    const videoFrame = document.querySelector('.video-frame');
    if (videoFrame) {
        videoFrame.addEventListener('mouseenter', () => {
            videoFrame.style.borderColor = '#00ffe4';
        });

        videoFrame.addEventListener('mouseleave', () => {
            videoFrame.style.borderColor = '#444';
        });
    }

    // Optional: Auto-scroll to output on detection
    const outputBox = document.querySelector('.output-box');
    if (outputBox) {
        setTimeout(() => {
            outputBox.scrollIntoView({ behavior: 'smooth' });
        }, 200);
    }

    // Distance color feedback (requires Python to inject via st.markdown or HTML)
    const distanceText = document.getElementById('distance-value');
    if (distanceText) {
        const distance = parseFloat(distanceText.textContent);
        if (distance < 30) {
            distanceText.style.color = "#ff4d4d";
        } else if (distance < 50) {
            distanceText.style.color = "#ffaa00";
        } else {
            distanceText.style.color = "#00ffcc";
        }
    }
});
