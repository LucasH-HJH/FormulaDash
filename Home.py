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
import streamlit as st
import fastf1
import fastf1.plotting
from fastf1.core import Laps
from fastf1.ergast import Ergast # Will be deprecated post 2024
ergast = Ergast()
import requests
import wikipedia as wiki
from bs4 import BeautifulSoup
from urllib.request import urlopen
from unidecode import unidecode
from urllib.parse import unquote
from streamlit.logger import get_logger
LOGGER = get_logger(__name__)

def getSeason(year):
  season = fastf1.get_event_schedule(year)
  events = season.to_records(list)
  return events

# def getCountryCoords(country):
#   geolocator = Nominatim(user_agent="my_app")
#   location = geolocator.geocode(country)

#   if location:
#       return location.longitude, location.latitude
#   else:
#       print(f"Coordinates not found for '{country}'.")
#       return None
  
# def cleanup(wiki_title):
#     try:
#         return unquote(wiki_title, errors='strict')
#     except UnicodeDecodeError:
#         return unquote(wiki_title, encoding='latin-1')
    
# def get_wiki_info(url):

#     # Extract the page title from the Wikipedia URL
#     wiki_title = url.split("/")[-1]
#     wiki_title = cleanup(wiki_title)  # Assuming cleanup function handles encoding

#     # Base URL for Wikipedia page
#     base_url = "https://en.wikipedia.org/wiki/"

#     # Send request to Wikipedia page
#     response = requests.get(f"{base_url}{wiki_title}")

#     # Check for successful response
#     if response.status_code != 200:
#         print(f"Error: Failed to access page {url} (status code: {response.status_code})")
#         return None

#     # Parse the HTML content
#     soup = BeautifulSoup(response.content, 'html.parser')

#     # Select all images within the infobox
#     infobox_images = soup.select(".infobox-image img")

#     # Check if there are any images
#     if not infobox_images:
#         return None

#     # Handle single image case
#     if len(infobox_images) == 1 or wiki_title == "Circuit_de_Monaco":
#         main_image_url = infobox_images[0].get('src')
#     # Handle multiple images (return second image)
#     else:
#         main_image_url = infobox_images[1].get('src')

#     # Handle relative URLs (optional)
#     if main_image_url.startswith("//"):
#         main_image_url = f"https:{main_image_url}"
#     elif not main_image_url.startswith("http"):
#         main_image_url = f"{base_url}{main_image_url}"

#     return main_image_url

def displayCurrentSeasonSchedule():
  with st.spinner('Fetching data...'):
    col1, col2 = st.columns(2, gap="Medium")
    currentSeasonEvents = getSeason(datetime.datetime.now().year)
    currentSeasonRaceSchedule = ergast.get_race_schedule(season=datetime.datetime.now().year)
    currentSeasonCircuits = ergast.get_circuits(season=datetime.datetime.now().year)
    currentSeasonScheduleDict = {}

    # Display season schedule
    for event in currentSeasonEvents:
      event_data = {}
      countryName = ""
      
      # Standardize country name
      if event["Country"] == "Great Britain":
          countryName = "United Kingdom"
      elif event["Country"] == "Abu Dhabi":
        countryName = "United Arab Emirates"
      else:
        countryName = event["Country"]
      country = pyc.countries.lookup(countryName)

      # Get Ergast circuitId to cross-ref to get circuit info
      for index, row in currentSeasonRaceSchedule.iterrows():
        if row["raceName"] == event["EventName"]:
          circuitId = row["circuitId"]
          for index, row in currentSeasonCircuits.iterrows():
            if circuitId == row["circuitId"]:
              # Add event_data to currentSeasonScheduleDict
              event_data["officialEventName"] = event["OfficialEventName"]
              event_data["roundNumber"] = event["RoundNumber"]
              event_data["location"] = event["Location"]
              event_data["circuitName"] = row["circuitName"]
              event_data["circuitLat"] = row["lat"]
              event_data["circuitLon"] = row["long"]
              event_data["circuitUrl"] = row["circuitUrl"]
              event_data["country"] = country
              event_data["eventDate"] = [event["EventDate"]]
              event_data["eventFormat"] = [event["EventFormat"]]
              event_data["session1"] = event["Session1"]
              event_data["session2"] = event["Session2"]
              event_data["session3"] = event["Session3"]
              event_data["session4"] = event["Session4"]
              event_data["session5"] = event["Session5"]
              event_data["session1Date"] = event["Session1Date"]
              event_data["session2Date"] = event["Session2Date"]
              event_data["session3Date"] = event["Session3Date"]
              event_data["session4Date"] = event["Session4Date"]
              event_data["session5Date"] = event["Session5Date"]
              currentSeasonScheduleDict[event["EventName"]] = event_data

    print(currentSeasonScheduleDict)

    # Display each event in currentSeasonScheduleDict
    for i, event in enumerate(currentSeasonScheduleDict.values()):
      country = event["country"]
      if pd.to_datetime(event["eventDate"]) < datetime.datetime.today():
        cardLabel = f'''Round {event["roundNumber"]} - {event["officialEventName"]} {country.flag} - 🏁'''
      else:
        cardLabel = f'''Round {event["roundNumber"]} - {event["officialEventName"]} {country.flag}'''
      
      with st.expander(cardLabel):
        st.markdown(f'''**Location:** {event["circuitName"]} - {event["location"]}, {country.name}\n''')
        
        if hasattr(event["session1Date"], 'tzinfo'):       
          st.markdown(f'''**{event["session1"]}:** {event["session1Date"].strftime("%d %b %Y %H:%M %Z")}''')
        if hasattr(event["session2Date"], 'tzinfo'):       
          st.markdown(f'''**{event["session2"]}:** {event["session2Date"].strftime("%d %b %Y %H:%M %Z")}''')
        if hasattr(event["session3Date"], 'tzinfo'):       
          st.markdown(f'''**{event["session3"]}:** {event["session3Date"].strftime("%d %b %Y %H:%M %Z")}''')
        if hasattr(event["session4Date"], 'tzinfo'):       
          st.markdown(f'''**{event["session4"]}:** {event["session4Date"].strftime("%d %b %Y %H:%M %Z")}''')
        if hasattr(event["session5Date"], 'tzinfo'):       
          st.markdown(f'''**{event["session5"]}:** {event["session5Date"].strftime("%d %b %Y %H:%M %Z")}''')
              

      # # Check if race over
      # if pd.to_datetime(event["EventDate"]) < datetime.datetime.today():
      #   cardLabel = f'''Round {event["RoundNumber"]} - {event["OfficialEventName"]} {country.flag} - 🏁'''
      # else:
      #   cardLabel = f'''Round {event["RoundNumber"]} - {event["OfficialEventName"]} {country.flag}'''
      
      # with col:
      #   with st.expander(cardLabel):
      #     # col1, col2 = st.columns(2)
          
      #     # with col1:
      #       st.markdown(f'''
      #       **Location:** {circuitName} - {event["Location"]}, {event["Country"]}\n
      #       ''')

      #       if pd.isna(event["Session1Date"]) is not True:       
      #         st.markdown(f'''**{event["Session1"]}:** {event["Session1Date"].strftime("%d %b %Y %H:%M %Z")}''')

      #       if pd.isna(event["Session2Date"]) is not True:       
      #         st.markdown(f'''**{event["Session2"]}:** {event["Session2Date"].strftime("%d %b %Y %H:%M %Z")}''')

      #       if pd.isna(event["Session3Date"]) is not True:       
      #         st.markdown(f'''**{event["Session3"]}:** {event["Session3Date"].strftime("%d %b %Y %H:%M %Z")}''')

      #       if pd.isna(event["Session4Date"]) is not True:       
      #         st.markdown(f'''**{event["Session4"]}:** {event["Session4Date"].strftime("%d %b %Y %H:%M %Z")}''')

      #       if pd.isna(event["Session5Date"]) is not True:       
      #         st.markdown(f'''**{event["Session5"]}:** {event["Session5Date"].strftime("%d %b %Y %H:%M %Z")}''')

def displayDriverCurrentStandings():
  with st.spinner('Fetching data...'):
    ergast = Ergast()
    currentDriverStandings = ergast.get_driver_standings(season='current', round='last')
    currentDriverStandings = currentDriverStandings.content[0]
    DriverStandingsDf = pd.DataFrame(columns=[])

    for i, _ in enumerate(currentDriverStandings.iterrows()):
        driver = currentDriverStandings.loc[i]

        # Create a dictionary to store the row data
        row_data = {
          "Position": driver["positionText"],  # Use column names if different
          "Driver": driver["givenName"] + ' ' + driver["familyName"],  # Combine names
          "Constructor": driver["constructorNames"],
          "Current Points": driver["points"],
          "Wins": driver["wins"]
        }

        # Append the row data as a Series to the DataFrame
        DriverStandingsDf = pd.concat([DriverStandingsDf, pd.DataFrame([row_data])], ignore_index=True)

    st.data_editor(
      DriverStandingsDf,
      height=737,
      use_container_width=True,
      disabled=True,
      hide_index=True,
    )

def displayConstructorCurrentStandings():
  with st.spinner('Fetching data...'):
    ergast = Ergast()
    currentConstructorStandings = ergast.get_constructor_standings(season='current', round='last')
    currentConstructorStandings = currentConstructorStandings.content[0]
    ConstructorsStandingsDf = pd.DataFrame(columns=[])

    for i, _ in enumerate(currentConstructorStandings.iterrows()):
      constructor = currentConstructorStandings.loc[i]

      # Create a dictionary to store the row data
      row_data = {
        "Position": constructor["positionText"],  # Use column names if different
        "Constructor": constructor["constructorName"],
        "Current Points": constructor["points"],
        "Wins": constructor["wins"]
      }

      # Append the row data as a Series to the DataFrame
      ConstructorsStandingsDf = pd.concat([ConstructorsStandingsDf, pd.DataFrame([row_data])], ignore_index=True)

    st.data_editor(
      ConstructorsStandingsDf,
      use_container_width=True,
      disabled=True,
      hide_index=True,
    )

def displayWDCPrediction():
  with st.spinner('Calculating...'):
    # Get current standings after last race
    ergast = Ergast()
    lastRace = ergast.get_race_schedule(season='current', round='last')
    currentRound = lastRace["round"].values[0]
    driver_standings = ergast.get_driver_standings(season="current", round="last")
    driver_standings =  driver_standings.content[0]

    # Calculate max points for remaining season
    POINTS_FOR_SPRINT = 8 + 25 + 1  # Winning the sprint, race and fastest lap
    POINTS_FOR_CONVENTIONAL = 25 + 1  # Winning the race and fastest lap

    events = fastf1.events.get_event_schedule(datetime.datetime.now().year, backend='ergast')
    events = events[events['RoundNumber'] > currentRound]

    # Count how many sprints and conventional races are left
    sprint_events = len(events.loc[events["EventFormat"] == "sprint_shootout"])
    conventional_events = len(events.loc[events["EventFormat"] == "conventional"])

    # Calculate points for each
    sprint_points = sprint_events * POINTS_FOR_SPRINT
    conventional_points = conventional_events * POINTS_FOR_CONVENTIONAL
    max_points = sprint_points + conventional_points

    # Calculate who can win
    LEADER_POINTS = int(driver_standings.loc[0]['points'])

    WDCPredictDf = pd.DataFrame(columns=[])

    for i, _ in enumerate(driver_standings.iterrows()):
        driver = driver_standings.loc[i]
        driver_max_points = int(driver["points"]) + max_points
        can_win = 'No' if driver_max_points < LEADER_POINTS else 'Yes'

        # Create a dictionary to store the row data
        row_data = {
          "Position": driver["positionText"],  # Use column names if different
          "Driver": driver["givenName"] + ' ' + driver["familyName"],  # Combine names
          "Constructor": driver["constructorNames"],
          "Current Points": driver["points"],
          "Theoretical Max Points": driver_max_points,
          "Can Win": can_win
        }

        # Append the row data as a Series to the DataFrame
        WDCPredictDf = pd.concat([WDCPredictDf, pd.DataFrame([row_data])], ignore_index=True)

    st.data_editor(
      WDCPredictDf,
      height=737,
      use_container_width=True,
      disabled=True,
      hide_index=True,
    )

def run():
  st.write("# Welcome to Formula Dash! 🏎️")

  st.header(f"{datetime.datetime.now().year} Season Standings")
  with st.expander("Current Season Standings"):
    tab1, tab2 = st.tabs(["Drivers", "Constructors"])
    with tab1:
      st.header("Drivers Standings")
      displayDriverCurrentStandings()
    with tab2:
      st.header("Constructors Standings")
      displayConstructorCurrentStandings()
        
  st.header(f"{datetime.datetime.now().year} Championship Prediction")
  with st.expander("Championship Prediction"):
    st.markdown(f'''Who can still win the **World Driver's Championship?**''')
    displayWDCPrediction()
  
  st.divider()

  st.header(f"{datetime.datetime.now().year} Season Schedule")
  displayCurrentSeasonSchedule()

  st.divider()

  #Sidebar for Anchor links
  st.sidebar.markdown(f'''
  # Jump to
  - [Season Standings](#{datetime.datetime.now().year}-season-standings)
  - [WDC Prediction](#world-driver-s-championship-prediction)
  - [Season Schedule](#{datetime.datetime.now().year}-season-schedule)
  ''', unsafe_allow_html=True)
    

st.set_page_config(
  page_title="Formula Dash",
  page_icon="🏎️"
)

if __name__ == "__main__":
  run()
