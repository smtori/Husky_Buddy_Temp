"""Analytical dashboard for Persona 4: Johanna Park."""

import logging
from typing import Any, List, Optional

import matplotlib.pyplot as plt  # type: ignore[import-not-found]
import pandas as pd
import requests  # type: ignore[import-untyped]
import streamlit as st  # type: ignore[import-not-found]
from requests.exceptions import RequestException  # type: ignore[import-untyped]
from modules.nav import SideBarLinks  # type: ignore[import-not-found]

logger = logging.getLogger(__name__)

st.set_page_config(page_title="Analytical Dashboard", layout="wide")

SideBarLinks()

API_BASES = ["http://api:4000", "http://localhost:4000"]

if st.button("👥  Users Dashboard", type="primary", use_container_width=True):
    st.switch_page("pages/41_Users_Dashboard.py")

if st.button("🤝  Matches Dashboard", type="primary", use_container_width=True):
    st.switch_page("pages/42_Matches_Dashboard.py")

if st.button("⭐  Feedback & Reports Dashboard", type="primary", use_container_width=True):
    st.switch_page("pages/43_Feedback_Reports_Dashboard.py")