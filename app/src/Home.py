##################################################
# This is the main/entry-point file for the
# sample application for your project
##################################################

# Set up basic logging infrastructure
import logging
logging.basicConfig(format='%(filename)s:%(lineno)s:%(levelname)s -- %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# import the main streamlit library as well
# as SideBarLinks function from src/modules folder
import streamlit as st
from modules.nav import SideBarLinks

# streamlit supports regular and wide layout (how the controls
# are organized/displayed on the screen).
st.set_page_config(layout='wide')

# If a user is at this page, we assume they are not
# authenticated.  So we change the 'authenticated' value
# in the streamlit session_state to false.
st.session_state['authenticated'] = False

# Use the SideBarLinks function from src/modules/nav.py to control
# the links displayed on the left-side panel.
# IMPORTANT: ensure src/.streamlit/config.toml sets
# showSidebarNavigation = false in the [client] section
SideBarLinks(show_home=True)

# ***************************************************
#    The major content of this page
# ***************************************************

logger.info("Loading the Home page of the app")
st.title('HuskyBuddy')
st.write('#### Welcome! Which HuskyBuddy user would you like to act as?')

# For each of the user personas for which we are implementing
# functionality, we put a button on the screen that the user
# can click to MIMIC logging in as that mock user.
with st.container(border=True):
    col1, col2 = st.columns([1,3])
    with col1:
        st.image("https://freesvg.org/img/man.png", use_container_width=True)
        # or use a URL: st.image("https://...")
    with col2:
        st.markdown("### Adam Johnson")
        st.markdown("**System Admin**")
        st.markdown(
            "Oversees the HuskyBuddy platform, reviews user reports, "
            "manages accounts, and ensures community guidelines are upheld."
        )

    if st.button("Act as Adam Johnson, System Admin",
                 type='primary',
                 use_container_width=True,
                 key="login_adam"):
        st.session_state['authenticated'] = True
        st.session_state['role'] = 'Admin'
        st.session_state['first_name'] = 'Adam'
        logger.info("Logging in as Adam Johnson")
        st.switch_page('pages/00_Admin_Home.py')

if st.button('Act as Brandon Heller, Student User',
             type='primary',
             use_container_width=True):
    st.session_state['authenticated'] = True
    st.session_state['role'] = 'student'
    st.session_state['first_name'] = 'Brandon'
    st.switch_page('pages/10_Brandon_Home.py')

if st.button("Act as Natalie Frost, Student User",
             type='primary',
             use_container_width=True):
    st.session_state['authenticated'] = True
    st.session_state['role'] = 'student'
    st.session_state['first_name'] = 'Natalie'
    st.switch_page('pages/20_Natalie_Home.py')


if st.button("Act as Johanna Park, Data Analyst",
             type='primary',
             use_container_width=True):
    st.session_state['authenticated'] = True
    st.session_state['role'] = 'data_analyst'
    st.session_state['first_name'] = 'Johanna'
    st.switch_page('pages/40_Johanna_Home.py')
