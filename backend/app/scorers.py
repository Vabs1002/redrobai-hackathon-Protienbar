import re
from datetime import datetime

# List of service consultancies to check against
SERVICE_COMPANIES = {
    'tcs', 'tata consultancy services', 'infosys', 'wipro', 'accenture', 
    'cognizant', 'capgemini', 'hcl', 'hcltech', 'tech mahindra', 
    'ltimindtree', 'mindtree', 'dxc technology', 'genpact', 'ibm consulting',
    'l&t technology services', 'persistent systems', 'mphasis', 'coforge', 'ust global'
}

# Preferred locations
PRIMARY_LOCATIONS = {'noida', 'pune'}
SECONDARY_LOCATIONS = {'delhi', 'ncr', 'gurgaon', 'ghaziabad', 'faridabad', 'mumbai', 'hyderabad', 'bangalore', 'bengaluru'}

# Target skills from the Job Description
CORE_SKILLS = {
    'vector search', 'vector database', 'embeddings', 'sentence-transformers', 'openai embeddings', 'bge', 'e5',
    'pinecone', 'weaviate', 'qdrant', 'milvus', 'opensearch', 'elasticsearch', 'faiss',
    'python',
    'ndcg', 'mrr', 'map', 'evaluation framework', 'ranking system', 'evaluation metrics',
    'nlp', 'natural language processing', 'information retrieval', 'ir'
}

def calculate_skills_score(skills):
    """
    Evaluates the depth, duration, and endorsements of core skills.
    """
    if not skills:
        return 0.0
        
    score = 0.0
    matched_skills = 0
    
    proficiency_map = {
        'expert': 1.0,
        'advanced': 0.8,
        'intermediate': 0.5,
        'beginner': 0.2
    }
    
    for skill in skills:
        name = skill.get("name", "").lower().strip()
        # Check if the skill matches any of our core skills
        is_core = any(core in name or name in core for core in CORE_SKILLS)
        
        if is_core:
            matched_skills += 1
            prof = skill.get("proficiency", "beginner").lower()
            prof_weight = proficiency_map.get(prof, 0.2)
            
            duration = skill.get("duration_months", 0)
            # Duration factor: caps at 4 years (48 months)
            duration_factor = min(duration / 48.0, 1.0)
            
            endorsements = skill.get("endorsements", 0)
            # Endorsements factor: caps at 50
            endorsements_factor = min(endorsements / 50.0, 1.0)
            
            # Combine factors for this skill
            skill_score = prof_weight * 0.5 + duration_factor * 0.3 + endorsements_factor * 0.2
            score += skill_score
            
    if matched_skills == 0:
        return 0.0
        
    # Average score of matched skills, scaled by the variety of matched skills (up to 5)
    variety_multiplier = min(matched_skills / 5.0, 1.0)
    avg_score = score / matched_skills
    
    return avg_score * variety_multiplier

def evaluate_career_quality(career_history, current_title):
    """
    Checks candidate work history for product vs service background,
    title-chasing behavior (job-hopping), and role title fit.
    """
    if not career_history:
        return 0.0
        
    title_lower = current_title.lower()
    
    # Exclude/disqualify non-engineering titles entirely
    disqualified_titles = ['hr', 'human resources', 'recruiter', 'marketing', 'content writer', 'copywriter', 'graphic designer', 'accountant', 'sales', 'civil engineer', 'mechanical engineer']
    for bad_title in disqualified_titles:
        if re.search(r'\b' + bad_title + r'\b', title_lower):
            return 0.0
            
    # Target engineering titles
    target_titles = ['machine learning', 'ml', 'ai', 'artificial intelligence', 'nlp', 'search', 'retrieval', 'backend', 'data engineer', 'software engineer', 'developer', 'staff engineer', 'principal engineer']
    is_target_title = any(target in title_lower for target in target_titles)
    if not is_target_title:
        return 0.1 # Unrelated engineering role gets very low score

    total_jobs = len(career_history)
    service_jobs_count = 0
    has_product_experience = False
    total_months = 0
    
    for job in career_history:
        company = job.get("company", "").lower().strip()
        is_service = any(service in company for service in SERVICE_COMPANIES)
        is_service = is_service or (job.get("industry", "").lower() in ["it services", "information technology & services", "management consulting"])
        
        duration = job.get("duration_months", 0)
        total_months += duration
        
        if is_service:
            service_jobs_count += 1
        else:
            has_product_experience = True

    # 1. Service consultancy check
    if service_jobs_count == total_jobs:
        return 0.05 # Dislike: Only worked at service companies
        
    # 2. Tenure / Job Hopping Check (Title chasers)
    # Average tenure in months (excluding current job if it's very short)
    avg_tenure_months = total_months / total_jobs if total_jobs > 0 else 0
    tenure_penalty = 1.0
    if total_jobs >= 3 and avg_tenure_months < 18:
        # Job switcher every 1.5 years or less
        tenure_penalty = 0.5

    # 3. Product alignment base score
    if service_jobs_count == 0:
        base_career_score = 1.0 # Pure product background
    else:
        # Mixed career path (some service, some product)
        # Note: If currently at service but has product exp, we allow it with minor penalty
        current_job_company = career_history[0].get("company", "").lower()
        current_is_service = any(service in current_job_company for service in SERVICE_COMPANIES)
        if current_is_service and has_product_experience:
            base_career_score = 0.7
        else:
            base_career_score = 1.0 - (service_jobs_count / total_jobs) * 0.4

    return base_career_score * tenure_penalty

def calculate_experience_alignment(years_of_experience):
    """
    Checks total years of experience, favoring the target range of 5-9 years.
    """
    if years_of_experience < 2:
        return 0.1
    elif years_of_experience < 4:
        return 0.5
    elif 5 <= years_of_experience <= 9:
        return 1.0 # Perfect match
    elif 9 < years_of_experience <= 12:
        return 0.8
    elif years_of_experience > 12:
        return 0.5 # Overqualified / more expensive
    else:
        # Between 4 and 5
        return 0.8

def calculate_logistics_score(location, country, notice_period_days):
    """
    Scores candidate based on Noida/Pune location and notice period.
    """
    loc_lower = location.lower().strip()
    country_lower = country.lower().strip()
    
    # Location scoring
    if any(primary in loc_lower for primary in PRIMARY_LOCATIONS) and "india" in country_lower:
        loc_score = 1.0
    elif any(secondary in loc_lower for secondary in SECONDARY_LOCATIONS) and "india" in country_lower:
        loc_score = 0.7
    elif "india" in country_lower:
        loc_score = 0.4 # Other locations in India
    else:
        loc_score = 0.1 # Outside India (no visa sponsorship)
        
    # Notice period scoring
    if notice_period_days <= 15:
        notice_score = 1.0
    elif notice_period_days <= 30:
        notice_score = 0.9
    elif notice_period_days <= 60:
        notice_score = 0.6
    else:
        notice_score = 0.2
        
    return loc_score * 0.6 + notice_score * 0.4

def calculate_availability_multiplier(signals):
    """
    Generates a multiplier based on platform activity, response rates, and open to work flag.
    A completely inactive candidate who doesn't respond gets down-weighted significantly.
    """
    response_rate = signals.get("recruiter_response_rate", 0.0) # 0.0 to 1.0
    open_to_work = signals.get("open_to_work_flag", False)
    
    # Parse last active date to check recency (reference is mid-2026)
    last_active_str = signals.get("last_active_date", "")
    recency_multiplier = 0.5
    
    try:
        last_active = datetime.strptime(last_active_str, "%Y-%m-%d")
        ref_date = datetime(2026, 6, 17) # current date reference
        days_inactive = (ref_date - last_active).days
        if days_inactive <= 7:
            recency_multiplier = 1.2
        elif days_inactive <= 30:
            recency_multiplier = 1.0
        elif days_inactive <= 90:
            recency_multiplier = 0.8
        elif days_inactive <= 180:
            recency_multiplier = 0.6
        else:
            recency_multiplier = 0.4 # Inactive for 6+ months
    except Exception:
        pass
        
    open_to_work_bonus = 1.2 if open_to_work else 0.8
    
    # Response rate weight
    response_factor = 0.5 + (response_rate * 0.7) # range 0.5 to 1.2
    
    # Combine signals
    multiplier = recency_multiplier * open_to_work_bonus * response_factor
    return max(multiplier, 0.1) # cap the minimum at 0.1 to avoid complete zeroing of valid matches
