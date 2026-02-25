/*
  Team Thiran - Web Interface JavaScript
  Handles file uploads, predictions, and report generation
*/

const uploadArea = document.getElementById('uploadArea');
const fileInput = document.getElementById('fileInput');
const resultsCard = document.getElementById('resultsCard');
const progressContainer = document.getElementById('progressContainer');
const progressBar = document.getElementById('progressBar');
const previewImage = document.getElementById('previewImage');
const reportModal = document.getElementById('reportModal');
const errorAlert = document.getElementById('errorAlert');

// Current analysis data
let currentAnalysis = {
    prediction: null,
    imagePath: null,
    report: null
};

// ============================================================================
// FILE UPLOAD HANDLING
// ============================================================================

if (uploadArea) {
    // Click to upload
    uploadArea.addEventListener('click', () => fileInput.click());

    // Drag and drop
    uploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadArea.classList.add('drag-over');
    });

    uploadArea.addEventListener('dragleave', () => {
        uploadArea.classList.remove('drag-over');
    });

    uploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadArea.classList.remove('drag-over');

        const files = e.dataTransfer.files;
        if (files.length > 0) {
            handleFileSelect(files[0]);
        }
    });

    // File input change
    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            handleFileSelect(e.target.files[0]);
        }
    });
}

function handleFileSelect(file) {
    // Validate file type
    const validTypes = ['image/jpeg', 'image/png', 'image/bmp', 'image/tiff'];
    if (!validTypes.includes(file.type)) {
        showError('Invalid file format. Please upload: JPG, PNG, BMP, or TIFF');
        return;
    }

    // Validate file size (max 50MB)
    if (file.size > 50 * 1024 * 1024) {
        showError('File size too large. Maximum 50 MB allowed.');
        return;
    }

    // Create FormData and upload
    const formData = new FormData();
    formData.append('file', file);

    uploadImage(formData);
}

// ============================================================================
// IMAGE UPLOAD & PREDICTION
// ============================================================================

function uploadImage(formData) {
    // Show progress
    progressContainer.classList.remove('hidden');
    resultsCard.classList.add('hidden');
    errorAlert.classList.add('hidden');

    // Simulate progress
    let progress = 0;
    const interval = setInterval(() => {
        if (progress < 90) {
            progress += Math.random() * 30;
            progressBar.style.width = Math.min(progress, 90) + '%';
        }
    }, 200);

    // Send prediction request
    fetch('/api/predict', {
        method: 'POST',
        body: formData
    })
    .then(response => {
        if (!response.ok) {
            return response.json().then(data => {
                throw new Error(data.error || 'Prediction failed');
            });
        }
        return response.json();
    })
    .then(data => {
        clearInterval(interval);
        progressBar.style.width = '100%';

        // Update current analysis
        currentAnalysis.prediction = data.prediction;
        currentAnalysis.imagePath = data.image_path;

        // Display results
        setTimeout(() => {
            displayResults(data);
            progressContainer.classList.add('hidden');
            resultsCard.classList.remove('hidden');
        }, 500);
    })
    .catch(error => {
        clearInterval(interval);
        progressContainer.classList.add('hidden');
        showError(error.message);
    });
}

function displayResults(data) {
    // Display image
    previewImage.src = 'data:image/png;base64,' + data.thumbnail;

    // Severity information
    const severityLevels = ['No DR', 'Mild', 'Moderate', 'Severe', 'Proliferative'];
    const severityText = severityLevels[data.prediction];

    // Update severity badge
    const severityBadge = document.getElementById('severityBadge');
    severityBadge.textContent = '⚕️ ' + severityText;
    severityBadge.className = 'severity-badge severity-' + data.prediction;

    // Update info items
    document.getElementById('severityLevel').textContent = data.prediction + '/4';
    document.getElementById('classification').textContent = severityText;
    document.getElementById('confidence').textContent = data.confidence;

    // Add clinical guidance
    const guidanceMap = {
        0: 'Regular eye checkups recommended. No immediate intervention needed.',
        1: 'Annual eye exams recommended. Monitor for progression.',
        2: 'Urgent eye examination needed. Consider referral to ophthalmologist.',
        3: 'Immediate eye examination required. Specialized treatment may be needed.',
        4: 'URGENT: Immediate ophthalmology consultation required. Treatment recommended.'
    };

    console.log('Analysis complete:', data);
}

// ============================================================================
// REPORT GENERATION
// ============================================================================

function generateReport() {
    if (currentAnalysis.prediction === null) {
        showError('No analysis available');
        return;
    }

    const patientInfo = {
        name: document.getElementById('patientName').value || 'Anonymous',
        email: document.getElementById('patientEmail').value || '',
        phone: document.getElementById('patientPhone').value || ''
    };

    // Show loading
    const reportStatus = document.getElementById('reportStatus');
    reportStatus.classList.remove('hidden');

    fetch('/api/generate-report', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            prediction: currentAnalysis.prediction,
            patient_info: patientInfo,
            image_path: currentAnalysis.imagePath
        })
    })
    .then(response => {
        if (!response.ok) {
            return response.json().then(data => {
                throw new Error(data.error || 'Report generation failed');
            });
        }
        return response.json();
    })
    .then(data => {
        currentAnalysis.report = data.report;
        reportStatus.classList.add('hidden');

        // Show verification modal
        showReportModal(data.report);
    })
    .catch(error => {
        reportStatus.classList.add('hidden');
        showError(error.message);
    });
}

function showReportModal(report) {
    const reportModalBody = document.getElementById('reportModalBody');

    // Format report HTML
    const reportHTML = `
        <div style="font-size: 0.95rem; line-height: 1.8;">
            <h6 style="color: var(--primary-color); font-weight: 700; margin-bottom: 15px;">
                🏥 Team Thiran - Medical Report
            </h6>

            <div style="border-bottom: 2px solid var(--border-color); padding-bottom: 15px; margin-bottom: 15px;">
                <p><strong>Report ID:</strong> ${report.report_id}</p>
                <p><strong>Patient Name:</strong> ${report.patient_name}</p>
                <p><strong>Phone:</strong> ${report.patient_phone || 'Not provided'}</p>
                <p><strong>Date:</strong> ${new Date().toLocaleDateString()}</p>
            </div>

            <div style="background: var(--light-gray); padding: 15px; border-radius: 8px; margin-bottom: 15px;">
                <p><strong>DR Severity Level:</strong> <span class="badge" style="background: var(--primary-color); color: white; font-size: 1rem;">${report.dr_level}/4</span></p>
                <p><strong>Classification:</strong> ${['No DR', 'Mild', 'Moderate', 'Severe', 'Proliferative'][report.dr_level]}</p>
            </div>

            <div style="margin-bottom: 15px;">
                <p><strong>Clinical Findings:</strong></p>
                <p style="color: var(--text-secondary);">${report.clinical_findings}</p>
            </div>

            <div style="margin-bottom: 15px;">
                <p><strong>Recommendations:</strong></p>
                <ul style="color: var(--text-secondary); margin-left: 20px;">
                    ${report.recommendations.map(rec => `<li>${rec}</li>`).join('')}
                </ul>
            </div>

            <div style="background: #ffeaa7; padding: 12px; border-radius: 8px; border-left: 4px solid var(--warning-color);">
                <p style="margin: 0; color: #ff6b6b; font-weight: 600;">
                    ⚠️ This is an automated analysis. Always consult a healthcare professional for diagnosis.
                </p>
            </div>
        </div>
    `;

    reportModalBody.innerHTML = reportHTML;
    reportModal.classList.add('show');
}

function sendReport() {
    const phone = document.getElementById('patientPhone').value;
    const method = document.getElementById('notificationMethod').value;

    if (!phone) {
        showError('Phone number is required to send report');
        return;
    }

    if (!method) {
        showError('Please select a notification method');
        return;
    }

    document.getElementById('sendReportBtn').disabled = true;
    document.getElementById('sendReportBtn').textContent = 'Sending...';

    fetch('/api/send-notification', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            phone: phone,
            method: method,
            report: currentAnalysis.report,
            report_id: currentAnalysis.report.report_id
        })
    })
    .then(response => {
        if (!response.ok) {
            return response.json().then(data => {
                throw new Error(data.error || 'Sending failed');
            });
        }
        return response.json();
    })
    .then(data => {
        closeModal();
        showSuccess('✅ Report sent successfully!');
        resetAnalysis();

        document.getElementById('sendReportBtn').disabled = false;
        document.getElementById('sendReportBtn').textContent = 'Send Report';
    })
    .catch(error => {
        showError('Failed to send report: ' + error.message);
        document.getElementById('sendReportBtn').disabled = false;
        document.getElementById('sendReportBtn').textContent = 'Send Report';
    });
}

// ============================================================================
// MODAL & UI UTILITIES
// ============================================================================

function closeModal() {
    reportModal.classList.remove('show');
}

function resetAnalysis() {
    fileInput.value = '';
    resultsCard.classList.add('hidden');
    progressContainer.classList.add('hidden');
    document.getElementById('patientName').value = '';
    document.getElementById('patientEmail').value = '';
    document.getElementById('patientPhone').value = '';
    document.getElementById('notificationMethod').value = '';

    currentAnalysis = {
        prediction: null,
        imagePath: null,
        report: null
    };
}

function showError(message) {
    errorAlert.classList.remove('hidden');
    document.getElementById('errorText').textContent = message;
    errorAlert.scrollIntoView({ behavior: 'smooth', block: 'center' });
}

function showSuccess(message) {
    const alert = document.createElement('div');
    alert.className = 'alert alert-success alert-dismissible fade show';
    alert.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    document.querySelector('.container').insertBefore(alert, document.querySelector('.card'));
}

// Close modal when clicking outside
document.addEventListener('click', (e) => {
    if (e.target === reportModal) {
        closeModal();
    }
});

// Prevent default drag behavior on page
document.addEventListener('dragover', (e) => {
    e.preventDefault();
});

document.addEventListener('drop', (e) => {
    e.preventDefault();
});
