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
from unidecode import unidecode
from urllib.parse import unquote
from fastf1.ergast import Ergast # Will be deprecated post 2024
ergast = Ergast()

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
            st.divider()
            
            col1, col2 = st.columns(2)
            
            for driver in driversList:
                if selectedDriver == driver.get("fullName"):
                    driverInfoDict = get_wiki_info(driver["driverUrl"])
                    with col1:
                        st.image(driverInfoDict.get("thumbnail_url"), width=300, caption=driverInfoDict.get("description"))

                    with col2:
                        st.markdown(f'''
                            **Name:** {selectedDriver} ({driver["driverCode"]})\n
                            **Driver Number:** {driver["driverNumber"]}\n
                            **Date of Birth:** {driver["dateOfBirth"].strftime('%Y-%b-%d')} ({(datetime.datetime.now() - driver["dateOfBirth"]).days // 365} Years Old)\n
                            **Nationality:** {driver["driverNationality"]}\n
                        ''')

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