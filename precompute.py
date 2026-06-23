import json
import os
import sys
import numpy as np
import re
import torch
from sentence_transformers import SentenceTransformer
from tqdm import tqdm

# Optimize PyTorch CPU utilization using all available cores (8 cores)
torch.set_num_threads(8)

# Add backend/app to path to import scorers
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend', 'app'))
import scorers

# Target Job Description Text representation for embedding
JD_TEXT = (
    "Senior AI Engineer, Applied Machine Learning, Information Retrieval, search ranking, "
    "vector database, Pinecone, Weaviate, Qdrant, Milvus, OpenSearch, FAISS, "
    "embeddings-based retrieval, sentence-transformers, Python, evaluation frameworks, "
    "NDCG, MRR, MAP, A/B testing, NLP, natural language processing"
)

CANDIDATES_FILE = "[PUB] India_runs_data_and_ai_challenge/India_runs_data_and_ai_challenge/candidates.jsonl"
OUTPUT_FILE = "similarity_scores.json"

# Strict word-boundary patterns for AI/ML/Retrieval title matching
AI_TITLE_PATTERNS = [
    r'\bml\b', r'\bai\b', r'\bnlp\b', r'\bsearch\b', r'\bretrieval\b', 
    r'\brecommender\b', r'\brecommendation\b', r'\bdata scientist\b', 
    r'\bdeep learning\b', r'\bnatural language\b', r'\binformation retrieval\b',
    r'\bmachine learning\b', r'\bapplied ml\b', r'\bapplied ai\b',
    r'\bcomputer vision\b', r'\bvector database\b'
]

# Exclusions
IRRELEVANT_TITLE_KEYWORDS = {
    'hr', 'human resources', 'recruiter', 'marketing', 'content writer', 'copywriter', 
    'graphic designer', 'accountant', 'sales', 'civil', 'mechanical', 'project manager',
    'product manager', 'scrum', 'finance', 'business analyst'
}

# Tighter skill matching keywords (exact match list)
CORE_AI_SKILLS = {
    'pinecone', 'milvus', 'weaviate', 'qdrant', 'faiss', 'opensearch', 'elasticsearch',
    'embeddings', 'sentence-transformers', 'transformer', 'ndcg', 'mrr', 'map', 'nlp',
    'information retrieval', 'machine learning', 'deep learning', 'recommender', 'vector search',
    'applied ml', 'fine-tuning', 'lora', 'qlora', 'bert', 'gpt', 'llm', 'pytorch', 'tensorflow',
    'scikit-learn', 'keras', 'huggingface', 'weights & biases', 'weights and biases', 'gans',
    'image classification', 'object detection', 'speech recognition', 'text-to-speech', 'tts',
    'natural language processing', 'semantic search', 'retrieval-augmented generation', 'rag'
}

def is_potentially_relevant(candidate):
    """
    Strict regex-based and skill density pre-filtering. Candidates that fail this are
    not technical AI/ML engineers and won't make the top 100, so we skip their embedding.
    """
    profile = candidate.get("profile", {})
    title = profile.get("current_title", "").lower()
    headline = profile.get("headline", "").lower()
    
    # 1. Exclude non-technical roles
    for word in IRRELEVANT_TITLE_KEYWORDS:
        if re.search(r'\b' + word + r'\b', title):
            return False
            
    # 2. Check if title or headline matches AI/ML patterns strictly using word boundaries
    has_ai_title = False
    for pattern in AI_TITLE_PATTERNS:
        if re.search(pattern, title) or re.search(pattern, headline):
            has_ai_title = True
            break
            
    # 3. Check if they have at least 3 core AI/ML/Retrieval skills using exact set matching
    skills = [s.get("name", "").lower().strip() for s in candidate.get("skills", [])]
    matching_skills_count = sum(1 for skill in skills if skill in CORE_AI_SKILLS)
    
    return has_ai_title or matching_skills_count >= 3

def main():
    if not os.path.exists(CANDIDATES_FILE):
        print(f"Error: Candidate file not found at {CANDIDATES_FILE}")
        sys.exit(1)
        
    print("Loading SentenceTransformer model 'all-MiniLM-L6-v2'...")
    model = SentenceTransformer('all-MiniLM-L6-v2')
    
    print("Embedding Job Description...")
    jd_embedding = model.encode(JD_TEXT, convert_to_numpy=True)
    # L2 normalize the JD embedding
    jd_embedding = jd_embedding / np.linalg.norm(jd_embedding)
    
    print("Reading candidates and pre-filtering...")
    candidate_ids = []
    candidate_texts = []
    similarities = {}
    
    with open(CANDIDATES_FILE, "r", encoding="utf-8") as f:
        for line in tqdm(f, desc="Filtering candidates"):
            try:
                candidate = json.loads(line)
                cid = candidate["candidate_id"]
                
                if is_potentially_relevant(candidate):
                    candidate_ids.append(cid)
                    
                    profile = candidate.get("profile", {})
                    headline = profile.get("headline", "")
                    summary = profile.get("summary", "")
                    current_title = profile.get("current_title", "")
                    
                    skills_list = ", ".join([s.get("name", "") for s in candidate.get("skills", [])])
                    text = f"{current_title} | {headline} | {summary} | Skills: {skills_list}"
                    candidate_texts.append(text)
                else:
                    similarities[cid] = 0.0
            except Exception as e:
                continue
                
    total_candidates = len(candidate_texts)
    print(f"Pre-filtering complete. Retained {total_candidates} relevant candidates for embedding out of 100,000.")
    
    if total_candidates > 0:
        batch_size = 512
        for i in tqdm(range(0, total_candidates, batch_size), desc="Embedding candidates"):
            batch_texts = candidate_texts[i:i+batch_size]
            batch_ids = candidate_ids[i:i+batch_size]
            
            batch_embeddings = model.encode(batch_texts, convert_to_numpy=True)
            
            for j, emb in enumerate(batch_embeddings):
                norm = np.linalg.norm(emb)
                if norm > 0:
                    normalized_emb = emb / norm
                    sim = float(np.dot(normalized_emb, jd_embedding))
                else:
                    sim = 0.0
                similarities[batch_ids[j]] = round(sim, 4)
            
    print(f"Saving similarity scores to {OUTPUT_FILE}...")
    with open(OUTPUT_FILE, "w", encoding="utf-8") as out:
        json.dump(similarities, out)
        
    print("Pre-computation completed successfully!")

if __name__ == "__main__":
    main()
