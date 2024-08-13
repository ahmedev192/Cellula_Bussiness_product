import io
import speech_recognition as sr
from moviepy.editor import AudioFileClip, VideoFileClip
from transformers import pipeline
from fastapi import UploadFile

def summarize(file_type, summarization_factor, file: UploadFile):
    if file_type == "video":
        # Save the uploaded video file to a temporary location
        temp_video_path = "temp_video_file.mp4"
        with open(temp_video_path, "wb") as temp_file:
            temp_file.write(file.file.read())

        # Convert video to audio
        audio = video_to_audio(temp_video_path)
        text = audio_to_text(audio)
        output = summarization_model(text, summarization_factor)
    
    elif file_type == "audio":
        # Save the uploaded audio file to a temporary location
        temp_audio_path = "temp_audio_file.wav"
        with open(temp_audio_path, "wb") as temp_file:
            temp_file.write(file.file.read())

        # Load the audio file
        audio = AudioFileClip(temp_audio_path)
        text = audio_to_text(audio)
        output = summarization_model(text, summarization_factor)
    
    else:
        text = file.file.read().decode('utf-8')
        output = summarization_model(text, summarization_factor)
    
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
    temp_audio_file = "temp_audio.wav"
    audio_clip.write_audiofile(temp_audio_file, codec='pcm_s16le')

    recognizer = sr.Recognizer()
    with sr.AudioFile(temp_audio_file) as source:
        audio_data = recognizer.record(source)
        try:
            text = recognizer.recognize_google(audio_data)
        except sr.UnknownValueError:
            text = "Speech was unintelligible"
        except sr.RequestError:
            text = "Could not request results from the speech recognition service"

    return text

def video_to_audio(video_path):
    video = VideoFileClip(video_path)
    audio = video.audio
    return audio
