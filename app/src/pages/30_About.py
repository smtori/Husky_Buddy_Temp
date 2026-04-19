import streamlit as st
from modules.nav import SideBarLinks

st.set_page_config(layout='wide')

SideBarLinks()

st.write("# About this App")

st.markdown(
    """
    HuskyBuddy is a data-driven matchmaking platform built exclusively for Northeastern University students. 
    By pairing Huskies based on shared interests, majors, career goals, and more, 
    HuskyBuddy makes it easy to meet new people, have meaningful conversations, and grow your network.
    """
)

# Add a button to return to home page
if st.button("Return to Home", type="primary"):
    st.switch_page("Home.py")
