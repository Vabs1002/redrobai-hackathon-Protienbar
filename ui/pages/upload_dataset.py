import streamlit as st
import pandas as pd
import json
import sys
import os
from pathlib import Path

# --- 1. PATH FIX FOR BACKEND IMPORTS ---
root_dir = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(root_dir))

from backend.app.honeypot import is_honeypot_profile
from backend.app.scorers import (
    calculate_skills_score,
    evaluate_career_quality,
    calculate_experience_alignment,
    calculate_logistics_score,
    calculate_availability_multiplier,
    CORE_SKILLS,
    SERVICE_COMPANIES
)

# --- 2. PAGE CONFIGURATION ---
st.set_page_config(page_title="Upload Dataset", page_icon="📤", layout="wide")
st.title(" 📤 Upload Candidate Dataset")
st.markdown("Upload a JSON or JSONL file containing candidate profiles.")

# File uploader
uploaded_file = st.file_uploader("Choose a file", type=["json", "jsonl"])

def calculate_fallback_semantic_score(candidate):
    skills = [s.get("name", "").lower().strip() for s in candidate.get("skills", [])]
    profile = candidate.get("profile", {})
    headline = profile.get("headline", "").lower()
    summary = profile.get("summary", "").lower()
    
    match_count = 0
    for core_skill in CORE_SKILLS:
        if any(core_skill in skill for skill in skills) or core_skill in headline or core_skill in summary:
            match_count += 1
    return min(match_count / 10.0, 0.5)

def generate_reasoning(candidate):
    profile = candidate.get("profile", {})
    title = profile.get("current_title", "Software Engineer")
    exp = profile.get("years_of_experience", 0.0)
    signals = candidate.get("redrob_signals", {})
    response_rate = int(signals.get("recruiter_response_rate", 0.0) * 100)
    notice = signals.get("notice_period_days", 30)
    
    candidate_skills = [s.get("name") for s in candidate.get("skills", [])]
    matching_skills = []
    for skill in candidate_skills:
        name_lower = skill.lower()
        if any(core in name_lower for core in CORE_SKILLS):
            matching_skills.append(skill)
            if len(matching_skills) >= 3:
                break
                
    skills_str = ", ".join(matching_skills) if matching_skills else "AI engineering"
    
    has_product = True
    for job in candidate.get("career_history", []):
        company = job.get("company", "").lower()
        if any(service in company for service in SERVICE_COMPANIES):
            has_product = False
            break
            
    product_badge = "product engineering background" if has_product else "mixed agency/consulting background"
    reasoning = f"{title} with {exp} yrs experience and a strong {product_badge}. Skills include {skills_str}. Highly responsive on platform ({response_rate}% response rate) with a {notice}-day notice period."
    return reasoning

def process_candidates(candidates_list):
    """Processes a list of candidate dictionaries through the scoring engine."""
    results = []
    
    # Load pre-computed similarity scores
    precomputed_scores = {}
    precompute_file = root_dir / 'similarity_scores.json'
    if precompute_file.exists():
        try:
            with open(precompute_file, 'r', encoding='utf-8') as pf:
                precomputed_scores = json.load(pf)
        except Exception:
            pass
            
    raw_profiles = {}
    
    for candidate in candidates_list:
        cid = candidate.get("candidate_id")
        if not cid:
            continue
            
        raw_profiles[cid] = candidate
        profile = candidate.get("profile", {})
        signals = candidate.get("redrob_signals", {})
        name = profile.get("anonymized_name", "Unknown Candidate")
        
        # 1. Run Honeypot Detection
        is_fraud = is_honeypot_profile(candidate)
        if is_fraud:
            continue
            
        # 2. Extract variables and calculate scores
        current_title = profile.get("current_title", "")
        yoe = profile.get("years_of_experience", 0.0)
        location = profile.get("location", "")
        country = profile.get("country", "")
        notice = signals.get("notice_period_days", 30)
        
        skills_score = calculate_skills_score(candidate.get("skills", []))
        career_score = evaluate_career_quality(candidate.get("career_history", []), current_title)
        
        # Filter out completely unrelated candidates (like in rank.py)
        if skills_score == 0.0 or career_score == 0.0:
            continue
            
        exp_score = calculate_experience_alignment(yoe)
        logistics_score = calculate_logistics_score(location, country, notice)
        
        # Get semantic similarity score
        semantic_score = precomputed_scores.get(cid)
        if semantic_score is None or semantic_score == 0.0:
            semantic_score = calculate_fallback_semantic_score(candidate)
            
        # Final Weighted Score (same weights as rank.py)
        weighted_score = (
            skills_score * 0.30 +
            semantic_score * 0.30 +
            career_score * 0.20 +
            exp_score * 0.10 +
            logistics_score * 0.10
        )
        
        avail_multiplier = calculate_availability_multiplier(signals)
        final_score = weighted_score * avail_multiplier
        final_score = max(0.0, min(final_score, 1.0))
        
        reasoning = generate_reasoning(candidate)
        
        results.append({
            "Candidate ID": cid,
            "Name": name,
            "Current Title": current_title,
            "Experience (yrs)": yoe,
            "Location": location or "Not Specified",
            "Score": round(final_score * 100.0, 1),
            "Notice Period": f"{notice} days",
            "Status": "Qualified",
            "Reasoning": reasoning,
            "raw_profile": candidate
        })
        
    # Sort by score descending, then candidate ID ascending for tie-breaks
    results.sort(key=lambda x: (-x["Score"], x["Candidate ID"]))
    
    # Assign ranks
    for rank, res in enumerate(results, 1):
        res["Rank"] = rank
        
    return results, raw_profiles

# --- 3. UI LOGIC ---
if uploaded_file is not None:
    try:
        # Support both JSON array and JSONL format
        file_content = uploaded_file.getvalue().decode("utf-8")
        if file_content.strip().startswith("["):
            data = json.loads(file_content)
        else:
            # Parse JSONL lines
            data = []
            for line in file_content.splitlines():
                if line.strip():
                    data.append(json.loads(line))
        
        if not isinstance(data, list):
            st.error("The JSON file must contain candidate profiles.")
        else:
            with st.spinner('Scoring candidates through the Agentic RAG engine...'):
                scored_data, raw_profiles = process_candidates(data)
                
            df = pd.DataFrame(scored_data)
            
            # Store in session state
            st.session_state["real_candidates"] = df
            st.session_state["real_raw_profiles"] = raw_profiles
            
            st.success(f"Successfully processed {len(df)} qualified candidates out of {len(data)} profiles!")
            st.subheader("🏆 Candidate Leaderboard")
            
            # Reorder columns to show Rank and ID first
            cols = ["Rank", "Candidate ID", "Name", "Current Title", "Experience (yrs)", "Location", "Score", "Reasoning"]
            display_df = df[cols]
            
            st.dataframe(
                display_df,
                hide_index=True,
                use_container_width=True,
                column_config={
                    "Score": st.column_config.ProgressColumn(
                        "Match Score",
                        help="Weighted score out of 100",
                        format="%.1f",
                        min_value=0,
                        max_value=100,
                    ),
                }
            )
            
    except Exception as e:
        st.error(f"Error reading file: {e}")