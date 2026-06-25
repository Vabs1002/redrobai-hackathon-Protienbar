"""
components/metrics.py

Reusable KPI / metric card component.
Used on the Dashboard and Analytics pages to surface headline numbers.
"""

import streamlit as st

_ACCENT_MAP = {
    "gold": "#C9A227",
    "teal": "#3DDC97",
    "red": "#E2574C",
    "blue": "#6E8CC9",
}


def metric_card(label: str, value: str, delta: str | None = None,
                 delta_direction: str = "neutral", accent: str = "gold") -> None:
    """Render a single KPI card.

    label:           small uppercase label, e.g. "TOTAL CANDIDATES"
    value:           the headline figure, e.g. "1,284"
    delta:           optional small supporting line, e.g. "+12% vs last batch"
    delta_direction: "up" | "down" | "neutral" — controls delta color
    accent:          "gold" | "teal" | "red" | "blue" — left edge accent color
    """
    accent_color = _ACCENT_MAP.get(accent, _ACCENT_MAP["gold"])
    delta_html = ""
    if delta:
        delta_html = f'<div class="metric-delta {delta_direction}">{delta}</div>'

    # NOTE: kept on one line deliberately — see section_header() in
    # components/helpers.py for why multi-line templates with optional
    # (sometimes-empty) interpolated lines can get mis-parsed as a code
    # block by Streamlit's markdown renderer.
    st.markdown(
        f'<div class="metric-card" style="--metric-accent:{accent_color};">'
        f'<div class="metric-label">{label}</div>'
        f'<div class="metric-value">{value}</div>{delta_html}</div>',
        unsafe_allow_html=True,
    )


def metric_row(metrics: list[dict]) -> None:
    """Render a row of metric cards from a list of dicts.

    Each dict supports keys: label, value, delta, delta_direction, accent.
    Example:
        metric_row([
            {"label": "TOTAL CANDIDATES", "value": "1,284", "accent": "blue"},
            {"label": "QUALIFIED", "value": "362", "delta": "+8%", "delta_direction": "up", "accent": "teal"},
        ])
    """
    cols = st.columns(len(metrics))
    for col, m in zip(cols, metrics):
        with col:
            metric_card(
                label=m.get("label", ""),
                value=m.get("value", "—"),
                delta=m.get("delta"),
                delta_direction=m.get("delta_direction", "neutral"),
                accent=m.get("accent", "gold"),
            )
