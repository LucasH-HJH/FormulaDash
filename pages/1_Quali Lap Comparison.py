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

def run():
    col1,col2 = st.columns(2)
    events = []
    eventList = []
    session = "Qualifying"
    sessionTimings=[]

    year=0
    eventName=""
    sessionName=""

    seasonsSince2021 = range(datetime.datetime(2021,1,1).year, datetime.datetime.now().year+1)
    seasonsSince2021 = reversed(seasonsSince2021)

    List2seasonsSince2021 = range(datetime.datetime(2021,1,1).year, datetime.datetime.now().year+1)
    List2seasonsSince2021 = reversed(List2seasonsSince2021)

    with col1:
        st.subheader("Comparison Lap #1")
        selectedSeason1 = st.selectbox(
        "Season",
        (seasonsSince2021),
        index=None,
        key="ALPHA",
        placeholder="Select Season",
        )

    with col2:
        st.subheader("Comparison Lap #2")
        selectedSeason2 = st.selectbox(
        "Season",
        (List2seasonsSince2021),
        index=None,
        key="BRAVO",
        placeholder="Select Season",
        )

    if selectedSeason1 != None:
        events = getSeason(int(selectedSeason1))
        for event in events:
            if event["EventName"] in ["Pre-Season Testing","Pre-Season Track Session","Pre-Season Test"]:
                continue
            else:
                eventList.append((event["EventName"]))

        st.subheader("Event To Compare")
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