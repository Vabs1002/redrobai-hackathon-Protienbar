import streamlit as st
import pandas as pd
import json
import sys
from pathlib import Path

# --- 1. PATH FIX FOR BACKEND IMPORTS ---
# This grabs the absolute path of your project root (3 levels up from this file)
# ui/pages/file.py -> ui/pages -> ui -> root
root_dir = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(root_dir))

# Now you can import from the backend folder!
from backend.app.honeypot import is_honeypot_profile
from backend.app.scorers import (
    calculate_skills_score,
    evaluate_career_quality,
    calculate_experience_alignment,
    calculate_logistics_score,
    calculate_availability_multiplier
)

# --- 2. PAGE CONFIGURATION ---
st.set_page_config(page_title="Upload Dataset", page_icon="📄", layout="wide")
st.title(" Upload Candidate Dataset")
st.markdown("Upload a JSON file containing an array of candidate profiles.")

# File uploader
uploaded_file = st.file_uploader("Choose a JSON file", type=["json"])

def process_candidates(candidates_list):
    """Processes a list of candidate dictionaries through the scoring engine."""
    results = []
    
    for candidate in candidates_list:
        profile = candidate.get("profile", {})
        signals = candidate.get("redrob_signals", {})
        name = profile.get("name", "Unknown Candidate")
        
        # Run Honeypot Detection
        is_fraud = is_honeypot_profile(candidate)
        
        if is_fraud:
            results.append({
                "Name": name,
                "Title": profile.get("current_title", ""),
                "Status": "Honeypot Detected",
                "Final Score": 0.0
            })
            continue 
            
        # Extract variables and calculate scores
        current_title = profile.get("current_title", "")
        yoe = profile.get("years_of_experience", 0)
        location = profile.get("location", "")
        country = profile.get("country", "")
        notice = profile.get("notice_period_days", 90)
        
        skills_score = calculate_skills_score(candidate.get("skills", []))
        career_score = evaluate_career_quality(candidate.get("career_history", []), current_title)
        exp_score = calculate_experience_alignment(yoe)
        logistics_score = calculate_logistics_score(location, country, notice)
        avail_multiplier = calculate_availability_multiplier(signals)
        
        # Final Weighted Score
        base_score = (skills_score * 0.4) + (career_score * 0.3) + (exp_score * 0.15) + (logistics_score * 0.15)
        final_score = base_score * avail_multiplier
        
        results.append({
            "Name": name,
            "Title": current_title,
            "Status": "Cleared",
            "Final Score": round(final_score * 100, 1)
        })
        
    return results

# --- 3. UI LOGIC ---
if uploaded_file is not None:
    try:
        data = json.load(uploaded_file)
        
        if not isinstance(data, list):
            st.error("The JSON file must contain a list (array) of candidate objects.")
        else:
            with st.spinner('Scoring candidates...'):
                scored_data = process_candidates(data)
                
            df = pd.DataFrame(scored_data)
            df = df.sort_values(by="Final Score", ascending=False).reset_index(drop=True)
            
            st.success(f"Successfully processed {len(data)} candidates!")
            st.subheader(" Candidate Leaderboard")
            
            st.dataframe(
                df,
                use_container_width=True,
                column_config={
                    "Final Score": st.column_config.ProgressColumn(
                        "Final Score",
                        help="Weighted score out of 100",
                        format="%f",
                        min_value=0,
                        max_value=100,
                    ),
                }
            )
            
    except Exception as e:
        st.error(f"Error reading file: {e}")