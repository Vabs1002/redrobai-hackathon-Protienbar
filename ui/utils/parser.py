"""
utils/parser.py

Stub module for parsing uploaded candidate datasets.
No real parsing happens yet — this only inspects the uploaded file
object enough to show placeholder metadata in the UI.

# TODO:
# Implement real parsing of the uploaded file (CSV / JSON resume export)
# into the candidate schema expected by rank.py. This likely involves
# validating columns, normalizing fields, and handling malformed rows.
"""

from typing import Optional


def parse_uploaded_file(uploaded_file) -> dict:
    """Inspect an uploaded file object and return lightweight metadata.

    This intentionally does NOT read/parse the actual contents — it only
    reports the filename and size so the Upload page can render a
    dataset info card without touching any backend logic.
    """
    if uploaded_file is None:
        return {"filename": None, "size_kb": None}

    size_kb = round(uploaded_file.size / 1024, 1) if hasattr(uploaded_file, "size") else None
    return {
        "filename": uploaded_file.name,
        "size_kb": size_kb,
    }


def validate_schema(uploaded_file) -> Optional[str]:
    """Placeholder schema validation.

    # TODO:
    # Validate that required columns (name, resume_text / structured
    # fields, location, experience, etc.) are present before allowing
    # the user to trigger ranking.
    Currently always returns None (no error) since no parsing occurs yet.
    """
    return None
