import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib import colormaps
from matplotlib.collections import LineCollection
import seaborn as sns
import pandas as pd
import datetime
import time
from timple.timedelta import strftimedelta
import streamlit as st
import fastf1
import fastf1.plotting

def getSeason(year):
    season = fastf1.get_event_schedule(year)
    events = season.to_records(list)
    return events

def getSessions(event):
    eventsSessionsList = []
    eventsSessionsList.append(event["Session1"])
    eventsSessionsList.append(event["Session2"])
    eventsSessionsList.append(event["Session3"])
    eventsSessionsList.append(event["Session4"])
    eventsSessionsList.append(event["Session5"])
    
    while("None" in eventsSessionsList):
        eventsSessionsList.remove("None")
    return eventsSessionsList

def getSessionTimings(event):
    sessionTimingsList = []
    sessionTimingsList.append(event["Session1Date"])
    sessionTimingsList.append(event["Session2Date"])
    sessionTimingsList.append(event["Session3Date"])
    sessionTimingsList.append(event["Session4Date"])
    sessionTimingsList.append(event["Session5Date"])

    while("None" in sessionTimingsList):
        sessionTimingsList.remove("None")
    return sessionTimingsList

def getSessionDetails(year,event,session):
    sessionDetails = fastf1.get_session(year, event, session)
    sessionDetails.load()
    return sessionDetails

def displaySessionDetails(sessionDetails, sessionName):
    sessionDetails = sessionDetails.results.loc[:, ['ClassifiedPosition','HeadshotUrl','FullName','Abbreviation','DriverNumber','TeamName','GridPosition','Q1','Q2','Q3','Time','Status','Points']]
    df = pd.DataFrame(sessionDetails)
    df = df.reset_index(drop=True)

    try:
        df["Time"] = df["Time"].fillna(pd.Timedelta(seconds=0))  # Replace NaNs with 0
        df["Time"] = df["Time"].apply(lambda x: strftimedelta(x, '%h:%m:%s.%ms'))
        df["Q1"] = df["Q1"].fillna(pd.Timedelta(seconds=0))  # Replace NaNs with 0
        df["Q1"] = df["Q1"].apply(lambda x: strftimedelta(x, '%m:%s.%ms'))
        df["Q2"] = df["Q2"].fillna(pd.Timedelta(seconds=0))  # Replace NaNs with 0
        df["Q2"] = df["Q2"].apply(lambda x: strftimedelta(x, '%m:%s.%ms'))
        df["Q3"] = df["Q3"].fillna(pd.Timedelta(seconds=0))  # Replace NaNs with 0
        df["Q3"] = df["Q3"].apply(lambda x: strftimedelta(x, '%m:%s.%ms'))
    
    except KeyError:
        print("No Time")

    if sessionName in ["Practice 1", "Practice 2", "Practice 3"]:
        df["ClassifiedPosition"] = df.index + 1
        df = df.drop(columns=["GridPosition","Q1","Q2","Q3","Time","Status","Points"])
    elif sessionName in ["Qualifying", "Sprint Shootout"]:
        df["ClassifiedPosition"] = df.index + 1
        df = df.drop(columns=["GridPosition","Time","Status","Points"])
    elif sessionName in ["Race", "Sprint"]:
        df = df.drop(columns=["Q1","Q2","Q3"])

    st.data_editor(
        df,
        height=737,
        use_container_width=True,
        column_config={
            "ClassifiedPosition": st.column_config.Column(
                "Pos."
            ),
            "HeadshotUrl": st.column_config.ImageColumn(
                "Driver",
            ),
            "FullName": st.column_config.TextColumn(
                "Name"
            ),
            "Abbreviation": st.column_config.TextColumn(
                "Abbrv.",
            ),
            "DriverNumber": st.column_config.TextColumn(
                "Driver No."
            ),
            "TeamName": st.column_config.TextColumn(
                "Constructor",
            ),
            "GridPosition": st.column_config.Column(
                "Grid Pos.",
            ),
            "Time": st.column_config.TextColumn(
                "Time"
            ),
        },
        disabled=True,
        hide_index=True,
    )
    
    return df

def displayCircuitMap(sessionDetails):
    lap = sessionDetails.laps.pick_fastest()
    pos = lap.get_pos_data()
    circuit_info = sessionDetails.get_circuit_info()

    def rotate(xy, *, angle):
        rot_mat = np.array([[np.cos(angle), np.sin(angle)],[-np.sin(angle), np.cos(angle)]])
        return np.matmul(xy, rot_mat)

    # Get an array of shape [n, 2] where n is the number of points and the second
    # axis is x and y.
    track = pos.loc[:, ('X', 'Y')].to_numpy()

    # Convert the rotation angle from degrees to radian.
    track_angle = circuit_info.rotation / 180 * np.pi

    # Rotate and plot the track map.
    rotated_track = rotate(track, angle=track_angle)
    plt.plot(rotated_track[:, 0], rotated_track[:, 1])

    offset_vector = [500, 0]  # offset length is chosen arbitrarily to 'look good'

    # Iterate over all corners.
    for _, corner in circuit_info.corners.iterrows():
        # Create a string from corner number and letter
        txt = f"{corner['Number']}{corner['Letter']}"

        # Convert the angle from degrees to radian.
        offset_angle = corner['Angle'] / 180 * np.pi

        # Rotate the offset vector so that it points sideways from the track.
        offset_x, offset_y = rotate(offset_vector, angle=offset_angle)

        # Add the offset to the position of the corner
        text_x = corner['X'] + offset_x
        text_y = corner['Y'] + offset_y

        # Rotate the text position equivalently to the rest of the track map
        text_x, text_y = rotate([text_x, text_y], angle=track_angle)

        # Rotate the center of the corner equivalently to the rest of the track map
        track_x, track_y = rotate([corner['X'], corner['Y']], angle=track_angle)

        # Draw a circle next to the track.
        plt.scatter(text_x, text_y, color='grey', s=140)

        # Draw a line from the track to this circle.
        plt.plot([track_x, text_x], [track_y, text_y], color='grey')

        # Finally, print the corner number inside the circle.
        plt.text(text_x, text_y, txt,
                va='center_baseline', ha='center', size='small', color='white')

    plt.title(sessionDetails.event['Location'] + ", " + sessionDetails.event['Country'])
    plt.xticks([])
    plt.yticks([])
    plt.axis('equal')
    st.pyplot(plt)
    plt.close()

def displayCircuitMapSpeedVis(sessionDetails):
    lap = sessionDetails.laps.pick_fastest()
    lapnumber = int(lap.LapNumber)
    laptime = lap.LapTime
    tyrecompound = lap.Compound
    # Get the hours, minutes, and seconds.
    minutes, seconds = divmod(laptime.seconds, 60)
    hours, minutes = divmod(minutes, 60)
    # Round the microseconds to millis.
    millis = round(laptime.microseconds/1000, 0)
    laptime_str = f"{minutes:02}:{seconds:02}.{millis:.0f}"
    event = sessionDetails.event
    session_name = sessionDetails.name
    year = event.EventDate.year
    driver = lap.Driver
    colormap = mpl.cm.plasma

    # Get telemetry data
    x = lap.telemetry['X']              # values for x-axis
    y = lap.telemetry['Y']              # values for y-axis
    color = lap.telemetry['Speed']      # value to base color gradient on

    points = np.array([x, y]).T.reshape(-1, 1, 2)
    segments = np.concatenate([points[:-1], points[1:]], axis=1)

    # We create a plot with title and adjust some setting to make it look good.
    fig, ax = plt.subplots(sharex=True, sharey=True, figsize=(12, 6.75))
    fig.suptitle(f'{event.EventName} {year} - {session_name} \n {driver} - {laptime_str} - Lap {lapnumber} - {tyrecompound} tyre', size=24, y=0.97)

    # Adjust margins and turn of axis
    plt.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.12)
    ax.axis('off')

    # After this, we plot the data itself.
    # Create background track line
    ax.plot(lap.telemetry['X'], lap.telemetry['Y'],color='black', linestyle='-', linewidth=16, zorder=0)

    # Create a continuous norm to map from data points to colors
    norm = plt.Normalize(color.min(), color.max())
    lc = LineCollection(segments, cmap=colormap, norm=norm,linestyle='-', linewidth=5)

    # Set the values used for colormapping
    lc.set_array(color)

    # Merge all line segments together
    line = ax.add_collection(lc)

    # Finally, we create a color bar as a legend.
    cbaxes = fig.add_axes([0.25, 0.05, 0.5, 0.05])
    normlegend = mpl.colors.Normalize(vmin=color.min(), vmax=color.max())
    legend = mpl.colorbar.ColorbarBase(cbaxes, norm=normlegend, cmap=colormap, orientation="horizontal")
    st.pyplot(plt)
    plt.close()

def displayCircuitGearVis(sessionDetails):
    lap = sessionDetails.laps.pick_fastest()
    tel = lap.get_telemetry()

    x = np.array(tel['X'].values)
    y = np.array(tel['Y'].values)

    points = np.array([x, y]).T.reshape(-1, 1, 2)
    segments = np.concatenate([points[:-1], points[1:]], axis=1)
    gear = tel['nGear'].to_numpy().astype(float)

    cmap = colormaps['Paired']
    lc_comp = LineCollection(segments, norm=plt.Normalize(1, cmap.N+1), cmap=cmap)
    lc_comp.set_array(gear)
    lc_comp.set_linewidth(4)

    plt.gca().add_collection(lc_comp)
    plt.axis('equal')
    plt.tick_params(labelleft=False, left=False, labelbottom=False, bottom=False)

    title = plt.suptitle(
        f"Fastest Lap Gear Shift Visualization\n"
        f"{lap['Driver']} - {sessionDetails.event['EventName']} {sessionDetails.event.year}"
    )

    cbar = plt.colorbar(mappable=lc_comp, label="Gear",boundaries=np.arange(1, 10))
    cbar.set_ticks(np.arange(1.5, 9.5))
    cbar.set_ticklabels(np.arange(1, 9))
    st.pyplot(plt)
    plt.close()

def displayRacePosChange(sessionDetails):
    fastf1.plotting.setup_mpl(misc_mpl_mods=False)

    fig, ax = plt.subplots(figsize=(8.0, 4.9))
    
    for drv in sessionDetails.drivers:
        drv_laps = sessionDetails.laps.pick_driver(drv)
        abb = drv_laps['Driver'].iloc[0]
        color = fastf1.plotting.driver_color(abb)
        ax.plot(drv_laps['LapNumber'], drv_laps['Position'],label=abb, color=color)
    
    ax.set_ylim([20.5, 0.5])
    ax.set_yticks([1, 5, 10, 15, 20])
    ax.set_xlabel('Lap')
    ax.set_ylabel('Position')

    ax.legend(bbox_to_anchor=(1.0, 1.02))
    plt.tight_layout()
    st.pyplot(plt)
    plt.close()

def displayRaceTyreStrategies(sessionDetails):
    laps = sessionDetails.laps
    drivers = sessionDetails.drivers
    drivers = [sessionDetails.get_driver(driver)["Abbreviation"] for driver in drivers]
    stints = laps[["Driver", "Stint", "Compound", "LapNumber"]]
    stints = stints.groupby(["Driver", "Stint", "Compound"])
    stints = stints.count().reset_index()
    stints = stints.rename(columns={"LapNumber": "StintLength"})
    fig, ax = plt.subplots(figsize=(5, 10))

    for driver in drivers:
        driver_stints = stints.loc[stints["Driver"] == driver]

        previous_stint_end = 0
        for idx, row in driver_stints.iterrows():
            # each row contains the compound name and stint length
            # we can use these information to draw horizontal bars
            plt.barh(
                y=driver,
                width=row["StintLength"],
                left=previous_stint_end,
                color=fastf1.plotting.COMPOUND_COLORS[row["Compound"]],
                edgecolor="black",
                fill=True
            )

            previous_stint_end += row["StintLength"]

    plt.title(f"{sessionDetails.event.year} {sessionDetails.event['EventName']} Tyre Strategy")
    plt.xlabel("Lap Number")
    plt.grid(False)
    # invert the y-axis so drivers that finish higher are closer to the top
    ax.invert_yaxis()

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)

    plt.tight_layout()
    st.pyplot(plt)
    plt.close()

def run():
    col1, col2, col3 = st.columns(3)
    events = []
    eventList = []
    sessions=[]
    sessionTimings=[]
    eventFormat = ""

    year=0
    eventName=""
    sessionName=""

    with col1:
        selectedSeason = st.selectbox(
        "Season",
        ("2024", "2023", "2022", "2021"),
        index=None,
        placeholder="Select Season",
        )

    if selectedSeason != None:
        events = getSeason(int(selectedSeason))
        for event in events:
            eventList.append((event["EventName"]))

    with col2:
        selectedEvent = st.selectbox(
        "Event",
        (eventList),
        index=None,
        placeholder="Select Event",
        )

    if selectedEvent != None:
        for event in events:
            if event["EventName"] == selectedEvent:
                sessions = getSessions(event)
                sessionTimings = getSessionTimings(event)
                eventFormat = event["EventFormat"]

    with col3:
        selectedSession = st.selectbox(
        "Session",
        (sessions),
        index=None,
        placeholder="Select Session",
        )

    try:
        if selectedSeason and selectedEvent and selectedSession != None:
            with st.spinner('Fetching data...'):

                sessionDetails = getSessionDetails(int(selectedSeason),selectedEvent,selectedSession)

                sessionDateTime = ""
                
                if eventFormat == "sprint_shootout":
                    if selectedSession == "Practice 1":
                        sessionDateTime = sessionTimings[0]
                    elif selectedSession == "Qualifying":
                        sessionDateTime = sessionTimings[1]
                    elif selectedSession == "Sprint Shootout":
                        sessionDateTime = sessionTimings[2]
                    elif selectedSession == "Sprint":
                        sessionDateTime = sessionTimings[3]
                    elif selectedSession == "Race":
                        sessionDateTime = sessionTimings[4]   
                else:
                    if selectedSession == "Practice 1":
                        sessionDateTime = sessionTimings[0]
                    elif selectedSession == "Practice 2":
                        sessionDateTime = sessionTimings[1]
                    elif selectedSession == "Practice 3":
                        sessionDateTime = sessionTimings[2]
                    elif selectedSession == "Qualifying":
                        sessionDateTime = sessionTimings[3]
                    elif selectedSession == "Race":
                        sessionDateTime = sessionTimings[4]

                with st.expander("Session Results"):
                    st.header("Session Results")
                    st.write(selectedSession," results for the ", selectedSeason, selectedEvent, "(",sessionDateTime.strftime('%a %-d %b %Y %H:%M:%S, %Z'),")")
                    
                    if selectedSession in ["Practice 1","Practice 2","Practice 3"]:
                        st.info('Practice sessions do not include times.', icon="ℹ️")
                    elif selectedSession in ["Race","Sprint"]:
                        st.info('Times after the first row is the gap from the session leader.', icon="ℹ️")
                    #Session Results
                    df = displaySessionDetails(sessionDetails, selectedSession)
                
                with st.expander("Circuit Overview"):
                    st.header("Circuit Overview")
                    st.write("Circuit related information for the ",selectedSession, " session")
                    circuitTab1, circuitTab2, circuitTab3 = st.tabs(["Circuit Map", "Speed Visualization", "Gear Changes"])
                    #Circuit Map
                    with circuitTab1:
                        displayCircuitMap(sessionDetails)
                    #Speed Visualization
                    with circuitTab2:
                        displayCircuitMapSpeedVis(sessionDetails)
                    #Gear Shift Visualization
                    with circuitTab3:
                        displayCircuitGearVis(sessionDetails)

                if selectedSession in ["Race","Sprint"]:
                    with st.expander("Race Overview"):
                        st.header("Race Overview")
                        st.write(f"{selectedSession} related information for the ",selectedEvent)

                        raceTab1, raceTab2= st.tabs(["Position Changes", "Tyre Strategies"])
                        #Position Changes
                        with raceTab1:
                            displayRacePosChange(sessionDetails)

                        with raceTab2:
                            displayRaceTyreStrategies(sessionDetails)

                if selectedSession in ["Race","Sprint"]:
                    #Sidebar for Anchor links
                    st.sidebar.markdown('''
                    # Jump to
                    - [Session Results](#session-results)
                    - [Circuit Overview](#circuit-overview)
                    - [Race Overview](#race-overview)
                    ''', unsafe_allow_html=True)
                else:
                    #Sidebar for Anchor links
                    st.sidebar.markdown('''
                    # Jump to
                    - [Session Results](#session-results)
                    - [Circuit Overview](#circuit-overview)
                    ''', unsafe_allow_html=True)

    except Exception as error:
        print("An exception occurred:", error)
        st.error("Information is not available yet or does not exist.")

st.set_page_config(page_title="Session Viewer", page_icon="🏁", layout="wide")
st.markdown("# Session Viewer")
st.write("""View specific session details here by selecting the Season, Event, and Session.""")

run()