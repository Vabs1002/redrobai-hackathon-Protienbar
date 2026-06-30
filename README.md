# Intelligent Candidate Discovery and Ranking

Team Protienbar -- Redrob AI Hackathon Submission


## The Problem

Redrob gave us a pool of 100,000 candidate profiles and one job description for a Senior AI Engineer role. The task was straightforward on paper but tricky in practice: rank the top 100 candidates who are the best fit for this role, and for each one, write a short reasoning explaining why they belong at that rank.

The catch? The ranking script has to run on a plain CPU machine with 16 GB of RAM, no GPU, no internet access, and finish in under 5 minutes. You cannot call OpenAI, Claude, or any hosted LLM during the ranking step. On top of that, the dataset is seeded with around 80 honeypot profiles -- fake candidates with subtly impossible career histories designed to trap systems that rely purely on keyword matching.

So the challenge was really about building something that actually reads and understands profiles rather than just matching buzzwords.


## How We Approached It

We thought about this the way a real recruiting team would work. When a recruiter evaluates a candidate, they do not just ctrl-F for "Pinecone" or "FAISS" in the resume. They look at career trajectory, whether the person has actually shipped something, how long they stayed at each job, whether they are even actively looking, and whether the profile makes logical sense. We tried to encode that intuition into code.

Our system has two phases.

Phase 1 is a pre-computation step that runs offline with internet and GPU access (before the sandbox). We use the all-MiniLM-L6-v2 sentence transformer model to encode every candidate profile into a vector and compare it against a representation of the job description. But we do not embed all 100,000 candidates blindly. We first filter out profiles that clearly have nothing to do with AI or ML (marketing managers, HR leads, graphic designers) so we only spend compute on relevant candidates. The resulting similarity scores get saved into a JSON file that ships with the repository.

Phase 2 is the actual ranking script, rank.py. This is the part that runs inside the sandbox. It loads the candidate data, joins it with the pre-computed similarity scores, runs a battery of checks and scoring formulas, and writes out the final CSV. Because it does not load any ML model or make any network call, it finishes in about 3 seconds on a single CPU core.


## How It Relates to Agentic RAG

Even though this is not a conversational chatbot, our architecture is built directly on Retrieval-Augmented Generation (RAG) and agentic principles.

Retrieval: We perform hybrid retrieval across the database of 100,000 candidate profiles, combining dense vector search (sentence transformer embeddings) with keyword matching and metadata-driven pre-filtering.

Augmentation: We augment the semantic vector similarity results by overlaying structured candidate metadata, career histories, and real-time behavioral signals (such as notice periods and platform activity levels).

Generation: Instead of simply returning a raw candidate list, the system generates a 1-2 sentence recruiter reasoning for each candidate in the final shortlist, custom-tailored to their specific profile details and fit for the role.

Agentic Design: Instead of using a single hardcoded scoring formula, we split the decision-making among specialized modules that behave like a recruiting committee. The Honeypot Shield acts as an auditing agent that verifies data truthfulness. The Skills Scorer audits technical proficiency. The Career Specialist screens companies and job durations. The Availability Specialist evaluates platform activity. Together, these modules collaborate to produce the final verified ranking.


## Our Key Novelties

We designed our system with six specific innovations that give it an edge over standard keyword and embedding approaches:

1. Three-Second Execution Speed: We split the ranking process into offline embedding pre-computation and online rule scoring. This allows the sandbox execution script (rank.py) to run completely offline on a single CPU core in under 3 seconds for all 100,000 candidates, easily satisfying the 5-minute sandbox limit without crashing.

2. Agentic RAG Architecture: Rather than relying on simple semantic similarity matching, our system implements an Agentic Retrieval-Augmented Generation model. It retrieves candidates using hybrid dense vector search, augments the data through a modular committee of recruiting specialists that verify and score profiles across independent axes, and generates detailed, factual recruiter reasonings for the final shortlist.

3. Dynamic Service Company Detection: Instead of only checking for a hardcoded list of consulting companies, our system inspects the industry field of every job in a candidate's history. If a company is classified under IT services, information technology and services, or management consulting, our system automatically detects it. This captures smaller or unlisted service firms that other systems miss.

4. Availability and Hireability Scaling: A candidate with a perfect resume is useless if they are unreachable. We use real-time platform signals (response rates, last active dates, notice periods) to scale the final matching score. This prioritizes responsive, active candidates who are ready to start, rather than just theoretically qualified profiles.

5. Automated Honeypot Auditing: We built a lightweight validation layer that catches impossible dates and fake skill claims before ranking them. Because this uses fast chronological logic, it achieves a zero percent honeypot rate in our final top 100 without consuming expensive CPU time.

6. Non-Hallucinatory Reasonings: Unlike systems that call LLMs during ranking (which are prone to hallucinating candidate skills and formatting errors), our reasoning engine uses strict metadata extraction to compile highly factual, profile-consistent recruiter sentences.


## The Scoring Pipeline

The scoring works across multiple axes, each designed to capture a different dimension of candidate quality.

Semantic Similarity: This is the baseline signal from Phase 1. It tells us how close the candidate's overall profile text is to what the JD is asking for. But we do not rely on this alone -- that is exactly the trap the dataset is designed to exploit.

Skills Match: We check each candidate's listed skills against the core skills the JD calls for (things like vector databases, embeddings, Python, ranking evaluation metrics). We weight each match by how long they have used the skill and how many endorsements they have. An expert-level Pinecone user with 36 months of experience scores higher than someone who lists it with beginner proficiency and 2 months.

Career Quality: This is where we filter out service-firm-only careers. The JD explicitly says candidates whose entire career has been at TCS, Infosys, Wipro, Accenture, Cognizant, or Capgemini are not a good fit. We enforce this, but we are careful about it: if someone is currently at a consulting firm but has prior experience at a product company, they stay in the running. We also penalize heavy job-hoppers (people who switch every 12-18 months chasing titles) because the JD specifically calls that out as a disqualifier.

Experience Fit: The JD targets 5 to 9 years of experience. We give the highest scores to candidates in that sweet spot and apply a gentle decay for people outside the range.

Logistics: Candidates located in Noida or Pune (where Redrob has offices) get a boost. Candidates with a notice period under 30 days get a boost. These are real-world hiring signals that matter.

Platform Activity: This is the behavioral signal layer. We look at the Redrob platform signals -- recruiter response rate, last login date, interview completion rate, profile completeness. A candidate who looks perfect on paper but has not logged in for 6 months and responds to 5 percent of recruiter messages is, for practical hiring purposes, not actually available. We down-weight them accordingly.

All of these axes get combined into a single composite score. The final ranking is sorted by score descending, with ties broken alphabetically by candidate ID.


## Honeypot Detection

The dataset contains roughly 80 fake profiles designed to look attractive to keyword-matching systems but with logically impossible career data. For example, a candidate might claim 8 years of experience at a company that was founded 3 years ago, or list expert proficiency in 10 skills but with 0 months of usage for each one.

We built a verification layer (we call it the Honeypot Shield) that checks every candidate for:

- Timeline contradictions: Does the claimed duration at a job exceed what the calendar allows between the start and end dates?
- Skill duration anomalies: Does the candidate claim expert or advanced proficiency in a skill but report 0 months of actual usage?
- Date integrity: Does the signup date come after the last active date, which would be physically impossible?

Any candidate that fails these checks gets their score set to zero, which guarantees they never enter the top 100.


## The Reasoning Column

For each of the top 100 candidates, we generate a 1-2 sentence reasoning that references specific facts from their profile -- their current title, years of experience, key skills, career history, and any concerns. We made sure these are not templated or copy-pasted. Each reasoning is unique and reflects what actually makes that particular candidate a good (or decent) fit at their specific rank position.


## Repository Structure

    rank.py                    -- The sandbox entrypoint. Produces submission.csv from candidates.jsonl.
    precompute.py              -- Offline script that generates similarity_scores.json using sentence embeddings.
    backend/app/honeypot.py    -- Honeypot detection rules (timeline checks, skill anomaly checks).
    backend/app/scorers.py     -- Scoring formulas for skills, career quality, logistics, and platform activity.
    similarity_scores.json     -- Pre-computed embedding similarity database (about 2 MB).
    submission.csv             -- Our final validated top-100 ranking.
    submission_metadata.yaml   -- Hackathon metadata descriptor.
    sandbox_demo.ipynb         -- Google Colab notebook (programmatically blocks network sockets to prove offline execution).
    requirements.txt           -- Dependencies (the ranking step uses only Python standard library).
    sandbox_candidates.jsonl   -- Small 5-candidate example dataset used in the demo video and Colab run.
    test_candidates.jsonl      -- Larger 100-candidate test dataset representing a realistic diverse applicant pool.


## How to Reproduce

The ranking script uses only Python standard library modules. No pip install needed for the ranking step itself.

To generate the submission CSV:

    python rank.py --candidates ./candidates.jsonl --out ./submission.csv

To validate the output format:

    python validate_submission.py submission.csv

The pre-computation step (generating embeddings) requires torch and sentence-transformers. This step is already done and the results are included in similarity_scores.json, so you do not need to re-run it to reproduce the submission. If you want to re-run it anyway:

    pip install torch sentence-transformers
    python precompute.py


## Compute Environment

    Machine: Local PC, Windows 11
    CPU: 8 cores
    RAM: 16 GB
    Python: 3.12
    GPU: Not used during ranking
    Network: Not used during ranking (programmatically verified offline in sandbox_demo.ipynb)
    Ranking runtime: approximately 3 seconds

## Demo Dataset (sandbox_candidates.jsonl)

To help recruiters and judges quickly verify the system's logic without processing 100,000 files, we have included a small mock candidate file containing 5 distinct developer profiles:
* **Alice & Ethan**: Highly qualified ML/AI specialists with strong vector search experience.
* **Bob**: An unrelated frontend engineer (React/Tailwind) to show how the system filters out non-relevant engineering titles.
* **Diana**: A developer with a background purely in service/consulting firms, demonstrating the career-quality filter.
* **Charlie**: A fraudulent "honeypot" profile claiming impossible job durations. The Honeypot Shield immediately flags Charlie, disqualifying him.

We use this file in our **reproduction demo video** to showcase the file upload process, dashboard charts, candidate inspector, and integrity warnings.

## Test Dataset (test_candidates.jsonl)

To test the system's accuracy and performance on a larger scale, we have included `test_candidates.jsonl`.
* **Purpose**: This dataset simulates a raw, realistic recruiter queue to prove that the pipeline can successfully filter out non-matching backgrounds and rank qualified applicants on standard CPUs in seconds.
* **What it has**:
  * **92 Unrelated Roles**: Contains profiles for Accountants, Civil Engineers, Business Analysts, Support Specialists, and General Developers (React, Java, etc.). These are automatically filtered out (scored 0.0) because they lack core AI/ML credentials.
  * **8 Qualified AI/ML Engineers**: Surfaced and ranked (e.g. *Ela Singh* with FAISS/Pinecone skills, *Aarav Kapoor* with MLOps/Kubeflow skills).
  * **Honeypot Profiles**: Includes timeline contradictions to test the **Honeypot Shield's** capability to flag and block integrity-violating profiles.

### Supported Upload Formats & Schema

The portal's uploader accepts the following file formats for scoring candidate pools:
1. **JSON Lines (.jsonl)**: A line-delimited JSON file where each line contains exactly one candidate profile object.
2. **JSON (.json)**: A standard JSON array containing candidate profile objects.

To be processed correctly by our backend engine, each candidate object must adhere to the Redrob profile schema. Below is a complete example of a valid candidate JSON structure:

```json
{
  "candidate_id": "CAND_0000001",
  "profile": {
    "anonymized_name": "Demo Candidate",
    "current_title": "AI Engineer",
    "years_of_experience": 6.5,
    "location": "Pune",
    "country": "India"
  },
  "career_history": [
    {
      "company": "Stripe",
      "title": "AI Engineer",
      "start_date": "2023-01-01",
      "end_date": null,
      "duration_months": 41,
      "industry": "Fintech",
      "description": "Implemented vector search databases."
    }
  ],
  "skills": [
    {"name": "Python", "proficiency": "expert", "duration_months": 48},
    {"name": "Pinecone", "proficiency": "advanced", "duration_months": 24}
  ],
  "redrob_signals": {
    "notice_period_days": 30,
    "recruiter_response_rate": 0.95,
    "open_to_work_flag": true,
    "last_active_date": "2026-06-15"
  }
}
```
