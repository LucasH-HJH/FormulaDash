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
import re
import requests
import json
import wikipedia as wiki
from unidecode import unidecode
from urllib.parse import unquote
from fastf1.ergast import Ergast # Will be deprecated post 2024
ergast = Ergast()
import pycountry as pyc
import os
import tempfile
import urllib.request
import csv

def getCountryFromNationality(nationality):
    url = "https://raw.githubusercontent.com/knowitall/chunkedextractor/master/src/main/resources/edu/knowitall/chunkedextractor/demonyms.csv"
    countryInfo = ""

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_filename = os.path.join(temp_dir, "demonyms.csv")

        try:
            with urllib.request.urlopen(url) as response, open(temp_filename, "wb") as f:
                data = response.read()
                f.write(data)

            # Process the downloaded CSV data
            with open(temp_filename, "r") as f:
                reader = csv.reader(f)
                data = list(reader)  # Convert to a list for easier processing
                
            for natCou in data: #natCou stands for Nationality,Country
                if nationality == "Monegasque":
                    nationality = "Monégasque"

                if nationality == natCou[0]:
                    countryInfo = pyc.countries.lookup(natCou[1])
                    break

            return countryInfo

        except urllib.error.URLError as e:
            print(f"Error: Failed to download CSV. {e}")
            return None  # Or raise an exception if preferred

def cleanup(wiki_title):
    try:
        return unquote(wiki_title, errors='strict')
    except UnicodeDecodeError:
        return unquote(wiki_title, encoding='latin-1')

def get_wiki_info(url):

  # Extract the page title from the Wikipedia URL
  wiki_title = url.split("/")[-1]
  wiki_title = cleanup(wiki_title)  # Assuming cleanup function handles encoding

  #SPECIAL CONDITION FOR ALEX ALBON
  if wiki_title == "Alexander_Albon":
    wiki_title = "Alex_Albon"

  # Base URL for the Wikipedia API endpoint
  base_url = "https://en.wikipedia.org/w/api.php"

  # Parameters for the API request
  params = {
      "action": "query",
      "format": "json",
      "prop": "pageimages|pageterms",
      "piprop": "original",
      "titles": wiki_title
  }

  # Send request to the API
  response = requests.get(base_url, params=params)

  # Parse the JSON response
  data = json.loads(response.text)

  # Check if the page exists and has information
  if 'query' in data and 'pages' in data['query'] and data['query']['pages']:
    page_id = list(data['query']['pages'].keys())[0]
    page_data = data['query']['pages'][page_id]

    # Create an empty dictionary to store information
    wiki_info = {}

    # Extract desired information (modify as needed)
    if 'original' in page_data and 'source' in page_data['original']:
      wiki_info['thumbnail_url'] = page_data['original']['source'] #Image
    
    if 'pageid' in page_data:
      wiki_info['page_id'] = page_data['pageid'] #Wikipedia PageID
    
    if 'terms' in page_data and 'description' in page_data['terms']:
        wiki_info['description'] = page_data['terms']['description'][0] #Description
    
    if 'terms' in page_data and 'alias' in page_data['terms']:
        wiki_info['alias'] = page_data['terms']['alias'] #Alias, can have multiple

    return wiki_info

  # Return None if page not found or error occurred
  return None

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

def displayDriverRaceResults(driverId):
    ergast = Ergast(result_type='pandas', auto_cast=True)
    driverResultsInfo = ergast.get_race_results(season='current',driver=driverId)
    races = []
    raceResults = []
    raceResultsDict = {}
    
    # Get race rounds
    for race in driverResultsInfo.description.iterrows():
        races.append(race[1].raceName)

    # Get results for race rounds
    for resultInfo in driverResultsInfo.content:
        for i, _ in enumerate(resultInfo.iterrows()):
            result = resultInfo.loc[i]
            try:
                row_data = {
                "Team": result["constructorName"],
                "Finish Pos.": result["position"],
                "Grid Pos.": result["grid"],
                "Points": result["points"],
                "Status": result["status"],
                "Laps": result["laps"],
                "Fastest Lap Rank": result["fastestLapRank"],
                "Fastest Lap Number": result["fastestLapNumber"],
                "Fastest Lap Time": result["fastestLapTime"],
                "Fastest Lap Average Speed": str(result["fastestLapAvgSpeed"]) + ' ' + result["fastestLapAvgSpeedUnits"]
                }
            except:
                row_data = {
                "Team": result["constructorName"],
                "Finish Pos.": result["position"],
                "Grid Pos.": result["grid"],
                "Points": result["points"],
                "Status": result["status"],
                "Laps": result["laps"],
                "Fastest Lap Rank": 0,
                "Fastest Lap Number": 0,
                "Fastest Lap Time": datetime.timedelta(0),
                "Fastest Lap Average Speed": 0
                }
            raceResults.append(row_data)
            
    raceResultsDict = dict(zip(races, raceResults))
    driverRaceResultsDf = pd.DataFrame.from_dict(raceResultsDict, orient='index')
    driverRaceResultsDf.index.name = 'Race'
    try:
        driverRaceResultsDf["Fastest Lap Time"] = driverRaceResultsDf["Fastest Lap Time"].fillna(pd.Timedelta(seconds=0))  # Replace NaNs with 0
        driverRaceResultsDf["Fastest Lap Time"] = driverRaceResultsDf["Fastest Lap Time"].apply(lambda x: strftimedelta(x, '%h:%m:%s.%ms'))
    except KeyError:
        print("No Time")
    
    st.dataframe(driverRaceResultsDf)

    #Chart Plotting
    fastf1.plotting.setup_mpl(misc_mpl_mods=False)
    plt.figure(figsize=(10, 6))
    plt.plot(driverRaceResultsDf["Points"], color="red")
    plt.xlabel("Race")
    plt.ylabel("Points")
    plt.title("Points Scored by Race")
    plt.ylim(0, 30)  # Set y-axis range from 0 to 30
    plt.grid(True)
    plt.scatter(driverRaceResultsDf.index, driverRaceResultsDf["Points"], color='red', s=50)
    st.pyplot(plt)
    plt.close()

def displayDriverStandingsInfo(driverId):
    ergast = Ergast(result_type='pandas', auto_cast=True)
    driverStandingsInfo = ergast.get_driver_standings(driver=driverId)
    driverSeasons = []
    driverStandings = []
    driverStandingsDict = {}

    # Get driver seasons
    for seasonInfo in driverStandingsInfo.description.iterrows():
        driverSeasons.append(seasonInfo[1].season)
        
    # Get standings for individual seasons
    for standingInfo in driverStandingsInfo.content:
        for i, _ in enumerate(standingInfo.iterrows()):
            standing = standingInfo.loc[i]
            row_data = {
                "Position": standing["positionText"],
                "Team": standing["constructorNames"],
                "Points": standing["points"],
                "Wins": standing["wins"]
            }
            driverStandings.append(row_data)

    driverStandingsDict = dict(zip(driverSeasons, driverStandings))
    driverStandingsDf = pd.DataFrame.from_dict(driverStandingsDict, orient='index')
    driverStandingsDf.index.name = 'Season'
    st.data_editor(
      driverStandingsDf,
      column_config={
            "Season": st.column_config.TextColumn(
                "Season"
            )
        },
      use_container_width=True,
      disabled=True
    )

    #Chart Plotting
    fastf1.plotting.setup_mpl(misc_mpl_mods=False)
    plt.figure(figsize=(10, 6))
    plt.plot(driverStandingsDf["Points"], color="red")
    plt.xlabel("Season")
    plt.ylabel("Points")
    plt.title("Points Scored by Season")
    plt.grid(True)
    plt.scatter(driverStandingsDf.index, driverStandingsDf["Points"], color='red', s=50)
    st.pyplot(plt)
    plt.close()


# def getConstructors():
#     ergast = Ergast()
#     constructorsInfo = ergast.get_constructor_info(season='current',round='last')
#     constructorsList = []
    
#     for i, _ in enumerate(constructorsInfo.iterrows()):
#         constructor = constructorsInfo.loc[i]
#         # Create a dictionary to store the row data
#         row_data = {
#             "constructorId": constructor["constructorId"],
#             "constructorUrl": constructor["constructorUrl"],
#             "constructorName": constructor["constructorName"],
#             "constructorNationality": constructor["constructorNationality"]
#         }
#         constructorsList.append(row_data)

#     print(constructorsList)
#     return constructorsList

def run():
    #tab1, tab2 = st.tabs(["Driver","Team"])
    selectedDriver = ""
    selectedConstructor = ""
    with st.spinner('Fetching data...'):
        driversList = getDrivers()

        driverNameList = []
        for driver in driversList:
            driverName = driver.get("fullName")
            driverNameList.append(driverName)
        selectedDriver = st.selectbox('Driver',driverNameList, index=None, placeholder="Select Driver")
        st.divider()
        col1, col2 = st.columns(2)
        
        for driver in driversList:
            if selectedDriver == driver.get("fullName"):
                driverInfoDict = get_wiki_info(driver["driverUrl"])
                driverCountryInfo = getCountryFromNationality(driver["driverNationality"])
                with col1:
                    st.image(driverInfoDict.get("thumbnail_url"), width=300, caption=driverInfoDict.get("description"))

                with col2:
                    st.subheader(f'''{selectedDriver} ({driver["driverCode"]})''')
                    st.markdown(f'''
                        **Driver Number:** {driver["driverNumber"]}\n
                        **Date of Birth:** {driver["dateOfBirth"].strftime('%Y-%b-%d')} ({(datetime.datetime.now() - driver["dateOfBirth"]).days // 365} Years Old)\n
                        **Nationality:** {driver["driverNationality"]} {driverCountryInfo.flag}\n
                    ''')
                    st.divider()
                    st.subheader("Summary")
                    if driver["fullName"] == "George Russell": # George Russell's wiki page name has (racing driver)
                        driver["fullName"] = "George Russell (racing driver)"
                    st.markdown(wiki.summary(driver["fullName"], auto_suggest=False, sentences=2)) # Display Summary of Driver
                    st.link_button("Go to Wikipedia Page", driver["driverUrl"], use_container_width=True)
                
                st.divider()
                st.header("Current Season Results")
                displayDriverRaceResults(driver["driverId"])
                st.divider()
                st.header("Career Results")
                displayDriverStandingsInfo(driver["driverId"])       

st.set_page_config(page_title="Driver/Team Viewer - Formula Dash", page_icon="👨‍🔧")
st.markdown("# Driver Viewer")
st.write("""View information regarding a Driver participating in the current season.""")

run()