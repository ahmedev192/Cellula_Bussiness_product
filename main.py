from fastapi import FastAPI, Depends, UploadFile, File, HTTPException, Form, Request
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from typing import Literal
from io import BytesIO
from fpdf import FPDF
from fastapi.responses import StreamingResponse
from datetime import datetime, timedelta
from summarize_utils import summarize  # Import the summarize function
from fastapi.middleware.cors import CORSMiddleware
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph
import mimetypes

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins; adjust this for production
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)
security = HTTPBasic()

# List of valid passwords
VALID_PASSWORDS = {"password1", "password2", "password3", "password4", "password5"}

# In-memory storage for IP addresses and their expiry times
ip_storage = {}
IP_VALIDITY_DURATION = timedelta(hours=2)

def verify_ip(request: Request):
    ip = request.client.host
    current_time = datetime.now()
    if ip_storage.get(ip) and ip_storage[ip] > current_time:
        return
    raise HTTPException(status_code=403, detail="Access forbidden: Invalid or expired IP")

@app.post("/login")
async def login(request: Request, password: str = Form(...)):
    try:
        if password not in VALID_PASSWORDS:
            raise HTTPException(status_code=403, detail="Invalid credentials")

        ip = request.client.host
        ip_storage[ip] = datetime.now() + IP_VALIDITY_DURATION
        return {"message": "Login successful"}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

def convert_text_to_pdf(text: str) -> BytesIO:
    try:
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)

        # Get default styles
        styles = getSampleStyleSheet()
        style = styles['BodyText']

        # Create a Paragraph with text and style
        paragraph = Paragraph(text, style)

        # Build the PDF
        doc.build([paragraph])

        buffer.seek(0)
        return buffer
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating PDF: {str(e)}")

@app.post("/upload")
async def upload_file(
    request: Request,
    file_type: Literal['audio', 'video', 'text'] = Form(...),
    summarization_factor: str = Form(...),
    file: UploadFile = File(...)
):
    try:
        # Verify IP before processing
        verify_ip(request)

        summarization_factor = float(summarization_factor)
        
        if file_type not in {'audio', 'video', 'text'}:
            raise HTTPException(status_code=400, detail="Invalid file type")

        # Check file extension and MIME type
        file_ext = file.filename.split('.')[-1].lower()
        mime_type, _ = mimetypes.guess_type(file.filename)

        if file_type == 'audio' and (file_ext != 'mp3' or mime_type != 'audio/mpeg'):
            raise HTTPException(status_code=400, detail="Invalid audio file format")
        if file_type == 'video' and (file_ext != 'mp4' or mime_type != 'video/mp4'):
            raise HTTPException(status_code=400, detail="Invalid video file format")
        if file_type == 'text' and (file_ext != 'txt' or mime_type != 'text/plain'):
            raise HTTPException(status_code=400, detail="Invalid text file format")

        try:
            summarized_text = summarize(file_type, summarization_factor, file)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error during summarization: {str(e)}")

        pdf = convert_text_to_pdf(summarized_text)

        return StreamingResponse(
            pdf,
            media_type="application/pdf",
            headers={"Content-Disposition": "attachment; filename=summarized_text.pdf"}
        )
    except HTTPException as e:
        raise e
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid summarization factor")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
