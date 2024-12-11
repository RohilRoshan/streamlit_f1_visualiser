import streamlit as st
import fastf1 as ff1
import pandas as pd
import matplotlib.pyplot as plt

# Enable FastF1 cache for faster data retrieval

# Streamlit App Title
st.title("F1 Telemetry Visualization App")

# Streamlit Form for Input Selection
with st.form("telemetry_form"):
    st.header("Configure Telemetry Parameters")

    year = st.number_input("Year", min_value=1950, max_value=2024, value=2024, step=1)
    
    gp = st.selectbox("Grand Prix", options=["Bahrain","Saudi Arabia", "Monaco","Spain","Emilia Romagna","Qatar","Las Vegas","Monza","United States","Abu Dhabi"])
    
    session_type = st.selectbox("Session Type", options=["FP1", "FP2", "FP3", "Q", "R"], index=3)

    drivers = st.multiselect("Select Drivers", options=["LEC", "NOR", "VER"])

    submitted = st.form_submit_button("Load and Visualize")

# Load session if the form is submitted
if submitted:
    # Display Loading Spinner
    with st.spinner(f"Loading session {session_type} for {gp} GP in {year}..."):
        session = ff1.get_session(year, gp, session_type)
        session.load()

    st.success("Session Loaded Successfully!")

    def get_fastest_lap_data(driver_code):
        laps = session.laps.pick_driver(driver_code)
        fastest_lap = laps.pick_fastest()
        telemetry = fastest_lap.get_car_data().add_distance()
        return fastest_lap, telemetry

    def get_sector_info(lap):
        sectors = ['Sector1Time', 'Sector2Time', 'Sector3Time']
        distances, times = [], []
        cumulative_time = pd.Timedelta(0)

        for sector in sectors:
            cumulative_time += lap[sector]
            distance_at_time = lap.get_car_data().add_distance().loc[lap.get_car_data().Time <= cumulative_time, 'Distance'].max()
            distances.append(distance_at_time)
            times.append(lap[sector].total_seconds())
        return distances, times

    # Plotting
    st.subheader(f"Telemetry Visualization - {gp} GP {year} {session_type} Session")

    fig, ax = plt.subplots(figsize=(24, 12), dpi=100)

    colors = {"LEC": 'red', "NOR": 'orange', "VER": 'blue'}
    sector_lines_plotted = False

    for driver in drivers:
        fastest_lap, telemetry = get_fastest_lap_data(driver)
        ax.plot(telemetry['Distance'], telemetry['Speed'], label=f"{driver} {fastest_lap['LapTime']}", color=colors[driver])
        
        if not sector_lines_plotted:
            sector_distances, sector_times = get_sector_info(fastest_lap)
            for i, dist in enumerate(sector_distances):
                ax.axvline(x=dist, linestyle='--', color='gray', alpha=0.7)
                ax.text(dist + 5, max(telemetry['Speed']) * 0.9, 
                        f"S{i + 1}\n{driver}: {sector_times[i]:.2f}s", 
                        color='black', fontsize=10, ha='left')
            sector_lines_plotted = True

    ax.set_title(f"Speed vs Distance - {gp} GP {year} {session_type}")
    ax.set_xlabel("Distance (m)")
    ax.set_ylabel("Speed (km/h)")
    ax.grid(True)

    st.pyplot(fig)
