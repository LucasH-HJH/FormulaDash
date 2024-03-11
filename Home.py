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
import pycountry as pyc
from geopy.geocoders import Nominatim
# import pydeck as pdk
# import folium
# from streamlit_folium import st_folium
import streamlit as st
import fastf1
import fastf1.plotting
from fastf1.core import Laps
from streamlit.logger import get_logger

LOGGER = get_logger(__name__)

def getSeason(year):
    season = fastf1.get_event_schedule(year)
    events = season.to_records(list)
    return events

def getCountryCoords(country):
  geolocator = Nominatim(user_agent="my_app")
  location = geolocator.geocode(country)

  if location:
      return location.longitude, location.latitude
  else:
      print(f"Coordinates not found for '{location_string}'.")
      return None

def run():
    st.write("# Welcome to Formula Dash! 🏎️")
    currentSeasonEvents = getSeason(datetime.datetime.now().year)
    sessionDetails = ""
    countryData = []

    st.header(f"{datetime.datetime.now().year} Season Schedule")

    with st.spinner('Fetching data...'):
      for event in currentSeasonEvents:
        countryName = ""
        if event["Country"] == "Great Britain":
            countryName = "United Kingdom"
        elif event["Country"] == "Abu Dhabi":
          countryName = "United Arab Emirates"
        else:
          countryName = event["Country"]
        
        country = pyc.countries.lookup(countryName)
        lon, lat = getCountryCoords(countryName)

      for event in currentSeasonEvents:
        cardLabel = ""
        countryName = ""
        
        if event["Country"] == "Great Britain":
            countryName = "United Kingdom"
        elif event["Country"] == "Abu Dhabi":
          countryName = "United Arab Emirates"
        else:
          countryName = event["Country"]
        country = pyc.countries.lookup(countryName)

        # if pd.to_datetime(event["EventDate"]) < datetime.datetime.today():
        #   cardLabel = f"{event["OfficialEventName"]} {country.flag} - Completed"
        # else:
        cardLabel = f"{event["OfficialEventName"]}"
        
        print(cardLabel)
        
        with st.expander(cardLabel):
          st.markdown(f'''
          **{country.flag} {event["EventName"]}** - Round {event["RoundNumber"]}\n
          **Location:** {event["Location"]}, {event["Country"]}\n
          ''')

          if pd.isna(event["Session1Date"]) is not True:       
            st.markdown(f"**{event["Session1"]}:** {event["Session1Date"].strftime("%d %b %Y %H:%M %Z")}")

          if pd.isna(event["Session2Date"]) is not True:       
            st.markdown(f"**{event["Session2"]}:** {event["Session2Date"].strftime("%d %b %Y %H:%M %Z")}")

          if pd.isna(event["Session3Date"]) is not True:       
            st.markdown(f"**{event["Session3"]}:** {event["Session3Date"].strftime("%d %b %Y %H:%M %Z")}")

          if pd.isna(event["Session4Date"]) is not True:       
            st.markdown(f"**{event["Session4"]}:** {event["Session4Date"].strftime("%d %b %Y %H:%M %Z")}")

          if pd.isna(event["Session5Date"]) is not True:       
            st.markdown(f"**{event["Session5"]}:** {event["Session5Date"].strftime("%d %b %Y %H:%M %Z")}")
    
st.set_page_config(
    page_title="Formula Dash",
    page_icon="🏎️"
)

if __name__ == "__main__":
    run()
