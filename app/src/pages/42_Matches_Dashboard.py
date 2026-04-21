"""Matches dashboard page for Persona 4: Johanna Park."""

import logging
from typing import Any, List, Optional

import matplotlib.pyplot as plt  # type: ignore[import-not-found]
import pandas as pd
import requests  # type: ignore[import-untyped]
import streamlit as st  # type: ignore[import-not-found]
from requests.exceptions import RequestException  # type: ignore[import-untyped]
from modules.nav import SideBarLinks  # type: ignore[import-not-found]

logger = logging.getLogger(__name__)

st.set_page_config(page_title="Matches Dashboard", layout="wide")

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
    """Return a qualitative label for the given percentage value."""
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

        fig, ax = plt.subplots(figsize=(5.0, 3.2))
        fig.patch.set_facecolor("none")
        ax.set_facecolor("none")
        xs = range(len(trend))
        ax.plot(xs, trend["Count"], marker="o", linewidth=2, color="#4b8cf5")
        ax.fill_between(xs, trend["Count"], alpha=0.15, color="#4b8cf5")
        ax.set_xticks(list(xs))
        ax.set_xticklabels(
            list(trend["Month"]), fontsize=8, rotation=45, color="#cccccc"
        )
        ax.tick_params(axis="y", colors="#cccccc", labelsize=8)
        for spine in ax.spines.values():
            spine.set_visible(False)
        ax.grid(axis="y", color="#555", linewidth=0.4, linestyle="--")
        st.pyplot(fig, use_container_width=True)
    else:
        st.info("No trend data.")


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
                st.metric(
                    label="", value=f"{pct}%", label_visibility="collapsed"
                )
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
                st.metric(
                    label="", value=f"{pct}%", label_visibility="collapsed"
                )
                st.caption(indicator)
            st.progress(pct / 100)
            st.divider()


def main() -> None:
    """Render the Matches dashboard page."""
    st.header("Matches Dashboard")
    st.caption("Persona 4: Johanna Park")

    if st.button("<- Back to Home", type="secondary"):
        st.switch_page("Home.py")

    st.markdown("---")

    errors: List[str] = []

    try:
        matches_raw = fetch_json("/matches")
    except RequestException as exc:
        matches_raw = []
        errors.append(f"Matches unavailable: {exc}")

    for err in errors:
        st.warning(err)

    matches_df = lower_status(pd.DataFrame(matches_raw))

    if not matches_df.empty and "matched_on" in matches_df.columns:
        matches_df["matched_on"] = pd.to_datetime(
            matches_df["matched_on"], errors="coerce"
        )

    # Metrics
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

    # Top metrics row
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Active Matches", f"{active_matches:,}", delta="18%")
    with col2:
        st.metric("Successful Meet Ups", f"{completed:,}")
    with col3:
        st.metric("No Meet Ups", f"{removed:,}")
    with col4:
        st.metric("Meet Up Rate", f"{meetup_rate:.0f}%", delta="-5%")

    st.write("")

    # Charts
    trend_col, breakdown_col = st.columns([1, 1], gap="large")

    with trend_col:
        with st.container(border=True):
            st.markdown("**Sign up Trend**")
            render_trend_chart(matches_df)

    with breakdown_col:
        with st.container(border=True):
            st.markdown("**Detailed Breakdown**")
            render_breakdown(matches_df)


main()
