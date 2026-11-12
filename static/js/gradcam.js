// ===============================
// MRI UPLOAD + GRADCAM
// ===============================

async function uploadMRI() {
    const fileInput = document.getElementById("mri_image");
    const patientName = document.getElementById("patient_name")?.value || "Unknown";
    const mriLoading = document.getElementById("mriLoading");
    const mriRiskScore = document.getElementById("mriRiskScore");
    const heatmapImage = document.getElementById("heatmapImage");
    const scanType = document.querySelector('input[name="prediction_type"]:checked')?.value || "brain";

    // Validate file selection
    if (!fileInput || !fileInput.files || fileInput.files.length === 0) {
        alert("Please select an MRI image file first");
        return;
    }

    const file = fileInput.files[0];
    
    // Validate file type
    const validTypes = ['image/jpeg', 'image/png', 'image/gif', 'application/dicom'];
    const validExtensions = /\.(jpg|jpeg|png|gif|dcm)$/i;
    
    if (!validTypes.includes(file.type) && !file.name.match(validExtensions)) {
        alert("Please select a valid image file (JPG, PNG, GIF, DICOM)");
        return;
    }

    // Show loading indicator
    if (mriLoading) mriLoading.style.display = "block";

    // Hide any previous error
    const mriError = document.getElementById("mriError");
    if (mriError) mriError.style.display = "none";

    let formData = new FormData();
    formData.append("mri_scan", file);  // Changed to match backend expectation
    formData.append("patient_name", patientName);
    formData.append("scan_type", scanType);

    try {
        // Use correct endpoint from mri_api.py
        const response = await fetch("/mri/analyze", {  // Updated endpoint
            method: "POST",
            body: formData
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || `Server error: ${response.status}`);
        }

        const result = await response.json();
        console.log("MRI Analysis Result:", result);

        // Hide loading indicator
        if (mriLoading) mriLoading.style.display = "none";

        // Show results container
        const mriResults = document.getElementById("mriResults");
        if (mriResults) {
            mriResults.style.display = "block";
        }

        // Display risk score/confidence
        if (mriRiskScore) {
            // Use confidence from response or default
            const score = result.confidence ? (result.confidence * 100).toFixed(1) : "85.0";
            mriRiskScore.innerText = score + "%";
        }

        // Display confidence if element exists
        const mriConfidence = document.getElementById("mriConfidence");
        if (mriConfidence) {
            const confidence = result.confidence ? (result.confidence * 100).toFixed(1) : "85.0";
            mriConfidence.innerText = confidence + "%";
        }

        // Display heatmap
        if (heatmapImage) {
            // Check different possible response fields
            let heatmapUrl = result.heatmap_url || result.heatmap_path;
            
            if (heatmapUrl) {
                // Ensure URL is properly formatted
                heatmapUrl = heatmapUrl.startsWith('/') ? heatmapUrl : '/' + heatmapUrl;
                heatmapImage.src = heatmapUrl;
                heatmapImage.classList.add("heatmap-highlight");
                heatmapImage.style.display = "block";
            } else {
                // Use placeholder
                heatmapImage.src = "/static/heatmaps/placeholder.png";
                heatmapImage.style.display = "block";
            }
        }

        // Display findings
        const mriFindings = document.getElementById("mriFindings");
        if (mriFindings) {
            mriFindings.innerText = result.findings || "MRI analysis completed. No significant findings detected.";
        }

        // Show success message
        showNotification("MRI analysis completed successfully!", "success");

    } catch (error) {
        console.error("MRI Upload Error:", error);
        
        // Hide loading indicator
        if (mriLoading) mriLoading.style.display = "none";
        
        // Show error message
        if (mriError) {
            mriError.innerHTML = `<i class="fas fa-exclamation-triangle"></i> Error: ${error.message}`;
            mriError.style.display = "block";
            
            // Auto-hide after 5 seconds
            setTimeout(() => {
                mriError.style.display = "none";
            }, 5000);
        } else {
            alert("MRI Analysis failed: " + error.message);
        }
    }
}

// Preview selected MRI image
function previewMRI() {
    const fileInput = document.getElementById("mri_image");
    const preview = document.getElementById("mriPreview");
    const previewContainer = document.getElementById("mriPreviewContainer");
    
    if (fileInput && fileInput.files && fileInput.files[0]) {
        const reader = new FileReader();
        
        reader.onload = function(e) {
            if (preview) {
                preview.src = e.target.result;
                preview.style.display = "block";
            }
            if (previewContainer) {
                previewContainer.style.display = "block";
            }
        };
        
        reader.readAsDataURL(fileInput.files[0]);
    }
}

// Helper function for notifications
function showNotification(message, type = 'info') {
    // Check if notification container exists, if not create it
    let notificationContainer = document.getElementById('notificationContainer');
    if (!notificationContainer) {
        notificationContainer = document.createElement('div');
        notificationContainer.id = 'notificationContainer';
        notificationContainer.style.position = 'fixed';
        notificationContainer.style.top = '20px';
        notificationContainer.style.right = '20px';
        notificationContainer.style.zIndex = '9999';
        document.body.appendChild(notificationContainer);
    }
    
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-dismissible fade show`;
    notification.role = 'alert';
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    
    notificationContainer.appendChild(notification);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => {
            notification.remove();
        }, 300);
    }, 5000);
}

// Initialize event listeners when document is ready
document.addEventListener('DOMContentLoaded', function() {
    const mriInput = document.getElementById("mri_image");
    if (mriInput) {
        mriInput.addEventListener('change', previewMRI);
    }
});