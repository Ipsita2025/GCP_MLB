import os
import tempfile

import streamlit as st
from google.cloud import secretmanager
from google.oauth2 import service_account
from google.genai import Client
from pytube import YouTube
import whisper
from transformers import pipeline
from concurrent.futures import ThreadPoolExecutor
from google.genai import types
from PIL import Image
project_id = "mlbhackathon2025"
secret_id = "mlb"

bucket_name='mlbhackathon'

# Function to retrieve the API key from Google Secret Manager
def get_api_key(secret_id, project_id):
    try:
        client = secretmanager.SecretManagerServiceClient()
        name = f"projects/{project_id}/secrets/{secret_id}/versions/latest"
        response = client.access_secret_version(request={"name": name})
        return response.payload.data.decode("UTF-8")
    except Exception as e:
        st.error(f"Error retrieving API key: {e}")
        return None


def initialize_genai_client(project_id):
    """Initialize and return the Gemini AI client."""
    try:
        return Client(vertexai=True, project=project_id, location="us-central1")
    except Exception as e:
        st.error(f"Error initializing GenAI client: {e}")
        return None
def generate():
  from google import genai
  client = genai.Client(
      vertexai=True,
      project="mlbhackathon2025",
      location="us-central1"
  )

  import types
  video1 = types.Part.from_uri(
      file_uri="https://www.youtube.com/watch?v=1nvQJLfrvck",
      mime_type="video/mp4",
  )

  model = "gemini-2.0-flash-exp"
  contents = [
    types.Content(
      role="user",
      parts=[
        video1,
        types.Part.from_text("""summarize this video for me in 100 words""")
      ]
    )
  ]
  generate_content_config = types.GenerateContentConfig(
    temperature = 1,
    top_p = 0.95,
    max_output_tokens = 8192,
    response_modalities = ["TEXT"],
    safety_settings = [types.SafetySetting(
      category="HARM_CATEGORY_HATE_SPEECH",
      threshold="OFF"
    ),types.SafetySetting(
      category="HARM_CATEGORY_DANGEROUS_CONTENT",
      threshold="OFF"
    ),types.SafetySetting(
      category="HARM_CATEGORY_SEXUALLY_EXPLICIT",
      threshold="OFF"
    ),types.SafetySetting(
      category="HARM_CATEGORY_HARASSMENT",
      threshold="OFF"
    )],
  )

  for chunk in client.models.generate_content_stream(
    model = model,
    contents = contents,
    config = generate_content_config,
    ):
    print(chunk, end="")



def main():
    # Set app configuration and icon
    st.set_page_config(page_title="Video Summarizer", page_icon="StatVision.jpg")

    # Sidebar for app icon upload
    st.sidebar.title("Video Summarizer")
    st.sidebar.markdown(
        """
        <style>
        .stFileUploader label { display: none; }
        </style>
        """,
        unsafe_allow_html=True
    )
    app_icon_path = "StatVision.jpg"
    if os.path.exists(app_icon_path):
        app_icon = Image.open(app_icon_path)
        st.sidebar.image(app_icon, caption="StatVision", use_container_width=True)

    # App title and description
    st.title("🎥 YouTube Video Summarizer")
    st.markdown(
        """
        <div class="app-header">Provide the URL of a YouTube video, and this app will summarize its content.</div>
        """,
        unsafe_allow_html=True
    )

    # Video URL input
    video_url = st.text_input("Enter the YouTube video URL",
                              placeholder="e.g., https://www.youtube.com/watch?v=example")

    # Summarize button and processing
    if st.button("Summarize Video"):
        if not video_url:
            st.error("Please enter a valid video URL.")
            return

        with st.spinner("Processing video..."):
            summary = generate()  # Fixed function call

        if summary:
            st.markdown("### ✍️ Summary:")
            st.success(summary)
        else:
            st.error("Error generating summary.")


if __name__ == "__main__":
    main()
