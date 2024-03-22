import streamlit as st

st.set_page_config(page_title="About - Formula Dash", page_icon="ℹ️")
st.markdown('''## What is Formula Dash?\n
Formula Dash is a dashboard designed to deliver on and off-track information related to Formula One.\n
It has features such as:
- View the current season calendar, driver and team standings, and World Drivers' Championship prediction on the **Home** page
- View specific session details using the **Session Viewer**
- View qualifying lap comparisons using the **Quali Lap Comparison**
- View driver & team information using the **Driver and Team Viewer**
''')
st.divider()
st.markdown('''## How was Formula Dash created?\n
Formula Dash was created using the **Streamlit** framework. It also uses the **Fastf1** python module along with **Ergast API**.\n
Most of the track-related visualizations were created through modifications of provided code in the FastF1 documentation.\n
Resources used for this project:
- [Streamlit](https://streamlit.io/)
- [Fastf1](https://docs.fastf1.dev/)
- [ErgastApi](https://ergast.com/mrd/)
''')
st.divider()
st.markdown('''## Frequently Asked Questions''')
with st.expander("Why is there missing data?"):
    st.markdown('''There could be multiple reasons for this. it's possible that there is unhandled missing data which makes it hard to plot out visualizations.\n
**The Ergast API will also be deprecated post-2024**, which may cause issues as almost 30 to 40% of this project relies on information provided by Ergast.\n
Unfortunately, I am not skilled enough to handle these errors. Sorry about that!''')
with st.expander("Why is fetching data so slow?"):
    st.markdown('''There is simply too much information handle. Such information includes lap timings, speeds, position changes, etc. This causes the calculation and plotting of the visualizations to be slower than expected.\n
On the bright side, data that has been parsed will be cached temporarily by Fastf1. This means loading times for information already has been loaded will be reduced.
''')
st.divider()
st.markdown('''## Notice\n
Formula Dash is unofficial and is not associated in any way with the Formula 1 companies. F1, FORMULA ONE, FORMULA 1, FIA FORMULA ONE WORLD CHAMPIONSHIP, GRAND PRIX and related marks are trade marks of Formula One Licensing B.V.
''')