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
from fastf1.ergast import Ergast # Will be deprecated post 2024
ergast = Ergast()

def getDrivers():
    ergast = Ergast()
    driversInfo = ergast.get_driver_info(season='current',round='last')
    driversList = []
    
    for i, _ in enumerate(driversInfo.iterrows()):
        driver = driversInfo.loc[i]
        # Create a dictionary to store the row data
        row_data = {
            "driverId": driver["driverId"],
            "driverNumber": driver["driverNumber"],
            "driverCode": driver["driverCode"],
            "driverUrl": driver["driverUrl"],
            "givenName": driver["givenName"],
            "familyName": driver["familyName"],
            "fullName": driver["givenName"] + ' ' + driver["familyName"],
            "dateOfBirth": driver["dateOfBirth"],
            "driverNationality": driver["driverNationality"]
        }
        driversList.append(row_data)

    return driversList

def getConstructors():
    ergast = Ergast()
    constructorsInfo = ergast.get_constructor_info(season='current',round='last')
    constructorsList = []
    
    for i, _ in enumerate(constructorsInfo.iterrows()):
        constructor = constructorsInfo.loc[i]
        # Create a dictionary to store the row data
        row_data = {
            "costructorId": constructor["constructorId"],
            "constructorUrl": constructor["constructorUrl"],
            "constructorName": constructor["constructorName"],
            "constructorNationality": constructor["constructorNationality"]
        }
        constructorsList.append(row_data)

    return constructorsList

def run():
    tab1, tab2 = st.tabs(["Driver","Team"])
    selectedDriver = ""
    selectedConstructor = ""
    with st.spinner('Fetching data...'):
        driversList = getDrivers()
        constructorsList = getConstructors()

        with tab1:
            driverNameList = []
            for driver in driversList:
                driverName = driver.get("fullName")
                driverNameList.append(driverName)
            selectedDriver = st.selectbox('Driver',driverNameList, index=None, placeholder="Select Driver")
            

        with tab2:
            constructorNameList = []
            for constructor in constructorsList:
                constructorName = constructor.get("constructorName")
                constructorNameList.append(constructorName)
            selectedConstructor = st.selectbox('Team',constructorNameList, index=None, placeholder="Select Team")
        

st.set_page_config(page_title="Driver/Team Viewer - Formula Dash", page_icon="👨‍🔧")
st.markdown("# Driver/Team Viewer")
st.write("""View information regarding a Driver or Team participating in the current season.""")

run()