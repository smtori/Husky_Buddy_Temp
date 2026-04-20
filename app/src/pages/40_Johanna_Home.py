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

def rate_label(pct: int) -> str:
    """Return a label for the given percentage value."""
    if pct >= 80:
        return "Excellent"
    elif pct >= 60:
        return "Good"
    elif pct >= 40:
        return "Fair"
    elif pct >= 20:
        return "Poor"
    else:
        return "Very Poor"


def lower_status(df: pd.DataFrame) -> pd.DataFrame:
    """Normalise the 'status' column to lowercase strings."""
    if not df.empty:
        raw = df.get("status", pd.Series(dtype=str))
        df["status"] = raw.fillna("").astype(str).str.lower()
    else:
        df["status"] = pd.Series(dtype=str)
    return df

def render_trend_chart(matches: pd.DataFrame) -> None:
    """Render the monthly sign-up trend line chart."""
    if not matches.empty and "matched_on" in matches.columns:
        month_order = [
            "Jan", "Feb", "Mar", "Apr", "May", "Jun",
            "Jul", "Aug", "Sep", "Oct", "Nov", "Dec",
        ]
        filtered = matches.dropna(subset=["matched_on"]).copy()
        filtered["Month"] = filtered["matched_on"].dt.strftime("%b")
        month_counts = filtered["Month"].value_counts()
        trend = pd.DataFrame({
            "Month": month_counts.index,
            "Count": month_counts.values,
        })
        trend["Month"] = pd.Categorical(
            trend["Month"], categories=month_order, ordered=True
        )
        trend = trend.sort_values("Month")

        fig, ax = plt.subplots(figsize=(3.5, 2.8))
        fig.patch.set_facecolor("none")
        ax.set_facecolor("none")
        xs = range(len(trend))
        ax.plot(xs, trend["Count"], marker="o", linewidth=2, color="#4b8cf5")
        ax.fill_between(xs, trend["Count"], alpha=0.15, color="#4b8cf5")
        ax.set_xticks(list(xs))
        ax.set_xticklabels(
            list(trend["Month"]), fontsize=7, rotation=45, color="#cccccc"
        )
        ax.tick_params(axis="y", colors="#cccccc", labelsize=7)
        for spine in ax.spines.values():
            spine.set_visible(False)
        ax.grid(axis="y", color="#555", linewidth=0.4, linestyle="--")
        st.pyplot(fig, use_container_width=True)
    else:
        st.info("No trend data.")


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
        fig, ax = plt.subplots(figsize=(3.5, 2.8))
        fig.patch.set_facecolor("none")
        ax.set_facecolor("none")
        ax.pie(
            demo["Users"],
            labels=demo["year"],
            autopct="%1.0f%%",
            colors=colors[: len(demo)],
            textprops={"color": "#cccccc", "fontsize": 8},
        )
        st.pyplot(fig, use_container_width=True)
    else:
        st.info("No demographic data.")


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
    fig, ax = plt.subplots(figsize=(5.5, 2.4))
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


def render_breakdown(matches: pd.DataFrame) -> None:
    """Render the major-pair success rate breakdown table."""
    if not matches.empty:
        pair_col = next(
            (
                col for col in
                ["major_pair", "major_combo", "pairing", "category"]
                if col in matches.columns
            ),
            None,
        )
        if pair_col:
            bd = (
                matches.groupby(pair_col)
                .agg(
                    total=("status", "count"),
                    done=("status", lambda x: (x == "completed").sum()),
                )
                .reset_index()
                .rename(columns={pair_col: "Category"})
            )
            bd["rate"] = (
                bd["done"] / bd["total"] * 100
            ).round(0).astype(int)
        else:
            status_counts = matches["status"].value_counts()
            bd = pd.DataFrame({
                "Category": status_counts.index.str.title(),
                "total": status_counts.values,
            })
            total_all = max(int(bd["total"].sum()), 1)
            bd["rate"] = (
                bd["total"] / total_all * 100
            ).round(0).astype(int)

        for _, row in bd.iterrows():
            pct = int(row["rate"])
            indicator = rate_label(pct)
            label_col, rate_col = st.columns([3, 1])
            with label_col:
                st.write(f"**{row['Category']}**")
                st.caption(f"{row['total']} total matches")
            with rate_col:
                st.metric(label="", value=f"{pct}%", label_visibility="collapsed")
                st.caption(indicator)
            st.progress(pct / 100)
            st.divider()
    else:
        static_rows = [
            ("CS + CS", 45, 78),
            ("Business + CS", 40, 74),
            ("Engineering + Engineering", 32, 70),
            ("DS + Business", 25, 77),
            ("Engineering + Business", 68, 61),
        ]
        for category, total, pct in static_rows:
            indicator = rate_label(pct)
            label_col, rate_col = st.columns([3, 1])
            with label_col:
                st.write(f"**{category}**")
                st.caption(f"{total} total matches")
            with rate_col:
                st.metric(label="", value=f"{pct}%", label_visibility="collapsed")
                st.caption(indicator)
            st.progress(pct / 100)
            st.divider()


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
    """Render the full Johanna Park analytical dashboard."""
    st.header("Analytical Dashboard")
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

    try:
        matches_raw = fetch_json("/matches")
    except RequestException as exc:
        matches_raw = []
        errors.append(f"Matches unavailable: {exc}")

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

    users_df = lower_status(pd.DataFrame(users_raw))
    matches_df = lower_status(pd.DataFrame(matches_raw))
    reports_df = lower_status(pd.DataFrame(reports_raw))
    satisfaction_df = pd.DataFrame(satisfaction_raw)

    if not users_df.empty:
        raw_year = users_df.get("year", pd.Series(dtype=str))
        users_df["year"] = raw_year.fillna("Unknown")

    if not matches_df.empty and "matched_on" in matches_df.columns:
        matches_df["matched_on"] = pd.to_datetime(
            matches_df["matched_on"], errors="coerce"
        )

    if not reports_df.empty:
        raw_reason = reports_df.get("reason", pd.Series(dtype=str))
        reports_df["reason"] = raw_reason.fillna("Unknown")

    total_users = len(users_df)
    active_matches = int(
        (matches_df["status"] == "active").sum()
    ) if not matches_df.empty else 0
    completed = int(
        (matches_df["status"] == "completed").sum()
    ) if not matches_df.empty else 0
    removed = int(
        (matches_df["status"] == "removed").sum()
    ) if not matches_df.empty else 0

    non_removed = max(
        int(
            (matches_df["status"] != "removed").sum()
        ) if not matches_df.empty else 0,
        1,
    )
    meetup_rate = round(completed / non_removed * 100, 1)

    avg_sat: Optional[float] = None
    if not satisfaction_df.empty and "rating" in satisfaction_df.columns:
        avg_sat = round(float(satisfaction_df["rating"].mean()), 1)

    left_col, right_col = st.columns([1, 1], gap="large")

    with left_col:
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Users", f"{total_users:,}", delta="5%")
        with col2:
            st.metric("Active Matches", f"{active_matches:,}", delta="18%")

        st.write("")

        col3, col4 = st.columns(2)
        with col3:
            st.metric("Meet Up Rate", f"{meetup_rate:.0f}%", delta="-5%")
        with col4:
            sat_label = f"{avg_sat}/5.0" if avg_sat is not None else "N/A"
            st.metric("Satisfaction Rating", sat_label, delta="0.4%")

        st.write("")

        chart_l, chart_r = st.columns(2)
        with chart_l:
            with st.container(border=True):
                st.markdown("**Sign up Trend**")
                render_trend_chart(matches_df)
        with chart_r:
            with st.container(border=True):
                st.markdown("**Demographics**")
                render_demographics_chart(users_df)

        st.write("")

        with st.container(border=True):
            st.markdown("**User Satisfaction Survey Results**")
            render_satisfaction_chart(satisfaction_df)

    with right_col:
        meet_col1, meet_col2 = st.columns(2)
        with meet_col1:
            st.metric(
                label="Successful Meet Ups",
                value=f"{completed:,}",
                delta=None,
            )
        with meet_col2:
            st.metric(
                label="No Meet Ups", 
                value=f"{removed:,}",
                delta=None,
            )

        st.write("")

        with st.container(border=True):
            st.metric(
                label="In Person Meetup Rate",
                value=f"{meetup_rate:.0f}%",
            )

        st.write("")

        with st.container(border=True):
            st.markdown("**Detailed Breakdown**")
            render_breakdown(matches_df)

        st.write("")

        with st.container(border=True):
            st.markdown("**Common Shared Interests**")
            render_interests(reports_df)


main()
