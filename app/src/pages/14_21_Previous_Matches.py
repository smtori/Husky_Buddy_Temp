import streamlit as st
import requests
from modules.nav import SideBarLinks
from typing import Any

st.set_page_config(layout="wide")

# Add sidebar links
SideBarLinks()

st.title("Previous Matches")

current_user_id = st.session_state.get('user_id', 1)
first_name = str(st.session_state.get('first_name', '')).strip().lower()

# Determine return page based on user
if first_name == 'natalie':
    return_page = 'pages/20_Natalie_Home.py'
elif first_name == 'brandon':
    return_page = 'pages/10_Brandon_Home.py'
elif current_user_id == 2:
    return_page = 'pages/20_Natalie_Home.py'
else:
    return_page = 'pages/10_Brandon_Home.py'

# Back button
if st.button("← Back to Home", type="secondary", use_container_width=False):
    st.switch_page(return_page)

BASE_URL = "http://web-api:4000"

# Load previous matches (removed, pending, completed)
@st.cache_data(ttl=30)  # type: ignore
def load_previous_matches(user_id: int) -> Any:
    try:
        resp = requests.get(f"{BASE_URL}/users/{user_id}/matches/previous", timeout=5)
        if resp.status_code == 200:
            return resp.json(), None
        if resp.status_code == 404:
            return [], None
        return None, f"API returned status {resp.status_code}."
    except requests.exceptions.RequestException as e:
        return None, f"Could not connect to the API: {e}"

matches_data, err = load_previous_matches(current_user_id)

if err:
    st.error(err)
    st.stop()

if not matches_data:
    st.info("No previous matches yet. Keep matching to see your history!")
    st.stop()

# Display matches in a table
st.subheader(f"Your Previous Matches ({len(matches_data)})")

# Create columns for display
col1, col2, col3, col4, col5, col6 = st.columns([2, 2, 2, 2, 2, 1])

with col1:
    st.markdown("**Buddy Name**")
with col2:
    st.markdown("**Status**")
with col3:
    st.markdown("**Matched On**")
with col4:
    st.markdown("**Last Activity**")
with col5:
    st.markdown("**Your Feedback**")
with col6:
    st.markdown("**Action**")

st.divider()

# Display each match
for match in matches_data:
    col1, col2, col3, col4, col5, col6 = st.columns([2, 2, 2, 2, 2, 1])
    
    with col1:
        st.markdown(f"{match.get('buddy_name', 'Unknown')}")
    
    with col2:
        status = match.get('status', 'unknown')
        status_color = {
            'completed': '✅ Completed',
            'removed': '❌ Removed',
            'pending': '⏳ Pending'
        }
        st.markdown(status_color.get(status, status.title()))
    
    with col3:
        st.markdown(match.get('matched_on', 'N/A'))
    
    with col4:
        last_activity = match.get('last_activity', 'N/A')
        st.markdown(last_activity if last_activity else 'No activity')
    
    with col5:
        rating = match.get('your_rating', 0)
        if rating > 0:
            stars = "⭐" * rating
            st.markdown(f"{stars} ({rating}/5)")
        else:
            st.markdown("No rating")
    
    with col6:
        if st.button("View", key=f"view_{match.get('match_id')}"):
            st.session_state.view_match_id = match.get('match_id')
            st.session_state.view_match_buddy = match.get('buddy_name')
            st.rerun()

st.divider()

# Show details if a match is selected for viewing
if "view_match_id" in st.session_state:
    st.subheader(f"Match Details with {st.session_state.view_match_buddy}")
    
    match_id = st.session_state.view_match_id
    
    @st.cache_data(ttl=30)  # type: ignore
    def load_match_details(mid: int) -> Any:
        try:
            resp = requests.get(f"{BASE_URL}/matches/{mid}", timeout=5)
            if resp.status_code == 200:
                return resp.json(), None
            return None, f"Could not load match details (Status {resp.status_code})"
        except requests.exceptions.RequestException as e:
            return None, f"Could not connect to the API: {e}"
    
    match_details, err = load_match_details(match_id)
    
    if err:
        st.error(err)
    elif match_details:
        # Display match information
        detail_col1, detail_col2, detail_col3 = st.columns(3)
        
        with detail_col1:
            st.markdown(f"**Status**: {match_details.get('status', 'Unknown').title()}")
            st.markdown(f"**Matched**: {match_details.get('matched_on', 'N/A')}")
        
        with detail_col2:
            st.markdown(f"**Your Rating**: {match_details.get('your_rating', 'Not rated')}")
            st.markdown(f"**Their Rating**: {match_details.get('their_rating', 'Not rated')}")
        
        with detail_col3:
            meetups_count = len(match_details.get('meetups', []))
            st.markdown(f"**Meetups**: {meetups_count}")
            st.markdown(f"**Your Comment**: {match_details.get('your_comment', 'No comment')}")
        
        # Show meetup history if available
        if match_details.get('meetups'):
            st.markdown("**Meetup History**")
            for meetup in match_details.get('meetups', []):
                met_date = meetup.get('meetup_date', 'N/A')
                location = meetup.get('spot_name', 'Unknown location')
                status = meetup.get('meetup_status', 'unknown')
                st.caption(f"📍 {location} · {met_date} · {status.title()}")
    
    if st.button("Close Details"):
        del st.session_state.view_match_id
        del st.session_state.view_match_buddy
        st.rerun()
