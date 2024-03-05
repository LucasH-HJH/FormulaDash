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
from fastf1.core import Laps

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

def getSessionDetails(year,event,session):
    sessionDetails = fastf1.get_session(year, event, session)
    sessionDetails.load()
    return sessionDetails

def getDriversInSession(sessionDetails):
    driverList = []
    for driver in sessionDetails.results.FullName:
        driverList.append(driver)
    return driverList

def run():
    events1 = []
    events2 = []
    eventList1 = []
    eventList2 = []

    sessionName = "Qualifying"

    driverList1 = []
    driverList2 = []

    selectedDriver1=""
    selectedDriver2=""

    year=0
    eventName=""

    seasonsSince2021 = range(datetime.datetime(2021,1,1).year, datetime.datetime.now().year+1)
    seasonsSince2021 = reversed(seasonsSince2021)

    List2seasonsSince2021 = range(datetime.datetime(2021,1,1).year, datetime.datetime.now().year+1)
    List2seasonsSince2021 = reversed(List2seasonsSince2021)

    st.subheader("Seasons to compare")
    col1,col2 = st.columns(2)
    
    with col1:
        selectedSeason1 = st.selectbox(
        "Season #1",
        (seasonsSince2021),
        index=None,
        key="ALPHA",
        placeholder="Select Season",
        )

    with col2:
        selectedSeason2 = st.selectbox(
        "Season #2",
        (List2seasonsSince2021),
        index=None,
        key="BRAVO",
        placeholder="Select Season",
        )

    if selectedSeason1 and selectedSeason2 != None:
        events1 = getSeason(int(selectedSeason1))
        events2 = getSeason(int(selectedSeason2))
        
        for event in events1:
            if event["EventName"] in ["Pre-Season Testing","Pre-Season Track Session","Pre-Season Test"]:
                continue
            else:
                if pd.Timestamp.today() < event["EventDate"]:
                    continue
                else:
                    eventList1.append((event["EventName"]))
        
        for event in events2:
            if event["EventName"] in ["Pre-Season Testing","Pre-Season Track Session","Pre-Season Test"]:
                continue
            else:
                if pd.Timestamp.today() < event["EventDate"]:
                    continue
                else:
                    eventList2.append((event["EventName"]))

        eventSet1 = set(eventList1)
        eventSet2 = set(eventList2)
        matchingEventsList = list(eventSet1.intersection(eventSet2))

        st.divider()
        st.subheader("Event to compare")
        selectedEvent = st.selectbox(
        "Event",
        (matchingEventsList),
        index=None,
        placeholder="Select Event",
        )

        if selectedEvent != None:
            with st.spinner('Fetching data...'):
                sessionDetails1 = getSessionDetails(int(selectedSeason1),selectedEvent,sessionName)
                sessionDetails2 = getSessionDetails(int(selectedSeason2),selectedEvent,sessionName)

                driverList1 = getDriversInSession(sessionDetails1)
                driverList2 = getDriversInSession(sessionDetails2)

                st.divider()
                st.subheader("Drivers to compare")
                col1,col2 = st.columns(2)
                with col1:
                    selectedDriver1 = st.selectbox(
                    "Driver #1",
                    (driverList1),
                    index=None,
                    placeholder="Select Driver",
                    )

                with col2:
                    selectedDriver2 = st.selectbox(
                    "Driver #2",
                    (driverList2),
                    index=None,
                    placeholder="Select Driver",
                    )

        if selectedDriver1 and selectedDriver2 != None:
            print("YAY")
            #continue from here
        

st.set_page_config(page_title="Quali Lap Comparison", page_icon="⏱️")
st.markdown("# Qualifying Lap Comparison")
st.write("""Compare two different fastest laps qualifying laps by selecting the Season, Event, and Drivers.""")

run()

# def plotting_demo():
#     progress_bar = st.sidebar.progress(0)
#     status_text = st.sidebar.empty()
#     last_rows = np.random.randn(1, 1)
#     chart = st.line_chart(last_rows)

#     for i in range(1, 101):
#         new_rows = last_rows[-1, :] + np.random.randn(5, 1).cumsum(axis=0)
#         status_text.text("%i%% Complete" % i)
#         chart.add_rows(new_rows)
#         progress_bar.progress(i)
#         last_rows = new_rows
#         time.sleep(0.05)

#     progress_bar.empty()

#     # Streamlit widgets automatically run the script from top to bottom. Since
#     # this button is not connected to any other logic, it just causes a plain
#     # rerun.
#     st.button("Re-run")


# st.set_page_config(page_title="Plotting Demo", page_icon="📈")
# st.markdown("# Plotting Demo")
# st.sidebar.header("Plotting Demo")
# st.write(
#     """This demo illustrates a combination of plotting and animation with
# Streamlit. We're generating a bunch of random numbers in a loop for around
# 5 seconds. Enjoy!"""
# )

# plotting_demo()

# show_code(plotting_demo)