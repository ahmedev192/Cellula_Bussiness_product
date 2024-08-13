from fastapi import FastAPI, Depends, UploadFile, File, HTTPException, Form, Request, Response, BackgroundTasks, Cookie
from fastapi.security import HTTPBasic
from typing import Literal
from fpdf import FPDF
from datetime import datetime, timedelta
import uuid
import re
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import tempfile
import os
import speech_recognition as sr
from moviepy.editor import AudioFileClip, VideoFileClip
from transformers import pipeline

TEMP_DIR = os.path.join(os.getcwd(), "temps")
os.makedirs(TEMP_DIR, exist_ok=True)

app = FastAPI()
security = HTTPBasic()



# In-memory storage for sessions
session_storage = {}
SESSION_EXPIRY_DURATION = timedelta(hours=2)



# List of valid passwords
VALID_PASSWORDS = {"password1", "password2", "password3", "password4", "password5"}


# Email validation regex
EMAIL_REGEX = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"

def verify_session_token(session_token: str):
    session = session_storage.get(session_token)
    if session and session['expiry_time'] > datetime.now():
        return
    raise HTTPException(status_code=403, detail="Access forbidden: Invalid or expired session")

def send_email_with_pdf(to_email: str, subject: str, body: str, pdf_path: str):
    try:
        sender_email = "cellula.corp@outlook.com"
        sender_password = "Password@0000"

        # Create email message
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        # Attach the PDF file only if it exists
        if pdf_path:
            with open(pdf_path, "rb") as f:
                part = MIMEApplication(f.read(), Name=os.path.basename(pdf_path))
                part['Content-Disposition'] = f'attachment; filename="{os.path.basename(pdf_path)}"'
                msg.attach(part)

        # Configure the SMTP server
        server = smtplib.SMTP('smtp.office365.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)
        server.quit()
        print('Email sent successfully')
    except Exception as e:
        print(f"Failed to send email: {str(e)}")








@app.post("/login")
async def login(request: Request, response: Response, password: str = Form(...), email: str = Form(...)):
    try:
        if password not in VALID_PASSWORDS:
            raise HTTPException(status_code=403, detail="Invalid credentials")
        
        if not re.match(EMAIL_REGEX, email):
            raise HTTPException(status_code=400, detail="Invalid email format")

        old_session_token = request.cookies.get("session_token")
        if old_session_token and old_session_token in session_storage:
            del session_storage[old_session_token]
        
        session_token = str(uuid.uuid4())
        session_storage[session_token] = {
            "email": email,
            "expiry_time": datetime.now() + SESSION_EXPIRY_DURATION
        }

        response.set_cookie(key="session_token", value=session_token, httponly=True, secure=True, samesite='Lax')

        return {"message": "Login successful"}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")









@app.post("/upload")
async def upload_file(
    request: Request,
    background_tasks: BackgroundTasks,
    file_type: Literal['audio', 'video', 'text'] = Form(...),
    summarization_factor: str = Form(...),
    file: UploadFile = File(...),
    session_token: str = Cookie(None),
):
    try:
        verify_session_token(session_token)
        summarization_factor = float(summarization_factor)
        email = session_storage[session_token]['email']

        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(file.file.read())
            temp_file_path = temp_file.name
            print(temp_file_path)

        background_tasks.add_task(summarize_in_background, file_type, summarization_factor, temp_file_path, email)

        return {"message": "File received. You will receive an email once the summarization is complete."}
    except HTTPException as e:
        raise e
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid summarization factor")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")






def summarize(file_type, summarization_factor, file_path: str):
    try:
        if file_type == "video":
            audio_clip = video_to_audio(file_path)
            text = audio_to_text(audio_clip)
        elif file_type == "audio":
            audio_clip = AudioFileClip(file_path)
            text = audio_to_text(audio_clip)
        else:
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()

        summary_text = summarization_model(text, summarization_factor)

        pdf_path = generate_pdf(summary_text)
        
        return pdf_path
    except Exception as e:
        print(f"Summarization failed: {str(e)}")
        return None
    finally:
        try:
            os.remove(file_path)
        except Exception as e:
            print(f"Failed to delete file {file_path}: {str(e)}")







def summarize_in_background(file_type, summarization_factor, file_path: str, email: str):
    try:
        pdf_path = summarize(file_type, summarization_factor, file_path)
        if pdf_path:
            send_email_with_pdf(email, "Your Summarization Result", "Please find the summarized content attached.", pdf_path)
            os.remove(pdf_path)
        else:
            send_email_with_pdf(email, "Summarization Failed", "An error occurred during the summarization process.", None)
    except Exception as e:
        send_email_with_pdf(email, "Summarization Failed", f"An error occurred: {str(e)}", None)









def summarization_model(text, summarization_factor):
    if not (0 < summarization_factor <= 1):
        raise ValueError("Summarization factor must be between 0 and 1.")

    summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
    original_length = len(text.split())
    max_length = int(original_length * summarization_factor)
    min_length = max(10, int(max_length * 0.5))

    summary = summarizer(
        text,
        max_length=max_length,
        min_length=min_length,
        do_sample=False
    )

    return summary[0]['summary_text']







def audio_to_text(audio_clip):
    with tempfile.NamedTemporaryFile(suffix=".wav", dir=TEMP_DIR, delete=False) as temp_audio_file:
        audio_clip.write_audiofile(temp_audio_file.name, codec='pcm_s16le')
        temp_audio_file_path = temp_audio_file.name
    
    recognizer = sr.Recognizer()
    try:
        with sr.AudioFile(temp_audio_file_path) as source:
            audio_data = recognizer.record(source)
            try:
                text = recognizer.recognize_google(audio_data)
            except sr.UnknownValueError:
                text = "Speech was unintelligible"
            except sr.RequestError:
                text = "Could not request results from the speech recognition service"
    finally:
        os.remove(temp_audio_file_path)
    
    return text






def video_to_audio(video_path):
    video = VideoFileClip(video_path)
    audio = video.audio
    return audio





def generate_pdf(summary_text):
    pdf_path = tempfile.mktemp(suffix=".pdf")
    pdf = FPDF()
    pdf.add_page()
    pdf.add_font("DejaVu", "", "fonts/DejaVuSans.ttf", uni=True)
    pdf.set_font("DejaVu", size=12)
    pdf.multi_cell(0, 10, summary_text)
    pdf.output(pdf_path)
    return pdf_path