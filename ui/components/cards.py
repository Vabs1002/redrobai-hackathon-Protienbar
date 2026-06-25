"""
components/cards.py

Reusable presentational components:
- feature_card     : home page capability cards
- info_box         : inline colored callouts
- status_badge     : small pill used for qualification status
- rank_badge       : the circular rank insignia (signature element)
"""

import streamlit as st


def feature_card(icon: str, title: str, description: str) -> None:
    """Render a single feature card (used in a 3-column row on Home)."""
    st.markdown(
        f"""
        <div class="feature-card">
            <div class="feature-icon">{icon}</div>
            <div class="feature-title">{title}</div>
            <div class="feature-desc">{description}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def info_box(text: str, kind: str = "info") -> None:
    """Render an inline callout box.

    kind: "info" | "success" | "warning" | "danger"
    """
    st.markdown(f'<div class="info-box {kind}">{text}</div>', unsafe_allow_html=True)


def status_badge(label: str, status: str = "neutral") -> str:
    """Return HTML for a small status pill.

    status: "qualified" | "rejected" | "review" | "neutral"
    Returns raw HTML (string) so it can be composed inline within tables
    or other markdown blocks via st.markdown(..., unsafe_allow_html=True).
    """
    return (
        f'<span class="status-badge {status}">'
        f'<span class="dot"></span>{label}</span>'
    )


def rank_badge(rank: int) -> str:
    """Return HTML for the circular rank insignia.

    Top 3 ranks render in gold ("top"), all others in a neutral ink tone.
    Returns raw HTML so it can be placed inside dataframes / markdown.
    """
    css_class = "top" if rank <= 3 else "standard"
    return f'<span class="rank-badge {css_class}">{rank}</span>'
