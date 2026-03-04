/*-----------------------------------*\
  #DOM ELEMENTS
\*-----------------------------------*/

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

/*-----------------------------------*\
  #STATE
\*-----------------------------------*/

let selectedFile = null;
let lastResult   = null;

/*-----------------------------------*\
  #SEVERITY MAPS
\*-----------------------------------*/

const severityLevels = {
  0: 'Level 0 — No DR',
  1: 'Level 1 — Mild',
  2: 'Level 2 — Moderate',
  3: 'Level 3 — Severe',
  4: 'Level 4 — Proliferative DR'
};

/*-----------------------------------*\
  #SHOW / HIDE CARDS
\*-----------------------------------*/

function showCard(cardId) {
  ['upload-card', 'loading-card', 'result-card', 'error-card'].forEach(id => {
    document.getElementById(id).style.display = 'none';
  });
  document.getElementById(cardId).style.display = 'block';
}

/*-----------------------------------*\
  #HANDLE FILE
\*-----------------------------------*/

function handleFile(file) {
  if (!file) return;
  const allowed = ['image/jpeg', 'image/jpg', 'image/png'];
  if (!allowed.includes(file.type)) {
    showError('Invalid file type. Please upload a JPG or PNG image.');
    return;
  }
  selectedFile = file;
  const reader = new FileReader();
  reader.onload = (e) => {
    previewImg.src               = e.target.result;
    fileName.textContent         = file.name;
    previewContainer.style.display = 'block';
    analyzeBtn.disabled          = false;
  };
  reader.readAsDataURL(file);
}

/*-----------------------------------*\
  #DRAG & DROP
\*-----------------------------------*/

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
  handleFile(e.dataTransfer.files[0]);
});

document.getElementById('browse-btn').addEventListener('click', (e) => {
  e.stopPropagation();
  fileInput.click();
});

fileInput.addEventListener('change', () => handleFile(fileInput.files[0]));

/*-----------------------------------*\
  #ANALYZE
\*-----------------------------------*/

analyzeBtn.addEventListener('click', async () => {
  if (!selectedFile) return;
  showCard('loading-card');
  try {
    const formData = new FormData();
    formData.append('file', selectedFile);
    const response = await fetch('/api/v1/predict', { method: 'POST', body: formData });
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

/*-----------------------------------*\
  #SHOW RESULT
\*-----------------------------------*/

function showResult(data) {
  // Normalize confidence to percentage
  data.confidence = data.confidence <= 1 ? data.confidence * 100 : data.confidence;
  lastResult = data;

  resultBadge.className        = `result-badge ${data.color}`;
  resultLabel.textContent      = data.severity_label;
  resultLevel.textContent      = severityLevels[data.severity_level];
  resultConfidence.textContent = `${data.confidence.toFixed(1)}%`;
  resultAdvice.textContent     = data.advice;

  // Animate confidence bar
  const bar = document.getElementById('confidence-bar');
  if (bar) setTimeout(() => bar.style.width = `${data.confidence.toFixed(1)}%`, 300);

  // Wire report button
  const reportBtn = document.getElementById('report-btn');
  if (reportBtn) reportBtn.onclick = () => openReportModal(data);

  showCard('result-card');
}

/*-----------------------------------*\
  #SHOW ERROR
\*-----------------------------------*/

function showError(message) {
  errorMessage.textContent = message;
  showCard('error-card');
}

/*-----------------------------------*\
  #RESET
\*-----------------------------------*/

function resetApp() {
  selectedFile                   = null;
  lastResult                     = null;
  fileInput.value                = '';
  previewImg.src                 = '';
  fileName.textContent           = '';
  previewContainer.style.display = 'none';
  analyzeBtn.disabled            = true;
  showCard('upload-card');
}

resetBtn.addEventListener('click', resetApp);
errorResetBtn.addEventListener('click', resetApp);

/*-----------------------------------*\
  #REPORT MODAL
\*-----------------------------------*/

const reportModalOverlay = document.getElementById('report-modal-overlay');
const modalCloseBtn      = document.getElementById('modal-close-btn');
const modalCancelBtn     = document.getElementById('modal-cancel-btn');
const generateReportBtn  = document.getElementById('generate-report-btn');
const modalGenerating    = document.getElementById('modal-generating');

function openReportModal(result) {
  lastResult = result;
  const now  = new Date();

  document.getElementById('prev-severity').textContent   = result.severity_label || '—';
  document.getElementById('prev-level').textContent      = `Level ${result.severity_level ?? '—'}`;
  document.getElementById('prev-confidence').textContent = `${result.confidence.toFixed(1)}%`;
  document.getElementById('prev-date').textContent       = now.toLocaleDateString('en-GB',
    { day: '2-digit', month: 'short', year: 'numeric' });
  document.getElementById('prev-advice').textContent     = result.advice || '';

  const prevBar = document.getElementById('prev-conf-bar');
  if (prevBar) setTimeout(() => prevBar.style.width = `${result.confidence.toFixed(1)}%`, 400);

  reportModalOverlay.classList.add('active');
  document.body.style.overflow = 'hidden';
}

function closeReportModal() {
  reportModalOverlay.classList.remove('active');
  document.body.style.overflow = '';
  if (modalGenerating) modalGenerating.style.display = 'none';
}

modalCloseBtn?.addEventListener('click',  closeReportModal);
modalCancelBtn?.addEventListener('click', closeReportModal);
reportModalOverlay?.addEventListener('click', (e) => {
  if (e.target === reportModalOverlay) closeReportModal();
});

/*-----------------------------------*\
  #GENERATE PDF REPORT
\*-----------------------------------*/

generateReportBtn?.addEventListener('click', async () => {
  const nameInput = document.getElementById('pt-name');
  const ageInput  = document.getElementById('pt-age');
  nameInput.classList.remove('error');
  ageInput.classList.remove('error');

  let valid = true;
  if (!nameInput.value.trim()) { nameInput.classList.add('error'); nameInput.focus(); valid = false; }
  if (!ageInput.value.trim())  { ageInput.classList.add('error'); if (valid) ageInput.focus(); valid = false; }
  if (!valid) return;

  modalGenerating.style.display = 'flex';

  const patient = {
    name:              nameInput.value.trim(),
    patient_id:        document.getElementById('pt-id').value.trim(),
    age:               ageInput.value.trim(),
    gender:            document.getElementById('pt-gender').value,
    dob:               document.getElementById('pt-dob').value,
    contact:           document.getElementById('pt-contact').value.trim(),
    diabetes_type:     document.getElementById('pt-diabetes-type').value,
    diabetes_duration: document.getElementById('pt-diabetes-duration').value.trim(),
    referring_doctor:  document.getElementById('pt-doctor').value.trim(),
    eye:               document.getElementById('pt-eye').value,
    notes:             document.getElementById('pt-notes').value.trim(),
  };

  try {
    const response = await fetch('/api/v1/generate-report', {
      method:  'POST',
      headers: { 'Content-Type': 'application/json' },
      body:    JSON.stringify({ patient, result: lastResult })
    });

    if (!response.ok) {
      const err = await response.json();
      throw new Error(err.detail || 'Report generation failed');
    }

    const blob = await response.blob();
    const url  = URL.createObjectURL(blob);
    const a    = document.createElement('a');
    a.href     = url;
    a.download = `DR_Report_${patient.name.replace(/\s+/g, '_')}_${new Date().toISOString().split('T')[0]}.pdf`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    closeReportModal();

  } catch (err) {
    alert(`Error: ${err.message}`);
  } finally {
    modalGenerating.style.display = 'none';
  }
});

/*-----------------------------------*\
  #CAMERA — WebRTC (Mac / Desktop / Mobile)
  Runs inside DOMContentLoaded so all
  modal elements are guaranteed to exist
\*-----------------------------------*/

document.addEventListener('DOMContentLoaded', () => {

  const cameraBtn          = document.getElementById('camera-btn');
  const cameraModalOverlay = document.getElementById('camera-modal-overlay');
  const cameraModalClose   = document.getElementById('camera-modal-close');
  const cameraVideo        = document.getElementById('camera-video');
  const cameraCanvas       = document.getElementById('camera-canvas');
  const cameraCaptureBtn   = document.getElementById('camera-capture-btn');
  const cameraRetakeBtn    = document.getElementById('camera-retake-btn');
  const cameraUseBtn       = document.getElementById('camera-use-btn');
  const cameraSwitchBtn    = document.getElementById('camera-switch-btn');
  const cameraPreviewWrap  = document.getElementById('camera-preview-wrap');
  const cameraPreviewImg   = document.getElementById('camera-preview-img');
  const cameraControlsLive = document.getElementById('camera-controls-live');
  const cameraControlsPrev = document.getElementById('camera-controls-preview');
  const cameraError        = document.getElementById('camera-error');
  const cameraErrorMsg     = document.getElementById('camera-error-msg');

  let cameraStream = null;
  let capturedBlob = null;
  let facingMode   = 'user';   // 'user' = front/webcam | 'environment' = rear

  // ── Open camera modal ──────────────────────────────────────────────────────
  cameraBtn?.addEventListener('click', (e) => {
    e.stopPropagation();

    // Must be on localhost or https — give clear message if not
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
      alert(
        'Camera not available.\n\n' +
        'Chrome only allows camera access on:\n' +
        '  • http://localhost:8000\n' +
        '  • https:// domains\n\n' +
        'Please open: http://localhost:8000\n' +
        'instead of http://0.0.0.0:8000'
      );
      return;
    }

    openCameraModal();
  });

  // ── Reset modal state & show ───────────────────────────────────────────────
  async function openCameraModal() {
    cameraError.style.display        = 'none';
    cameraPreviewWrap.style.display  = 'none';
    cameraControlsLive.style.display = 'flex';
    cameraControlsPrev.style.display = 'none';
    capturedBlob = null;

    cameraModalOverlay.classList.add('active');
    document.body.style.overflow = 'hidden';

    await startCamera();
  }

  // ── Start webcam stream ────────────────────────────────────────────────────
  async function startCamera() {
    stopCamera();   // always stop previous stream first
    try {
      cameraStream = await navigator.mediaDevices.getUserMedia({
        video: {
          facingMode,
          width:  { ideal: 1280 },
          height: { ideal: 720  },
        },
        audio: false,
      });
      cameraVideo.srcObject     = cameraStream;
      cameraVideo.style.display = 'block';
      cameraError.style.display = 'none';

    } catch (err) {
      cameraVideo.style.display = 'none';
      cameraError.style.display = 'flex';

      if (err.name === 'NotAllowedError') {
        cameraErrorMsg.textContent =
          'Camera access denied.\n\nGo to Chrome → Settings → Privacy & Security → Camera and allow this site.';
      } else if (err.name === 'NotFoundError') {
        cameraErrorMsg.textContent = 'No camera found on this device.';
      } else {
        cameraErrorMsg.textContent = `Camera error: ${err.message}`;
      }
    }
  }

  // ── Stop webcam stream ─────────────────────────────────────────────────────
  function stopCamera() {
    if (cameraStream) {
      cameraStream.getTracks().forEach(track => track.stop());
      cameraStream = null;
    }
    cameraVideo.srcObject = null;
  }

  // ── Switch front / rear camera ─────────────────────────────────────────────
  cameraSwitchBtn?.addEventListener('click', async () => {
    facingMode = facingMode === 'user' ? 'environment' : 'user';
    await startCamera();
  });

  // ── Capture snapshot from live video ──────────────────────────────────────
  cameraCaptureBtn?.addEventListener('click', () => {
    const canvas  = cameraCanvas;
    canvas.width  = cameraVideo.videoWidth  || 1280;
    canvas.height = cameraVideo.videoHeight || 720;

    const ctx = canvas.getContext('2d');

    // Mirror for front camera so photo matches the live preview
    if (facingMode === 'user') {
      ctx.translate(canvas.width, 0);
      ctx.scale(-1, 1);
    }
    ctx.drawImage(cameraVideo, 0, 0, canvas.width, canvas.height);

    // Show captured preview
    cameraPreviewImg.src             = canvas.toDataURL('image/jpeg', 0.95);
    cameraPreviewWrap.style.display  = 'block';
    cameraVideo.style.display        = 'none';
    cameraControlsLive.style.display = 'none';
    cameraControlsPrev.style.display = 'flex';

    // Store blob for "Use This Photo"
    canvas.toBlob((blob) => { capturedBlob = blob; }, 'image/jpeg', 0.95);
  });

  // ── Retake photo ───────────────────────────────────────────────────────────
  cameraRetakeBtn?.addEventListener('click', () => {
    capturedBlob                     = null;
    cameraPreviewWrap.style.display  = 'none';
    cameraVideo.style.display        = 'block';
    cameraControlsLive.style.display = 'flex';
    cameraControlsPrev.style.display = 'none';
  });

  // ── Use captured photo ─────────────────────────────────────────────────────
  cameraUseBtn?.addEventListener('click', () => {
    if (!capturedBlob) return;
    const file = new File(
      [capturedBlob],
      `webcam_${Date.now()}.jpg`,
      { type: 'image/jpeg' }
    );
    closeCameraModal();
    handleFile(file);   // ✅ reuses existing handleFile — untouched
  });

  // ── Close camera modal ─────────────────────────────────────────────────────
  function closeCameraModal() {
    stopCamera();
    cameraModalOverlay.classList.remove('active');
    document.body.style.overflow = '';
    capturedBlob = null;
  }

  cameraModalClose?.addEventListener('click', closeCameraModal);

  cameraModalOverlay?.addEventListener('click', (e) => {
    if (e.target === cameraModalOverlay) closeCameraModal();
  });

  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && cameraModalOverlay?.classList.contains('active')) {
      closeCameraModal();
    }
  });

}); // ── end DOMContentLoaded