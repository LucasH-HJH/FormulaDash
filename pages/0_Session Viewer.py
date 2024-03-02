import numpy as np
import pandas as pd
import datetime
import time
import streamlit as st
import fastf1

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

    if session == "Practice 1" or "Practice 2" or "Practice 3":
            return sessionDetails.results.loc[:, ['Position','HeadshotUrl','FullName','Abbreviation','DriverNumber','CountryCode','TeamName','ClassifiedPosition','GridPosition','Q1','Q2','Q3','Time','Status','Points']]
    elif session == "Qualifying":
            return sessionDetails.results.loc[:, ['Position','HeadshotUrl','FullName','Abbreviation','DriverNumber','CountryCode','TeamName','ClassifiedPosition','GridPosition','Q1','Q2','Q3','Time','Status','Points']]
    elif session == "Race":
            return sessionDetails.results.loc[:, ['Position','HeadshotUrl','FullName','Abbreviation','DriverNumber','CountryCode','TeamName','ClassifiedPosition','GridPosition','Q1','Q2','Q3','Time','Status','Points']]
    elif session == "Sprint Shootout":
            return sessionDetails.results.loc[:, ['Position','HeadshotUrl','FullName','Abbreviation','DriverNumber','CountryCode','TeamName','ClassifiedPosition','GridPosition','Q1','Q2','Q3','Time','Status','Points']]
    elif session =="Sprint":
            return sessionDetails.results.loc[:, ['ClassifiedPosition','HeadshotUrl','FullName','Abbreviation','DriverNumber','CountryCode','TeamName','GridPosition','Time','Status','Points']] 

def displaySessionDetails(sessionDetails):
    df = pd.DataFrame(sessionDetails)
    df = df.reset_index(drop=True)

    def format_timedelta(timedelta_obj):
        if pd.isna(timedelta_obj):
            return "-"  # Return a placeholder for NaN values

        total_seconds = timedelta_obj.total_seconds()
        hours = int(total_seconds // 3600)
        minutes = int((total_seconds % 3600) // 60)
        seconds = int(total_seconds % 60)
        milliseconds = int(total_seconds * 1000 % 1000)  # Extract milliseconds
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}.{milliseconds:03d}"

    # Convert Time to timedelta and format manually
    df["Time"] = df["Time"].apply(
        lambda x: format_timedelta(x)  # Call a separate function for formatting
    )

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

                st.divider()
                st.subheader("Session Results")
                st.write(selectedSession," results for the ", selectedSeason, selectedEvent, "(",sessionDateTime.strftime('%a %-d %b %Y %H:%M:%S, %Z'),")")
                st.write("Times after the first row are the gap from the session leader.")
                df = displaySessionDetails(sessionDetails)  
    except KeyError:
        st.error("Information is not available yet or does not exist.")

st.set_page_config(page_title="Session Viewer", page_icon="📹", layout="wide")
st.markdown("# Session Viewer")
st.write("""View specific session details here by selecting the Season, Event, and Session.""")

run()