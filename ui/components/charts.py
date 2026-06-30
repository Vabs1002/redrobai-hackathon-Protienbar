"""
components/charts.py

All Plotly figure builders live here, each returning a `go.Figure`
(or `px` figure) styled with the shared dark theme. Every function
currently uses randomly generated placeholder data.

# TODO:
# Replace each dummy data generator with the corresponding ranked /
# scored output from rank.py + scorers.py once the backend is wired up.
"""

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ---------------------------------------------------------------------------
# Shared theme
# ---------------------------------------------------------------------------

INK = "#0B0D12"
PANEL = "#14171F"
GRID = "#242833"
TEXT = "#EAEBF0"
TEXT_MUTED = "#8B90A0"

GOLD = "#C9A227"
TEAL = "#3DDC97"
RED = "#E2574C"
BLUE = "#6E8CC9"
LAVENDER = "#9B8CC9"

CATEGORICAL_SEQUENCE = [GOLD, TEAL, BLUE, LAVENDER, RED, "#5C6072"]


def _apply_theme(fig: go.Figure, height: int = 320) -> go.Figure:
    """Apply the shared dark styling to any figure before returning it."""
    fig.update_layout(
        height=height,
        paper_bgcolor=PANEL,
        plot_bgcolor=PANEL,
        font=dict(family="Inter, sans-serif", color=TEXT_MUTED, size=12),
        margin=dict(l=10, r=10, t=10, b=10),
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            font=dict(color=TEXT_MUTED, size=11),
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="left",
            x=0,
        ),
        hoverlabel=dict(bgcolor=INK, font_color=TEXT, bordercolor=GRID),
    )
    fig.update_xaxes(showgrid=False, zeroline=False, linecolor=GRID, color=TEXT_MUTED)
    fig.update_yaxes(showgrid=True, gridcolor=GRID, zeroline=False, color=TEXT_MUTED)
    return fig


def chart_card(title: str, subtitle: str, fig: go.Figure) -> None:
    """Render a chart inside the standard 'chart-card' panel wrapper."""
    st.markdown(
        f"""
        <div class="chart-card">
            <div class="chart-card-title">{title}</div>
            <div class="chart-card-subtitle">{subtitle}</div>
        """,
        unsafe_allow_html=True,
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    st.markdown("</div>", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Dummy data generators
# ---------------------------------------------------------------------------

from typing import Optional

def _rng(seed: int = 42) -> np.random.Generator:
    return np.random.default_rng(seed)


def score_distribution_fig(df: Optional[pd.DataFrame] = None) -> go.Figure:
    """Histogram of candidate ranking scores (0-100)."""
    if df is not None and not df.empty:
        scores = df["Score"]
    else:
        scores = _rng(1).normal(68, 14, 600).clip(0, 100)
    fig = px.histogram(scores, nbins=24, color_discrete_sequence=[GOLD])
    fig.update_traces(marker_line_width=0)
    fig.update_layout(showlegend=False)
    fig.update_xaxes(title="Score")
    fig.update_yaxes(title="Candidates")
    return _apply_theme(fig)


def experience_distribution_fig(df: Optional[pd.DataFrame] = None) -> go.Figure:
    """Distribution of years of experience across candidates."""
    if df is not None and not df.empty:
        years = df["Experience (yrs)"]
    else:
        years = _rng(2).gamma(shape=2.2, scale=2.4, size=600).clip(0, 20)
    fig = px.histogram(years, nbins=20, color_discrete_sequence=[TEAL])
    fig.update_traces(marker_line_width=0)
    fig.update_layout(showlegend=False)
    fig.update_xaxes(title="Years of experience")
    fig.update_yaxes(title="Candidates")
    return _apply_theme(fig)


def candidate_locations_fig(df: Optional[pd.DataFrame] = None) -> go.Figure:
    """Bar chart of candidate counts by city/region."""
    if df is not None and not df.empty:
        grouped = df.groupby("Location").size().reset_index(name="count")
        df_plot = grouped.sort_values("count").tail(8)
        fig = px.bar(df_plot, x="count", y="Location", orientation="h",
                     color_discrete_sequence=[BLUE])
    else:
        cities = ["Bengaluru", "Pune", "Hyderabad", "Delhi NCR", "Mumbai",
                  "Chennai", "Remote", "Other"]
        counts = _rng(3).integers(40, 260, len(cities))
        df_dummy = pd.DataFrame({"city": cities, "count": counts}).sort_values("count")
        fig = px.bar(df_dummy, x="count", y="city", orientation="h",
                     color_discrete_sequence=[BLUE])
    fig.update_traces(marker_line_width=0)
    fig.update_layout(showlegend=False)
    fig.update_xaxes(title="Candidates")
    fig.update_yaxes(title="")
    return _apply_theme(fig)


def qualification_funnel_fig(df: Optional[pd.DataFrame] = None) -> go.Figure:
    """Funnel: sourced -> screened -> qualified -> shortlisted -> selected."""
    stages = ["Sourced", "Screened", "Qualified", "Shortlisted", "Selected"]
    if df is not None and not df.empty:
        total = len(df)
        qualified = len(df[df["Status"] == "Qualified"])
        shortlisted = len(df[df["Score"] >= 65.0])
        selected = len(df[df["Score"] >= 80.0])
        values = [total, total, qualified, shortlisted, selected]
    else:
        values = [1284, 940, 512, 180, 24]
    fig = go.Figure(go.Funnel(
        y=stages,
        x=values,
        marker=dict(color=[GOLD, TEAL, BLUE, LAVENDER, "#5C6072"]),
        textinfo="value+percent initial",
        textfont=dict(color=TEXT),
    ))
    return _apply_theme(fig, height=360)


def top_skills_fig(df: Optional[pd.DataFrame] = None) -> go.Figure:
    """Horizontal bar chart of most frequent candidate skills."""
    if df is not None and not df.empty:
        skills_list = []
        for raw in df["raw_profile"]:
            if isinstance(raw, dict):
                for skill_obj in raw.get("skills", []):
                    name = skill_obj.get("name")
                    if name:
                        skills_list.append(name)
        if skills_list:
            counts = pd.Series(skills_list).value_counts().reset_index()
            counts.columns = ["skill", "count"]
            df_plot = counts.head(10).sort_values("count")
        else:
            df_plot = pd.DataFrame({"skill": [], "count": []})
        fig = px.bar(df_plot, x="count", y="skill", orientation="h",
                     color_discrete_sequence=[GOLD])
    else:
        skills = ["Python", "SQL", "AWS", "React", "Kubernetes",
                  "Data Modeling", "NLP", "Go", "Terraform", "GraphQL"]
        counts = sorted(_rng(4).integers(60, 420, len(skills)), reverse=True)
        df_dummy = pd.DataFrame({"skill": skills, "count": counts}).sort_values("count")
        fig = px.bar(df_dummy, x="count", y="skill", orientation="h",
                     color_discrete_sequence=[GOLD])
    fig.update_traces(marker_line_width=0)
    fig.update_layout(showlegend=False)
    fig.update_xaxes(title="Mentions")
    fig.update_yaxes(title="")
    return _apply_theme(fig, height=360)


def availability_distribution_fig(df: Optional[pd.DataFrame] = None) -> go.Figure:
    """Pie/donut of candidate notice-period buckets."""
    if df is not None and not df.empty:
        counts = df["Notice Period"].value_counts().reset_index()
        counts.columns = ["Notice Period", "count"]
        fig = px.pie(
            names=counts["Notice Period"], values=counts["count"], hole=0.55,
            color_discrete_sequence=CATEGORICAL_SEQUENCE,
        )
    else:
        labels = ["Immediate", "15 days", "30 days", "60+ days"]
        values = [18, 34, 31, 17]
        fig = px.pie(
            names=labels, values=values, hole=0.55,
            color_discrete_sequence=CATEGORICAL_SEQUENCE,
        )
    fig.update_traces(textfont=dict(color=TEXT), marker=dict(line=dict(color=PANEL, width=2)))
    return _apply_theme(fig, height=320)


def career_quality_distribution_fig(df: Optional[pd.DataFrame] = None) -> go.Figure:
    """Distribution of a composite 'career quality' signal across bands."""
    bands = ["Exceptional", "Strong", "Moderate", "Weak"]
    if df is not None and not df.empty:
        bands_list = []
        for score in df["Score"]:
            if score >= 80:
                bands_list.append("Exceptional")
            elif score >= 65:
                bands_list.append("Strong")
            elif score >= 50:
                bands_list.append("Moderate")
            else:
                bands_list.append("Weak")
        counts = pd.Series(bands_list).value_counts()
        total = len(df)
        values = [round((counts.get(b, 0) / total) * 100, 1) for b in bands]
    else:
        values = [9, 31, 42, 18]
    fig = px.bar(x=bands, y=values, color=bands,
                 color_discrete_sequence=[GOLD, TEAL, BLUE, RED])
    fig.update_traces(marker_line_width=0)
    fig.update_layout(showlegend=False)
    fig.update_xaxes(title="")
    fig.update_yaxes(title="% of candidates")
    return _apply_theme(fig)
