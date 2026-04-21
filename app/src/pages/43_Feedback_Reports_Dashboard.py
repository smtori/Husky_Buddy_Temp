"""Feedback and Reports dashboard page for Persona 4: Johanna Park."""

import logging
from typing import Any, List, Optional, Union

import pandas as pd
import requests  # type: ignore[import-untyped]
import streamlit as st  # type: ignore[import-not-found]
from requests.exceptions import RequestException  # type: ignore[import-untyped]
from modules.nav import SideBarLinks  # type: ignore[import-not-found]

logger = logging.getLogger(__name__)

st.set_page_config(page_title="Feedback & Reports Dashboard", layout="wide")

SideBarLinks()

API_BASES = ["http://api:4000", "http://localhost:4000"]


def fetch_json(path: str) -> Union[List[Any], dict]:
    """Fetch JSON from the first reachable API base for the given path."""
    last_error: Optional[RequestException] = None
    for base in API_BASES:
        try:
            response = requests.get(f"{base}{path}", timeout=5)
            response.raise_for_status()
            return response.json()
        except RequestException as exc:
            last_error = exc
    if last_error is not None:
        raise last_error
    return []


def render_satisfaction_stats(stats: dict) -> None:
    """Render aggregate satisfaction statistics."""
    avg = stats.get("avg_satisfaction")
    total = stats.get("total_responses")
    lo = stats.get("lowest_rating")
    hi = stats.get("highest_rating")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Responses", f"{int(total or 0):,}")
    with col2:
        lo_label = f"{int(lo)} ⭐" if lo is not None else "—"
        st.metric("Lowest Rating", lo_label)
    with col3:
        hi_label = f"{int(hi)} ⭐" if hi is not None else "—"
        st.metric("Highest Rating", hi_label)

    st.write("")

    # Average rating as a visual bar
    if avg is not None:
        avg_float = float(avg)
        pct = avg_float / 5.0
        st.markdown(
            f"**Average Rating:** {avg_float:.2f} / 5.00"
        )
        st.progress(pct)
    else:
        st.info("No ratings submitted yet.")


def render_interests(by_interest: List[dict]) -> None:
    """Render the most common student interests."""
    if not by_interest:
        st.info("No interest data.")
        return

    for item in by_interest:
        name = str(item.get("tag_type", ""))
        cnt = int(item.get("user_count") or 0)
        name_col, count_col = st.columns([3, 1])
        with name_col:
            st.write(f"**{name}**")
        with count_col:
            st.caption(f"{cnt} students")
        st.divider()


def main() -> None:
    """Render the Feedback and Reports dashboard page."""
    st.header("Feedback & Reports Dashboard")
    st.caption("Persona 4: Johanna Park")

    if st.button("<- Back to Home", type="secondary"):
        st.switch_page("Home.py")

    st.markdown("---")

    errors: List[str] = []

    try:
        satisfaction = fetch_json("/dashboard/analytics/satisfaction")
        if not isinstance(satisfaction, dict):
            satisfaction = {}
    except RequestException as exc:
        satisfaction = {}
        errors.append(f"Satisfaction stats unavailable: {exc}")

    try:
        demographics = fetch_json("/dashboard/analytics/demographics")
        if not isinstance(demographics, dict):
            demographics = {}
    except RequestException as exc:
        demographics = {}
        errors.append(f"Interest data unavailable: {exc}")

    for err in errors:
        st.warning(err)

    by_interest = list(demographics.get("by_interest") or [])

    # Top satisfaction metric
    avg = satisfaction.get("avg_satisfaction")
    sat_label = f"{float(avg):.2f}/5.00" if avg is not None else "N/A"
    metric_col, _ = st.columns([1, 2])
    with metric_col:
        st.metric("Average Satisfaction", sat_label)

    st.write("")

    # Stats + interests side by side
    sat_col, interests_col = st.columns([1, 1], gap="large")

    with sat_col:
        with st.container(border=True):
            st.markdown("**User Satisfaction Overview**")
            render_satisfaction_stats(satisfaction)

    with interests_col:
        with st.container(border=True):
            st.markdown("**Common Interest Categories**")
            render_interests(by_interest)


main()