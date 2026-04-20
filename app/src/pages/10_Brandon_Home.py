import logging
logger = logging.getLogger(__name__)

import streamlit as st
from modules.nav import SideBarLinks

st.set_page_config(layout='wide')

# Show appropriate sidebar links for the role of the currently logged in user
SideBarLinks()

st.title(f"Welcome, {st.session_state['first_name']}.")
st.write('### What would you like to do today?')

with st.container(border=True):
    header_left, header_right = st.columns([1, 3], gap="medium")
 
    with header_left:
        # Profile picture — placeholder via DiceBear.
        # Replace the URL with an uploaded/local image path when ready.
        st.image(
            "brandon.svg",
            width=200,
        )
 
    with header_right:
        st.title(f"{first_name} {last_name}")
        st.caption(f"@{first_name.lower()}{last_name.lower()} · Northeastern University 🐾")

# --------------------
with st.container(border=True):
    s1, s2, s3, s4 = st.columns(4)
    s1.metric("Matches", 12, "+2 this week")
    s2.metric("Chats", 47, "+5 today")
    s3.metric("Meetups", 8, "+1 this week")
    s4.metric("Rating", "4.9", "⭐")
 
st.write("")  # spacer
 # --------------------
if st.button("✏️  Edit Profile", type="primary", use_container_width=True):
            st.switch_page("pages/15_Edit_Profile.py")
 
if st.button("💬  HuskyBuddy Chats", type="primary", use_container_width=True):
            st.switch_page("pages/14_Brandon_Match_Chat.py")
 
if st.button("📝  Submit a Report", use_container_width=True):
        st.switch_page("pages/11_Submit_Report.py")
 
 
# if st.button('Edit Profile',
#              type='primary',
#              use_container_width=True):
#         st.switch_page('pages/15_Edit_Profile.py')

# if st.button('View HuskyBuddy Chat',
#              type='primary',
#              use_container_width=True):
#     st.switch_page('pages/14_Brandon_Match_Chat.py')

# if st.button('Submit a Report',
#              type='primary',
#              use_container_width=True):
#     st.switch_page('pages/11_Submit_Report.py')