"""
pages/4_👤_Candidate_Inspector.py

Deep-dive view into a single candidate: profile, career timeline,
score breakdown, availability, warnings, and recruiter-facing reasoning.

# TODO:
# Replace all generate_dummy_* calls with the real candidate record,
# score breakdown (scorers.py), and honeypot warnings (honeypot.py).
"""

import streamlit as st

from components.cards import info_box, status_badge, rank_badge
from components.helpers import configure_page, section_header, divider
from utils.loader import (
    generate_dummy_candidates,
    generate_dummy_skills,
    generate_dummy_timeline,
    generate_dummy_score_breakdown,
)

configure_page(title="Candidate Inspector", icon="👤")

section_header(
    "Candidate Inspector",
    eyebrow="Deep Dive",
    subtitle="Inspect a single candidate's profile, scoring, and reasoning in detail.",
)

if "real_candidates" in st.session_state:
    df = st.session_state["real_candidates"]
    is_real = True
else:
    info_box(
        "<strong>No Candidate Pool Loaded</strong><br>Please navigate to the <strong>Upload Dataset</strong> page to upload a candidate JSON/JSONL file and rank them first.",
        kind="warning"
    )
    st.stop()

selected_name = st.selectbox(
    "Select Candidate",
    options=df["Name"] + " — " + df["Candidate ID"],
)

selected_id = selected_name.split("—")[-1].strip()
candidate = df[df["Candidate ID"] == selected_id].iloc[0]

divider()

# ---------------------------------------------------------------------------
# Profile overview
# ---------------------------------------------------------------------------

header_col1, header_col2 = st.columns([4, 1])
with header_col1:
    st.markdown(
        f"""
        <div style="display:flex; align-items:center; gap:0.8rem;">
            {rank_badge(int(candidate['Rank']))}
            <div>
                <div style="font-family:'Space Grotesk',sans-serif; font-size:1.3rem; font-weight:600;">
                    {candidate['Name']}
                </div>
                <div style="color:#8B90A0; font-size:0.85rem;">{candidate['Current Title']}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
with header_col2:
    status_kind = {"Qualified": "qualified", "Rejected": "rejected",
                   "Needs Review": "review"}.get(candidate["Status"], "neutral")
    st.markdown(status_badge(candidate["Status"], status_kind), unsafe_allow_html=True)

st.write("")

p1, p2, p3, p4 = st.columns(4)
with p1:
    st.markdown(f"**Current Role**  \n{candidate['Current Title']}")
with p2:
    st.markdown(f"**Experience**  \n{candidate['Experience (yrs)']} years")
with p3:
    st.markdown(f"**Location**  \n{candidate['Location']}")
with p4:
    st.markdown(f"**Notice Period**  \n{candidate['Notice Period']}")

st.write("")

# Skills
if is_real:
    skills = [s.get("name") for s in candidate["raw_profile"].get("skills", [])]
else:
    seed = int(candidate["Candidate ID"].split("-")[-1])
    skills = generate_dummy_skills(seed)

st.markdown("**Skills**")
skill_chips = " ".join(
    f'<span class="status-badge neutral" style="margin-right:6px;">{s}</span>'
    for s in skills
)
st.markdown(skill_chips, unsafe_allow_html=True)

divider()

# ---------------------------------------------------------------------------
# Career timeline
# ---------------------------------------------------------------------------

section_header("Career Timeline", eyebrow=None)

if is_real:
    timeline = []
    for job in candidate["raw_profile"].get("career_history", []):
        start_year = job.get("start_date", "Unknown")[:4]
        end_date = job.get("end_date")
        end_year = end_date[:4] if end_date else "Present"
        timeline.append({
            "company": job.get("company", "Company"),
            "title": job.get("title", "Role"),
            "start_year": start_year,
            "end_year": end_year
        })
else:
    seed = int(candidate["Candidate ID"].split("-")[-1])
    timeline = generate_dummy_timeline(seed)

for entry in reversed(timeline):
    st.markdown(
        f"""
        <div style="display:flex; gap:0.9rem; padding:0.5rem 0; border-bottom:1px solid #1C1F29;">
            <div style="font-family:'JetBrains Mono',monospace; color:#C9A227; min-width:110px; font-size:0.82rem;">
                {entry['start_year']} – {entry['end_year']}
            </div>
            <div>
                <div style="font-weight:500; font-size:0.92rem;">{entry['title']}</div>
                <div style="color:#8B90A0; font-size:0.82rem;">{entry['company']}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

divider()

# ---------------------------------------------------------------------------
# Score breakdown
# ---------------------------------------------------------------------------

section_header("Score Breakdown", eyebrow=None)

if is_real:
    import sys
    import os
    import json
    
    parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    sys.path.append(os.path.join(parent_dir, 'backend', 'app'))
    import scorers
    import honeypot
    
    # Load precomputed scores
    precomputed_scores = {}
    precompute_file = os.path.join(parent_dir, 'similarity_scores.json')
    if os.path.exists(precompute_file):
        try:
            with open(precompute_file, 'r', encoding='utf-8') as pf:
                precomputed_scores = json.load(pf)
        except Exception:
            pass
            
    cand_raw = candidate["raw_profile"]
    profile = cand_raw.get("profile", {})
    history = cand_raw.get("career_history", [])
    skills_list = cand_raw.get("skills", [])
    signals = cand_raw.get("redrob_signals", {})
    cid = cand_raw.get("candidate_id")
    
    s_score = scorers.calculate_skills_score(skills_list)
    c_score = scorers.evaluate_career_quality(history, profile.get("current_title", ""))
    e_score = scorers.calculate_experience_alignment(profile.get("years_of_experience", 0.0))
    l_score = scorers.calculate_logistics_score(
        profile.get("location", ""),
        profile.get("country", ""),
        signals.get("notice_period_days", 30)
    )
    sem_score = precomputed_scores.get(cid)
    if sem_score is None or sem_score == 0.0:
        skills_names = [s.get("name", "").lower().strip() for s in skills_list]
        hl = profile.get("headline", "").lower()
        sum_text = profile.get("summary", "").lower()
        match_count = 0
        for core_skill in scorers.CORE_SKILLS:
            if any(core_skill in skill for skill in skills_names) or core_skill in hl or core_skill in sum_text:
                match_count += 1
        sem_score = min(match_count / 10.0, 0.5)
        
    is_fake = honeypot.is_honeypot_profile(cand_raw)
    integrity_score = 0 if is_fake else 100
    
    breakdown = {
        "Skill Match": int(s_score * 100),
        "Semantic Match": int(sem_score * 100),
        "Experience Fit": int(e_score * 100),
        "Career Trajectory": int(c_score * 100),
        "Location Fit": int(l_score * 100),
        "Integrity / Honeypot": integrity_score
    }
else:
    seed = int(candidate["Candidate ID"].split("-")[-1])
    breakdown = generate_dummy_score_breakdown(seed)

for label, value in breakdown.items():
    bcol1, bcol2 = st.columns([1, 4])
    with bcol1:
        st.markdown(f"<div style='font-size:0.85rem; padding-top:0.3rem;'>{label}</div>",
                    unsafe_allow_html=True)
    with bcol2:
        st.progress(value / 100, text=f"{value}/100")

divider()

# ---------------------------------------------------------------------------
# Availability + Warnings + Reasoning
# ---------------------------------------------------------------------------

col_a, col_b = st.columns(2)
with col_a:
    section_header("Availability", eyebrow=None)
    info_box(f"Notice period: <strong>{candidate['Notice Period']}</strong>", kind="info")

with col_b:
    section_header("Warnings", eyebrow=None)
    if is_real:
        if integrity_score == 0:
            info_box("Integrity screen flagged inconsistent role dates or fake skill proficiencies. Disqualified (Honeypot Shield).", kind="danger")
        else:
            info_box("No integrity or honeypot warnings detected for this candidate.", kind="success")
    else:
        if candidate["Status"] == "Rejected":
            info_box("Integrity screen flagged inconsistent role dates. Manual review recommended.",
                      kind="danger")
        elif candidate["Status"] == "Needs Review":
            info_box("Minor skill-claim mismatch detected. Low confidence — review recommended.",
                      kind="warning")
        else:
            info_box("No integrity or honeypot warnings detected for this candidate.", kind="success")

divider()

section_header("Recruiter Reasoning", eyebrow=None)
st.markdown(
    f"""
    <div class="info-box info">{candidate['Reasoning']}</div>
    """,
    unsafe_allow_html=True,
)
