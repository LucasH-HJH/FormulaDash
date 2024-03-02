import numpy as np
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

def run():
    col1, col2, col3 = st.columns(3)
    events = []
    eventList = []
    sessions=[]

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

    with col3:
        selectedSession = st.selectbox(
        "Session",
        (sessions),
        index=None,
        placeholder="Select Session",
        )
    

st.set_page_config(page_title="Session Viewer", page_icon="📹")
st.markdown("# Session Viewer")
st.write("""View specific session details here using the dropdown inputs.""")

run()