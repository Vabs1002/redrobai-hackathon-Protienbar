"""
app.py — Home

Entry point for the multipage app. Streamlit's native page navigation
(driven by the pages/ folder) is used instead of a manual sidebar menu.
"""

import base64
from pathlib import Path

import streamlit as st

from components.cards import feature_card
from components.helpers import configure_page, LOGO_PATH, divider

configure_page(title="Home", icon="🏆")


# ---------------------------------------------------------------------------
# Hero
# ---------------------------------------------------------------------------

def _logo_b64() -> str | None:
    if LOGO_PATH.exists():
        return base64.b64encode(LOGO_PATH.read_bytes()).decode()
    return None


logo_b64 = _logo_b64()

with st.container():
    col_logo, col_text = st.columns([1, 5], vertical_alignment="center")
    with col_logo:
        if logo_b64:
            st.markdown(
                f'<img src="data:image/png;base64,{logo_b64}" '
                f'width="86" class="logo-mark" />',
                unsafe_allow_html=True,
            )
        else:
            st.markdown("### 🏆")
    with col_text:
        st.markdown(
            """
            <div class="hero-wrap">
                <div class="eyebrow">Internal HR Analytics Tool</div>
                <div class="hero-title">AI Candidate Discovery &amp; Ranking</div>
                <div class="hero-sub">
                    Surface, score, and shortlist candidates automatically —
                    combining semantic ranking, integrity screening, and
                    explainable reasoning in a single recruiter workspace.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

divider()

# ---------------------------------------------------------------------------
# Feature cards
# ---------------------------------------------------------------------------

st.markdown('<div class="eyebrow">Core Capabilities</div>', unsafe_allow_html=True)
st.write("")

c1, c2, c3 = st.columns(3)
with c1:
    feature_card(
        icon="🧠",
        title="Semantic Ranking",
        description=(
            "Candidates are embedded and ranked against role requirements "
            "using semantic similarity rather than brittle keyword matching."
        ),
    )
with c2:
    feature_card(
        icon="🛡️",
        title="Honeypot Detection",
        description=(
            "Resumes are screened for manipulation signals and prompt-injection "
            "attempts before being surfaced to recruiters."
        ),
    )
with c3:
    feature_card(
        icon="🔍",
        title="Explainable AI",
        description=(
            "Every score ships with a human-readable rationale, so recruiters "
            "can see exactly why a candidate was ranked the way they were."
        ),
    )

st.write("")
st.write("")

# ---------------------------------------------------------------------------
# Primary CTA
# ---------------------------------------------------------------------------

col_a, col_b, col_c = st.columns([2, 2, 2])
with col_b:
    if st.button("Upload Candidate Dataset", type="primary", use_container_width=True):
        # TODO:
        # Once Upload page is wired to the backend, this can switch_page
        # directly into pages/1_Upload_Dataset.py. For now this button
        # has no functionality per the prototype scope.
        st.switch_page("pages/upload_dataset.py")

st.markdown(
    '<p style="text-align:center; color:#5C6072; font-size:0.8rem; margin-top:0.6rem;">'
    "Use the sidebar to navigate between Dashboard, Shortlisted Candidates, "
    "Candidate Inspector, and Analytics.</p>",
    unsafe_allow_html=True,
)
