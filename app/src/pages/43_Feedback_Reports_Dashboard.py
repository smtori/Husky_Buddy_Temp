"""Feedback and Reports dashboard page for Persona 4: Johanna Park."""

import logging
from typing import Any, List, Optional

import matplotlib.pyplot as plt  # type: ignore[import-not-found]
import pandas as pd
import requests  # type: ignore[import-untyped]
import streamlit as st  # type: ignore[import-not-found]
from requests.exceptions import RequestException  # type: ignore[import-untyped]
from modules.nav import SideBarLinks  # type: ignore[import-not-found]

logger = logging.getLogger(__name__)

st.set_page_config(page_title="Feedback & Reports Dashboard", layout="wide")

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


def lower_status(df: pd.DataFrame) -> pd.DataFrame:
    """Normalise the 'status' column to lowercase strings."""
    if not df.empty:
        raw = df.get("status", pd.Series(dtype=str))
        df["status"] = raw.fillna("").astype(str).str.lower()
    else:
        df["status"] = pd.Series(dtype=str)
    return df


def render_satisfaction_chart(satisfaction: pd.DataFrame) -> None:
    """Render the 1-5 star satisfaction horizontal bar chart."""
    if not satisfaction.empty and "rating" in satisfaction.columns:
        counts = (
            satisfaction["rating"]
            .value_counts()
            .reindex([5, 4, 3, 2, 1], fill_value=0)
        )
        rating_counts = pd.DataFrame({
            "Rating": pd.Index([5, 4, 3, 2, 1]),
            "Count": counts.values,
        })
    else:
        rating_counts = pd.DataFrame({
            "Rating": pd.Index([5, 4, 3, 2, 1]),
            "Count": [0, 0, 0, 0, 0],
        })

    bar_colors = ["#4CAF50", "#8BC34A", "#f0a500", "#FF7043", "#e74c3c"]
    fig, ax = plt.subplots(figsize=(6.0, 3.0))
    fig.patch.set_facecolor("none")
    ax.set_facecolor("none")
    ax.barh(
        rating_counts["Rating"].astype(str),
        rating_counts["Count"],
        color=bar_colors,
        height=0.55,
    )
    ax.set_yticks(range(5))
    ax.set_yticklabels(["1", "2", "3", "4", "5"],
                       color="#cccccc", fontsize=9)
    ax.tick_params(axis="x", colors="#cccccc", labelsize=8)
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.grid(axis="x", color="#555", linewidth=0.4, linestyle="--")
    st.pyplot(fig, use_container_width=True)


def render_interests(reports: pd.DataFrame) -> None:
    """Render the common shared interests section."""
    interest_col = next(
        (
            col for col in
            ["interest", "shared_interest", "tag", "interest_name"]
            if not reports.empty and col in reports.columns
        ),
        None,
    )

    if interest_col:
        interest_counts = reports[interest_col].value_counts().head(6)
        rows = [
            (str(name), int(cnt))
            for name, cnt in zip(interest_counts.index, interest_counts.values)
        ]
    else:
        rows = [
            ("Career + Co-ops", 30),
            ("Sports + Fitness", 25),
            ("Technology", 15),
            ("Music", 10),
        ]

    for name, cnt in rows:
        name_col, count_col = st.columns([3, 1])
        with name_col:
            st.write(f"**{name}**")
        with count_col:
            st.caption(f"{cnt} matches")
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
        reports_raw = fetch_json("/reports")
    except RequestException as exc:
        reports_raw = []
        errors.append(f"Reports unavailable: {exc}")

    try:
        satisfaction_raw = fetch_json("/satisfaction")
    except RequestException:
        satisfaction_raw = []

    for err in errors:
        st.warning(err)

    reports_df = lower_status(pd.DataFrame(reports_raw))
    satisfaction_df = pd.DataFrame(satisfaction_raw)

    if not reports_df.empty:
        raw_reason = reports_df.get("reason", pd.Series(dtype=str))
        reports_df["reason"] = raw_reason.fillna("Unknown")

    avg_sat: Optional[float] = None
    if not satisfaction_df.empty and "rating" in satisfaction_df.columns:
        avg_sat = round(float(satisfaction_df["rating"].mean()), 1)

    # Top metric
    metric_col, _ = st.columns([1, 2])
    with metric_col:
        sat_label = f"{avg_sat}/5.0" if avg_sat is not None else "N/A"
        st.metric("Satisfaction Rating", sat_label, delta="0.4%")

    st.write("")

    # Charts
    sat_col, interests_col = st.columns([1, 1], gap="large")

    with sat_col:
        with st.container(border=True):
            st.markdown("**User Satisfaction Survey Results**")
            render_satisfaction_chart(satisfaction_df)

    with interests_col:
        with st.container(border=True):
            st.markdown("**Common Shared Interests**")
            render_interests(reports_df)


main()
