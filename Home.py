import csv
import pandas as pd
import datetime
from datetime import date
from timple.timedelta import strftimedelta
import pycountry as pyc
import streamlit as st
from streamlit_calendar import calendar
import fastf1
import fastf1.plotting
from fastf1.ergast import Ergast # Will be deprecated post 2024
ergast = Ergast()
import requests
import wikipedia as wiki
from bs4 import BeautifulSoup
from urllib.request import urlopen
from unidecode import unidecode
from urllib.parse import unquote
from streamlit_extras.stylable_container import stylable_container
from streamlit.logger import get_logger
LOGGER = get_logger(__name__)

def queryDriverHeadshot():
  driverHeadshotDict = {}
  # HAVE TO UPDATE driver_headshot.csv MANUALLY IF THERE ARE CHANGES
  with open("info-database/driver_headshot.csv", 'r') as csvfile:
    reader = csv.reader(csvfile)
    for row in reader:
      driver_abbreviation, driver_image_url = row
      driverHeadshotDict[driver_abbreviation] = driver_image_url
  
  return driverHeadshotDict

def queryConstructorLogo():
  constructorLogoDict = {}
  # HAVE TO UPDATE constructor_logo.csv MANUALLY IF THERE ARE CHANGES
  with open("info-database/constructor_logo.csv", 'r') as csvfile:
    reader = csv.reader(csvfile)
    for row in reader:
      constructor_id, constructor_logo_url = row
      constructorLogoDict[constructor_id] = constructor_logo_url
  
  return constructorLogoDict

def getSeason(year):
  season = fastf1.get_event_schedule(year)
  events = season.to_records(list)
  return events
  
def cleanup(wiki_title):
    try:
        return unquote(wiki_title, errors='strict')
    except UnicodeDecodeError:
        return unquote(wiki_title, encoding='latin-1')
    
def get_wiki_info(url):

    # Extract the page title from the Wikipedia URL
    wiki_title = url.split("/")[-1]
    wiki_title = cleanup(wiki_title)  # Assuming cleanup function handles encoding

    # Base URL for Wikipedia page
    base_url = "https://en.wikipedia.org/wiki/"

    # Send request to Wikipedia page
    response = requests.get(f"{base_url}{wiki_title}")

    # Check for successful response
    if response.status_code != 200:
        print(f"Error: Failed to access page {url} (status code: {response.status_code})")
        return None

    # Parse the HTML content
    soup = BeautifulSoup(response.content, 'html.parser')

    # Select all images within the infobox
    infobox_images = soup.select(".infobox-image img")

    # Check if there are any images
    if not infobox_images:
        return None

    # Handle single image case
    if len(infobox_images) == 1 or wiki_title == "Circuit_de_Monaco" or wiki_title == "Melbourne_Grand_Prix_Circuit":
        main_image_url = infobox_images[0].get('src')
    # Handle multiple images (return second image)
    else:
        main_image_url = infobox_images[1].get('src')

    # Handle relative URLs (optional)
    if main_image_url.startswith("//"):
        main_image_url = f"https:{main_image_url}"
    elif not main_image_url.startswith("http"):
        main_image_url = f"{base_url}{main_image_url}"

    return main_image_url

def getCurrentSeasonSchedule():
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
              event_data["eventName"] = event["EventName"]
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

    #print(currentSeasonScheduleDict)
    return currentSeasonScheduleDict

def displayCurrentSeasonSchedule(currentSeasonScheduleDict):
  # Display each event in currentSeasonScheduleDict
  currentRound = ergast.get_race_results(season="current",round="last")
  nextRound = currentRound.description["round"] + 1

  for i, event in enumerate(currentSeasonScheduleDict.values()):
    country = event["country"]
    
    # Completed event
    if pd.to_datetime(event["eventDate"]) < datetime.datetime.today(): 
      cardLabel = f'''Round {event["roundNumber"]} - {event["officialEventName"]} {country.flag} - 🏁'''
      cardExpand = False

    # Not completed and is next event
    elif pd.to_datetime(event["eventDate"]) > datetime.datetime.today() and event["roundNumber"] == nextRound.item():
      cardLabel = f'''Round {event["roundNumber"]} - {event["officialEventName"]} {country.flag}'''
      cardExpand = True
    
    # Not completed and is not next event
    else: 
      cardLabel = f'''Round {event["roundNumber"]} - {event["officialEventName"]} {country.flag}'''
      cardExpand = False
    
    with st.expander(cardLabel,expanded=cardExpand):
      col1, col2 = st.columns(2, gap="Medium")
      
      with col1:
        if cardExpand:
            st.markdown(''':red[Upcoming Race Weekend!]''')
        
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

      with col2:
        with stylable_container(
          key="circuit_image_container",
          css_styles='''
          {
            background-color: white;
            border: 1px solid rgba(49, 51, 63, 0.2);
            border-radius: 0.5rem;
            display: flex;
            justify-content: center;
            align-items: center;
            color:black;
          }
          '''
        ):
          st.image(get_wiki_info(event["circuitUrl"]), use_column_width="always")
        st.link_button("Go to Wikipedia Page", event["circuitUrl"], use_container_width=True)

def displayCurrentSeasonCalendar(currentSeasonScheduleDict):
  with st.spinner('Fetching data...'):
    events = [] # Initialize events list
    calendar_resources = [] # Initialize calendar resources

    # Populate Event Calendar Events
    for i, event in enumerate(currentSeasonScheduleDict.values()):
        sessionName = ""
        
        if event["session1"]:
          sessionName = event['eventName'] + ' - ' + event['session1']
          events.append({"title": sessionName, "backgroundColor": "#FFBD45", "borderColor": "#FFBD45", "start": event["session1Date"].strftime("%Y-%m-%dT%H:%M:%S"), "end": event["session1Date"].strftime("%Y-%m-%dT%H:%M:%S"), "resourceId": str(event["roundNumber"])})

        if event["session2"]:
          sessionName = event['eventName'] + ' - ' + event['session2']
          events.append({"title": sessionName, "backgroundColor": "#FFBD45", "borderColor": "#FFBD45", "start": event["session2Date"].strftime("%Y-%m-%dT%H:%M:%S"), "end": event["session2Date"].strftime("%Y-%m-%dT%H:%M:%S"), "resourceId": str(event["roundNumber"])})

        if event["session3"]:
          sessionName = event['eventName'] + ' - ' + event['session3']
          events.append({"title": sessionName, "backgroundColor": "#FFBD45", "borderColor": "#FFBD45", "start": event["session3Date"].strftime("%Y-%m-%dT%H:%M:%S"), "end": event["session3Date"].strftime("%Y-%m-%dT%H:%M:%S"), "resourceId": str(event["roundNumber"])})

        if event["session4"]:
          sessionName = event['eventName'] + ' - ' + event['session4']
          events.append({"title": sessionName, "backgroundColor": "#FFBD45", "borderColor": "#FFBD45", "start": event["session4Date"].strftime("%Y-%m-%dT%H:%M:%S"), "end": event["session4Date"].strftime("%Y-%m-%dT%H:%M:%S"), "resourceId": str(event["roundNumber"])})

        if event["session5"]:
          sessionName = event['eventName'] + ' - ' + event['session5']
          events.append({"title": sessionName, "backgroundColor": "#FF6C6C", "borderColor": "#FF6C6C", "start": event["session5Date"].strftime("%Y-%m-%dT%H:%M:%S"), "end": event["session5Date"].strftime("%Y-%m-%dT%H:%M:%S"), "resourceId": str(event["roundNumber"])})

    # Populate Event Calendar Resources
    for i, event in enumerate(currentSeasonScheduleDict.values()):
        calendar_resources.append({"id": str(event["roundNumber"]), "event": event["officialEventName"], "location": event["location"], "date": pd.to_datetime(event["eventDate"][0]).strftime("%Y-%m-%dT%H:%M:%S")})

  currentDate = date.today().strftime("%Y-%m-%d")

  calendar_options = {
      "editable": "false",
      "navLinks": "false",
      "resources": calendar_resources,
      "headerToolbar": {
          "left": "today prev,next",
          "center": "title",
          "right": "dayGridDay,dayGridWeek,dayGridMonth",
      },
      "initialDate": currentDate,
      "initialView": "dayGridMonth",
  }

  calendar(
      events=st.session_state.get("events", events),
      options=calendar_options,
      custom_css="""
      .fc-event-past {
          opacity: 0.8;
      }
      .fc-event-time {
          font-style: italic;
      }
      .fc-event-title {
          font-weight: 700;
      }
      .fc-toolbar-title {
          font-size: 2rem;
      }
      """,
  )

def displayDriverCurrentStandings():
  with st.spinner('Fetching data...'):
    # Get current round standings
    ergast = Ergast()
    currentDriverStandings = ergast.get_driver_standings(season='current', round='last')
    currentDriverStandingsContent = currentDriverStandings.content[0]
    currentRound = currentDriverStandings.description["round"].item()

    driverHeadshotDict = queryDriverHeadshot() # Get Driver Headshots

    # Get previous round standings
    lastRound = currentDriverStandings.description["round"].item() - 1
    previousDriverStandings = ""
    
    if lastRound != 1: # Check if not first round
      previousDriverStandings = ergast.get_driver_standings(season='current', round=str(lastRound))
      previousDriverStandingsContent = previousDriverStandings.content[0]

    DriverStandingsDf = pd.DataFrame(columns=[])

    for i, _ in enumerate(currentDriverStandingsContent.iterrows()):
        driverCurrent = currentDriverStandingsContent.loc[i]
        currentStanding = driverCurrent["position"]
        previousStanding = 0
        driverPic = ""

        for e, _ in enumerate(previousDriverStandingsContent.iterrows()):
           driverPrev = previousDriverStandingsContent.loc[e]
           if driverCurrent["driverId"] == driverPrev["driverId"]:
              previousStanding = driverPrev["position"]

        # Check standings difference between current and previous round
        standingDiffLabel = ""

        standingDiff = (currentStanding - previousStanding) * -1
        if standingDiff > 0:
           standingDiffLabel = f"🔼 {standingDiff}"
        elif standingDiff < 0:
           standingDiffLabel = f"🔽 {standingDiff}"
        else:
           standingDiffLabel = "-"

        # Get Driver Headshots
        for driver_abbr, image_url in driverHeadshotDict.items():
          if driver_abbr == driverCurrent["driverCode"]:
            driverPic = image_url
            break
          
        if driverPic == "": # Placeholder Driver Image
          driverPic = "https://media.formula1.com/d_driver_fallback_image.png/content/dam/fom-website/drivers/"
            
        # Create a dictionary to store the row data
        row_data = {
          "Position": driverCurrent["positionText"],  # Use column names if different
          "Driver": driverPic,
          "Name": driverCurrent["givenName"] + ' ' + driverCurrent["familyName"],  # Combine names
          "Constructor": driverCurrent["constructorNames"],
          "Current Points": driverCurrent["points"],
          "Wins": driverCurrent["wins"],
          "+/-": standingDiffLabel
        }

        # Append the row data as a Series to the DataFrame
        DriverStandingsDf = pd.concat([DriverStandingsDf, pd.DataFrame([row_data])], ignore_index=True)

    st.data_editor(
      DriverStandingsDf,
      column_config={
         "Pos +/-": st.column_config.TextColumn(
            help="Standing difference from the previous round"
         ),
         "Driver": st.column_config.ImageColumn(
            "Driver"
        )
      },
      height=737,
      use_container_width=True,
      disabled=True,
      hide_index=True,
    )

def displayConstructorCurrentStandings():
  with st.spinner('Fetching data...'):
    ergast = Ergast()
    currentConstructorStandings = ergast.get_constructor_standings(season='current', round='last')
    
    # Get previous round standings
    lastRound = currentConstructorStandings.description["round"].item() - 1
    previousConstructorStandings = ""

    currentConstructorStandings = currentConstructorStandings.content[0]
    ConstructorsStandingsDf = pd.DataFrame(columns=[])

    constructorLogoDict = queryConstructorLogo()
    
    if lastRound != 1: # Check if not first round
      previousConstructorStandings = ergast.get_constructor_standings(season='current', round=str(lastRound))
      previousConstructorStandingsContent = previousConstructorStandings.content[0]

    for i, _ in enumerate(currentConstructorStandings.iterrows()):
      constructorCurrent = currentConstructorStandings.loc[i]
      currentStanding = constructorCurrent["position"]
      constructorPic = ""

      for e, _ in enumerate(previousConstructorStandingsContent.iterrows()):
        constructorPrev = previousConstructorStandingsContent.loc[e]
        if constructorCurrent["constructorId"] == constructorPrev["constructorId"]:
          previousStanding = constructorPrev["position"]

      # Check standings difference between current and previous round
      standingDiffLabel = ""

      standingDiff = (currentStanding - previousStanding) * -1
      if standingDiff > 0:
          standingDiffLabel = f"🔼 {standingDiff}"
      elif standingDiff < 0:
          standingDiffLabel = f"🔽 {standingDiff}"
      else:
          standingDiffLabel = "-"

      # Get Constructor Logos
      for constructor_id, constructor_logo_url in constructorLogoDict.items():
        if constructor_id == constructorCurrent["constructorId"]:
          constructorPic = constructor_logo_url
          break
        
      if constructorPic == "": # Placeholder Driver Image
        constructorPic = "https://media.formula1.com/d_driver_fallback_image.png/content/dam/fom-website/drivers/"
      
      # Create a dictionary to store the row data
      row_data = {
        "Position": constructorCurrent["positionText"],  # Use column names if different
        "Constructor": constructorPic,
        "Name": constructorCurrent["constructorName"],
        "Current Points": constructorCurrent["points"],
        "Wins": constructorCurrent["wins"],
        "+/-": standingDiffLabel
      }

      # Append the row data as a Series to the DataFrame
      ConstructorsStandingsDf = pd.concat([ConstructorsStandingsDf, pd.DataFrame([row_data])], ignore_index=True)

    st.data_editor(
      ConstructorsStandingsDf,
      column_config={
          "Pos +/-": st.column_config.TextColumn(
            help="Standing difference from the previous round"
         ),
         "Constructor": st.column_config.ImageColumn(
            "Constructor", width="small"
        )
      },
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

    driverHeadshotDict = queryDriverHeadshot() # Get Driver Headshots

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

        # Get Driver Headshots
        for driver_abbr, image_url in driverHeadshotDict.items():
          if driver_abbr == driver["driverCode"]:
            driverPic = image_url
            break
          
        if driverPic == "": # Placeholder Driver Image
          driverPic = "https://media.formula1.com/d_driver_fallback_image.png/content/dam/fom-website/drivers/"

        # Create a dictionary to store the row data
        row_data = {
          "Position": driver["positionText"],  # Use column names if different
          "Driver": driverPic,
          "Name": driver["givenName"] + ' ' + driver["familyName"],  # Combine names
          "Constructor": driver["constructorNames"],
          "Current Points": driver["points"],
          "Theoretical Max Points": driver_max_points,
          "Can Win": can_win
        }

        # Append the row data as a Series to the DataFrame
        WDCPredictDf = pd.concat([WDCPredictDf, pd.DataFrame([row_data])], ignore_index=True)

    st.data_editor(
      WDCPredictDf,
      column_config={
         "Driver": st.column_config.ImageColumn(
            "Driver", width="small"
        )
      },
      height=737,
      use_container_width=True,
      disabled=True,
      hide_index=True,
    )

def run():
  st.write("# Welcome to Formula Dash! 🏎️")
  currentSeasonScheduleDict = getCurrentSeasonSchedule()

  st.header(f"{datetime.datetime.now().year} Season Standings")
  with st.expander("Current Season Standings",expanded=True):
    tab1, tab2, tab3 = st.tabs(["Drivers", "Constructors", "Championship Prediction"])
    with tab1:
      displayDriverCurrentStandings()
    with tab2:
      displayConstructorCurrentStandings()
    with tab3:
      displayWDCPrediction()

  st.divider()

  st.header(f"{datetime.datetime.now().year} Season Schedule")
  calendarTab, scheduleTab = st.tabs(["Calendar View", "Schedule View"])
  with calendarTab:
    displayCurrentSeasonCalendar(currentSeasonScheduleDict)
  with scheduleTab:
    displayCurrentSeasonSchedule(currentSeasonScheduleDict)

  st.divider()

  #Sidebar for Anchor links
  st.sidebar.markdown(f'''
  # Jump to
  - [Season Standings](#{datetime.datetime.now().year}-season-standings)
  - [Season Schedule](#{datetime.datetime.now().year}-season-schedule)
  ''', unsafe_allow_html=True)
    

st.set_page_config(
  page_title="Formula Dash",
  page_icon="🏎️"
)

if __name__ == "__main__":
  run()
