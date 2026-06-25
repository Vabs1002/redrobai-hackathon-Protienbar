"""
components/helpers.py

Shared low-level UI helpers used across every page:
- CSS injection
- page config
- the small "section header" building block used to open most sections

Keeping these in one place means every page looks consistent without
re-implementing the same boilerplate.
"""

from pathlib import Path
import streamlit as st

# Resolve paths relative to the ui/ package root so this works no matter
# which page imports it.
ROOT_DIR = Path(__file__).resolve().parent.parent
STYLE_PATH = ROOT_DIR / "styles" / "style.css"
LOGO_PATH = ROOT_DIR / "assets" / "logo.png"


def inject_css() -> None:
    """Load styles/style.css and inject it into the current page.

    Call this once near the top of every page (after st.set_page_config).
    """
    if STYLE_PATH.exists():
        css = STYLE_PATH.read_text()
        st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)


def configure_page(title: str, icon: str = "🏆") -> None:
    """Apply consistent page configuration + inject the stylesheet.

    Every page in pages/ should call this first, before any other
    Streamlit command, since set_page_config must run first.
    """
    st.set_page_config(
        page_title=f"{title} · Candidate Discovery & Ranking",
        page_icon=icon,
        layout="wide",
        initial_sidebar_state="expanded",
    )
    inject_css()


def section_header(title: str, subtitle: str | None = None, eyebrow: str | None = None) -> None:
    """Render the consistent section header used throughout the app.

    eyebrow: small gold uppercase label above the title (optional)
    subtitle: muted supporting line below the title (optional)

    NOTE: built as a single-line string deliberately. Streamlit's markdown
    renderer follows CommonMark's indented-code-block rule: an indented
    HTML line preceded by a blank line gets parsed as a code block rather
    than raw HTML. When eyebrow/subtitle are omitted, a multi-line/indented
    template leaves a blank-ish line right before the next indented <div>,
    which triggers exactly that. Keeping it on one line avoids the issue.
    """
    eyebrow_html = f'<div class="eyebrow">{eyebrow}</div>' if eyebrow else ""
    subtitle_html = f'<div class="section-subtitle">{subtitle}</div>' if subtitle else ""
    st.markdown(
        f'<div class="section-block">{eyebrow_html}'
        f'<div class="section-title">{title}</div>{subtitle_html}</div>',
        unsafe_allow_html=True,
    )


def divider() -> None:
    """Thin, low-contrast divider — used instead of st.divider() for
    a more deliberate, lower-contrast rule than Streamlit's default."""
    st.markdown('<hr class="divider-line" />', unsafe_allow_html=True)
