"""
pages/2_📊_Dashboard.py

Top-level KPI dashboard with placeholder charts driven by randomly
generated dummy data.

# TODO:
# Replace KPI values and chart data sources with real outputs from
# rank.py / scorers.py once the ranking run has been executed.
"""

import streamlit as st

from components.charts import (
    chart_card,
    score_distribution_fig,
    experience_distribution_fig,
    candidate_locations_fig,
    qualification_funnel_fig,
)
from components.helpers import configure_page, section_header, divider
from components.metrics import metric_row
from utils.loader import generate_dummy_candidates

configure_page(title="Dashboard", icon="📊")

section_header(
    "Dashboard",
    eyebrow="Overview",
    subtitle="Snapshot of the current candidate pool and ranking run.",
)

# ---------------------------------------------------------------------------
# Dummy data
# ---------------------------------------------------------------------------

df = generate_dummy_candidates(n=120)
total = len(df)
qualified = int((df["Status"] == "Qualified").sum())
rejected = int((df["Status"] == "Rejected").sum())
avg_score = round(df["Score"].mean(), 1)
top_score = round(df["Score"].max(), 1)

# ---------------------------------------------------------------------------
# KPI row
# ---------------------------------------------------------------------------

metric_row([
    {"label": "Total Candidates", "value": f"{total:,}", "accent": "blue"},
    {"label": "Qualified Candidates", "value": f"{qualified:,}",
     "delta": f"{qualified/total:.0%} of pool", "delta_direction": "up", "accent": "teal"},
    {"label": "Rejected Candidates", "value": f"{rejected:,}",
     "delta": f"{rejected/total:.0%} of pool", "delta_direction": "down", "accent": "red"},
    {"label": "Average Score", "value": f"{avg_score}", "accent": "gold"},
    {"label": "Top Candidate Score", "value": f"{top_score}", "accent": "gold"},
])

st.write("")
divider()

# ---------------------------------------------------------------------------
# Charts
# ---------------------------------------------------------------------------

row1_col1, row1_col2 = st.columns(2)
with row1_col1:
    chart_card(
        "Score Distribution",
        "Spread of candidate ranking scores across the pool.",
        score_distribution_fig(),
    )
with row1_col2:
    chart_card(
        "Experience Distribution",
        "Years of professional experience across candidates.",
        experience_distribution_fig(),
    )

row2_col1, row2_col2 = st.columns(2)
with row2_col1:
    chart_card(
        "Candidate Locations",
        "Geographic concentration of the candidate pool.",
        candidate_locations_fig(),
    )
with row2_col2:
    chart_card(
        "Qualification Funnel",
        "Candidates remaining at each stage of the pipeline.",
        qualification_funnel_fig(),
    )
