import logging
logger = logging.getLogger(__name__)

import streamlit as st
from modules.nav import SideBarLinks

st.set_page_config(layout='wide')

SideBarLinks()

st.title('System Admin Home Page')
st.write('### What would you like to do today?')

if st.button('Edit Profile',
             type='primary',
             use_container_width=True):
    st.switch_page('pages/15_Edit_Profile.py')