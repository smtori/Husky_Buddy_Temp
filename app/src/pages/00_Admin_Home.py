import logging
logger = logging.getLogger(__name__)

import streamlit as st
from modules.nav import SideBarLinks

st.set_page_config(layout='wide')

# Show appropriate sidebar links for the role of the currently logged in user
SideBarLinks()

st.title(f"Welcome System Admin, {st.session_state['first_name']}.")
st.write('### What would you like to do today?')

if st.button('View User Account Management',
             type='primary',
             use_container_width=True):
    st.switch_page('pages/03_User_Account_Management.py')

if st.button('View Moderation Logs',
             type='primary',
             use_container_width=True):
    st.switch_page('pages/04_Moderation_Logs.py')
