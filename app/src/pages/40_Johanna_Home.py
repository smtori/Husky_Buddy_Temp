"""Analytical dashboard for Persona 4: Johanna Park."""

import logging
from typing import Any, List, Optional

import matplotlib.pyplot as plt  # type: ignore[import-untyped]
import pandas as pd
import requests  # type: ignore[import-untyped]
import streamlit as st  # type: ignore[import-not-found]
from requests.exceptions import RequestException  # type: ignore[import-untyped]
from modules.nav import SideBarLinks  # type: ignore[import-not-found]

logger = logging.getLogger(__name__)

st.set_page_config(page_title="Analytical Dashboard", layout="wide")

SideBarLinks()

st.markdown("""
<style>
[data-testid="metric-container"] {
    background: #3a3a3a;
    border-radius: 12px;
    padding: 16px 20px;
}
[data-testid="metric-container"] label {
    color: #cccccc !important;
    font-size: 0.8rem !important;
    font-weight: 600 !important;
    text-transform: uppercase;
    letter-spacing: 0.04em;
}
[data-testid="stMetricValue"] {
    font-size: 2rem !important;
    font-weight: 800 !important;
    color: #ffffff !important;
}
[data-testid="stMetricDeltaIcon-Up"]   { color: #4CAF50 !important; }
[data-testid="stMetricDeltaIcon-Down"] { color: #e74c3c !important; }

.meetup-card {
    border-radius: 14px;
    padding: 18px 10px;
    text-align: center;
}
.meetup-card .num { font-size: 2.2rem; font-weight: 800; color: #fff; line-height: 1; }
.meetup-card .lbl { font-size: 0.78rem; color: rgba(255,255,255,0.85); margin-top: 4px; }
.green-card { background: #4CAF50; }
.red-card   { background: #e74c3c; }

.rate-badge {
    display: inline-block;
    border-radius: 20px;
    padding: 5px 12px;
    font-size: 0.8rem;
    font-weight: 700;
    color: #fff;
}
.badge-green  { background: #4CAF50; }
.badge-yellow { background: #f0a500; }
.badge-red    { background: #e74c3c; }

.interest-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 9px 0;
    border-bottom: 1px solid #444;
}
.interest-row:last-child { border-bottom: none; }
.i-label { font-weight: 600; font-size: 0.88rem; }
.i-count  { color: #999; font-size: 0.8rem; }
</style>
""", unsafe_allow_html=True)

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


def badge_class(rate: int) -> str:
    """Return the CSS badge class for a given success-rate percentage."""
    if rate >= 75:
        return "badge-green"
    if rate >= 65:
        return "badge-yellow"
    return "badge-red"


def render_trend_chart(matches: pd.DataFrame) -> None:
    """Render the monthly sign-up trend line chart."""
    if not matches.empty and "matched_on" in matches.columns:
        month_order = [
            "Jan", "Feb", "Mar", "Apr", "May", "Jun",
            "Jul", "Aug", "Sep", "Oct", "Nov", "Dec",
        ]
        trend = (
            matches.dropna(subset=["matched_on"])
            .assign(Month=lambda d: d["matched_on"].dt.strftime("%b"))
            .groupby("Month")
            .size()
            .reset_index(name="Count")
        )
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
        demo = (
            users.groupby("year")
            .size()
            .reset_index(name="Users")
        )
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
            bd = (
                matches.groupby("status")
                .size()
                .reset_index(name="total")
                .rename(columns={"status": "Category"})
            )
            bd["Category"] = bd["Category"].str.title()
            total_all = max(int(bd["total"].sum()), 1)
            bd["rate"] = (
                bd["total"] / total_all * 100
            ).round(0).astype(int)

        for _, row in bd.iterrows():
            css = badge_class(int(row["rate"]))
            st.markdown(
                f'<div style="display:flex;justify-content:space-between;'
                f'align-items:center;padding:10px 4px;'
                f'border-bottom:1px solid #444">'
                f'<div>'
                f'<div style="font-weight:600;font-size:0.88rem">'
                f'{row["Category"]}</div>'
                f'<div style="color:#888;font-size:0.77rem">'
                f'{row["total"]} total matches</div>'
                f'</div>'
                f'<span class="rate-badge {css}">'
                f'{row["rate"]}% Success Rate</span>'
                f'</div>',
                unsafe_allow_html=True,
            )
    else:
        static_rows = [
            ("CS + CS", 45, 78),
            ("Business + CS", 40, 74),
            ("Engineering + Engineering", 32, 70),
            ("DS + Business", 25, 77),
            ("Engineering + Business", 68, 61),
        ]
        for category, total, pct in static_rows:
            css = badge_class(pct)
            st.markdown(
                f'<div style="display:flex;justify-content:space-between;'
                f'align-items:center;padding:10px 4px;'
                f'border-bottom:1px solid #444">'
                f'<div>'
                f'<div style="font-weight:600;font-size:0.88rem">'
                f'{category}</div>'
                f'<div style="color:#888;font-size:0.77rem">'
                f'{total} total matches</div>'
                f'</div>'
                f'<span class="rate-badge {css}">'
                f'{pct}% Success Rate</span>'
                f'</div>',
                unsafe_allow_html=True,
            )


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
        top = (
            reports.groupby(interest_col)
            .size()
            .reset_index(name="count")
            .rename(columns={interest_col: "Interest"})
            .sort_values("count", ascending=False)
            .head(6)
        )
        rows = [(str(r["Interest"]), int(r["count"])) for _, r in top.iterrows()]
    else:
        rows = [
            ("Career + Co-ops", 30),
            ("Sports + Fitness", 25),
            ("Technology", 15),
            ("Music", 10),
        ]

    interest_html = "".join(
        f'<div class="interest-row">'
        f'<span class="i-label">{name}</span>'
        f'<span class="i-count">{cnt} total matches</span>'
        f'</div>'
        for name, cnt in rows
    )
    st.markdown(interest_html, unsafe_allow_html=True)


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
            st.markdown(
                f'<div class="meetup-card green-card">'
                f'<div class="num">{completed:,}</div>'
                f'<div class="lbl">successful meet ups</div>'
                f'</div>',
                unsafe_allow_html=True,
            )
        with meet_col2:
            st.markdown(
                f'<div class="meetup-card red-card">'
                f'<div class="num">{removed:,}</div>'
                f'<div class="lbl">no meet ups</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

        st.write("")

        with st.container(border=True):
            st.markdown(
                f'<div style="text-align:center;padding:4px 0">'
                f'<p style="margin:0;color:#aaa;font-size:0.8rem;'
                f'font-weight:600;text-transform:uppercase;'
                f'letter-spacing:.05em">In person meetup rate</p>'
                f'<p style="margin:0;font-size:2.4rem;font-weight:800;'
                f'color:#fff">{meetup_rate:.0f}%</p>'
                f'</div>',
                unsafe_allow_html=True,
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
