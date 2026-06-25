"""
components/tables.py

Reusable table rendering for candidate data.
Currently renders dummy DataFrames only.

# TODO:
# Replace input dataframe with the ranked output produced by rank.py
# (typically loaded from a generated submission.csv / ranking result).
"""

import pandas as pd
import streamlit as st

from components.cards import rank_badge, status_badge


def render_search_filter_bar(df: pd.DataFrame) -> pd.DataFrame:
    """Render a search box + status filter row above a candidate table
    and return the filtered dataframe.
    """
    col1, col2, col3 = st.columns([3, 1.3, 1.3])

    with col1:
        query = st.text_input(
            "Search candidates",
            placeholder="Search by name, title, or location...",
            label_visibility="collapsed",
        )

    with col2:
        status_options = ["All statuses"] + sorted(df["Status"].unique().tolist())
        status_filter = st.selectbox("Status", status_options, label_visibility="collapsed")

    with col3:
        sort_options = ["Score (high to low)", "Score (low to high)", "Experience", "Rank"]
        sort_choice = st.selectbox("Sort by", sort_options, label_visibility="collapsed")

    filtered = df.copy()

    if query:
        mask = (
            filtered["Name"].str.contains(query, case=False, na=False)
            | filtered["Current Title"].str.contains(query, case=False, na=False)
            | filtered["Location"].str.contains(query, case=False, na=False)
        )
        filtered = filtered[mask]

    if status_filter != "All statuses":
        filtered = filtered[filtered["Status"] == status_filter]

    if sort_choice == "Score (high to low)":
        filtered = filtered.sort_values("Score", ascending=False)
    elif sort_choice == "Score (low to high)":
        filtered = filtered.sort_values("Score", ascending=True)
    elif sort_choice == "Experience":
        filtered = filtered.sort_values("Experience (yrs)", ascending=False)
    elif sort_choice == "Rank":
        filtered = filtered.sort_values("Rank", ascending=True)

    return filtered


def render_candidate_table(df: pd.DataFrame) -> None:
    """Render the shortlisted-candidates table with rank insignia and
    status badges rendered as HTML inside the dataframe.
    """
    display_df = df.copy()
    display_df["Rank"] = display_df["Rank"].apply(rank_badge)
    display_df["Status"] = display_df["Status"].apply(
        lambda s: status_badge(s, _status_to_kind(s))
    )

    st.markdown(
        display_df.to_html(escape=False, index=False, classes="candidate-table"),
        unsafe_allow_html=True,
    )


def _status_to_kind(status: str) -> str:
    mapping = {
        "Qualified": "qualified",
        "Rejected": "rejected",
        "Needs Review": "review",
    }
    return mapping.get(status, "neutral")


def render_data_table(df: pd.DataFrame, height: int = 420) -> None:
    """Generic, sortable/filterable native Streamlit dataframe — used
    where a lighter-weight table (no custom HTML) is preferred.
    """
    st.dataframe(df, use_container_width=True, height=height, hide_index=True)
