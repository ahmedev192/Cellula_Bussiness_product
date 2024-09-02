# from fastapi import FastAPI, Depends, UploadFile, File, HTTPException, Form, Request, Response, BackgroundTasks, Cookie
# from fastapi.security import HTTPBasic
# from typing import Literal
# from fpdf import FPDF
# from datetime import datetime, timedelta
# import uuid
# import re
# import smtplib
# from email.mime.text import MIMEText
# from email.mime.multipart import MIMEMultipart
# from email.mime.application import MIMEApplication
# import tempfile
# import os
# import speech_recognition as sr
# from moviepy.editor import AudioFileClip, VideoFileClip
# from transformers import pipeline
# from datetime import datetime
# from starlette.middleware.cors import CORSMiddleware
# from fastapi.responses import FileResponse
# from fastapi import FastAPI, Depends
# from fastapi.responses import RedirectResponse
# from fastapi.staticfiles import StaticFiles

# TEMP_DIR = os.path.join(os.getcwd(), "temps")
# os.makedirs(TEMP_DIR, exist_ok=True)

# app = FastAPI()
# # Serve static files from the "frontend" directory
# app.mount("/frontend", StaticFiles(directory="frontend"), name="frontend")

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],  # Adjust as necessary
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )
# security = HTTPBasic()



# # In-memory storage for sessions
# session_storage = {}
# SESSION_EXPIRY_DURATION = timedelta(hours=2)



# # List of valid passwords
# # VALID_PASSWORDS = {"password1", "password2", "password3", "password4", "password5"}
# VALID_PASSWORDS = {
#     "A2#b3@d4", "C9!f7%k2", "M8&x5^n6", "R1$e8@w3", "Q2!t7#b6", "S7%l2*c5", "V4@r9^g1", 
#     "P6&n3$m8", "X5^f7#w2", "D3!r6$k9", "Y9@p2#l5", "Z8^c7&t4", "J1%h3!b6", "T4#n2@w7", 
#     "K2$l5%c8", "F7!r9#j3", "G6^m2&x4", "L3$p8@q5", "U5!y7#n2", "E8^f3&s6", "N4@k1$l9", 
#     "W9!m7#t2", "B6%p5@v8", "A1&c3#r7", "D7^g2!x4", "M2%w5$n3", "X8#y7@k4", "T3$l9^f1", 
#     "F4!c6@p2", "P5%n8#r3", "V7^t2!w6", "R9&m3#j4", "K1@f6$l8", "C2#n7%y9", "Z6^b4@r3", 
#     "W8!p5#l1", "S7%c2&t9", "L3$r8!j6", "Y4@w9^m2", "G5%k1!x3", "B6&n7#p4", "E2^r3@j9", 
#     "H1$l5%f8", "Q7!w9#t3", "M6&p4^b2", "T3@r8$n7", "D9!c1#y5", "J2^m6%f3", "L8&p7@r2", 
#     "S1$k9#x4", "W2!n6^b3", "X5@l7$y8", "C6#r2&n9", "G3^w4!k1", "Q8%m7@p2", "A9$r6#j5", 
#     "H4!f3&x2", "N7^t1@p9", "K3%y8#l4", "J6&r2!b5", "P5@n7^x8", "F3#c9$w1", "R4!t2@l6", 
#     "T9^m3&k7", "V2#j8%p4", "Y5@r1$l7", "B8!x6^n2", "A3%f7$w9", "L1@c5#k4", "C2&j9!p7", 
#     "M7$r4^t1", "N6!x2%y8", "W3@b8#f9", "J9^l5&p2", "H1!k6@n3", "Q8$c4@t7", "S2#f7^x5", 
#     "D9&l3!r4", "P6^w2$k7", "G7@n1%m3", "K4#y5!p8", "C8$l6^r3", "B2!f1@k9", "X5%j4&t7", 
#     "W9#p3^l1", "R2!t8@n7", "M6$y1%k4", "L9^x7&c2", "V3@r8#j1", "S7^f5%p4", "J1$l9!t3", 
#     "F6!c2@r8", "Q3#k7^p5", "A8%w1$l4", "H9&n2!j3", "T4@r6$x9", "N5!c7#p2", "B1$y8^k4", 
#     "M6%t3@f9", "G9!j5&l2", "K4^w8#p7", "X2@r9%f1", "Y5!n7^l3", "L3$p9!k2", "V7&w6@t4", 
#     "C1#f3%r8", "D8@l9!k2", "J7^n3$y4", "W4!p5#t6", "F9%k2^j8", "T1@r7$w3", "S8^p6!c2", 
#     "H4!y3@n7", "Q9^m2#p5", "N5@k1$l8", "B3$r8!c2", "L7%t4^f1", "G6@r3$n5", "X9!j5#y2", 
#     "A4%p7^k1", "V3&r8!c2", "P6@l9$w4", "F7#y2^k3", "C8!r1@m5", "S2^p4&j7", "M9@l6#t5", 
#     "Y5%k3!r1", "T4$w2@f8", "J6^n7#p9", "H1!c5^r3", "Q7@p4$l2", "G9%m3&k8", "N2#t1^r7", 
#     "B5@l3$p8", "L9!y6!w1", "D4#n2@m7", "X3@k5%t8", "V8^r9#p1", "W1$y4@n3", "S7!f6^k9", 
#     "J3@p8$r2", "A9%t4&n1", "M5!k2@l7", "C6^w3!r9", "F1$l8#y7", "P4%k9@c2", "T6^n3!p8", 
#     "H2#r5%j9", "L8@k1$w4", "B3!f7^p6", "password"
# }



# # Email validation regex
# EMAIL_REGEX = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"

# def verify_session_token(session_token: str):
#     session = session_storage.get(session_token)
#     if session and session['expiry_time'] > datetime.now():
#         return
#     raise HTTPException(status_code=403, detail="Access forbidden: Invalid or expired session")

# def send_email_with_pdf(to_email: str, subject: str, body: str, pdf_path: str):
#     try:
#         sender_email = "cellula.corp@outlook.com"
#         sender_password = "Password@0000"

#         # Create email message
#         msg = MIMEMultipart()
#         msg['From'] = sender_email
#         msg['To'] = to_email
#         msg['Subject'] = subject
#         msg.attach(MIMEText(body, 'plain'))

#         # Attach the PDF file only if it exists
#         if pdf_path:
#             with open(pdf_path, "rb") as f:
#                 part = MIMEApplication(f.read(), Name=os.path.basename(pdf_path))
#                 part['Content-Disposition'] = f'attachment; filename="{os.path.basename(pdf_path)}"'
#                 msg.attach(part)

#         # Configure the SMTP server
#         server = smtplib.SMTP('smtp.office365.com', 587)
#         server.starttls()
#         server.login(sender_email, sender_password)
#         server.send_message(msg)
#         server.quit()
#         print('Email sent successfully')
#     except Exception as e:
#         print(f"Failed to send email: {str(e)}")






# def get_session(session_token: str = Cookie(None)):
#     if not session_token or session_token not in session_storage:
#         raise HTTPException(status_code=403, detail="Session not found or expired")
#     print("current Session Token : " + session_token)
#     verify_session_token(session_token)
    
#     return session_token





# @app.post("/login")
# async def login(
#     request: Request, 
#     response: Response, 
#     password: str = Form(...), 
#     email: str = Form(...)
# ):
#     try:
#         if password not in VALID_PASSWORDS:
#             raise HTTPException(status_code=403, detail="Invalid credentials")
        
#         if not re.match(EMAIL_REGEX, email):
#             raise HTTPException(status_code=400, detail="Invalid email format")

#         old_session_token = request.cookies.get("session_token")
#         if old_session_token and old_session_token in session_storage:
#             del session_storage[old_session_token]
        
#         session_token = str(uuid.uuid4())
#         session_storage[session_token] = {
#             "email": email,
#             "expiry_time": datetime.now() + SESSION_EXPIRY_DURATION
#         }

#         response.set_cookie(
#             key="session_token", 
#             value=session_token, 
#             httponly=True, 
#             secure=True, 
#             samesite='Lax'
#         )

#         # Redirect to the upload page after a successful login
#         redirect_response = RedirectResponse(url="/upload", status_code=302)
#         redirect_response.set_cookie(
#             key="session_token", 
#             value=session_token, 
#             httponly=True, 
#             secure=True, 
#             samesite='Lax'
#         )


#         return redirect_response
    
#     except HTTPException as e:
#         raise e
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")








# @app.get("/chat")
# def redirect_to_whatsapp():
#     # WhatsApp link for messaging you directly
#     whatsapp_link = "https://wa.me/+201027443136"

#     # Redirect to WhatsApp link
#     return RedirectResponse(url=whatsapp_link)



# @app.get("/upload")
# async def upload():
#     return FileResponse('./frontend/HTML/timeKnife.html')




# @app.get("/")
# async def root():
#     return FileResponse('./frontend/HTML/index.html')



# @app.get("/login")
# async def root():
#     return FileResponse('./frontend/HTML/loginToTimeKnife.html')












# @app.post("/upload")
# async def upload_file(
#     request: Request,
#     background_tasks: BackgroundTasks,
#     file_type: Literal['audio', 'video', 'text'] = Form(...),
#     summarization_factor: str = Form(...),
#     file: UploadFile = File(...),
#     session_token: str = Depends(get_session),
# ):

#     try:
#         summarization_factor = float(summarization_factor)
#         email = session_storage[session_token]['email']

#         with tempfile.NamedTemporaryFile(delete=False) as temp_file:
#             temp_file.write(file.file.read())
#             temp_file_path = temp_file.name
#             print(temp_file_path)

#         background_tasks.add_task(summarize_in_background, file_type, summarization_factor, temp_file_path, email)

#         return {"message": "File received. You will receive an email once the summarization is complete."}
#     except HTTPException as e:
#         raise e
#     except ValueError:
#         raise HTTPException(status_code=400, detail="Invalid summarization factor")
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")






# def summarize(file_type, summarization_factor, file_path: str):
#     try:
#         if file_type == "video":
#             audio_clip = video_to_audio(file_path)
#             text = audio_to_text(audio_clip)
#         elif file_type == "audio":
#             audio_clip = AudioFileClip(file_path)
#             text = audio_to_text(audio_clip)
#         else:
#             with open(file_path, 'r', encoding='utf-8') as f:
#                 text = f.read()

#         summary_text = summarization_model(text, summarization_factor)

#         pdf_path = generate_pdf(summary_text)
        
#         return pdf_path
#     except Exception as e:
#         print(f"Summarization failed: {str(e)}")
#         return None
#     finally:
#         try:
#             os.remove(file_path)
#         except Exception as e:
#             print(f"Failed to delete file {file_path}: {str(e)}")







# def summarize_in_background(file_type, summarization_factor, file_path: str, email: str):
#     try:
#         pdf_path = summarize(file_type, summarization_factor, file_path)
#         if pdf_path:
#             send_email_with_pdf(email, "Your Summarization Result", "Please find the summarized content attached.", pdf_path)
#             os.remove(pdf_path)
#         else:
#             send_email_with_pdf(email, "Summarization Failed", "An error occurred during the summarization process.", None)
#     except Exception as e:
#         send_email_with_pdf(email, "Summarization Failed", f"An error occurred: {str(e)}", None)









# def summarization_model(text, summarization_factor, chunk_size=512):
#     if not (0 < summarization_factor <= 1):
#         raise ValueError("Summarization factor must be between 0 and 1.")

#     summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
#     text_chunks = [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]
#     summaries = []

#     for chunk in text_chunks:
#         original_length = len(chunk.split())
#         max_length = int(original_length * summarization_factor)
#         min_length = max(10, int(max_length * 0.5))

#         summary = summarizer(
#             chunk,
#             max_length=max_length,
#             min_length=min_length,
#             do_sample=False
#         )
#         summaries.append(summary[0]['summary_text'])

#     return " ".join(summaries)







# def audio_to_text(audio_clip):
#     with tempfile.NamedTemporaryFile(suffix=".wav", dir=TEMP_DIR, delete=False) as temp_audio_file:
#         audio_clip.write_audiofile(temp_audio_file.name, codec='pcm_s16le')
#         temp_audio_file_path = temp_audio_file.name
    
#     recognizer = sr.Recognizer()
#     try:
#         with sr.AudioFile(temp_audio_file_path) as source:
#             audio_data = recognizer.record(source)
#             try:
#                 text = recognizer.recognize_google(audio_data)
#             except sr.UnknownValueError:
#                 text = "Speech was unintelligible"
#             except sr.RequestError:
#                 text = "Could not request results from the speech recognition service"
#     finally:
#         os.remove(temp_audio_file_path)
    
#     return text






# def video_to_audio(video_path):
#     video = VideoFileClip(video_path)
#     audio = video.audio
#     return audio





# def generate_pdf(summary_text):
#     pdf_path = tempfile.mktemp(suffix=".pdf")
#     pdf = FPDF()
#     pdf.add_page()
#     pdf.add_font("DejaVu", "", "fonts/DejaVuSans.ttf", uni=True)
#     pdf.set_font("DejaVu", size=12)
#     pdf.multi_cell(0, 10, summary_text)
#     pdf.output(pdf_path)
#     return pdf_path







# # Chat Boot : 



# # Initialize a sentence transformer model
# embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

# def query_database(message: str):
#     # Convert the message to an embedding
#     message_embedding = embedding_model.encode([message])  # This returns a list of embeddings

#     # Query ChromaDB using the embedding
#     results = collection.query(embeddings=message_embedding)
#     print("Query results:", results)

#     return results



# # Initialize the ChromaDB client
# chroma_client = chromadb.Client()

# # Assuming you've already created a collection in ChromaDB
# collection = chroma_client.get_or_create_collection("my_collection")
# ###################################################### collection.add(query=query, response=correct_response) hn add info bta3t el company
# # Session storage for chat history
# chat_history = {}

# class ChatEntry(BaseModel):
#     message: str
#     timestamp: str

# class Message(BaseModel):
#     message: str  # Remove session_id from the Message class


# class Response(BaseModel):
#     session_id: str
#     response: str
#     history: List[ChatEntry]

# def query_database(message: str):
#     # Query ChromaDB to get the closest match
#     results = collection.query(message)
#     return results

# def check_scope(result) -> bool:
#     # Define a threshold to determine if the result is within the scope
#     threshold = 0.7  # Example threshold
    
#     # Check if the result contains the score
#     if "score" in result:
#         return result["score"] >= threshold
#     else:
#         print("Result does not contain 'score'. Full result:", result)
#         return False





# @app.post("/chat", response_model=Response)
# def chat(message: Message, session_token: str = Depends(get_session)):
#     session_id = session_token  # Use the session token as the session ID
    
#     user_message = message.message

#     # Initialize chat history if not present
#     if session_id not in chat_history:
#         chat_history[session_id] = []

#     # Get current timestamp
#     timestamp = datetime.now().isoformat()

#     # Add the user message to the chat history with timestamp
#     chat_history[session_id].append(ChatEntry(message=f"User: {user_message}", timestamp=timestamp))

#     # Convert the user message to an embedding
#     message_embedding = embedding_model.encode([user_message])  # Convert to embedding list

#     # Query the database with the embedding
#     result = query_database(message_embedding)

#     # Check if the response is in scope
#     if check_scope(result):
#         response = result["data"]
#     else:
#         response = "It's out of my scope, please contact us."

#     # Add the bot response to the chat history with timestamp
#     chat_history[session_id].append(ChatEntry(message=f"Bot: {response}", timestamp=timestamp))

#     # Sort the history by timestamp
#     sorted_history = sorted(chat_history[session_id], key=lambda x: x.timestamp)

#     return Response(session_id=session_id, response=response, history=sorted_history)



# @app.get("/chat/history", response_model=List[ChatEntry])
# def get_history(session_id: str = Depends(get_session)):
#     # Get the session ID from the session dependency
#     session_id = session_id  # Use the session token as the session ID

#     # Check if the session ID exists in the chat history
#     if session_id not in chat_history:
#         # Return an empty list or an appropriate response if the session ID does not exist
#         return []

#     # Sort the chat history by timestamp before returning
#     sorted_history = sorted(chat_history[session_id], key=lambda x: x.timestamp)
    
#     return sorted_history












from flask import Flask, request, redirect, send_file, url_for, render_template, make_response
from flask_cors import CORS
from werkzeug.utils import secure_filename
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
from concurrent.futures import ThreadPoolExecutor

TEMP_DIR = os.path.join(os.getcwd(), "temps")
os.makedirs(TEMP_DIR, exist_ok=True)

app = Flask(__name__)
executor = ThreadPoolExecutor(max_workers=4)

CORS(app)  # Add CORS support

session_storage = {}
SESSION_EXPIRY_DURATION = timedelta(hours=2)

# List of valid passwords
VALID_PASSWORDS = {
    "A2#b3@d4", "C9!f7%k2", "M8&x5^n6", "R1$e8@w3", "Q2!t7#b6", "S7%l2*c5", "V4@r9^g1", 
    "P6&n3$m8", "X5^f7#w2", "D3!r6$k9", "Y9@p2#l5", "Z8^c7&t4", "J1%h3!b6", "T4#n2@w7", 
    "K2$l5%c8", "F7!r9#j3", "G6^m2&x4", "L3$p8@q5", "U5!y7#n2", "E8^f3&s6", "N4@k1$l9", 
    "W9!m7#t2", "B6%p5@v8", "A1&c3#r7", "D7^g2!x4", "M2%w5$n3", "X8#y7@k4", "T3$l9^f1", 
    "F4!c6@p2", "P5%n8#r3", "V7^t2!w6", "R9&m3#j4", "K1@f6$l8", "C2#n7%y9", "Z6^b4@r3", 
    "W8!p5#l1", "S7%c2&t9", "L3$r8!j6", "Y4@w9^m2", "G5%k1!x3", "B6&n7#p4", "E2^r3@j9", 
    "H1$l5%f8", "Q7!w9#t3", "M6&p4^b2", "T3@r8$n7", "D9!c1#y5", "J2^m6%f3", "L8&p7@r2", 
    "S1$k9#x4", "W2!n6^b3", "X5@l7$y8", "C6#r2&n9", "G3^w4!k1", "Q8%m7@p2", "A9$r6#j5", 
    "H4!f3&x2", "N7^t1@p9", "K3%y8#l4", "J6&r2!b5", "P5@n7^x8", "F3#c9$w1", "R4!t2@l6", 
    "T9^m3&k7", "V2#j8%p4", "Y5@r1$l7", "B8!x6^n2", "A3%f7$w9", "L1@c5#k4", "C2&j9!p7", 
    "M7$r4^t1", "N6!x2%y8", "W3@b8#f9", "J9^l5&p2", "H1!k6@n3", "Q8$c4@t7", "S2#f7^x5", 
    "D9&l3!r4", "P6^w2$k7", "G7@n1%m3", "K4#y5!p8", "C8$l6^r3", "B2!f1@k9", "X5%j4&t7", 
    "W9#p3^l1", "R2!t8@n7", "M6$y1%k4", "L9^x7&c2", "V3@r8#j1", "S7^f5%p4", "J1$l9!t3", 
    "F6!c2@r8", "Q3#k7^p5", "A8%w1$l4", "H9&n2!j3", "T4@r6$x9", "N5!c7#p2", "B1$y8^k4", 
    "M6%t3@f9", "G9!j5&l2", "K4^w8#p7", "X2@r9%f1", "Y5!n7^l3", "L3$p9!k2", "V7&w6@t4", 
    "C1#f3%r8", "D8@l9!k2", "J7^n3$y4", "W4!p5#t6", "F9%k2^j8", "T1@r7$w3", "S8^p6!c2", 
    "H4!y3@n7", "Q9^m2#p5", "N5@k1$l8", "B3$r8!c2", "L7%t4^f1", "G6@r3$n5", "X9!j5#y2", 
    "A4%p7^k1", "V3&r8!c2", "P6@l9$w4", "F7#y2^k3", "C8!r1@m5", "S2^p4&j7", "M9@l6#t5", 
    "Y5%k3!r1", "T4$w2@f8", "J6^n7#p9", "H1!c5^r3", "Q7@p4$l2", "G9%m3&k8", "N2#t1^r7", 
    "B5@l3$p8", "L9!y6!w1", "D4#n2@m7", "X3@k5%t8", "V8^r9#p1", "W1$y4@n3", "S7!f6^k9", 
    "J3@p8$r2", "A9%t4&n1", "M5!k2@l7", "C6^w3!r9", "F1$l8#y7", "P4%k9@c2", "T6^n3!p8", 
    "H2#r5%j9", "L8@k1$w4", "B3!f7^p6", "password"
}

EMAIL_REGEX = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"

def verify_session_token(session_token):
    session = session_storage.get(session_token)
    if session and session['expiry_time'] > datetime.now():
        return
    raise Exception("Access forbidden: Invalid or expired session")

def send_email_with_pdf(to_email, subject, body, pdf_path):
    try:
        sender_email = "cellula.corp@outlook.com"
        sender_password = "Password@0000"

        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        if pdf_path:
            with open(pdf_path, "rb") as f:
                part = MIMEApplication(f.read(), Name=os.path.basename(pdf_path))
                part['Content-Disposition'] = f'attachment; filename="{os.path.basename(pdf_path)}"'
                msg.attach(part)

        server = smtplib.SMTP('smtp.office365.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)
        server.quit()
        print('Email sent successfully')
    except Exception as e:
        print(f"Failed to send email: {str(e)}")

@app.route("/login", methods=["POST"])
def login():
    password = request.form.get("password")
    email = request.form.get("email")
    if password not in VALID_PASSWORDS:
        return "Invalid credentials", 403

    if not re.match(EMAIL_REGEX, email):
        return "Invalid email format", 400

    old_session_token = request.cookies.get("session_token")
    if old_session_token and old_session_token in session_storage:
        del session_storage[old_session_token]

    session_token = str(uuid.uuid4())
    session_storage[session_token] = {
        "email": email,
        "expiry_time": datetime.now() + SESSION_EXPIRY_DURATION
    }

    response = make_response(redirect(url_for('upload')))
    response.set_cookie("session_token", session_token, httponly=True, secure=True, samesite='Lax')
    return response

@app.route("/chat")
def redirect_to_whatsapp():
    whatsapp_link = "https://wa.me/+201027443136"
    return redirect(whatsapp_link)

@app.route("/upload", methods=["GET", "POST"])
def upload():
    if request.method == "POST":
        file_type = request.form.get("file_type")
        summarization_factor = request.form.get("summarization_factor")
        file = request.files.get("file")

        session_token = request.cookies.get("session_token")
        if not session_token or session_token not in session_storage:
            return "Session not found or expired", 403

        verify_session_token(session_token)
        email = session_storage[session_token]['email']

        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            file.save(temp_file)
            temp_file_path = temp_file.name

        summarize_in_background(file_type, float(summarization_factor), temp_file_path, email)
        return "File received. You will receive an email once the summarization is complete."

    return render_template('timeKnife.html')

@app.route("/")
def root():
    return render_template('index.html')

@app.route("/login")
def login_page():
    return render_template('loginToTimeKnife.html')


def summarize(file_type, summarization_factor, file_path):
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

def summarize_in_background(file_type, summarization_factor, file_path, email):
    executor.submit(process_summary, file_type, summarization_factor, file_path, email)

def process_summary(file_type, summarization_factor, file_path, email):
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

if __name__ == "__main__":
    app.run(debug=True)
