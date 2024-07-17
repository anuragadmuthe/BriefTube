import streamlit as st
from dotenv import load_dotenv
import os
import google.generativeai as genai
from youtube_transcript_api import YouTubeTranscriptApi
import re

load_dotenv()  # load all the environment variables
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

prompt = """You are Yotube video summarizer. You will be taking the transcript text
and summarizing the entire video and providing the important summary in points
within 250 words. Please provide the summary of the text given here:  """

## getting the transcript data from yt videos
def extract_transcript_details(youtube_video_url):
    try:
        video_id = re.search(r'(?:v=|\/)([0-9A-Za-z_-]{11}).*', youtube_video_url)
        if video_id:
            video_id = video_id.group(1)
        else:
            raise ValueError("Could not extract video ID from the provided link.")
        
        transcript_text = YouTubeTranscriptApi.get_transcript(video_id)

        transcript = ""
        for i in transcript_text:
            transcript += " " + i["text"]

        return transcript

    except Exception as e:
        raise e

## getting the summary based on Prompt from Google Gemini Pro
def generate_gemini_content(transcript_text, prompt):
    model = genai.GenerativeModel("gemini-pro")
    response = model.generate_content(prompt + transcript_text)
    return response.text

st.title("YouTube Transcript to Detailed Notes Converter")
youtube_link = st.text_input("Enter YouTube Video Link:")

if youtube_link:
    video_id_match = re.search(r'(?:v=|\/)([0-9A-Za-z_-]{11}).*', youtube_link)
    if video_id_match:
        video_id = video_id_match.group(1)
        thumbnail_url = f"https://img.youtube.com/vi/{video_id}/0.jpg"
        try:
            st.image(thumbnail_url, use_column_width=True)
        except Exception as e:
            st.error(f"Error loading thumbnail: {e}")
    else:
        st.error("Could not extract video ID from the provided link.")

if st.button("Get Detailed Notes"):
    try:
        transcript_text = extract_transcript_details(youtube_link)

        if transcript_text:
            summary = generate_gemini_content(transcript_text, prompt)
            st.markdown("## Detailed Notes:")
            st.write(summary)
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")