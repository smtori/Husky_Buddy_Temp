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


def persona_card(image_url, name, role, description,
                 button_label, button_key,
                 session_role, first_name, target_page):
    """Render a persona card with image, description, and login button."""
    with st.container(border=True):
        col1, col2 = st.columns([1, 3])
        with col1:
            st.image(image_url, use_container_width=True)
        with col2:
            st.markdown(f"### {name}")
            st.markdown(f"**{role}**")
            st.markdown(description)

        if st.button(button_label,
                     type='primary',
                     use_container_width=True,
                     key=button_key):
            st.session_state['authenticated'] = True
            st.session_state['role'] = session_role
            st.session_state['first_name'] = first_name
            logger.info(f"Logging in as {name}")
            st.switch_page(target_page)


# ── 2x2 Grid of persona cards ──────────────────────────────────────────────
row1_col1, row1_col2 = st.columns(2)

with row1_col1:
    persona_card(
        image_url="https://freesvg.org/img/man.png",
        name="Adam Johnson",
        role="System Admin",
        description=(
            "Oversees the HuskyBuddy platform, reviews user reports, "
            "manages accounts, and ensures community guidelines are upheld."
        ),
        button_label="Act as Adam Johnson, System Admin",
        button_key="login_adam",
        session_role="Admin",
        first_name="Adam",
        target_page="pages/00_Admin_Home.py",
    )

with row1_col2:
    persona_card(
        image_url="https://freesvg.org/img/man.png",
        name="Brandon Heller",
        role="Student User",
        description=(
            "A Northeastern student using HuskyBuddy to find study partners, "
            "discover campus spots, and connect with peers who share his interests."
        ),
        button_label="Act as Brandon Heller, Student User",
        button_key="login_brandon",
        session_role="student",
        first_name="Brandon",
        target_page="pages/10_Brandon_Home.py",
    )

row2_col1, row2_col2 = st.columns(2)

with row2_col1:
    persona_card(
        image_url="https://freesvg.org/img/1526098537.png",
        name="Natalie Frost",
        role="Student User",
        description=(
            "A Northeastern student exploring HuskyBuddy to meet classmates, "
            "plan meetups, and build a community around her academic interests."
        ),
        button_label="Act as Natalie Frost, Student User",
        button_key="login_natalie",
        session_role="student",
        first_name="Natalie",
        target_page="pages/20_Natalie_Home.py",
    )

with row2_col2:
    persona_card(
        image_url="https://freesvg.org/img/1526098537.png",
        name="Johanna Park",
        role="Data Analyst",
        description=(
            "Analyzes platform usage data, tracks engagement trends, and "
            "provides insights to help improve the HuskyBuddy experience."
        ),
        button_label="Act as Johanna Park, Data Analyst",
        button_key="login_johanna",
        session_role="data_analyst",
        first_name="Johanna",
        target_page="pages/40_Johanna_Home.py",
    )