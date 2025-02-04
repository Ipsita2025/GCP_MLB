import streamlit as st
import pandas as pd
import numpy as np
import statsapi
from pybaseball import playerid_lookup, statcast_batter

# Define Risk Factors
RISK_FACTORS = {
    "Exit Velocity Drop": ("launch_speed", 3),  # 3 mph drop
    "Spin Rate Drop": ("release_spin_rate", 150),  # 150 rpm drop
    "Pitch Velocity Drop": ("release_speed", 2),  # 2 mph drop
    "Arm Angle Changes": ("arm_angle", 5),  # 5-degree change
    "Sprint Speed Drop": ("sprint_speed", 0.5),  # 0.5 ft/sec drop
}


def get_player_info(name):
    """Find player ID using MLB API & pybaseball"""
    mlb_data = statsapi.lookup_player(name)
    if not mlb_data:
        return None

    full_name = mlb_data[0]['fullName']
    player_id = mlb_data[0]['id']

    name_parts = full_name.split()
    last, first = name_parts[-1], name_parts[0]
    pb_data = playerid_lookup(last, first)

    if pb_data.empty:
        return None

    return {
        "id": player_id,
        "name": full_name,
        "statcast_id": pb_data.iloc[0]["key_mlbam"]
    }


def fetch_statcast_data(player_id):
    """Retrieve player's recent Statcast metrics"""
    try:
        data = statcast_batter("2024-04-01", "2024-07-01", player_id)
        return data if not data.empty else None
    except:
        return None


def fetch_injury_history(player_id):
    """Fetch past injuries for a player using MLB API"""
    try:
        injury_data = statsapi.player_stat_data(player_id, group="health", type="career")
        return injury_data.get("stats", [])
    except:
        return []


def analyze_injury_risk(statcast_data):
    """Analyze recent player trends to detect injury risks"""
    if statcast_data is None:
        return []

    risk_results = []
    recent_data = statcast_data.sort_values('game_date', ascending=False).head(10)

    for metric, (column, threshold) in RISK_FACTORS.items():
        if column in recent_data.columns:
            recent_values = recent_data[column].dropna()
            if len(recent_values) >= 2:
                change = recent_values.iloc[0] - np.mean(recent_values.iloc[1:])

                if abs(change) >= threshold:
                    risk_results.append({
                        "Metric": metric,
                        "Change": f"{change:.2f}",
                        "Risk Level": "High" if change < 0 else "Moderate"
                    })

    return risk_results


def display_risk_details():
    """Streamlit UI for MLB Player Injury Risk Analysis"""
    st.title("⚾ MLB Player Injury Risk Analysis")

    # User Input: Player Name
    player_name = st.text_input("Enter Player Name (First Last):")

    if player_name:
        with st.spinner("Fetching Player Data..."):
            player_info = get_player_info(player_name)

        if player_info:
            st.success(f"✅ Player Found: {player_info['name']} (ID: {player_info['id']})")

            # Fetch Statcast Data
            with st.spinner("Fetching Statcast Metrics..."):
                statcast_data = fetch_statcast_data(player_info["statcast_id"])

            # Fetch Injury History
            with st.spinner("Fetching Injury History..."):
                injury_history = fetch_injury_history(player_info["id"])

            # Perform Injury Risk Analysis
            risk_results = analyze_injury_risk(statcast_data)

            # Display Results
            if risk_results:
                st.markdown(f"### 🚨 Injury Risk Analysis for {player_info['name']}")
                st.table(pd.DataFrame(risk_results))
            else:
                st.success("✅ No significant injury risks detected.")

            # Display Injury History
            if injury_history:
                st.markdown("### 📋 Past Injury History")
                injury_df = pd.DataFrame(injury_history).rename(columns={"description": "Injury", "date": "Date"})
                st.table(injury_df)
            else:
                st.success("✅ No past injuries found.")

