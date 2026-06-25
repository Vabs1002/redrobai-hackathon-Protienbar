"""
pages/5_📈_Analytics.py

Aggregate analytics across the full candidate pool: skills, experience,
locations, availability, career quality, and score distribution.

# TODO:
# Replace dummy chart data with aggregated metrics computed from the
# real ranked candidate set once rank.py / scorers.py are integrated.
"""

import streamlit as st

from components.charts import (
    chart_card,
    top_skills_fig,
    experience_distribution_fig,
    candidate_locations_fig,
    availability_distribution_fig,
    career_quality_distribution_fig,
    score_distribution_fig,
)
from components.helpers import configure_page, section_header, divider
from components.metrics import metric_row
from utils.loader import generate_dummy_candidates

configure_page(title="Analytics", icon="📈")

section_header(
    "Analytics",
    eyebrow="Pool-Wide Insights",
    subtitle="Aggregate signal across the entire candidate pool.",
)

df = generate_dummy_candidates(n=150)

# ---------------------------------------------------------------------------
# Summary metrics
# ---------------------------------------------------------------------------

metric_row([
    {"label": "Candidates Analyzed", "value": f"{len(df):,}", "accent": "blue"},
    {"label": "Unique Locations", "value": f"{df['Location'].nunique()}", "accent": "teal"},
    {"label": "Median Experience", "value": f"{df['Experience (yrs)'].median():.0f} yrs", "accent": "gold"},
    {"label": "Median Score", "value": f"{df['Score'].median():.1f}", "accent": "gold"},
])

st.write("")
divider()

# ---------------------------------------------------------------------------
# Charts
# ---------------------------------------------------------------------------

r1c1, r1c2 = st.columns(2)
with r1c1:
    chart_card("Top Skills", "Most frequently observed skills across the pool.", top_skills_fig())
with r1c2:
    chart_card("Experience Histogram", "Distribution of years of experience.", experience_distribution_fig())

r2c1, r2c2 = st.columns(2)
with r2c1:
    chart_card("Candidate Locations", "Where candidates are based.", candidate_locations_fig())
with r2c2:
    chart_card("Availability Distribution", "Notice-period buckets across the pool.", availability_distribution_fig())

r3c1, r3c2 = st.columns(2)
with r3c1:
    chart_card("Career Quality Distribution", "Composite career-trajectory signal, banded.", career_quality_distribution_fig())
with r3c2:
    chart_card("Score Distribution", "Overall ranking score spread.", score_distribution_fig())
