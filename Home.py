import streamlit as st
import fastf1
from streamlit.logger import get_logger

LOGGER = get_logger(__name__)


def run():
    st.set_page_config(
        page_title="Formula Dash",
        page_icon="🏎️",
        layout="wide"
    )

    st.write("# Welcome to Formula Dash! 🏎️")

    st.markdown(
      """
        testing this out
      """
    )


if __name__ == "__main__":
    run()
