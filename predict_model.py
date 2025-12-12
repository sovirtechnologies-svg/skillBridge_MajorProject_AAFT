import pickle
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
from utils import parse_skills
import os

def load_models():
    print("Loading Unified AI Models... (This might take a moment)")
    try:
        with open('models/candidates.pkl', 'rb') as f: cand_data = pickle.load(f)
        with open('models/jobs.pkl', 'rb') as f: job_data = pickle.load(f)
        with open('models/trainings.pkl', 'rb') as f: train_data = pickle.load(f)
        return cand_data, job_data, train_data
    except FileNotFoundError:
        print("❌ Error: 'models/' folder not found. Please run 'python train_model.py' first.")
        return None, None, None

def start_prediction_tool():
    cand_data, job_data, train_data = load_models()
    if not cand_data: return

    # Extract DataFrames and Embeddings
    jobs_df = job_data['df']
    job_embeddings = job_data['emb']
    
    tr_df = train_data['df']
    tr_embeddings = train_data['emb']
    
    # Load the AI for on-the-fly encoding
    model = SentenceTransformer("all-MiniLM-L6-v2")

    print("\n" + "="*60)
    print(f"🤖  SKILLBRIDGE UNIFIED PREDICTOR  🤖")
    print(f"   Loaded {len(jobs_df)} jobs from CSV, JSON, and 'all.csv'.")
    print("="*60)

    while True:
        print("\nOptions:")
        print(" [1] Search Jobs by Skill/Description (e.g., 'python developer in jakarta')")
        print(" [2] Find Training for a Skill (e.g., 'learn plc programming')")
        print(" [q] Quit")
        
        choice = input("\nSelect: ").strip().lower()
        if choice == 'q': break
        
        if choice == '1':
            query_text = input("Enter Job Search Query: ").strip()
            if not query_text: continue
            
            # 1. Encode the query
            query_vec = model.encode([query_text])
            
            # 2. Calculate Similarity against ALL jobs
            scores = cosine_similarity(query_vec, job_embeddings)[0]
            
            # 3. Get Top 5 Matches
            top_indices = scores.argsort()[-5:][::-1]
            
            print(f"\n🎯 Top 5 Job Recommendations:")
            print("-" * 70)
            for idx in top_indices:
                job = jobs_df.iloc[idx]
                score = scores[idx] * 100
                
                # Display logic based on Source Type
                source_badge = "⭐ PREMIUM" if job['source_type'] == 'Premium' else "🌍 GENERAL"
                
                print(f"[{source_badge}] Match: {score:.1f}%")
                print(f"   Title:   {job['unified_title']}")
                print(f"   Company: {job['unified_company']}")  # <--- ENABLED HERE
                
                if job['source_type'] == 'Premium':
                    # Premium jobs have structured skills
                    skills = str(job['unified_skills'])
                    print(f"   Skills:  {skills[:90]}..." if len(skills)>90 else skills)
                else:
                    # General jobs rely on description text
                    # Show a snippet of the text we used for embedding
                    desc_snippet = str(job['text_for_emb'])[:100].replace('\n', ' ')
                    print(f"   Excerpt: {desc_snippet}...")
                print("-" * 70)

        elif choice == '2':
            query_text = input("Enter Training Topic: ").strip()
            if not query_text: continue
            
            query_vec = model.encode([query_text])
            scores = cosine_similarity(query_vec, tr_embeddings)[0]
            top_indices = scores.argsort()[-3:][::-1]
            
            print(f"\n📚 Recommended Training Modules:")
            print("-" * 70)
            for idx in top_indices:
                tr = tr_df.iloc[idx]
                score = scores[idx] * 100
                print(f"[{score:.1f}%] {tr['title']}")
                print(f"       {tr['description']}")
            print("-" * 70)

if __name__ == "__main__":
    start_prediction_tool()