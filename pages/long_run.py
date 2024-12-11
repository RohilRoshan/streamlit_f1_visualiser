import streamlit as st
import fastf1 as ff1
import pandas as pd
import matplotlib.pyplot as plt



st.title("Long Run Analysis - Lap Time vs Lap Number")

with st.form("long_run_form"):
        year = st.number_input("Year", min_value=1950, max_value=2024, value=2024, step=1)
        gp = st.text_input("Grand Prix", value="Qatar")
        session_type = st.selectbox("Session Type", options=["FP1", "FP2", "FP3", "R"], index=3)
        drivers = st.multiselect("Select Drivers", options=["LEC", "NOR", "VER"], default=["LEC", "NOR"])
        submitted = st.form_submit_button("Load and Plot")

if submitted:
        with st.spinner(f"Loading session {session_type} for {gp} GP in {year}..."):
            session = ff1.get_session(year, gp, session_type)
            session.load()

        st.success("Session Loaded Successfully!")
        fig, ax = plt.subplots(figsize=(24, 12))

        for driver in drivers:
            laps = session.laps.pick_driver(driver)
            ax.scatter(laps['LapNumber'], laps['LapTime'].dt.total_seconds(), label=driver)

        ax.set_title(f"Lap Time vs Lap Number - {gp} GP {year} {session_type} Session")
        ax.set_xlabel("Lap Number")
        ax.set_ylabel("Lap Time (seconds)")
        ax.legend()
        ax.grid(True)
        
        st.pyplot(fig)