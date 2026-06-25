"""
utils/loader.py

Generates placeholder / dummy data used throughout the prototype UI.

# TODO:
# Replace every function in this file with real data loaded from the
# backend pipeline (rank.py -> ranked candidates, scorers.py -> score
# breakdowns, honeypot.py -> integrity warnings) once integration begins.
"""

import numpy as np
import pandas as pd

_FIRST_NAMES = [
    "Aarav", "Diya", "Kabir", "Meera", "Rohan", "Ishita", "Vikram", "Ananya",
    "Sahil", "Tanya", "Arjun", "Priya", "Nikhil", "Sneha", "Rahul", "Kavya",
    "Dev", "Naina", "Yash", "Riya",
]
_LAST_NAMES = [
    "Sharma", "Verma", "Iyer", "Khan", "Reddy", "Nair", "Gupta", "Kapoor",
    "Joshi", "Menon", "Chawla", "Bose", "Pillai", "Rao", "Mehta", "Sinha",
]
_TITLES = [
    "Backend Engineer", "Data Scientist", "Frontend Engineer",
    "ML Engineer", "DevOps Engineer", "Product Manager",
    "Full Stack Developer", "Data Analyst", "Platform Engineer",
    "QA Engineer",
]
_LOCATIONS = [
    "Bengaluru", "Pune", "Hyderabad", "Delhi NCR", "Mumbai",
    "Chennai", "Remote", "Gurugram",
]
_NOTICE = ["Immediate", "15 days", "30 days", "60 days", "90 days"]
_SKILLS_POOL = [
    "Python", "SQL", "AWS", "React", "Kubernetes", "Data Modeling",
    "NLP", "Go", "Terraform", "GraphQL", "Docker", "Spark", "Airflow",
    "TypeScript", "PyTorch",
]
_STATUSES = ["Qualified", "Needs Review", "Rejected"]


def _rng(seed: int = 7) -> np.random.Generator:
    return np.random.default_rng(seed)


def generate_dummy_candidates(n: int = 60) -> pd.DataFrame:
    """Build a placeholder dataframe of ranked candidates.

    Columns intentionally mirror what rank.py is expected to eventually
    output, so swapping in the real backend later is a drop-in change.
    """
    rng = _rng(11)
    rows = []
    for i in range(n):
        first = rng.choice(_FIRST_NAMES)
        last = rng.choice(_LAST_NAMES)
        score = float(np.clip(rng.normal(70, 13), 30, 99))
        # Status is correlated with score so the leaderboard reads
        # sensibly (high scorers skew Qualified, low scorers skew Rejected).
        if score >= 75:
            status = rng.choice(_STATUSES, p=[0.8, 0.17, 0.03])
        elif score >= 55:
            status = rng.choice(_STATUSES, p=[0.4, 0.45, 0.15])
        else:
            status = rng.choice(_STATUSES, p=[0.1, 0.35, 0.55])
        rows.append({
            "Rank": i + 1,
            "Candidate ID": f"CND-{1000 + i}",
            "Name": f"{first} {last}",
            "Current Title": rng.choice(_TITLES),
            "Experience (yrs)": int(rng.integers(1, 16)),
            "Location": rng.choice(_LOCATIONS),
            "Score": round(score, 1),
            "Notice Period": rng.choice(_NOTICE),
            "Status": status,
            "Reasoning": _placeholder_reasoning(status),
        })

    df = pd.DataFrame(rows).sort_values("Score", ascending=False).reset_index(drop=True)
    df["Rank"] = range(1, len(df) + 1)
    return df


def _placeholder_reasoning(status: str) -> str:
    if status == "Qualified":
        return "Strong skill overlap with role requirements; consistent career trajectory."
    if status == "Needs Review":
        return "Partial skill match; recommend manual review of recent role gap."
    return "Insufficient relevant experience for the target role."


def generate_dummy_skills(candidate_seed: int) -> list[str]:
    rng = _rng(candidate_seed)
    k = int(rng.integers(4, 8))
    return list(rng.choice(_SKILLS_POOL, size=k, replace=False))


def generate_dummy_timeline(candidate_seed: int) -> list[dict]:
    """Placeholder career timeline entries for the Candidate Inspector page."""
    rng = _rng(candidate_seed + 1)
    companies = ["Nimbus Labs", "Orbit Systems", "Quanta Health", "Vertex Retail",
                 "BrightGrid", "Acme Cloud", "Northstar Analytics"]
    n_roles = int(rng.integers(2, 4))
    chosen = rng.choice(companies, size=n_roles, replace=False)
    timeline = []
    start_year = 2024 - sum(int(rng.integers(1, 4)) for _ in range(n_roles))
    for company in chosen:
        duration = int(rng.integers(1, 4))
        timeline.append({
            "company": company,
            "title": rng.choice(_TITLES),
            "start_year": start_year,
            "end_year": start_year + duration,
        })
        start_year += duration
    return timeline


def generate_dummy_score_breakdown(candidate_seed: int) -> dict:
    rng = _rng(candidate_seed + 2)
    return {
        "Skill Match": int(rng.integers(55, 98)),
        "Experience Fit": int(rng.integers(50, 95)),
        "Career Trajectory": int(rng.integers(45, 92)),
        "Location Fit": int(rng.integers(40, 99)),
        "Integrity / Honeypot": int(rng.integers(80, 100)),
    }


def generate_dummy_dataset_info(filename: str | None) -> dict:
    """Placeholder dataset metadata shown after a file is 'uploaded'."""
    rng = _rng(3)
    return {
        "filename": filename or "—",
        "estimated_candidates": int(rng.integers(800, 1500)),
        "status": "Ready to rank" if filename else "Awaiting upload",
    }
