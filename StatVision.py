import os
import vertexai
import pandas as pd
import matplotlib.pyplot as plt
from PIL import Image
import streamlit as st
import statsapi
from pybaseball import playerid_lookup, statcast_batter
from google.oauth2 import service_account
from vertexai.generative_models import GenerativeModel, Part, SafetySetting

# Constants
PROJECT_ID = "mlbhackathon2025"
BUCKET_NAME = "mlbhackathon"
MAX_RETRIES = 3
DEFAULT_IMAGE = "StatVision.jpg"

# Service account initialization
key_file_path = os.path.join(os.getcwd(), 'sa.json')
credentials = service_account.Credentials.from_service_account_file(key_file_path)
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = key_file_path

# Model initialization
vertexai.init(project=PROJECT_ID, location="us-central1")
model = GenerativeModel("gemini-1.5-pro-002")

SAFETY_SETTINGS = {
    SafetySetting.HarmCategory.HARM_CATEGORY_HATE_SPEECH: SafetySetting.HarmBlockThreshold.BLOCK_ONLY_HIGH,
    SafetySetting.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: SafetySetting.HarmBlockThreshold.BLOCK_ONLY_HIGH,
    SafetySetting.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: SafetySetting.HarmBlockThreshold.BLOCK_ONLY_HIGH,
    SafetySetting.HarmCategory.HARM_CATEGORY_HARASSMENT: SafetySetting.HarmBlockThreshold.BLOCK_ONLY_HIGH,
}

ANALYSIS_PROMPT = """Analyze the baseball video and extract these Statcast metrics with timestamps:
1. Pitch velocity (mph) - Speed of pitch at release point
2. Exit velocity (mph) - Speed of ball off the bat
3. Launch angle (degrees) - Vertical angle of batted ball
4. Spin rate (rpm) - Rate of ball spin for pitches
5. Projected distance (feet) - Estimated flight distance of batted balls

For each metric occurrence in the video:
- Provide exact timestamp range (HH:MM:SS - HH:MM:SS)
- Metric name and value with units
- Visual evidence used for identification
- Contextual analysis of the play

Format response as Markdown table with columns:
| Timestamp Range | Metric | Value | Identification Method | Play Analysis |
|-----------------|--------|-------|------------------------|---------------|
"""


def get_player_stats(player_name: str):
    """Get comprehensive player stats using pybaseball and MLB API"""
    try:
        # Use MLB API first to get the correct full name
        mlb_data = statsapi.lookup_player(player_name)
        if not mlb_data:
            st.error(f"No player found for {player_name}")
            return None

        full_name = mlb_data[0]['fullName']
        name_parts = full_name.split()

        # Handle cases where player has only one name
        first = name_parts[0]
        last = name_parts[1] if len(name_parts) > 1 else ""

        # Use pybaseball lookup
        pb_data = playerid_lookup(last, first)
        if pb_data.empty:
            st.warning(f"No Statcast data available for {full_name}")
            return None

        player_id = pb_data.iloc[0]['key_mlbam']
        statcast_data = statcast_batter('2023-01-21', pd.Timestamp.today().strftime('%Y-%m-%d'), player_id)

        # Fetch MLB season stats
        mlb_stats = statsapi.player_stat_data(
            mlb_data[0]['id'],
            group="hitting",
            type="season"
        )

        return {
            'statcast': statcast_data,
            'mlb_stats': mlb_stats,
            'player_info': {
                'name': full_name,
                'id': player_id,
                'position': mlb_data[0]['primaryPosition']['abbreviation']
            }
        }

    except Exception as e:
        st.error(f"Error fetching player data: {str(e)}")
        return None


def analyze_video(video_url: str) -> str:
    """Analyze video and return formatted metrics analysis."""
    video_part = Part.from_uri(mime_type="video/mp4", uri=video_url)

    generation_config = {
        "max_output_tokens": 8192,
        "temperature": 0.3,
        "top_p": 0.95,
    }

    for attempt in range(MAX_RETRIES):
        try:
            responses = model.generate_content(
                [video_part, ANALYSIS_PROMPT],
                generation_config=generation_config,
                safety_settings=SAFETY_SETTINGS,
                stream=True,
            )
            return "".join([chunk.text for chunk in responses])
        except Exception as e:
            if attempt == MAX_RETRIES - 1:
                raise RuntimeError(f"Analysis failed after {MAX_RETRIES} attempts") from e


def translate_text(text: str, target_language: str = "English") -> str:
    """ †ranslate using Gemini 1.5 Pro model"""

    generation_config = {
        "max_output_tokens": 8192,
        "temperature": 0.3,
        "top_p": 0.95,
    }

    for attempt in range(MAX_RETRIES):
        try:
            responses = model.generate_content(
                [text, f"Translate the text to {target_language}"],
                generation_config=generation_config,
                safety_settings=SAFETY_SETTINGS,
                stream=True,
            )
            return "".join([chunk.text for chunk in responses])
        except Exception as e:
            if attempt == MAX_RETRIES - 1:
                raise RuntimeError(f"Translation failed after {MAX_RETRIES} attempts") from e


def get_player_names(analysis: str) -> str:
    """Extract player names from analysis response"""

    generation_config = {
        "max_output_tokens": 8192,
        "temperature": 0.0,
        "top_p": 0.95,
    }

    for attempt in range(MAX_RETRIES):
        try:
            responses = model.generate_content(
                [analysis,
                 "Extract player names from the analysis in coma-separated format. Example: 'Mike Trout, Shohei Ohtani'"],
                generation_config=generation_config,
                safety_settings=SAFETY_SETTINGS,
                stream=True,
            )
            return "".join([chunk.text for chunk in responses])
        except Exception as e:
            if attempt == MAX_RETRIES - 1:
                raise RuntimeError(f"Failed after {MAX_RETRIES} attempts") from e


def plot_statcast_data(data: pd.DataFrame, metric: str):
    """Generate visualization for statcast metrics"""
    plt.figure(figsize=(10, 6))

    if metric == 'Exit Velocity':
        plt.hist(data['launch_speed'].dropna(), bins=20, color='blue', alpha=0.7)
        plt.title('Exit Velocity Distribution')
        plt.xlabel('MPH')
    elif metric == 'Spin Rate':
        plt.scatter(data['release_spin_rate'], data['release_speed'], c='green', alpha=0.5)
        plt.title('Spin Rate vs Pitch Velocity')
        plt.xlabel('Spin Rate (RPM)')
        plt.ylabel('Velocity (MPH)')

    plt.grid(True)
    st.pyplot(plt)


# Language Support
LANGUAGES = ["English", "Spanish", "French", "German", "Chinese", "Japanese", "Hindi"]


def display_home_page():
    # st.set_page_config(page_title="StatCast Analyzer Pro", page_icon=DEFAULT_IMAGE, layout="wide")

    try:
        app_icon = Image.open(DEFAULT_IMAGE) if os.path.exists(DEFAULT_IMAGE) else None
    except Exception as e:
        st.sidebar.warning(f"Couldn't load app icon: {str(e)}")
        app_icon = None

    with st.sidebar:
        st.title("StatCast Analyzer")
        if app_icon:
            st.image(app_icon, use_container_width=True)

        # player_name = st.text_input("Enter Player Name:", help="Format: First Last")
        compare_historical = st.checkbox("Enable Players Historical Data", value=True)
        visualize_metrics = st.checkbox("Enable Metric Visualizations", value=True)
        lang = st.selectbox("Select Language", LANGUAGES, index=0)

    st.title("⚾ MLB StatCast Video Analysis")
    video_url = st.text_input(
        "Video URL:",
        placeholder="https://youtube.com/watch?v=...",
        help="Must be a public YouTube video with visible gameplay"
    )

    if st.button("Analyze Video", type="primary"):
        if not video_url.startswith("https://www.youtube.com/watch?v="):
            st.error("Please enter a valid YouTube URL")
            return

        with st.spinner("Analyzing video content..."):
            try:
                analysis = analyze_video(video_url)

                if "| Timestamp Range | Metric |" in analysis:
                    st.markdown("### 📊 StatCast Metrics Analysis")
                    if lang != "English":
                        st.markdown(translate_text(analysis, lang))
                    else:
                        st.markdown(analysis)
                    try:
                        player_names = get_player_names(analysis).split(",")
                    except Exception as e:
                        st.error(f"Error extracting player names: {str(e)}")
                        player_names = []

                if compare_historical:
                    for player_name in player_names:
                        with st.spinner("Fetching player data..."):
                            player_data = get_player_stats(player_name)
                            # st.write(player_data)
                            # st.write(player_data["mlb_stats"]["id","first_name","last_name","current_team","position"])
                            # st.write(player_data["mlb_stats"]["stats"][0])

                            if player_data:
                                st.markdown(f"### 🏆 {player_data['player_info']['name']} Performance Insights")
                                col1, col2 = st.columns([.8, .2])

                                with col1:
                                    st.markdown("**Statcast Data**")
                                    if not player_data['statcast'].empty:
                                        st.dataframe(
                                            player_data['statcast'][
                                                ['game_date', 'pitch_type', 'release_speed', 'launch_speed',
                                                 'launch_angle', 'arm_angle', 'release_spin_rate']].sort_values(
                                                'game_date', ascending=False).reset_index(drop=True).iloc[:10],

                                        )
                                    else:
                                        st.warning("No recent Statcast data available")

                                with col2:
                                    st.markdown("**Season Stats**")
                                    if 'stats' in player_data['mlb_stats']:
                                        stats = player_data['mlb_stats']['stats'][0]['stats']
                                        st.write(f"""
                                        - AVG: {stats.get('avg', 'N/A')}
                                        - HR: {stats.get('homeRuns', 'N/A')}
                                        - RBI: {stats.get('rbi', 'N/A')}
                                        - OPS: {stats.get('ops', 'N/A')}
                                        """)
                                    else:
                                        st.warning("No MLB API stats available")

                                if visualize_metrics and not player_data['statcast'].empty:
                                    st.markdown("### 📈 Metric Visualizations")
                                    col1, col2 = st.columns(2)
                                    with col1:
                                        plot_statcast_data(player_data['statcast'], 'Exit Velocity')
                                    with col2:
                                        plot_statcast_data(player_data['statcast'], 'Spin Rate')

                    st.success("Analysis complete!")
                else:
                    st.warning("No StatCast metrics detected. Try a different video.")

            except Exception as e:
                st.error(f"Analysis failed: {str(e)}")
                st.info("Ensure video contains visible gameplay")