import numpy as np
import pandas as pd
import datetime
import time
import streamlit as st
import fastf1

def format_time(timedelta_value):
    """
    Formats a timedelta object into a text representation (01:29.990),
    handling NaN values.
    """
    if pd.isna(timedelta_value):
        return "-"

    total_seconds = timedelta_value.total_seconds()

    # Ensure integer values for hours, minutes, seconds
    hours = int(total_seconds // 3600)
    remainder = total_seconds % 3600
    minutes = int(remainder // 60)
    seconds = int(remainder % 60)
    milliseconds = timedelta_value.microseconds // 1000

    # Format each component with leading zeros
    formatted_hours = f"{hours:02d}"
    formatted_minutes = f"{minutes:02d}"
    formatted_seconds = f"{seconds:02d}.{milliseconds:03d}"

    # Combine formatted components with colon separators
    return ":".join([formatted_hours, formatted_minutes, formatted_seconds])

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

    match session:
        case "Practice 1" | "Practice 2" | "Practice 3":
            return sessionDetails.results.loc[:, ['Position','HeadshotUrl','FullName','Abbreviation','DriverNumber','CountryCode','TeamName','ClassifiedPosition','GridPosition','Q1','Q2','Q3','Time','Status','Points']]
        case "Qualifying":
            return sessionDetails.results.loc[:, ['Position','HeadshotUrl','FullName','Abbreviation','DriverNumber','CountryCode','TeamName','ClassifiedPosition','GridPosition','Q1','Q2','Q3','Time','Status','Points']]
        case "Race":
            return sessionDetails.results.loc[:, ['Position','HeadshotUrl','FullName','Abbreviation','DriverNumber','CountryCode','TeamName','ClassifiedPosition','GridPosition','Q1','Q2','Q3','Time','Status','Points']]
        case "Sprint Shootout":
            return sessionDetails.results.loc[:, ['Position','HeadshotUrl','FullName','Abbreviation','DriverNumber','CountryCode','TeamName','ClassifiedPosition','GridPosition','Q1','Q2','Q3','Time','Status','Points']]
        case "Sprint":
            return sessionDetails.results.loc[:, ['ClassifiedPosition','HeadshotUrl','FullName','Abbreviation','DriverNumber','CountryCode','TeamName','GridPosition','Time','Status','Points']] 

def displaySessionDetails(sessionDetails):
    df = pd.DataFrame(sessionDetails)
    df["Time"] = df["Time"].apply(format_time)
    df = df.reset_index(drop=True)

    st.data_editor(
        df,
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
            "CountryCode": st.column_config.TextColumn(
                "Country"
            ),
            "TeamName": st.column_config.TextColumn(
                "Constructor",
            ),
            "GridPosition": st.column_config.Column(
                "Grid",
            ),
            "Time": st.column_config.Column(
                "Time"
            ),
        },
        hide_index=True,
    )

    return df

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
                    match selectedSession:
                        case "Practice 1":
                            sessionDateTime = sessionTimings[0]
                        case "Qualifying":
                            sessionDateTime = sessionTimings[1]
                        case "Sprint Shootout":
                            sessionDateTime = sessionTimings[2]
                        case "Sprint":
                            sessionDateTime = sessionTimings[3]
                        case "Race":
                            sessionDateTime = sessionTimings[4]   
                else:
                    match selectedSession:
                        case "Practice 1":
                            sessionDateTime = sessionTimings[0]
                        case "Practice 2":
                            sessionDateTime = sessionTimings[1]
                        case "Practice 3":
                            sessionDateTime = sessionTimings[2]
                        case "Qualifying":
                            sessionDateTime = sessionTimings[3]
                        case "Race":
                            sessionDateTime = sessionTimings[4]

                st.divider()
                st.subheader("Session Results")
                st.write(selectedSession," results for the ", selectedSeason, selectedEvent, "(",sessionDateTime.strftime('%a %-d %b %Y %H:%M:%S, %Z'),")")
                df = displaySessionDetails(sessionDetails)  
    except KeyError:
        st.error("Information is not available yet or does not exist.")

st.set_page_config(page_title="Session Viewer", page_icon="📹", layout="wide")
st.markdown("# Session Viewer")
st.write("""View specific session details here by selecting the Season, Event, and Session.""")

run()