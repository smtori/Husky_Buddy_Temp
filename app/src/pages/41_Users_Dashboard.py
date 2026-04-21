"""Users dashboard page for Johanna Park"""

import logging
from typing import Any, List, Optional

import matplotlib.pyplot as plt  
import pandas as pd
import requests  
import streamlit as st  
from requests.exceptions import RequestException 
from modules.nav import SideBarLinks 
from typing import Any, List, Optional, Union

logger = logging.getLogger(__name__)

st.set_page_config(page_title="Users Dashboard", layout="wide")

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
 
 
def render_demographics_chart(by_year: List[dict]) -> None:
    """Render the year-of-study demographics pie chart."""
    if not by_year:
        st.info("No demographic data.")
        return
 
    demo = pd.DataFrame(by_year)
    demo = demo.rename(columns={"user_count": "Users"})
    colors = [
        "#4b8cf5", "#4CAF50", "#f0a500",
        "#e74c3c", "#9b59b6", "#1abc9c",
    ]
    fig, ax = plt.subplots(figsize=(5.0, 4.0))
    fig.patch.set_facecolor("none")
    ax.set_facecolor("none")
    ax.pie(
        demo["Users"],
        labels=demo["year"],
        autopct="%1.0f%%",
        colors=colors[: len(demo)],
        textprops={"color": "#cccccc", "fontsize": 10},
    )
    st.pyplot(fig, use_container_width=True)
 
 
def render_majors_table(
    by_major: List[dict],
    total_students: int,
    top_n: int = 10,
) -> None:
    if not by_major:
        st.info("No majors data available.")
        return
 
    df = pd.DataFrame(by_major)
    df = df.rename(columns={"user_count": "Students", "major_name": "Major"})
    df = df.sort_values("Students", ascending=False)
 
    if total_students > 0:
        df["% of Students"] = (
            df["Students"] / total_students * 100
        ).round(1).astype(str) + "%"
    else:
        df["% of Students"] = "—"
 
    display_cols = ["Major", "Students", "% of Students"]
 
    top_df = df.head(top_n)[display_cols].reset_index(drop=True)
    top_df.index = top_df.index + 1
    st.dataframe(top_df, use_container_width=True)
 
    if len(df) > top_n:
        with st.expander(f"Show all {len(df)} majors"):
            full_df = df[display_cols].reset_index(drop=True)
            full_df.index = full_df.index + 1
            st.dataframe(full_df, use_container_width=True)
 
 
def main() -> None:
    """Render the Users dashboard page."""
    st.header("Users Dashboard")
    st.caption("Persona 4: Johanna Park")
 
    if st.button("<- Back to Home", type="secondary"):
        st.switch_page("Home.py")
 
    st.markdown("---")
 
    errors: List[str] = []
 
    try:
        overview = fetch_json("/dashboard/analytics")
        if not isinstance(overview, dict):
            overview = {}
    except RequestException as exc:
        overview = {}
        errors.append(f"Overview unavailable: {exc}")
 
    try:
        demographics = fetch_json("/dashboard/analytics/demographics")
        if not isinstance(demographics, dict):
            demographics = {}
    except RequestException as exc:
        demographics = {}
        errors.append(f"Demographics unavailable: {exc}")
 
    for err in errors:
        st.warning(err)
 
    total_users = int(overview.get("total_users") or 0)
    verified_users = int(overview.get("verified_users") or 0)
    by_year = list(demographics.get("by_year") or [])
    by_major = list(demographics.get("by_major") or [])
 
    # Top-level metrics
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Users", f"{total_users:,}")
    with col2:
        st.metric("Verified Users", f"{verified_users:,}")
 
    st.write("")
 
    # Demographics chart + majors table side by side
    demo_col, majors_col = st.columns([1, 1], gap="large")
 
    with demo_col:
        with st.container(border=True):
            st.markdown("**Demographics — Year of Study**")
            render_demographics_chart(by_year)
 
    with majors_col:
        with st.container(border=True):
            st.markdown("**Majors Distribution** (Top 10)")
            st.caption(
                "Students may declare multiple majors, so percentages "
                "can sum to more than 100%."
            )
            render_majors_table(by_major, total_users)
 
 
main()
 