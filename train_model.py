import os
import pickle
import pandas as pd
import json
from sentence_transformers import SentenceTransformer
from utils import load_csv, parse_skills  # Assumes you have utils.py from previous step

def prepare_unified_model():
    print("--- 1. Loading Data Sources ---")
    
    # A. Load Standard Data (Candidates & Trainings)
    try:
        cand = load_csv('data/candidates.csv')
        trainings = load_csv('data/trainings.csv')
    except FileNotFoundError:
        print("⚠️ Warning: candidates.csv or trainings.csv not found. Skill Gap features may be limited.")
        cand = pd.DataFrame(columns=['candidate_id', 'first_name', 'skills', 'summary'])
        trainings = pd.DataFrame(columns=['module_id', 'title', 'description', 'skills_covered'])

    # B. Load NEW Job Data Sources
    print("   - Loading 'job_dataset.csv'...")
    job_csv = pd.read_csv('data/job_dataset.csv')
    
    print("   - Loading 'job_dataset.json'...")
    with open('data/job_dataset.json', 'r') as f:
        job_json_data = json.load(f)
    job_json = pd.DataFrame(job_json_data)
    
    print("   - Loading 'all.csv' (The big one)...")
    # Using '|' separator and skipping bad lines for safety
    all_csv = pd.read_csv('data/all.csv', sep='|', on_bad_lines='skip')
    
    print("--- 2. Unifying Job Data ---")
    
    # --- Process Source 1: The Clean Dataset (CSV + JSON) ---
    # We merge CSV and JSON (dropping duplicates)
    premium_jobs = pd.concat([job_csv, job_json]).drop_duplicates(subset='JobID')
    
    # Standardize columns
    premium_jobs['unified_id'] = premium_jobs['JobID']
    premium_jobs['unified_title'] = premium_jobs['Title']
    premium_jobs['unified_company'] = "Tech/IT Sector" # Placeholder
    premium_jobs['unified_skills'] = premium_jobs['Skills'] # Explicit skills
    # Create rich text for embedding
    premium_jobs['text_for_emb'] = (
        premium_jobs['Title'].fillna('') + " " + 
        premium_jobs['ExperienceLevel'].fillna('') + " " + 
        premium_jobs['Responsibilities'].fillna('') + " " + 
        premium_jobs['Skills'].fillna('')
    )
    premium_jobs['source_type'] = 'Premium'

    # --- Process Source 2: The Raw Dataset (all.csv) ---
    # Standardize columns
    all_csv['unified_id'] = "RAW-" + all_csv['id'].astype(str)
    all_csv['unified_title'] = all_csv['job_title']
    all_csv['unified_company'] = all_csv['company_industry'].fillna("Unknown")
    all_csv['unified_skills'] = "" # No explicit skills column in all.csv
    # Create rich text for embedding
    all_csv['text_for_emb'] = (
        all_csv['job_title'].fillna('') + " " + 
        all_csv['job_description'].fillna('') + " " + 
        all_csv['job_function'].fillna('')
    )
    all_csv['source_type'] = 'General'
    
    # OPTIONAL: Limit all.csv to first 5000 rows to save training time
    # Remove .head(5000) if you want to process the full 34k rows (might take ~10 mins)
    all_csv = all_csv.head(5000)

    # --- Combine Everything ---
    # Select only necessary columns for the final dataframe
    cols = ['unified_id', 'unified_title', 'unified_company', 'unified_skills', 'text_for_emb', 'source_type']
    unified_jobs = pd.concat([premium_jobs[cols], all_csv[cols]], ignore_index=True)
    
    print(f"   -> Total Unique Jobs: {len(unified_jobs)}")

    print("--- 3. generating Embeddings (AI Brain) ---")
    model = SentenceTransformer("all-MiniLM-L6-v2")
    
    # Encode Candidates
    cand['text_for_emb'] = cand['summary'].fillna('') + ' ' + cand['skills'].fillna('')
    if not cand.empty:
        cand_emb = model.encode(cand['text_for_emb'].tolist(), show_progress_bar=True)
    else:
        cand_emb = []

    # Encode Trainings
    trainings['text_for_emb'] = trainings['title'].fillna('') + ' ' + trainings['description'].fillna('')
    if not trainings.empty:
        train_emb = model.encode(trainings['text_for_emb'].tolist(), show_progress_bar=True)
    else:
        train_emb = []

    # Encode Unified Jobs
    job_emb = model.encode(unified_jobs['text_for_emb'].tolist(), show_progress_bar=True)

    print("--- 4. Saving Models ---")
    os.makedirs('models', exist_ok=True)
    
    with open('models/candidates.pkl', 'wb') as f:
        pickle.dump({'df': cand, 'emb': cand_emb}, f)
    
    # Save the Unified Job Model
    with open('models/jobs.pkl', 'wb') as f:
        pickle.dump({'df': unified_jobs, 'emb': job_emb}, f)
        
    with open('models/trainings.pkl', 'wb') as f:
        pickle.dump({'df': trainings, 'emb': train_emb}, f)
        
    print("✅ Training Complete! Model is ready.")

if __name__ == "__main__":
    prepare_unified_model()