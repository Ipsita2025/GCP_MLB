import streamlit as st

# Function to display glossary content
def display_statcast_glossary():
    st.title("📊 Statcast Glossary")
    st.markdown("A comprehensive glossary of Statcast metrics used in baseball analytics.")

    # Glossary content in categories
    metrics = {
        "Exit Velocity (EV)": "How fast, in miles per hour, a ball was hit by a batter.",
        "Launch Angle (LA)": "How high/low, in degrees, a ball was hit by a batter.",
        "Barrels": "A batted ball with the perfect combination of exit velocity and launch angle.",
        "Hard Hit": "Statcast defines a 'hard-hit ball' as one hit with an exit velocity of 95 mph or higher.",
        "Launch Angle Sweet Spot": "A batted-ball event with a launch angle between eight and 32 degrees.",
        "Batted Ball Event (BBE)": "A Batted Ball Event represents any batted ball that produces a result.",
        "Pitch Velocity": "How hard, in miles per hour, a pitch is thrown.",
        "Pitch Movement": "The movement of a pitch in inches, both in raw numbers and as a measurement against average.",
        "Active Spin": "Statcast refers to the spin that contributes to movement as Active Spin.",
        "Spin Rate": "How much spin, in revolutions per minute, a pitch was thrown with.",
        "Extension": "How far off the mound, in feet, a pitcher releases the pitch.",
        "Pop Time": "How quickly, in seconds, a catcher can get the ball out of his glove and to the base on a stolen base or pickoff attempt.",
        "Arm Strength": "How hard, in miles per hour, a fielder throws the ball.",
        "Lead Distance": "How far, in feet, a runner is ranging off the bag at the time of a pitcher's first movement or pitch release.",
        "Jump": "Jump is a Statcast metric that shows which players have the fastest reactions and most direct routes to the outfield.",
        "Outs Above Average (OAA)": "A range-based metric of skill that shows how many outs a player has saved over his peers.",
        "Fielding Run Value": "Statcast's overall metric for capturing a player's measurable defensive performance.",
        "Catch Probability": "The likelihood, in percent, that an outfielder will be able to make a catch on an individual batted ball.",
        "Expected Earned Run Avg (xERA)": "xERA is a simple 1:1 translation of xwOBA, converted to the ERA scale.",
        "Sprint Speed": "A measurement of a player's top running speed, expressed in 'feet per second' in a player's fastest one-second window.",
        "Bolt": "A Bolt is any run where the Sprint Speed is at least 30 ft/sec.",
        "EV50": "For a batter, EV50 is an average of the hardest 50% of his batted balls.",
        "Adjusted EV": "Adjusted EV averages the maximum of 88 and the actual exit velocity of each batted ball event.",
        "Blocks Above Average": "A Statcast metric designed to express the demonstrated skill of catchers at preventing wild pitches or passed balls.",
        "Bat Speed": "Bat speed is measured at the sweet-spot of the bat.",
        "Fast Swing Rate": "A fast swing is one that has 75 MPH or more of bat speed.",
        "Swing Length": "The total (sum) distance in feet traveled of the head of the bat in X/Y/Z space.",
        "Squared-Up Rate": "How much exit velocity was obtained compared to the maximum possible exit velocity available.",
        "Blasts": "A more valuable subset of squared-up balls, defining batted balls that were both squared-up and with a fast swing.",
        "Swords": "A bat tracking metric that quantifies when a pitcher forces a batter to take a non-competitive, ugly-looking swing."
    }

    # Display the glossary in a grid format
    st.markdown("### Statcast Metrics")
    columns = st.columns(3)  # Three columns layout

    # Iterate over the metrics and add them to the grid
    for idx, (metric, description) in enumerate(metrics.items()):
        with columns[idx % 3]:  # Place in one of the three columns
            st.markdown(f"**{metric}**")
            st.write(description)

