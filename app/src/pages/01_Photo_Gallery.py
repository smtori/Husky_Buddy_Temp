import logging
logger = logging.getLogger(__name__)
import streamlit as st
import requests
from modules.nav import SideBarLinks

st.set_page_config(layout='wide')

SideBarLinks()

BASE_URL = "http://web-api:4000"

current_user_id = st.session_state['user_id']

st.header(f"My HuskyBuddy Photo Gallery")
st.write(f"### Hi, {st.session_state['first_name']}.")

# ── Load Photos ─────────────────────────────────────────────
def load_photos():
    try:
        resp = requests.get(f"{BASE_URL}/users/{current_user_id}/photos")
        if resp.status_code == 200:
            return resp.json()
        else:
            st.error("Could not load photos.")
            return []
    except requests.exceptions.RequestException:
        st.error("Could not connect to the API.")
        return []

photos = load_photos()

if not photos:
    st.info("No meetup photos yet! Complete a HuskyBuddy chat and upload a photo to get started.")
else:
    st.write(f"### You have {len(photos)} meetup photo(s)!")
    cols = st.columns(3)
    for i, photo in enumerate(photos):
        with cols[i % 3]:
            st.image(
                f"assets/marino_meetup.webp",
                use_container_width=True
            )
            st.caption(f"📍 {photo['caption']}")
            st.write(f"Uploaded by **{photo['first_name']} {photo['last_name']}**")
            st.write(f"🗓️ {photo['uploaded_at'][:16]}")
            st.divider()

# ── Upload New Photo ────────────────────────────────────────
st.write("---")
st.subheader("Upload a New Photo")

with st.form("upload_photo_form"):
    match_id = st.number_input("Match ID", min_value=1, step=1)
    caption = st.text_area("Caption")
    submitted = st.form_submit_button("Upload Photo")

    if submitted:
        if not caption:
            st.error("Caption is required.")
        else:
            try:
                resp = requests.post(
                    f"{BASE_URL}/users/{current_user_id}/photos",
                    json={
                        "match_id": match_id,
                        "photo_url": "assets/tatte_meetup.jpg",
                        "caption": caption
                    }
                )
                if resp.status_code == 201:
                    st.success("Photo uploaded successfully!")
                    st.rerun()
                else:
                    st.error(f"Failed to upload: {resp.json().get('error')}")
            except requests.exceptions.RequestException:
                st.error("Could not connect to the API.")