import logging
logger = logging.getLogger(__name__)

import streamlit as st
from modules.nav import SideBarLinks

st.set_page_config(layout='wide')

# Show appropriate sidebar links for the role of the currently logged in user
SideBarLinks()

st.title(f"Welcome, {st.session_state['first_name']}.")
st.write('### What would you like to do today?')

if st.button('Edit Profile',
             type='primary',
             use_container_width=True):
    st.switch_page('pages/15_Edit_Profile.py')

if st.button('View HuskyBuddy Chat',
             type='primary',
             use_container_width=True):
    st.switch_page('pages/14_Brandon_Match_Chat.py')

if st.button('Submit a Report',
             type='primary',
             use_container_width=True):
    st.switch_page('pages/11_Submit_Report.py')