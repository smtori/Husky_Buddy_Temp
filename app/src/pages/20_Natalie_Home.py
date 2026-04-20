import logging
logger = logging.getLogger(__name__)
 
import streamlit as st
import requests
from modules.nav import SideBarLinks
from typing import Any
 
st.set_page_config(layout='wide')

# Show appropriate sidebar links for the role of the currently logged in user
SideBarLinks()

st.title(f"Welcome, {st.session_state['first_name']}.")

BASE_URL = "http://web-api:4000"
 
# Natalie's student_id in 00_husky-buddy.sql
current_user_id = st.session_state.get('user_id', 2)
 
# Pull profile from api
@st.cache_data(ttl=30)  # small cache so we don't hammer the API on every rerun
def load_profile(user_id: int) -> Any:
    try:
        resp = requests.get(f"{BASE_URL}/users/{user_id}/profile", timeout=5)
        if resp.status_code == 200:
            return resp.json(), None
        if resp.status_code == 404:
            return None, "Profile not found."
        return None, f"API returned status {resp.status_code}."
    except requests.exceptions.RequestException as e:
        return None, f"Could not connect to the API: {e}"
 
profile, err = load_profile(current_user_id)
 
if err or profile is None:
    st.error(err or "Could not load profile.")
    st.stop()
 
first_name = profile["first_name"]
last_name  = profile["last_name"]
year       = profile["year"]
email      = profile["email"]
status     = profile.get("status") or ""
majors     = profile.get("majors", [])
interests  = profile.get("interests", [])
spots      = profile.get("campus_spots", [])
 
# Define variables
first_name = st.session_state.get('first_name', 'Natalie')
last_name  = st.session_state.get('last_name', 'Frost')

with st.container(border=True):
    header_left, header_right = st.columns([1, 3], gap="medium")
 
    with header_left: # Profile picture
        st.image(
            f"https://api.dicebear.com/9.x/avataaars/svg?backgroundColor=transparent&accessories[]&accessoriesColor[]&clothing=blazerAndShirt,blazerAndSweater,collarAndSweater,overall,shirtCrewNeck,shirtScoopNeck,shirtVNeck&clothingGraphic[]&eyebrows=default,defaultNatural,flatNatural&eyes=default&facialHair=beardLight,beardMedium,moustacheFancy,moustacheMagnum,beardMajestic&facialHairColor=2c1b18,4a312c,724133&hairColor=2c1b18,4a312c,724133,a55728,b58143,c93305&mouth=default,serious,smile,twinkle&seed=Jessica",
            width=200,
        )
 
    with header_right:
        # Name + verification badge
        badge = " ✅" if status == "verified" else ""
        st.title(f"{first_name} {last_name}{badge}")
        st.caption(f"@{first_name.lower()}{last_name.lower()} · Northeastern University 🐾 · {email}")
 
        # Quick-info row: year + first major
        info_a, info_b = st.columns([1, 3])
        info_a.markdown(f"📚 **{year} Year**")
        if majors:
            info_b.markdown(f"🎓 **{' · '.join(majors)}**")
        else:
            info_b.markdown("🎓 _No major listed_")
 
        # ── Major tags ──
        st.markdown("**Majors**")
        if majors:
            major_cols = st.columns(min(len(majors), 4))
            for col, m in zip(major_cols, majors):
                col.button(f"🎓 {m}", disabled=True, use_container_width=True, key=f"maj_{m}")
        else:
            st.caption("_No majors added yet. Edit your profile to add some!_")
 
        # ── Interest tags ──
        st.markdown("**Interests**")
        if interests:
            int_cols = st.columns(min(len(interests), 4))
            for col, i in zip(int_cols, interests):
                col.button(f" {i}", disabled=True, use_container_width=True, key=f"int_{i}")
        else:
            st.caption("_No interests added yet._")
 
        # ── Favorite campus spots ──
        st.markdown("**Favorite Campus Spots**")
        if spots:
            spot_cols = st.columns(min(len(spots), 4))
            for col, s in zip(spot_cols, spots):
                col.button(f"📍 {s['spot_name']}", disabled=True,
                    use_container_width=True, key=f"spot_{s['spot_name']}")
        else:
            st.caption("_No favorite spots added yet._")
 
 
# --------------------
with st.container(border=True):
    s1, s2, s3, s4 = st.columns(4)
    s1.metric("Network", 20, "+1 this week")
    s2.metric("Chats", 88, "+6 today")
    s3.metric("Meetups", 20, "+3 this week")
 
st.write("")  # spacer
 # --------------------
if st.button("✏️  Edit Profile", type="primary", use_container_width=True):
            st.switch_page("pages/14_24_Edit_Profile.py")
 
if st.button("💬  HuskyBuddy Chats", type="primary", use_container_width=True):
            st.switch_page("pages/13_23_Match_Chat.py")
 
if st.button("📝  Submit a Report", use_container_width=True):
        st.switch_page("pages/12_22_Submit_Report.py")
if st.button('📸  View Photo Gallery', type='primary',use_container_width=True):
    st.switch_page('pages/11_21_Photo_Gallery.py')
 