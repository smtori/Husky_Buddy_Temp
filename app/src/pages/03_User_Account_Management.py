import logging
logger = logging.getLogger(__name__)

import streamlit as st
import requests
from modules.nav import SideBarLinks

st.set_page_config(page_title="User Account Management", layout="wide")

SideBarLinks()

st.header("User Account Management")
st.write(f"### Hi, {st.session_state['first_name']}.")

st.markdown("""
<style>
.block-container {
    padding-top: 2rem;
    padding-left: 2rem;
    padding-right: 2rem;
}

.user-card-box {
        border: 2px solid #222;
        border-radius: 18px;
        padding: 24px;
    background-color: #f7f7f7;
}

.user-name {
    font-size: 1.25rem;
    font-weight: 700;
    margin-bottom: 0.35rem;
}

.user-email {
    color: #555;
    font-size: 1rem;
    margin-bottom: 0.35rem;
}

.user-meta {
    color: #777;
    font-size: 0.95rem;
    margin-bottom: 0.25rem;
}

.status-badge {
    border: 1.5px solid #222;
    border-radius: 999px;
    padding: 8px 16px;
    font-weight: 600;
    font-size: 1rem;
    background: white;
    display: inline-block;
}

.status-verified {
    border-color: #222;
    color: #222;
}

.status-pending {
    border-color: #888;
    color: #888;
}

.status-flagged {
    border-color: #d97706;
    color: #d97706;
}

.status-suspended {
    border-color: #dc2626;
    color: #dc2626;
}


div.stButton > button {
    border-radius: 14px;
    height: 46px;
    font-weight: 600;
    border: 1.5px solid #222;
    background: white;

}

div.stButton > button:hover {
    background: #f0f0f0;
}

div[data-testid="stVerticalBlock"] div[data-testid="stVerticalBlockBorderWrapper"] {
    border-radius: 18px;
    padding: 8px;
}

</style>
""", unsafe_allow_html=True)

API_URL = "http://api:4000/users"

try:
    response = requests.get(API_URL, timeout=5)
    response.raise_for_status()
    users = response.json()
except Exception as e:
    st.error(f"Could not load users: {e}")
    users = []

st.caption(f"Loaded {len(users)} users")

search = st.text_input(
    "Search",
    label_visibility="collapsed",
    placeholder="Search by name or email..."
)

if search:
    q = search.lower().strip()
    users = [
        u for u in users
        if q in u["name"].lower() or q in u["email"].lower()
    ]

if "user_filter" not in st.session_state:
    st.session_state["user_filter"] = "All"

c1, c2, c3, c4 = st.columns(4)

with c1:
    if st.button("All", key="filter_all", use_container_width=True):
        st.session_state["user_filter"] = "All"
with c2:
    if st.button("Flagged", key="filter_flagged", use_container_width=True):
        st.session_state["user_filter"] = "Flagged"
with c3:
    if st.button("Pending", key="filter_pending", use_container_width=True):
        st.session_state["user_filter"] = "Pending"
with c4:
    if st.button("Suspended", key="filter_suspended", use_container_width=True):
        st.session_state["user_filter"] = "Suspended"

selected_filter = st.session_state["user_filter"]

if selected_filter != "All":
    users = [u for u in users if u["status"].lower() == selected_filter.lower()]

STATUS_ICONS = {
    "verified": "✅",
    "pending": "🕐",
    "flagged": "🚩",
    "suspended": "🚫"
}

for user in users:
    uid = user["student_id"]
    status = user["status"].lower()
    icon = STATUS_ICONS.get(status, "")

    badge_color = {
        "verified": "#222",
        "pending": "#888",
        "flagged": "#d97706",
        "suspended": "#dc2626"
    }.get(status, "#222")

    with st.container(border=True):
        top_left, top_right = st.columns([5, 2])

        with top_left:
            st.markdown(f"### {user['name']}")
            st.markdown(user["email"])
            st.markdown(user["year"])
            st.markdown(f"**Student ID:** {uid}")

        with top_right:
            st.markdown(
                f"""
                <div style="display:flex; justify-content:flex-end; margin-top: 8px;">
                    <div style="
                        border: 2px solid {badge_color};
                        color: {badge_color};
                        border-radius: 999px;
                        padding: 8px 18px;
                        font-weight: 600;
                        background: white;
                        display: inline-block;
                    ">
                        {icon} {user['status'].title()}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

        st.write("")

        b1, b2, b3, b4 = st.columns(4)

        with b1:
            if st.button("🚩 Flag", key=f"flag_{uid}", use_container_width=True):
                requests.put(f"http://api:4000/users/{uid}", json={**user, "status": "flagged"})
                st.rerun()

        with b2:
            if st.button("🚫 Suspend", key=f"suspend_{uid}", use_container_width=True):
                requests.put(f"http://api:4000/users/{uid}", json={**user, "status": "suspended"})
                st.rerun()

        with b3:
            if st.button("✅ Verify", key=f"verify_{uid}", use_container_width=True):
                requests.put(f"http://api:4000/users/{uid}", json={**user, "status": "verified"})
                st.rerun()

        with b4:
            if st.button("🗑 Remove", key=f"delete_{uid}", use_container_width=True):
                requests.delete(f"http://api:4000/users/{uid}")
                st.rerun()

    st.write("")