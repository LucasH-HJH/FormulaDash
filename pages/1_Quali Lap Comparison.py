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
    driverList = {}
    for driver in sessionDetails.results.Abbreviation:
        driverList.update({(sessionDetails.get_driver(driver).FullName) : driver})
    return driverList

def displayQualiLapComparison(sessionDetails1, selectedSeason1, driverDict1, selectedDriver1, sessionDetails2, selectedSeason2, driverDict2, selectedDriver2):
    fastf1.plotting.setup_mpl(misc_mpl_mods=False)

    selectedDriverAbbrv1 = ""
    selectedDriverAbbrv2 = ""

    circuit_info = sessionDetails1.get_circuit_info()

    for name, abbrv in driverDict1.items():
        if name == selectedDriver1:
            selectedDriverAbbrv1 = abbrv

    for name, abbrv in driverDict2.items():
        if name == selectedDriver2:
            selectedDriverAbbrv2 = abbrv

    driver1PlotLabel = f"{selectedDriverAbbrv1} {selectedSeason1}"
    driver2PlotLabel = f"{selectedDriverAbbrv2} {selectedSeason2}"

    driverLap1 = sessionDetails1.laps.pick_drivers(selectedDriverAbbrv1).pick_fastest()
    driverLap2 = sessionDetails2.laps.pick_drivers(selectedDriverAbbrv2).pick_fastest()

    driverTel1 = driverLap1.get_car_data().add_distance()
    driverTel2 = driverLap2.get_car_data().add_distance()

    #driver1Color = fastf1.plotting.driver_color(selectedDriverAbbrv1)
    #driver2Color = fastf1.plotting.driver_color(selectedDriverAbbrv2)

    fig, ax = plt.subplots()
    #ax.plot(driverTel1['Distance'], driverTel1['Speed'], color=driver1Color, label=selectedDriverAbbrv1)
    #ax.plot(driverTel2['Distance'], driverTel2['Speed'], color=driver2Color, label=selectedDriverAbbrv2)
    ax.plot(driverTel1['Distance'], driverTel1['Speed'], color="Yellow", label=driver1PlotLabel)
    ax.plot(driverTel2['Distance'], driverTel2['Speed'], color="Blue", label=driver2PlotLabel)

    ax.set_xlabel('Distance in m')
    ax.set_ylabel('Speed in km/h')

    v_min = driverTel1['Speed'].min()
    v_max = driverTel1['Speed'].max()
    ax.vlines(x=circuit_info.corners['Distance'], ymin=v_min-20, ymax=v_max+20,
            linestyles='dotted', colors='grey')

    for _, corner in circuit_info.corners.iterrows():
        txt = f"{corner['Number']}{corner['Letter']}"
        ax.text(corner['Distance'], v_min-30, txt,
            va='center_baseline', ha='center', size='small')

    ax.legend()
    if sessionDetails1.event["EventDate"] != sessionDetails2.event["EventDate"]:
        plt.suptitle(f"Fastest Quali Lap Comparison - {sessionDetails1.event['EventName']} \n "f"{selectedDriverAbbrv1} {sessionDetails1.event.year} VS "f"{selectedDriverAbbrv2} {sessionDetails2.event.year}")
    else:
        plt.suptitle(f"Fastest Quali Lap Comparison \n "f"{sessionDetails1.event['EventName']} {sessionDetails1.event.year}")
    st.pyplot(plt)
    plt.close()
    st.divider()

    def convertTimestampToString(timestamp):
        return strftimedelta(timestamp, '%m:%s.%ms')
    
    col1, col2 = st.columns(2, gap="medium")
    with col1:
        st.subheader(f'''{selectedDriverAbbrv1} {sessionDetails1.event.year} - {driverLap1["Team"]}''')
        st.markdown(f'''
            **Lap Time**: {convertTimestampToString(driverLap1["LapTime"])}\n
            **Sector 1 Time**: {convertTimestampToString(driverLap1["Sector1Time"])} ({driverLap1["SpeedI1"]} km/h)\n
            **Sector 2 Time**: {convertTimestampToString(driverLap1["Sector2Time"])} ({driverLap1["SpeedI2"]} km/h)\n
            **Sector 3 Time**: {convertTimestampToString(driverLap1["Sector3Time"])} ({driverLap1["SpeedFL"]} km/h)\n
            **Tyre Compound**: {driverLap1["Compound"]}\n
            **Tyre Life**: {int(driverLap1["TyreLife"])} Lap(s)\n
        ''')

    with col2:
        st.subheader(f'''{selectedDriverAbbrv2} {sessionDetails2.event.year} - {driverLap2["Team"]}''')
        st.markdown(f'''
            **Lap Time**: {convertTimestampToString(driverLap2["LapTime"])}\n
            **Sector 1 Time**: {convertTimestampToString(driverLap2["Sector1Time"])} ({driverLap2["SpeedI1"]} km/h)\n
            **Sector 2 Time**: {convertTimestampToString(driverLap2["Sector2Time"])} ({driverLap2["SpeedI2"]} km/h)\n
            **Sector 3 Time**: {convertTimestampToString(driverLap2["Sector3Time"])} ({driverLap2["SpeedFL"]} km/h)\n
            **Tyre Compound**: {driverLap2["Compound"]}\n
            **Tyre Life**: {int(driverLap2["TyreLife"])} Lap(s)\n
        ''')

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
            if event["EventName"] in ["Pre-Season Testing","Pre-Season Track Session","Pre-Season Test"]: # ignore pre-season sessions
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

                driverDict1 = getDriversInSession(sessionDetails1)
                driverDict2 = getDriversInSession(sessionDetails2)

                st.divider()
                st.subheader("Drivers to compare")
                col1,col2 = st.columns(2)
                with col1:
                    selectedDriver1 = st.selectbox(
                    "Driver #1",
                    (driverDict1),
                    index=None,
                    placeholder="Select Driver",
                    )

                with col2:
                    selectedDriver2 = st.selectbox(
                    "Driver #2",
                    (driverDict2),
                    index=None,
                    placeholder="Select Driver",
                    )

            if selectedDriver1 and selectedDriver2 != None:
                st.divider()
                displayQualiLapComparison(sessionDetails1, selectedSeason1, driverDict1, selectedDriver1, sessionDetails2, selectedSeason2, driverDict2, selectedDriver2)

st.set_page_config(page_title="Quali Lap Comparison - Formula Dash", page_icon="⏱️")
st.markdown("# ⏱️ Qualifying Lap Comparison")
st.write("""Compare two fastest qualifying laps by selecting the Season, Event, and Drivers.""")

run()