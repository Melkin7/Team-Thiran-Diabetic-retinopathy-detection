# ── Imports ───────────────────────────────────────────────────────────────────
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import uvicorn
import shutil
import os
import uuid
import tempfile
import torch
import pathlib
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from io import BytesIO
import base64
from datetime import datetime

from backend.model import load_model, main as model_predict

# ── Twilio WhatsApp ───────────────────────────────────────────────────────────
try:
    from twilio.rest import Client as TwilioClient
    TWILIO_AVAILABLE = True
except ImportError:
    TWILIO_AVAILABLE = False
    print("⚠️  Twilio not installed — WhatsApp notifications disabled")

def send_whatsapp_notification(patient_name: str, severity_label: str, confidence: float, pdf_buffer: BytesIO = None):
    """Send WhatsApp notification with PDF report after DR report generation"""
    if not TWILIO_AVAILABLE:
        print("⚠️  Twilio not available")
        return False
    try:
        account_sid   = os.getenv("TWILIO_ACCOUNT_SID", "")
        auth_token    = os.getenv("TWILIO_AUTH_TOKEN", "")
        from_whatsapp = os.getenv("TWILIO_WHATSAPP", "whatsapp:+14155238886")
        to_whatsapp   = os.getenv("RECIPIENT_PHONE", "")
        public_host   = os.getenv("PUBLIC_HOST", "http://localhost:8000")

        if not to_whatsapp.startswith("whatsapp:"):
            to_whatsapp = f"whatsapp:{to_whatsapp}"

        if not all([account_sid, auth_token, to_whatsapp]) or account_sid == "your_account_sid_here":
            print("⚠️  Twilio credentials not configured — skipping WhatsApp")
            return False

        # Normalize confidence
        if confidence <= 1.0:
            confidence = confidence * 100

        client = TwilioClient(account_sid, auth_token)

        # ── Save PDF temporarily & build public URL ────────────────────
        media_url    = None
        tmp_pdf_path = None

        if pdf_buffer:
            reports_dir  = os.path.join(os.path.dirname(__file__), "reports")
            os.makedirs(reports_dir, exist_ok=True)

            tmp_filename = f"DR_Report_{uuid.uuid4().hex[:8]}.pdf"
            tmp_pdf_path = os.path.join(reports_dir, tmp_filename)

            pdf_buffer.seek(0)
            with open(tmp_pdf_path, "wb") as f:
                f.write(pdf_buffer.read())
            pdf_buffer.seek(0)

            media_url = f"{public_host}/reports/{tmp_filename}"
            print(f"📄 PDF saved: {tmp_pdf_path}")
            print(f"🔗 Media URL: {media_url}")

        message_body = (
            f"🏥 *Doclab — DR Screening Result*\n\n"
            f"👤 Patient: {patient_name}\n"
            f"🔬 Diagnosis: {severity_label}\n"
            f"📊 Confidence: {confidence:.1f}%\n\n"
            f"📄 Your full medical report is attached.\n"
            f"Please consult your ophthalmologist for further evaluation.\n"
            f"— Team Thiran | Doclab AI"
        )

        # ── Send with PDF if URL is available ─────────────────────────
        if media_url:
            message = client.messages.create(
                body=message_body,
                from_=from_whatsapp,
                to=to_whatsapp,
                media_url=[media_url]
            )
        else:
            message = client.messages.create(
                body=message_body,
                from_=from_whatsapp,
                to=to_whatsapp
            )

        print(f"✅ WhatsApp sent with PDF! SID: {message.sid}")
        return True

    except Exception as e:
        print(f"⚠️  WhatsApp notification failed: {e}")
        return False

# ── DR Severity Metadata ──────────────────────────────────────────────────────
severity_info = {
    0: {"label": "No DR",            "color": "green",   "advice": "No signs of diabetic retinopathy detected."},
    1: {"label": "Mild",             "color": "yellow",  "advice": "Mild DR detected. Schedule a follow-up within 12 months."},
    2: {"label": "Moderate",         "color": "orange",  "advice": "Moderate DR detected. Schedule a follow-up within 6 months."},
    3: {"label": "Severe",           "color": "red",     "advice": "Severe DR detected. Immediate ophthalmologist referral required."},
    4: {"label": "Proliferative DR", "color": "darkred", "advice": "Proliferative DR detected. Urgent treatment required immediately."},
}

# ── Global model store ────────────────────────────────────────────────────────
ml_model = None

# ── Lifespan: Load model ONCE when server starts ──────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    global ml_model
    print("Loading model at startup...")
    ml_model = load_model()
    print("Model ready!")
    yield
    print("Server shutting down...")

# ── App Initialization ────────────────────────────────────────────────────────
app = FastAPI(
    title="Team Thiran - Diabetic Retinopathy Detection API",
    description="ResNet152-based DR classification API",
    version="1.0.0",
    lifespan=lifespan
)

# ── CORS Middleware ───────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Serve Frontend Static Files ───────────────────────────────────────────────
app.mount("/static", StaticFiles(directory="frontend/web"), name="static")

# ── Serve Generated PDF Reports ───────────────────────────────────────────────
pathlib.Path("reports").mkdir(exist_ok=True)
app.mount("/reports", StaticFiles(directory="reports"), name="reports")

# ── Routes ────────────────────────────────────────────────────────────────────
@app.get("/")
def root():
    return FileResponse("frontend/web/index.html")

@app.get("/api/v1/health")
def health_check():
    return {
        "status": "healthy",
        "model": "ResNet152",
        "classes": 5,
        "device": "cuda" if torch.cuda.is_available() else "cpu"
    }

@app.post("/api/v1/predict")
async def predict(file: UploadFile = File(...)):
    allowed_types = ["image/jpeg", "image/png", "image/jpg"]
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type: {file.content_type}. Only JPEG/PNG allowed."
        )

    tmp_path = None
    try:
        suffix = os.path.splitext(file.filename)[1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            shutil.copyfileobj(file.file, tmp)
            tmp_path = tmp.name

        value, label, confidence = model_predict(tmp_path, ml_model)

        return JSONResponse(content={
            "success":        True,
            "severity_level": value,
            "severity_label": label,
            "confidence":     confidence,
            "color":          severity_info[value]["color"],
            "advice":         severity_info[value]["advice"]
        })

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")

    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.remove(tmp_path)

@app.post("/api/v1/generate-report")
async def generate_report(request: dict):
    try:
        patient = request.get("patient", {})
        result  = request.get("result",  {})

        buffer = BytesIO()
        doc    = SimpleDocTemplate(
            buffer, pagesize=A4,
            rightMargin=2*cm, leftMargin=2*cm,
            topMargin=2*cm,   bottomMargin=2*cm
        )

        # ── Colors ─────────────────────────────────────────────────────
        TEAL       = colors.HexColor("#007B8A")
        DARK_TEAL  = colors.HexColor("#003D4C")
        LIGHT_GRAY = colors.HexColor("#F0F4F5")
        WHITE      = colors.white
        BLACK      = colors.HexColor("#1A1A1A")
        MID_GRAY   = colors.HexColor("#666666")

        SEV_COLORS = {
            "green":   colors.HexColor("#16A34A"),
            "yellow":  colors.HexColor("#CA8A04"),
            "orange":  colors.HexColor("#EA580C"),
            "red":     colors.HexColor("#DC2626"),
            "darkred": colors.HexColor("#991B1B"),
        }
        badge_color = SEV_COLORS.get(result.get("color", "green"), TEAL)

        # ── Styles ──────────────────────────────────────────────────────
        def ps(name, size, font="Helvetica", color=BLACK, align=TA_LEFT, space_before=0, space_after=4, leading=None):
            return ParagraphStyle(name, fontSize=size, fontName=font,
                                  textColor=color, alignment=align,
                                  spaceBefore=space_before, spaceAfter=space_after,
                                  leading=leading or size*1.4)

        S = {
            "h_white":    ps("hw",  20, "Helvetica-Bold", WHITE,     TA_CENTER),
            "sub_white":  ps("sw",   9, "Helvetica",      WHITE,     TA_CENTER),
            "small_gray": ps("sg",   8, "Helvetica",      MID_GRAY,  TA_LEFT),
            "section":    ps("sec", 11, "Helvetica-Bold", DARK_TEAL, TA_LEFT, 14, 6),
            "normal":     ps("nm",  10, "Helvetica",      BLACK),
            "bold":       ps("bd",  10, "Helvetica-Bold", BLACK),
            "badge":      ps("bg",  14, "Helvetica-Bold", WHITE,     TA_CENTER),
            "small":      ps("sm",   8, "Helvetica",      MID_GRAY,  TA_CENTER),
            "disclaimer": ps("di",   7, "Helvetica-Oblique", MID_GRAY, TA_CENTER),
            "key":        ps("ky",   9, "Helvetica-Bold", DARK_TEAL),
            "val":        ps("vl",   9, "Helvetica",      BLACK),
        }

        elements = []
        now = datetime.now()
        W   = 17.5 * cm

        # ── 1. HEADER BANNER ────────────────────────────────────────────
        header_data = [[
            Paragraph("<b>TEAM THIRAN</b>", ps("ht", 18, "Helvetica-Bold", WHITE, TA_LEFT)),
            Paragraph("Diabetic Retinopathy<br/>Detection System", ps("hst", 9, "Helvetica", WHITE, TA_CENTER)),
            Paragraph(f"Report ID<br/><b>TT-{now.strftime('%Y%m%d%H%M%S')}</b>",
                      ps("hid", 8, "Helvetica", WHITE, TA_RIGHT)),
        ]]
        ht = Table(header_data, colWidths=[5*cm, 8*cm, 4.5*cm])
        ht.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (-1,-1), DARK_TEAL),
            ("PADDING",    (0,0), (-1,-1), 14),
            ("VALIGN",     (0,0), (-1,-1), "MIDDLE"),
        ]))
        elements += [ht, Spacer(1, 0.3*cm)]

        # Meta bar
        meta = [[
            Paragraph(f"Date: <b>{now.strftime('%B %d, %Y')}</b>", S["small_gray"]),
            Paragraph(f"Time: <b>{now.strftime('%I:%M %p')}</b>", S["small_gray"]),
            Paragraph("Model: <b>ResNet152 v1.0</b>", S["small_gray"]),
            Paragraph("Institution: <b>Team Thiran</b>", S["small_gray"]),
        ]]
        mt = Table(meta, colWidths=[W/4]*4)
        mt.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (-1,-1), LIGHT_GRAY),
            ("PADDING",    (0,0), (-1,-1), 8),
            ("ALIGN",      (0,0), (-1,-1), "CENTER"),
        ]))
        elements += [mt, Spacer(1, 0.4*cm)]

        # ── 2. PATIENT INFORMATION ───────────────────────────────────────
        elements.append(Paragraph("PATIENT INFORMATION", S["section"]))
        elements.append(HRFlowable(width="100%", thickness=1.5, color=TEAL, spaceAfter=10))

        pt_rows = [
            [Paragraph("Full Name",     S["key"]), Paragraph(patient.get("name","N/A"),             S["val"]),
             Paragraph("Patient ID",    S["key"]), Paragraph(patient.get("patient_id","N/A"),        S["val"])],
            [Paragraph("Age",           S["key"]), Paragraph(str(patient.get("age","N/A")),          S["val"]),
             Paragraph("Gender",        S["key"]), Paragraph(patient.get("gender","N/A"),            S["val"])],
            [Paragraph("Date of Birth", S["key"]), Paragraph(patient.get("dob","N/A"),              S["val"]),
             Paragraph("Contact",       S["key"]), Paragraph(patient.get("contact","N/A"),           S["val"])],
            [Paragraph("Diabetes Type", S["key"]), Paragraph(patient.get("diabetes_type","N/A"),     S["val"]),
             Paragraph("Duration",      S["key"]), Paragraph(patient.get("diabetes_duration","N/A"), S["val"])],
            [Paragraph("Referring Dr",  S["key"]), Paragraph(patient.get("referring_doctor","N/A"),  S["val"]),
             Paragraph("Eye Examined",  S["key"]), Paragraph(patient.get("eye","Both Eyes"),         S["val"])],
        ]
        pt = Table(pt_rows, colWidths=[3*cm, 5.75*cm, 3*cm, 5.75*cm])
        pt.setStyle(TableStyle([
            ("BACKGROUND",     (0,0), (0,-1), LIGHT_GRAY),
            ("BACKGROUND",     (2,0), (2,-1), LIGHT_GRAY),
            ("PADDING",        (0,0), (-1,-1), 9),
            ("GRID",           (0,0), (-1,-1), 0.4, colors.HexColor("#DDDDDD")),
            ("ROWBACKGROUNDS", (1,0), (-1,-1), [WHITE, colors.HexColor("#FAFAFA")]),
        ]))
        elements += [pt, Spacer(1, 0.4*cm)]

        # ── 3. DIAGNOSIS RESULT ──────────────────────────────────────────
        elements.append(Paragraph("DIAGNOSIS RESULT", S["section"]))
        elements.append(HRFlowable(width="100%", thickness=1.5, color=TEAL, spaceAfter=10))

        confidence = float(result.get("confidence", 0))
        sev_level  = int(result.get("severity_level", 0))
        sev_label  = result.get("severity_label", "No DR")
        advice     = result.get("advice", "")

        if confidence <= 1.0:
            confidence = confidence * 100

        risk_map   = ["None","Low","Moderate","High","Critical"]
        action_map = ["Annual Screening","Monitor in 12 months",
                      "Monitor in 6 months","Urgent Referral","Emergency Treatment"]

        badge = Table(
            [[Paragraph(f"{sev_label}  ·  Level {sev_level}/4  ·  Confidence {confidence:.1f}%", S["badge"])]],
            colWidths=[W]
        )
        badge.setStyle(TableStyle([
            ("BACKGROUND",     (0,0), (-1,-1), badge_color),
            ("PADDING",        (0,0), (-1,-1), 14),
            ("ROUNDEDCORNERS", [8]),
        ]))
        elements += [badge, Spacer(1, 0.25*cm)]

        filled = int(confidence / 5)
        bar_p  = Paragraph(
            f"<font name='Helvetica-Bold' color='#007B8A'>{'█' * filled}</font>"
            f"<font color='#CCCCCC'>{'░' * (20-filled)}</font>  {confidence:.1f}%",
            ps("bar", 10, color=DARK_TEAL)
        )
        elements += [bar_p, Spacer(1, 0.2*cm)]

        res_rows = [
            [Paragraph("Severity Level",     S["key"]), Paragraph(f"Level {sev_level} — {sev_label}", S["val"])],
            [Paragraph("Confidence Score",   S["key"]), Paragraph(f"{confidence:.2f}%",               S["val"])],
            [Paragraph("Risk Category",      S["key"]), Paragraph(risk_map[sev_level],                S["val"])],
            [Paragraph("Recommended Action", S["key"]), Paragraph(action_map[sev_level],              S["val"])],
            [Paragraph("AI Model Used",      S["key"]), Paragraph("ResNet152 (Fine-tuned on APTOS 2019)", S["val"])],
        ]
        rt = Table(res_rows, colWidths=[4.5*cm, 13*cm])
        rt.setStyle(TableStyle([
            ("BACKGROUND",     (0,0), (0,-1), LIGHT_GRAY),
            ("PADDING",        (0,0), (-1,-1), 10),
            ("GRID",           (0,0), (-1,-1), 0.4, colors.HexColor("#DDDDDD")),
            ("ROWBACKGROUNDS", (1,0), (-1,-1), [WHITE, colors.HexColor("#FAFAFA")]),
        ]))
        elements += [rt, Spacer(1, 0.25*cm)]

        adv = Table(
            [[Paragraph("Clinical Advice", S["key"]), Paragraph(advice, S["val"])]],
            colWidths=[3.5*cm, 14*cm]
        )
        adv.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (-1,-1), colors.HexColor("#E8F8F8")),
            ("LINEBEFORE", (0,0), (0,-1),  4, TEAL),
            ("PADDING",    (0,0), (-1,-1), 11),
        ]))
        elements += [adv, Spacer(1, 0.4*cm)]

        # ── 4. DR SEVERITY REFERENCE TABLE ──────────────────────────────
        elements.append(Paragraph("DR SEVERITY REFERENCE SCALE", S["section"]))
        elements.append(HRFlowable(width="100%", thickness=1.5, color=TEAL, spaceAfter=10))

        scale_header = [
            Paragraph("Level",          ps("sh", 9,"Helvetica-Bold",WHITE,TA_CENTER)),
            Paragraph("Classification", ps("sh2",9,"Helvetica-Bold",WHITE,TA_CENTER)),
            Paragraph("Risk",           ps("sh3",9,"Helvetica-Bold",WHITE,TA_CENTER)),
            Paragraph("Features",       ps("sh4",9,"Helvetica-Bold",WHITE,TA_CENTER)),
            Paragraph("Action",         ps("sh5",9,"Helvetica-Bold",WHITE,TA_CENTER)),
        ]
        scale_rows = [
            scale_header,
            ["0","No DR",         "None",     "No abnormalities",                        "Annual screening"],
            ["1","Mild NPDR",     "Low",      "Microaneurysms only",                     "Follow-up 12 months"],
            ["2","Moderate NPDR", "Moderate", "Hemorrhages, hard exudates",              "Follow-up 6 months"],
            ["3","Severe NPDR",   "High",     "Venous beading, IRMA",                    "Urgent referral"],
            ["4","Proliferative", "Critical", "Neovascularisation, vitreous hemorrhage", "Emergency treatment"],
        ]
        row_bgs = [DARK_TEAL,
                   colors.HexColor("#F0FFF4"), colors.HexColor("#FEFCE8"),
                   colors.HexColor("#FFF7ED"), colors.HexColor("#FFF1F1"),
                   colors.HexColor("#FFEBEB")]

        st = Table(scale_rows, colWidths=[1.2*cm, 3.5*cm, 2*cm, 6*cm, 4.8*cm])
        sc_style = [
            ("BACKGROUND", (0,0), (-1,0),  DARK_TEAL),
            ("TEXTCOLOR",  (0,0), (-1,0),  WHITE),
            ("FONTNAME",   (0,1), (-1,-1), "Helvetica"),
            ("FONTSIZE",   (0,0), (-1,-1), 9),
            ("PADDING",    (0,0), (-1,-1), 8),
            ("GRID",       (0,0), (-1,-1), 0.4, colors.HexColor("#DDDDDD")),
            ("ALIGN",      (0,0), (0,-1),  "CENTER"),
            ("FONTNAME",   (0, sev_level+1), (-1, sev_level+1), "Helvetica-Bold"),
        ]
        for i, bg in enumerate(row_bgs):
            sc_style.append(("BACKGROUND", (0,i), (-1,i), bg))
        st.setStyle(TableStyle(sc_style))
        elements += [st, Spacer(1, 0.4*cm)]

        # ── 5. CLINICAL NOTES ────────────────────────────────────────────
        elements.append(Paragraph("CLINICAL NOTES", S["section"]))
        elements.append(HRFlowable(width="100%", thickness=1.5, color=TEAL, spaceAfter=10))

        notes = patient.get("notes") or "No additional clinical notes provided."
        nt = Table([[Paragraph(notes, S["normal"])]], colWidths=[W])
        nt.setStyle(TableStyle([
            ("BACKGROUND",   (0,0), (-1,-1), LIGHT_GRAY),
            ("PADDING",      (0,0), (-1,-1), 12),
            ("MINROWHEIGHT", (0,0), (-1,-1), 50),
            ("GRID",         (0,0), (-1,-1), 0.4, colors.HexColor("#DDDDDD")),
        ]))
        elements += [nt, Spacer(1, 0.4*cm)]

        # ── 6. SIGNATURE SECTION ─────────────────────────────────────────
        elements.append(Paragraph("VERIFICATION & SIGNATURES", S["section"]))
        elements.append(HRFlowable(width="100%", thickness=1.5, color=TEAL, spaceAfter=10))

        sig_style = ps("sig", 9, color=BLACK, align=TA_CENTER, space_after=0)
        sig_data  = [[
            Paragraph("Physician / Reviewer\n\n\n\n_______________________\nSignature & Stamp", sig_style),
            Paragraph("Patient Acknowledgment\n\n\n\n_______________________\nPatient Signature",  sig_style),
            Paragraph(f"Date Verified\n\n\n\n_______________________\n{now.strftime('%B %d, %Y')}", sig_style),
        ]]
        sig = Table(sig_data, colWidths=[W/3]*3)
        sig.setStyle(TableStyle([
            ("BOX",        (0,0), (-1,-1), 0.5, colors.HexColor("#CCCCCC")),
            ("INNERGRID",  (0,0), (-1,-1), 0.5, colors.HexColor("#CCCCCC")),
            ("PADDING",    (0,0), (-1,-1), 18),
            ("VALIGN",     (0,0), (-1,-1), "TOP"),
            ("BACKGROUND", (0,0), (-1,-1), LIGHT_GRAY),
        ]))
        elements += [sig, Spacer(1, 0.35*cm)]

        # ── 7. FOOTER ────────────────────────────────────────────────────
        elements.append(HRFlowable(width="100%", thickness=0.5,
                                   color=colors.HexColor("#CCCCCC"), spaceAfter=6))
        elements.append(Paragraph(
            "⚠ DISCLAIMER: This report is AI-generated for informational purposes only and does not constitute "
            "a clinical diagnosis. Consult a qualified ophthalmologist for medical decisions.",
            S["disclaimer"]
        ))
        elements.append(Paragraph(
            f"Team Thiran · Diabetic Retinopathy Detection System · ResNet152 · "
            f"Generated: {now.strftime('%Y-%m-%d %H:%M:%S')}",
            ps("ft", 7, color=colors.HexColor("#AAAAAA"), align=TA_CENTER)
        ))

        # ── BUILD PDF ─────────────────────────────────────────────────────
        doc.build(elements)
        buffer.seek(0)

        # ── Send WhatsApp with PDF attachment ─────────────────────────────
        try:
            send_whatsapp_notification(
                patient_name   = patient.get("name", "Patient"),
                severity_label = result.get("severity_label", "Unknown"),
                confidence     = float(result.get("confidence", 0)),
                pdf_buffer     = buffer
            )
        except Exception as wa_err:
            print(f"⚠️  WhatsApp send failed (non-critical): {wa_err}")

        # ── Return PDF to browser ─────────────────────────────────────────
        buffer.seek(0)
        filename = f"DR_Report_{patient.get('name','Patient').replace(' ','_')}_{now.strftime('%Y%m%d')}.pdf"
        return StreamingResponse(
            buffer,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Report generation failed: {str(e)}")

# ── Run Server ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    uvicorn.run("server:app", host="127.0.0.1", port=8000, reload=True)