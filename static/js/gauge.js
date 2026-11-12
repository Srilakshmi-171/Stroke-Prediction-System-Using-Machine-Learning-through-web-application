// ==========================================
// ADVANCED MEDICAL RISK GAUGE
// ==========================================

function updateGauge(targetValue) {

    const gauge = document.getElementById("gauge");
    const riskText = document.getElementById("riskValue");
    const riskLevelText = document.getElementById("riskLevelText");

    let current = 0;
    let speed = 20; // lower = faster animation

    const interval = setInterval(() => {

        if (current >= targetValue) {
            clearInterval(interval);
        } else {
            current++;
        }

        // Degree calculation
        let degrees = current * 3.6;

        // Risk color zones
        let color;

        if (current < 40) {
            color = "#2ecc71"; // Low (Green)
            riskLevelText.innerText = "Low Risk";
        } 
        else if (current < 70) {
            color = "#f1c40f"; // Moderate (Yellow)
            riskLevelText.innerText = "Moderate Risk";
        } 
        else {
            color = "#e74c3c"; // High (Red)
            riskLevelText.innerText = "High Risk";
        }

        // Apply gradient
        gauge.style.background = `
            conic-gradient(
                ${color} ${degrees}deg,
                #e0e0e0 ${degrees}deg
            )
        `;

        // Update numeric value smoothly
        riskText.innerText = current + "%";
        riskText.style.color = color;

        // Add glow effect
        gauge.style.boxShadow = `0 0 25px ${color}`;

    }, speed);
}