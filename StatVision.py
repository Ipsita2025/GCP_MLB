import os

import vertexai
from PIL import Image
import streamlit as st
from google.cloud import secretmanager
from google.oauth2 import service_account
from google.genai import Client
from google.genai import types
from vertexai.generative_models import GenerativeModel, Part, SafetySetting


# Constants
PROJECT_ID = "mlbhackathon2025"
SECRET_ID = "mlb"
BUCKET_NAME = "mlbhackathon"

# Set the environment variable for the service account key file
key_file_path ='sa.json'
print(key_file_path)
credentials = service_account.Credentials.from_service_account_file(key_file_path)
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = key_file_path


# Function to initialize the GenAI client
def initialize_genai_client(project_id):
    """Initialize and return the GenAI client."""
    try:
        return Client(vertexai=True, project=project_id, location="us-central1")
    except Exception as e:
        st.error(f"Error initializing GenAI client: {e}")
        return None

#video_url='https://www.youtube.com/watch?v=1nvQJLfrvck'

# Defining model
vertexai.init(project="mlbhackathon2025", location="us-central1")
model = GenerativeModel("gemini-1.5-pro-002",)

# Function to summarize a YouTube video
def generate(video_url):

    # Taking part of the video
    video1 = Part.from_uri(
    mime_type="video/mp4",
    uri=video_url,
    )

    generation_config = {
    "max_output_tokens": 8192,
    "temperature": 1,
    "top_p": 0.95,
    }


    safety_settings = [
    SafetySetting(
        category=SafetySetting.HarmCategory.HARM_CATEGORY_HATE_SPEECH,
        threshold=SafetySetting.HarmBlockThreshold.OFF
    ),
    SafetySetting(
        category=SafetySetting.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
        threshold=SafetySetting.HarmBlockThreshold.OFF
    ),
    SafetySetting(
        category=SafetySetting.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
        threshold=SafetySetting.HarmBlockThreshold.OFF
    ),
    SafetySetting(
        category=SafetySetting.HarmCategory.HARM_CATEGORY_HARASSMENT,
        threshold=SafetySetting.HarmBlockThreshold.OFF
    ),
    ]

    responses = model.generate_content(
        [video1, """extracts fundamental Statcast metrics (e.g., pitch speed, exit velocity) from the video. 
        Provide list of metrics you want to extract from the video along with one line defintition of each.
        Use format as below to show the metrics:
        Time stamp range , Stastcast metrics,   How you got it
        Provide viewers with thought-provoking summaries.
Offer context-specific highlights that make the content accessible to users with diverse levels of expertise.
Present results in a visually compelling manner, using dynamic charts, timelines, or heatmaps.
Encourage exploration by suggesting additional content or deeper insights based on the analyzed video.
Focus on enhancing user engagement and delight, while ensuring technical robustness and scalability.
        """],
        generation_config=generation_config,
        safety_settings=safety_settings,
        stream=True,
    )

    return responses

    # for response in responses:
    #     print(response.text, end="")






# Main function for the Streamlit app

# Set app configuration and icon
st.set_page_config(page_title="Turning Game Footage into Actionable Stats.", page_icon="StatVision.jpg")

# Sidebar for app icon upload
st.sidebar.title("StatVision: Turning Game Footage into Actionable Stats.")
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
st.title("🎥 StatVision YouTube Video Summarizer")
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
    else:

    #return
        with st.spinner("Processing video..."):
            try:
                responses = generate(video_url)
            except Exception as e:
                st.error(f"Error generating video summary: {e}")
            if responses:
                for response in responses:
                    st.write(response.text)
            else:
                st.error("Summary of the video could not be generated. Please try again.")
        # if summary:
        #     st.markdown("### ✍️ Summary:")
        #     st.success(summary)
        # else:
        #     st.error("Error generating summary. Please try again.")


