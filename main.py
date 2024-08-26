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
from pydantic import BaseModel
from typing import List
import chromadb
from datetime import datetime
from sentence_transformers import SentenceTransformer


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









def summarization_model(text, summarization_factor, chunk_size=512):
    if not (0 < summarization_factor <= 1):
        raise ValueError("Summarization factor must be between 0 and 1.")

    summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
    text_chunks = [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]
    summaries = []

    for chunk in text_chunks:
        original_length = len(chunk.split())
        max_length = int(original_length * summarization_factor)
        min_length = max(10, int(max_length * 0.5))

        summary = summarizer(
            chunk,
            max_length=max_length,
            min_length=min_length,
            do_sample=False
        )
        summaries.append(summary[0]['summary_text'])

    return " ".join(summaries)







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








# Chat Boot : 



# Initialize a sentence transformer model
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

def query_database(message: str):
    # Convert the message to an embedding
    message_embedding = embedding_model.encode([message])  # This returns a list of embeddings

    # Query ChromaDB using the embedding
    results = collection.query(embeddings=message_embedding)
    print("Query results:", results)

    return results



# Initialize the ChromaDB client
chroma_client = chromadb.Client()

# Assuming you've already created a collection in ChromaDB
collection = chroma_client.get_or_create_collection("my_collection")
###################################################### collection.add(query=query, response=correct_response) hn add info bta3t el company
# Session storage for chat history
chat_history = {}

class ChatEntry(BaseModel):
    message: str
    timestamp: str

class Message(BaseModel):
    message: str  # Remove session_id from the Message class


class Response(BaseModel):
    session_id: str
    response: str
    history: List[ChatEntry]

def query_database(message: str):
    # Query ChromaDB to get the closest match
    results = collection.query(message)
    return results

def check_scope(result) -> bool:
    # Define a threshold to determine if the result is within the scope
    threshold = 0.7  # Example threshold
    
    # Check if the result contains the score
    if "score" in result:
        return result["score"] >= threshold
    else:
        print("Result does not contain 'score'. Full result:", result)
        return False


def get_session(session_token: str = Cookie(None)):
    if not session_token or session_token not in session_storage:
        raise HTTPException(status_code=403, detail="Session not found or expired")
    
    verify_session_token(session_token)
    
    return session_token




@app.post("/chat", response_model=Response)
def chat(message: Message, session_token: str = Depends(get_session)):
    session_id = session_token  # Use the session token as the session ID
    
    user_message = message.message

    # Initialize chat history if not present
    if session_id not in chat_history:
        chat_history[session_id] = []

    # Get current timestamp
    timestamp = datetime.now().isoformat()

    # Add the user message to the chat history with timestamp
    chat_history[session_id].append(ChatEntry(message=f"User: {user_message}", timestamp=timestamp))

    # Convert the user message to an embedding
    message_embedding = embedding_model.encode([user_message])  # Convert to embedding list

    # Query the database with the embedding
    result = query_database(message_embedding)

    # Check if the response is in scope
    if check_scope(result):
        response = result["data"]
    else:
        response = "It's out of my scope, please contact us."

    # Add the bot response to the chat history with timestamp
    chat_history[session_id].append(ChatEntry(message=f"Bot: {response}", timestamp=timestamp))

    # Sort the history by timestamp
    sorted_history = sorted(chat_history[session_id], key=lambda x: x.timestamp)

    return Response(session_id=session_id, response=response, history=sorted_history)



@app.get("/chat/history", response_model=List[ChatEntry])
def get_history(session_id: str = Depends(get_session)):
    # Get the session ID from the session dependency
    session_id = session_id  # Use the session token as the session ID

    # Check if the session ID exists in the chat history
    if session_id not in chat_history:
        # Return an empty list or an appropriate response if the session ID does not exist
        return []

    # Sort the chat history by timestamp before returning
    sorted_history = sorted(chat_history[session_id], key=lambda x: x.timestamp)
    
    return sorted_history