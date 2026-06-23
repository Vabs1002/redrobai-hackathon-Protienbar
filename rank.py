#!/usr/bin/env python3
import json
import csv
import argparse
import sys
import os

# Add backend/app to path to import scoring modules
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend', 'app'))
import honeypot
import scorers

def parse_args():
    parser = argparse.ArgumentParser(description="Rank candidates against JD.")
    parser.add_argument(
        "--candidates",
        required=True,
        help="Path to candidates.jsonl file"
    )
    parser.add_argument(
        "--out",
        required=True,
        help="Path to save output submission.csv"
    )
    return parser.parse_args()

def calculate_fallback_semantic_score(candidate):
    """
    Fallback scoring using local keyword matching for unseen candidates (no internet/no precomputed score).
    """
    skills = [s.get("name", "").lower().strip() for s in candidate.get("skills", [])]
    headline = candidate.get("profile", {}).get("headline", "").lower()
    summary = candidate.get("profile", {}).get("summary", "").lower()
    
    match_count = 0
    for core_skill in scorers.CORE_SKILLS:
        if any(core_skill in skill for skill in skills) or core_skill in headline or core_skill in summary:
            match_count += 1
            
    # Max score of 0.5 for fallback to prevent it outranking verified embedding scores
    return min((match_count / len(scorers.CORE_SKILLS)) * 0.5, 0.5)

def generate_reasoning(candidate, composite_score):
    """
    Generates a natural, professional 1-2 sentence recruiter-like reasoning for the CSV.
    """
    profile = candidate.get("profile", {})
    title = profile.get("current_title", "Software Engineer")
    exp = profile.get("years_of_experience", 0.0)
    signals = candidate.get("redrob_signals", {})
    response_rate = int(signals.get("recruiter_response_rate", 0.0) * 100)
    notice = signals.get("notice_period_days", 30)
    
    # Extract top matching skills for reasoning context
    candidate_skills = [s.get("name") for s in candidate.get("skills", [])]
    matching_skills = []
    for skill in candidate_skills:
        name_lower = skill.lower()
        if any(core in name_lower for core in scorers.CORE_SKILLS):
            matching_skills.append(skill)
            if len(matching_skills) >= 3:
                break
                
    skills_str = ", ".join(matching_skills) if matching_skills else "AI engineering"
    
    # Check if they have product background
    has_product = True
    for job in candidate.get("career_history", []):
        company = job.get("company", "").lower()
        if any(service in company for service in scorers.SERVICE_COMPANIES):
            has_product = False
            break
            
    product_badge = "product engineering background" if has_product else "mixed agency/consulting background"
    
    reasoning = f"{title} with {exp} yrs experience and a strong {product_badge}. Skills include {skills_str}. Highly responsive on platform ({response_rate}% response rate) with a {notice}-day notice period."
    return reasoning

def main():
    args = parse_args()
    
    if not os.path.exists(args.candidates):
        print(f"Error: Candidates file not found at '{args.candidates}'")
        sys.exit(1)
        
    # Load pre-computed similarity scores
    precomputed_scores = {}
    precompute_file = os.path.join(os.path.dirname(__file__), 'similarity_scores.json')
    if os.path.exists(precompute_file):
        try:
            with open(precompute_file, 'r', encoding='utf-8') as pf:
                precomputed_scores = json.load(pf)
            print(f"Loaded {len(precomputed_scores)} precomputed similarity scores.")
        except Exception as e:
            print(f"Warning: Could not load precomputed scores: {e}. Falling back to keyword search.")
    else:
        print("Warning: similarity_scores.json not found. Running with local fallback matchers.")

    ranked_list = []
    
    print("Reading and scoring candidates...")
    with open(args.candidates, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                candidate = json.loads(line)
                cid = candidate.get("candidate_id")
                
                # Step 1: Honeypot Filter
                if honeypot.is_honeypot_profile(candidate):
                    # Honeypots get score 0.0 to prevent ranking them in the top 100
                    continue
                    
                # Step 2: Scoring components
                skills_score = scorers.calculate_skills_score(candidate.get("skills", []))
                
                profile = candidate.get("profile", {})
                current_title = profile.get("current_title", "")
                career_history = candidate.get("career_history", [])
                career_score = scorers.evaluate_career_quality(career_history, current_title)
                
                # If career_score or skills_score is 0 (i.e. completely disqualified title or no match), skip
                if career_score == 0.0 or skills_score == 0.0:
                    continue
                    
                exp_score = scorers.calculate_experience_alignment(profile.get("years_of_experience", 0.0))
                
                signals = candidate.get("redrob_signals", {})
                logistics_score = scorers.calculate_logistics_score(
                    profile.get("location", ""), 
                    profile.get("country", ""), 
                    signals.get("notice_period_days", 30)
                )
                
                # Fetch semantic score
                semantic_score = precomputed_scores.get(cid)
                if semantic_score is None:
                    semantic_score = calculate_fallback_semantic_score(candidate)
                    
                # Step 3: Composite Formula
                # Weights: Skills (30%), Semantic Match (30%), Career Quality (20%), Experience (10%), Logistics (10%)
                weighted_score = (
                    skills_score * 0.30 +
                    semantic_score * 0.30 +
                    career_score * 0.20 +
                    exp_score * 0.10 +
                    logistics_score * 0.10
                )
                
                # Step 4: Apply Availability Multiplier
                availability_multiplier = scorers.calculate_availability_multiplier(signals)
                final_score = weighted_score * availability_multiplier
                
                # Ensure the final score stays in [0.0, 1.0] range
                final_score = max(0.0, min(final_score, 1.0))
                
                reasoning = generate_reasoning(candidate, final_score)
                
                ranked_list.append({
                    "candidate_id": cid,
                    "score": round(final_score, 4),
                    "reasoning": reasoning
                })
            except Exception as e:
                # Silently skip lines with parsing issues to prevent crashes in the sandbox
                continue
                
    print(f"Scoring complete. Total qualified candidates: {len(ranked_list)}")
    
    # Step 5: Sort and Break Ties
    # Sort by score descending, then by candidate_id ascending for ties (challenge rules)
    ranked_list.sort(key=lambda x: (-x["score"], x["candidate_id"]))
    
    # Take top 100
    top_100 = ranked_list[:100]
    
    # Step 6: Write to CSV
    print(f"Writing top 100 candidates to '{args.out}'...")
    with open(args.out, 'w', encoding='utf-8', newline='') as csvfile:
        writer = csv.writer(csvfile)
        # Header
        writer.writerow(["candidate_id", "rank", "score", "reasoning"])
        # Rows
        for rank, cand in enumerate(top_100, 1):
            writer.writerow([
                cand["candidate_id"],
                rank,
                f"{cand['score']:.4f}",
                cand["reasoning"]
            ])
            
    print("CSV generated successfully.")

if __name__ == "__main__":
    main()
