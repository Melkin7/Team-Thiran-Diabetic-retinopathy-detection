// ── DOM Elements ──────────────────────────────────────────────────────────────
const dropZone         = document.getElementById('drop-zone');
const fileInput        = document.getElementById('file-input');
const previewContainer = document.getElementById('preview-container');
const previewImg       = document.getElementById('preview-img');
const fileName         = document.getElementById('file-name');
const analyzeBtn       = document.getElementById('analyze-btn');

const uploadCard       = document.getElementById('upload-card');
const loadingCard      = document.getElementById('loading-card');
const resultCard       = document.getElementById('result-card');
const errorCard        = document.getElementById('error-card');

const resultBadge      = document.getElementById('result-badge');
const resultLabel      = document.getElementById('result-label');
const resultLevel      = document.getElementById('result-level');
const resultConfidence = document.getElementById('result-confidence');
const resultAdvice     = document.getElementById('result-advice');
const errorMessage     = document.getElementById('error-message');

const resetBtn         = document.getElementById('reset-btn');
const errorResetBtn    = document.getElementById('error-reset-btn');

// ── State ─────────────────────────────────────────────────────────────────────
let selectedFile = null;

// ── Severity Level Labels ─────────────────────────────────────────────────────
const severityLevels = {
    0: 'Level 0 — No DR',
    1: 'Level 1 — Mild',
    2: 'Level 2 — Moderate',
    3: 'Level 3 — Severe',
    4: 'Level 4 — Proliferative DR'
};

// ── Show/Hide Cards ───────────────────────────────────────────────────────────
function showCard(cardId) {
    ['upload-card', 'loading-card', 'result-card', 'error-card'].forEach(id => {
        document.getElementById(id).style.display = 'none';
    });
    document.getElementById(cardId).style.display = 'block';
}

// ── Handle File Selection ─────────────────────────────────────────────────────
function handleFile(file) {
    if (!file) return;

    // Validate type
    const allowed = ['image/jpeg', 'image/jpg', 'image/png'];
    if (!allowed.includes(file.type)) {
        showError('Invalid file type. Please upload a JPG or PNG image.');
        return;
    }

    selectedFile = file;

    // Show preview
    const reader = new FileReader();
    reader.onload = (e) => {
        previewImg.src = e.target.result;
        fileName.textContent = file.name;
        previewContainer.style.display = 'block';
        analyzeBtn.disabled = false;
    };
    reader.readAsDataURL(file);
}

// ── Drag & Drop Events ────────────────────────────────────────────────────────
dropZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropZone.classList.add('dragover');
});

dropZone.addEventListener('dragleave', () => {
    dropZone.classList.remove('dragover');
});

dropZone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropZone.classList.remove('dragover');
    const file = e.dataTransfer.files[0];
    handleFile(file);
});

// FIX: Browse button triggers file input — dropzone click no longer conflicts
document.getElementById('browse-btn').addEventListener('click', (e) => {
    e.stopPropagation();
    fileInput.click();
});

fileInput.addEventListener('change', () => {
    handleFile(fileInput.files[0]);
});

// ── Analyze Button Click ──────────────────────────────────────────────────────
analyzeBtn.addEventListener('click', async () => {
    if (!selectedFile) return;

    showCard('loading-card');

    try {
        const formData = new FormData();
        formData.append('file', selectedFile);

        const response = await fetch('/api/v1/predict', {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            const err = await response.json();
            throw new Error(err.detail || 'Server error occurred.');
        }

        const data = await response.json();
        showResult(data);

    } catch (error) {
        showError(error.message);
    }
});

// ── Show Result ───────────────────────────────────────────────────────────────
function showResult(data) {
    resultBadge.className        = `result-badge ${data.color}`;
    resultLabel.textContent      = data.severity_label;
    resultLevel.textContent      = severityLevels[data.severity_level];
    resultConfidence.textContent = `${(data.confidence * 100).toFixed(1)}%`;
    resultAdvice.textContent     = data.advice;

    showCard('result-card');
}

// ── Show Error ────────────────────────────────────────────────────────────────
function showError(message) {
    errorMessage.textContent = message;
    showCard('error-card');
}

// ── Reset ─────────────────────────────────────────────────────────────────────
function resetApp() {
    selectedFile = null;
    fileInput.value = '';
    previewImg.src = '';
    fileName.textContent = '';
    previewContainer.style.display = 'none';
    analyzeBtn.disabled = true;
    showCard('upload-card');
}

resetBtn.addEventListener('click', resetApp);
errorResetBtn.addEventListener('click', resetApp);