import streamlit as st
import requests
from modules.nav import SideBarLinks

# Add sidebar links
SideBarLinks()

st.set_page_config(layout="wide")
st.title("HuskyBuddy Chat")

BASE_URL = "http://web-api:4000"

current_user_id = 1 # Brandon's  ID

# Get a random match
if "match_id" not in st.session_state:
    st.markdown("Ready to chat with one of your HuskyBuddy matches?")
    if st.button("Start a random chat!", use_container_width=True):
        try:
            resp = requests.get(f"{BASE_URL}/chat/random/{current_user_id}")
            if resp.status_code == 200:
                data = resp.json()
                st.session_state.match_id = data["match_id"]
                st.session_state.buddy_name = data["buddy_name"]
                st.rerun()
            elif resp.status_code == 404:
                st.error("You don't have any active matches yet!")
            else:
                st.error("Something went wrong.")
        except requests.exceptions.RequestException:
            st.error("Could not connect to the API.")
    st.stop()

# Chat interface
match_id = st.session_state.match_id
buddy_name = st.session_state.buddy_name

st.subheader(f"Chatting with {buddy_name}")

if st.button("New random chat"):
    del st.session_state["match_id"]
    del st.session_state["buddy_name"]
    st.rerun()

# Load messages
def load_messages():
    try:
        resp = requests.get(f"{BASE_URL}/chat/{match_id}")
        if resp.status_code == 200:
            return resp.json()
    except requests.exceptions.RequestException:
        st.error("Could not connect to the API.")
    return []

messages = load_messages()

for msg in messages:
    role = "user" if msg["sender_id"] == current_user_id else "assistant"
    with st.chat_message(role):
        st.markdown(f"**{msg['sender_name']}**: {msg['content']}")

# Send message
if prompt := st.chat_input("Type a message..."):
    try:
        resp = requests.post(f"{BASE_URL}/chat/{match_id}", json={
            "sender_id": current_user_id,
            "content": prompt
        })
        if resp.status_code == 201:
            st.rerun()
        elif resp.status_code == 403:
            st.error("You're not part of this match.")
        else:
            st.error("Failed to send message.")
    except requests.exceptions.RequestException:
        st.error("Could not connect to the API.")