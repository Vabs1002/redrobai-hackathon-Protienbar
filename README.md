# Intelligent Candidate Discovery & Ranking (Agentic RAG)

An advanced candidate ranking pipeline built to discover the top 100 candidates for the Senior AI Engineer role at Redrob from a pool of 100,000 profiles. The system is designed to run 100% offline, satisfies all sandbox constraints (finishes in under 5 seconds on CPU), and incorporates verification agents to eliminate honeypot profile traps.

---

## Technical Highlights

### 1. Agentic RAG Architecture
Instead of a simple flat vector search, our approach mimics a human recruiting team by splitting candidate scoring into specialized axes:
* **The JD Analyzer Agent (Offline)**: Parses the job description to extract target job titles, target skills (Pinecone, Milvus, NDCG evaluation, Python), and disqualifying criteria (consulting consultancies, junior LangChain-only developers).
* **Heuristic Pruning & Pre-filtering**: Filters out generic non-technical candidates (e.g. HR, marketing, sales) and candidates without any AI/ML background before vector search.
* **Recruiter Committee Scoring (Online)**:
  * **Skills Specialist**: Scores candidates based on matching skills, weighted by proficiency, tenure duration, and peer endorsements.
  * **Career Specialist**: Screens career histories. Disqualifies service-firm-only consultancies (TCS, Wipro, Infosys, etc.) while allowing current service-firm employees who have prior product-company experience. Applies penalties for high job-switching frequencies ("title-chasers").
  * **Logistics Specialist**: Ranks candidates based on Noida/Pune location alignment and notice periods (favoring < 30 days).
  * **Availability Specialist**: Multiplies final match scores by real-time platform signals (recruiter response rate, signup and activity recency, and interview attendance).

### 2. The Honeypot Shield (Verification Agent)
The dataset contains ~80 fake profiles with impossible data (e.g. 8 years experience at a 3-year-old company or expert skill levels with 0 months used) designed to trap basic keyword embedding search engines. Our verification agent checks every candidate profile for:
* **Temporal Contradictions**: Checks if start dates exceed end dates, or if the claimed `duration_months` exceeds the actual calendar date difference.
* **Skill Duration Anomaly**: Checks if candidates claim expert/advanced skills but have 0 months of usage.
* **Metadata Integrity**: Checks if signup dates occur after last active dates.
If any test fails, the candidate's score is immediately set to 0.0, ensuring they are completely filtered out of our top-100 shortlist.

### 3. Sandbox-Safe Execution (Zero Network / Under 5 Seconds)
To meet the strict sandbox requirements (CPU-only, no network, under 5 minutes):
* **Phase 1: Pre-computation**: Candidate profiles are encoded and compared against the target JD embedding using all-MiniLM-L6-v2. The resulting semantic scores are cached locally in `similarity_scores.json`.
* **Phase 2: Reproduction (rank.py)**: Loads candidate data, joins it with our cached similarity scores, runs honeypot checks, executes the scoring committee formulas, and writes the output. Since it does not load PyTorch or the internet, it runs in **under 5 seconds** on a single CPU core.

---

## File Structure

* `rank.py`: The sandbox entrypoint script.
* `precompute.py`: Script used to pre-compute embeddings offline.
* `backend/app/honeypot.py`: Validation checks for date anomalies and fake expert profiles.
* `backend/app/scorers.py`: Scoring formulas for skills, career quality, logistics, and response rates.
* `similarity_scores.json`: Cached precomputed candidate embedding similarities.
* `submission_metadata.yaml`: Hackathon submission descriptor.
* `requirements.txt`: Package file (pure Python standard library used for ranking).

---

## Setup and Reproduction

### Prerequisites
The ranking script is written in pure Python and requires no external third-party dependencies to run. It executes instantly using Python's standard libraries.

### Command to Run
Run the ranking script on the candidates file:
```bash
python rank.py --candidates ./candidates.jsonl --out ./submission.csv
```

### Validator Command
Verify the format of the output CSV using the official validator:
```bash
python validate_submission.py submission.csv
```
