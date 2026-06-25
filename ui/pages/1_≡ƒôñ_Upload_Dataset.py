"""
pages/1_📤_Upload_Dataset.py

Upload page — accepts a file (not actually parsed) and simulates a
ranking run with a spinner + progress bar + success message.

# TODO:
# Replace utils.parser.parse_uploaded_file with real parsing, and
# utils.runner.simulate_ranking_run with an actual call into rank.py.
"""

import streamlit as st

from components.cards import info_box
from components.helpers import configure_page, section_header, divider
from utils.loader import generate_dummy_dataset_info
from utils.parser import parse_uploaded_file
from utils.runner import simulate_ranking_run

configure_page(title="Upload Dataset", icon="📤")

section_header(
    "Upload Candidate Dataset",
    eyebrow="Step 1 of 2",
    subtitle="Upload a resume export to begin a new ranking run.",
)

# ---------------------------------------------------------------------------
# File uploader
# ---------------------------------------------------------------------------

uploaded_file = st.file_uploader(
    "Drop your dataset here, or browse files",
    type=["csv", "json", "xlsx"],
    help="Supported formats: CSV, JSON, XLSX",
)

info_box(
    "<strong>Supported formats:</strong> .csv, .json, .xlsx &nbsp;·&nbsp; "
    "Each row should represent one candidate with resume text and metadata.",
    kind="info",
)

divider()

# ---------------------------------------------------------------------------
# Dataset information card
# ---------------------------------------------------------------------------

section_header("Dataset Information", eyebrow=None)

file_meta = parse_uploaded_file(uploaded_file)
dataset_info = generate_dummy_dataset_info(file_meta["filename"])

col1, col2, col3 = st.columns(3)
with col1:
    st.markdown(
        f"""
        <div class="metric-card" style="--metric-accent:#6E8CC9;">
            <div class="metric-label">Selected Filename</div>
            <div class="metric-value" style="font-size:1.1rem;">{dataset_info['filename']}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
with col2:
    st.markdown(
        f"""
        <div class="metric-card" style="--metric-accent:#C9A227;">
            <div class="metric-label">Estimated Candidate Count</div>
            <div class="metric-value">{dataset_info['estimated_candidates']:,}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
with col3:
    st.markdown(
        f"""
        <div class="metric-card" style="--metric-accent:#3DDC97;">
            <div class="metric-label">Status</div>
            <div class="metric-value" style="font-size:1.1rem;">{dataset_info['status']}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.write("")
divider()

# ---------------------------------------------------------------------------
# Run ranking
# ---------------------------------------------------------------------------

section_header("Run Ranking", eyebrow=None,
               subtitle="This simulates the ranking pipeline for demo purposes only.")

run_disabled = uploaded_file is None
if run_disabled:
    info_box("Upload a dataset above to enable the ranking run.", kind="warning")

if st.button("Run Ranking", type="primary", disabled=run_disabled):
    progress_bar = st.progress(0, text="Initializing ranking pipeline...")

    with st.spinner("Scoring candidates against role requirements..."):
        def _update(pct: int) -> None:
            progress_bar.progress(pct, text=f"Ranking candidates... {pct}%")

        # TODO:
        # Execute rank.py after dataset upload
        simulate_ranking_run(on_progress=_update)

    progress_bar.progress(100, text="Ranking complete.")
    st.success(
        "Ranking run complete. Candidates have been scored — head to the "
        "Dashboard or Shortlisted Candidates page to review results."
    )
