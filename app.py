import streamlit as st
from StatVision import display_home_page
from glossary import display_statcast_glossary
from injuryrisk import display_risk_details
DEFAULT_IMAGE = "StatVision.jpg"
# Set the page title and sidebar
st.set_page_config(page_title="StatCast Analyzer Pro", page_icon=DEFAULT_IMAGE)
# Sidebar navigation
st.sidebar.title("StatVision Navigation")
page = st.sidebar.radio("Go to", ["Home", "Statcast Glossary",'injuryriskanalysis'])

# Show the selected page
if page == "Home":
    display_home_page()  # Call function from hom.py
elif page == "Statcast Glossary":
    display_statcast_glossary()  # Call function from glossary.py
elif page=="injuryriskanalysis" :
    display_risk_details()