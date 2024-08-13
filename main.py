from fastapi import FastAPI, Depends, UploadFile, File, HTTPException, Form, Request
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from typing import Literal
from io import BytesIO
from fpdf import FPDF
from fastapi.responses import StreamingResponse
from datetime import datetime, timedelta
from summarize_utils import summarize  # Import the summarize function

app = FastAPI()
security = HTTPBasic()

# List of valid passwords
VALID_PASSWORDS = ["password1", "password2", "password3", "password4", "password5"]

# In-memory storage for IP addresses and their expiry times
ip_storage = {}
IP_VALIDITY_DURATION = timedelta(hours=2)

def verify_ip(request: Request):
    ip = request.client.host
    current_time = datetime.now()
    if ip in ip_storage:
        if ip_storage[ip] > current_time:
            return  # IP is valid
    raise HTTPException(status_code=403, detail="Access forbidden: Invalid or expired IP")

@app.post("/login")
async def login(request: Request, password: str = Form(...)):
    if password not in VALID_PASSWORDS:
        raise HTTPException(status_code=403, detail="Invalid credentials")
    
    ip = request.client.host
    ip_storage[ip] = datetime.now() + IP_VALIDITY_DURATION
    return {"message": "Login successful"}

def convert_text_to_pdf(text: str) -> BytesIO:
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, text)
    pdf_output = BytesIO()
    pdf_output.write(pdf.output(dest='S').encode('latin1'))  # Encode as bytes and write to BytesIO
    pdf_output.seek(0)
    return pdf_output

@app.post("/upload")
async def upload_file(
    request: Request,  # Place request parameter first
    file_type: Literal['audio', 'video', 'text'] = Form(...),
    summarization_factor: str = Form(...), 
    file: UploadFile = File(...)
):
    # Verify IP before processing
    verify_ip(request)
    summarization_factor = float(summarization_factor)
    print(f"file_type: {file_type}, summarization_factor: {summarization_factor}")
    
    # Process the file and summarization factor
    summarized_text = summarize(file_type, summarization_factor, file)
    print(f"{summarized_text}")

    # Convert summarized text to PDF
    pdf = convert_text_to_pdf(summarized_text)
    
    return StreamingResponse(pdf, media_type="application/pdf", headers={"Content-Disposition": "attachment; filename=summarized_text.pdf"})

