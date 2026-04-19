import logging

logger = logging.getLogger(__name__)

import streamlit as st
from modules.nav import SideBarLinks
import requests

# Add sidebar links
SideBarLinks()

st.set_page_config(layout="wide")


st.title("Submit a report.")
st.markdown("Submit a report to help keep HuskyBuddy a safe place.")

# ── Session state ──────────────────────────────────────────────────────────────
if "show_success_modal" not in st.session_state:
    st.session_state.show_success_modal = False
if "form_key_counter" not in st.session_state:
    st.session_state.form_key_counter = 0

# ── Success dialog ─────────────────────────────────────────────────────────────
@st.dialog("Thank you for submitting your report.")
def show_success_dialog():
    st.markdown("### Your report has been successfully submitted.")
    st.markdown("An administrator will review your report soon.")
    if st.button("Back to Home", use_container_width=True, key="dialog_home"):
        st.session_state.show_success_modal = False
        st.switch_page("Home.py")

# ── API base ───────────────────────────────────────────────────────────────────
BASE_URL = "http://web-api:4000"

# ── Form ───────────────────────────────────────────────────────────────────────
if not st.session_state.show_success_modal:
    with st.form(f"submit_report_form_{st.session_state.form_key_counter}"):

        # ── Basic info ────────────────────────────────────
        st.subheader("Your Information")
        first_name = st.text_input("First Name *")
        last_name  = st.text_input("Last Name *")

        email = st.text_input("Northeastern Email *", placeholder="abc@northeastern.edu")

        # ── Report Information ────────────────────────────────
        st.subheader("Report Information")
        reported_name = st.text_input("Reported User's Name *", placeholder="Who are you reporting?")
        report_reason = st.text_input("Report Information *", placeholder="Provide incident details?")
        incident_date = st.date_input("Date of Incident", value=None)

        submitted = st.form_submit_button("Submit Report", use_container_width=True)

    if submitted:
                missing = []
                if not first_name:
                    missing.append("First Name")
                if not last_name:
                    missing.append("Last Name")
                if not email:
                    missing.append("Northeastern Email")
                if not reported_name:
                    missing.append("Reported User's Name")
                if not report_reason:
                    missing.append("Report Information")
                if not incident_date:
                    missing.append("Date of Incident")

                if missing:
                    st.error(f"Please fill in: {', '.join(missing)}")
                elif not email.lower().endswith("@northeastern.edu"):
                    st.error("Email must be a valid @northeastern.edu address.")
                else:
                    report_data = {
                        "first_name": first_name,
                        "last_name": last_name,
                        "email": email,
                        "reported_name": reported_name,
                        "report_reason": report_reason,
                        "incident_date": incident_date.isoformat() if incident_date else None,
                    }

                    try:
                        response = requests.post(f"{BASE_URL}/reports", json=report_data)

                        if response.status_code in (200, 201):
                            st.session_state.show_success_modal = True
                            st.rerun()
                        else:
                            st.error(
                                f"Failed to submit report: "
                                f"{response.json().get('error', 'Unknown error')}"
                            )

                    except requests.exceptions.RequestException as e:
                        st.error(f"Error connecting to the API: {str(e)}")
                        st.info("Please ensure the API server is running.")

    if st.button("Cancel", key="page_cancel"):
        st.switch_page("Home.py")

if st.session_state.show_success_modal:
    show_success_dialog()