"""
pages/3_🏆_Shortlisted_Candidates.py

Interactive candidate leaderboard with search, filter, sort, and a
(placeholder) CSV download button.

# TODO:
# Replace generate_dummy_candidates() with the ranked dataframe produced
# by rank.py, typically loaded from submission.csv.
"""

import streamlit as st

from components.helpers import configure_page, section_header, divider
from components.tables import render_search_filter_bar, render_candidate_table
from utils.loader import generate_dummy_candidates

configure_page(title="Shortlisted Candidates", icon="🏆")

section_header(
    "Shortlisted Candidates",
    eyebrow="Leaderboard",
    subtitle="Ranked candidates from the most recent run, searchable and filterable.",
)

from components.cards import info_box

if "real_candidates" in st.session_state:
    df = st.session_state["real_candidates"]
else:
    info_box(
        "<strong>No Candidate Pool Loaded</strong><br>Please navigate to the <strong>Upload Dataset</strong> page to upload a candidate JSON/JSONL file and rank them first.",
        kind="warning"
    )
    st.stop()

filtered_df = render_search_filter_bar(df)

st.caption(f"Showing {len(filtered_df)} of {len(df)} candidates")

render_candidate_table(filtered_df)

divider()

# ---------------------------------------------------------------------------
# Download
# ---------------------------------------------------------------------------

col1, col2 = st.columns([5, 1])
with col2:
    # TODO:
    # Wire this up to export the real ranked dataframe once backend
    # integration is complete. Currently exports the dummy dataframe.
    csv_bytes = filtered_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        "Download CSV",
        data=csv_bytes,
        file_name="shortlisted_candidates.csv",
        mime="text/csv",
        use_container_width=True,
    )
