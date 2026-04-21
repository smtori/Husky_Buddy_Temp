"""Users dashboard page for Johanna Park"""

import logging
from typing import Any, List, Optional

import matplotlib.pyplot as plt  
import pandas as pd
import requests  
import streamlit as st  
from requests.exceptions import RequestException 
from modules.nav import SideBarLinks 

logger = logging.getLogger(__name__)

st.set_page_config(page_title="Users Dashboard", layout="wide")

SideBarLinks()

API_BASES = ["http://api:4000", "http://localhost:4000"]


def fetch_json(path: str) -> List[Any]:
    """Fetch JSON from the first reachable API base for the given path."""
    last_error: Optional[RequestException] = None
    for base in API_BASES:
        try:
            response = requests.get(f"{base}{path}", timeout=5)
            response.raise_for_status()
            return list(response.json())
        except RequestException as exc:
            last_error = exc
    if last_error is not None:
        raise last_error
    return []


def render_demographics_chart(users: pd.DataFrame) -> None:
    """Render the year-of-study demographics pie chart."""
    if not users.empty:
        year_counts = users["year"].value_counts()
        demo = pd.DataFrame({
            "year": year_counts.index,
            "Users": year_counts.values,
        })
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
    else:
        st.info("No demographic data.")


def main() -> None:
    """Render the Users dashboard page."""
    st.header("Users Dashboard")
    st.caption("Persona 4: Johanna Park")

    if st.button("<- Back to Home", type="secondary"):
        st.switch_page("Home.py")

    st.markdown("---")

    errors: List[str] = []

    try:
        users_raw = fetch_json("/users")
    except RequestException as exc:
        users_raw = []
        errors.append(f"Users unavailable: {exc}")

    for err in errors:
        st.warning(err)

    users_df = pd.DataFrame(users_raw)

    if not users_df.empty:
        raw_year = users_df.get("year", pd.Series(dtype=str))
        users_df["year"] = raw_year.fillna("Unknown")

    total_users = len(users_df)

    # Top-level metric
    metric_col, _ = st.columns([1, 2])
    with metric_col:
        st.metric("Total Users", f"{total_users:,}", delta="5%")

    st.write("")

    # Demographics chart
    with st.container(border=True):
        st.markdown("**Demographics — Year of Study**")
        render_demographics_chart(users_df)


main()