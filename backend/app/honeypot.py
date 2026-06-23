import datetime
from datetime import datetime as dt

def parse_date(date_str):
    if not date_str:
        return None
    try:
        return dt.strptime(date_str, "%Y-%m-%d")
    except Exception:
        return None

def is_honeypot_profile(candidate):
    """
    Checks if a candidate is a honeypot (trap) candidate by auditing data consistency.
    Returns True if an anomaly is detected, False otherwise.
    """
    profile = candidate.get("profile", {})
    career_history = candidate.get("career_history", [])
    skills = candidate.get("skills", [])
    education = candidate.get("education", [])
    signals = candidate.get("redrob_signals", {})
    
    # --- Check 1: Timeline Dates and Durations ---
    for job in career_history:
        start_str = job.get("start_date")
        end_str = job.get("end_date")
        duration = job.get("duration_months", 0)
        
        # Anomaly 1.1: Negative duration
        if duration < 0:
            return True
            
        start_date = parse_date(start_str)
        if not start_date:
            continue
            
        # If currently working, reference is the candidate's last active date or current date
        if job.get("is_current") or not end_str:
            last_active_str = signals.get("last_active_date")
            end_date = parse_date(last_active_str)
            if not end_date:
                end_date = dt.now()
        else:
            end_date = parse_date(end_str)
            
        if not end_date:
            continue
            
        # Anomaly 1.2: Job starts after it ends
        if start_date > end_date:
            return True
            
        # Anomaly 1.3: Claimed job duration exceeds the calendar time by a large margin
        # (e.g. 8 years duration in a 3-year calendar span)
        calendar_months = (end_date.year - start_date.year) * 12 + (end_date.month - start_date.month)
        # We allow a buffer of 2 months for rounding differences, but anything beyond is impossible.
        if duration > calendar_months + 2:
            return True

    # --- Check 2: Skill Duration and Proficiency Anomaly ---
    # Trap: Expert/Advanced proficiency in skills but with 0 months used
    expert_zero_duration_count = 0
    for skill in skills:
        prof = skill.get("proficiency", "").lower()
        dur = skill.get("duration_months", 0)
        if prof in ["expert", "advanced"] and dur == 0:
            expert_zero_duration_count += 1
            
    # If a candidate lists 5 or more expert/advanced skills with 0 months, it is a trap profile
    if expert_zero_duration_count >= 5:
        return True

    # --- Check 3: Platform Timeline Logic ---
    # Anomaly 3.1: Signup date is after last active date (dates run backward)
    signup_str = signals.get("signup_date")
    last_active_str = signals.get("last_active_date")
    if signup_str and last_active_str:
        signup_date = parse_date(signup_str)
        last_active_date = parse_date(last_active_str)
        if signup_date and last_active_date and last_active_date < signup_date:
            return True

    # --- Check 4: Education Chronology ---
    # Anomaly 4.1: Education end year is earlier than start year
    for edu in education:
        start_yr = edu.get("start_year")
        end_yr = edu.get("end_year")
        if start_yr and end_yr and end_yr < start_yr:
            return True

    return False
