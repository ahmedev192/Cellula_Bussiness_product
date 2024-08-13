import io
import tempfile
import os
import speech_recognition as sr
from moviepy.editor import AudioFileClip, VideoFileClip
from transformers import pipeline
from fastapi import UploadFile

# Define the temporary directory relative to the current working directory
TEMP_DIR = os.path.join(os.getcwd(), "temps")

# Ensure the temporary directory exists
os.makedirs(TEMP_DIR, exist_ok=True)

def summarize(file_type, summarization_factor, file: UploadFile):
    temp_file_paths = []
    
    try:
        if file_type == "video":
            # Save the uploaded video file to a temporary location
            with tempfile.NamedTemporaryFile(suffix=".mp4", dir=TEMP_DIR, delete=False) as temp_file:
                temp_file.write(file.file.read())
                temp_video_path = temp_file.name
            temp_file_paths.append(temp_video_path)

            # Convert video to audio
            audio = video_to_audio(temp_video_path)
            text = audio_to_text(audio)
            output = summarization_model(text, summarization_factor)
        
        elif file_type == "audio":
            # Save the uploaded audio file to a temporary location
            with tempfile.NamedTemporaryFile(suffix=".wav", dir=TEMP_DIR, delete=False) as temp_file:
                temp_file.write(file.file.read())
                temp_audio_path = temp_file.name
            temp_file_paths.append(temp_audio_path)

            # Load the audio file
            audio = AudioFileClip(temp_audio_path)
            text = audio_to_text(audio)
            output = summarization_model(text, summarization_factor)
        
        else:
            text = file.file.read().decode('utf-8')
            output = summarization_model(text, summarization_factor)

    finally:
        # Clean up temporary files
        for temp_file_path in temp_file_paths:
            os.remove(temp_file_path)
    
    return output

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
    with sr.AudioFile(temp_audio_file_path) as source:
        audio_data = recognizer.record(source)
        try:
            text = recognizer.recognize_google(audio_data)
        except sr.UnknownValueError:
            text = "Speech was unintelligible"
        except sr.RequestError:
            text = "Could not request results from the speech recognition service"
    
    os.remove(temp_audio_file_path)
    return text

def video_to_audio(video_path):
    video = VideoFileClip(video_path)
    audio = video.audio
    return audio
