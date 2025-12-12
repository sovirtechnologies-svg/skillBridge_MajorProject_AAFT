from flask import Flask, jsonify, request
from flask_cors import CORS
import pickle
import numpy as np
import random  # Added to generate realistic UI data (colors, locations)
from utils import parse_skills
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
import os
import uuid
from datetime import datetime
from werkzeug.utils import secure_filename
import pypdf  # For PDFs
import docx   # For Word Docs

# --- MEMORY STORAGE FOR POSTS (Prototype) ---
posts = [
    {
        "id": "1",
        "author": "Sarah Chen",
        "role": "Senior AI Engineer at TechCorp",
        "avatar": "https://ui-avatars.com/api/?name=Sarah+Chen&background=06b6d4&color=fff&bold=true",
        "content": "🚀 Excited to share that our AI team just launched a groundbreaking feature that improved model accuracy by 35%! The journey from research to production taught us invaluable lessons about scalability and teamwork.",
        "image": "https://images.unsplash.com/photo-1677442136019-21780ecad995?w=800&h=400&fit=crop",
        "likes": 247,
        "comments": 52,
        "shares": 18,
        "time": "2h ago"
    }
]
app = Flask(__name__)
CORS(app)

print("Loading Unified AI Models...")
try:
    with open('models/candidates.pkl','rb') as f: cand_art = pickle.load(f)
    with open('models/jobs.pkl','rb') as f: job_art = pickle.load(f)
    with open('models/trainings.pkl','rb') as f: train_art = pickle.load(f)
except FileNotFoundError:
    print("❌ Error: Models not found. Run 'train_model.py' first.")
    exit()

candidates_df = cand_art['df']
jobs_df = job_art['df']
job_embeddings = job_art['emb']
tr_df = train_art['df']
tr_embeddings = train_art['emb']

model = SentenceTransformer("all-MiniLM-L6-v2")

# --- UI HELPERS ---
# These lists help the UI look realistic and colorful
LOCATIONS = ["Bangalore, India", "Hyderabad, Remote", "Mumbai, Hybrid", "Delhi NCR", "Pune, On-site", "Chennai, India"]
TIMES = ["2 hours ago", "5 hours ago", "1 day ago", "Just now", "3 days ago", "1 week ago"]
COLORS = ["bg-blue-100 text-blue-600", "bg-green-100 text-green-600", "bg-purple-100 text-purple-600", "bg-orange-100 text-orange-600", "bg-red-100 text-red-600"]

@app.route('/api/jobs', methods=['GET'])
def list_jobs():
    """Returns the feed of jobs with UI enhancements."""
    limit = 20
    subset = jobs_df.head(limit)
    out = []
    for _, row in subset.iterrows():
        company = row['unified_company']
        # Generate a nice 2-letter logo (e.g., "GO" for Google)
        logo_text = company[:2].upper() if company and isinstance(company, str) else "JO"
        
        out.append({
            'job_id': str(row['unified_id']),
            'title': row['unified_title'],
            'company': company if company else "Confidential", # Company is now VISIBLE
            'source_type': row['source_type'],
            'required_skills': str(row['unified_skills']) if row['source_type'] == 'Premium' else "See Description",
            
            # UI Fields (Required for the Frontend to look good)
            'location': random.choice(LOCATIONS),
            'posted': random.choice(TIMES),
            'logo': logo_text,
            'color': random.choice(COLORS)
        })
    return jsonify(out)

@app.route('/api/recommend', methods=['POST'])
def recommend():
    """Search endpoint for the Frontend."""
    data = request.json
    query = data.get('query', '')
    
    if not query:
        return jsonify({'results': []})

    query_vec = model.encode([query])
    
    # Calculate Similarity
    job_scores = cosine_similarity(query_vec, job_embeddings)[0]
    top_job_indices = job_scores.argsort()[-10:][::-1] # Top 10 matches
    
    jobs_list = []
    for idx in top_job_indices:
        job = jobs_df.iloc[idx]
        company = job['unified_company']
        logo_text = company[:2].upper() if company and isinstance(company, str) else "AI"

        jobs_list.append({
            'job_id': str(job['unified_id']),
            'title': job['unified_title'],
            'company': company if company else "Confidential",
            'match_score': round(float(job_scores[idx]) * 100, 1),
            
            # UI Specifics for Search Results
            'location': "Recommended Match",
            'posted': "Based on your search",
            'logo': logo_text,
            'color': "bg-brand text-white", # Highlight matched jobs in Blue
            'source_type': job['source_type']
        })
    
    return jsonify({'results': jobs_list})

@app.route('/api/candidates', methods=['GET'])
def list_candidates():
    out = candidates_df[['candidate_id', 'first_name', 'email', 'skills']].fillna('').to_dict(orient='records')
    return jsonify(out)

# --- API: POSTS ---
@app.route('/api/posts', methods=['GET'])
def get_posts():
    return jsonify(posts)

@app.route('/api/posts', methods=['POST'])
def create_post():
    data = request.json
    new_post = {
        "id": str(uuid.uuid4()),
        "author": "Current User", # In a real app, get from session
        "role": "Software Engineer",
        "avatar": "https://ui-avatars.com/api/?name=Current+User&background=0a66c2&color=fff&bold=true",
        "content": data.get('content', ''),
        "image": None, # Image upload can be added later
        "likes": 0,
        "comments": 0,
        "shares": 0,
        "time": "Just now"
    }
    posts.insert(0, new_post) # Add to top
    return jsonify(new_post)

@app.route('/api/posts/<post_id>', methods=['DELETE'])
def delete_post(post_id):
    global posts
    posts = [p for p in posts if p['id'] != post_id]
    return jsonify({'success': True})
# --- HELPER: Extract Text from Resume ---
def extract_text_from_file(file, filename):
    text = ""
    try:
        if filename.endswith('.pdf'):
            reader = pypdf.PdfReader(file)
            for page in reader.pages:
                text += page.extract_text() + " "
        elif filename.endswith('.docx'):
            doc = docx.Document(file)
            for para in doc.paragraphs:
                text += para.text + " "
        elif filename.endswith('.txt'):
            text = file.read().decode('utf-8')
    except Exception as e:
        print(f"Error parsing file: {e}")
        return ""
    
    # Basic cleaning: Remove newlines and extra spaces
    return " ".join(text.split())

# --- API: Resume Upload & Match ---
@app.route('/api/upload-resume', methods=['POST'])
def upload_resume():
    if 'resume' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['resume']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    # 1. Extract Text from the uploaded file
    print(f"DEBUG: Processing upload for {file.filename}")
    resume_text = extract_text_from_file(file, file.filename)
    
    if not resume_text:
        print("DEBUG: Resume text extraction failed")
        return jsonify({'error': 'Could not extract text from file'}), 400
    
    print(f"DEBUG: Extracted text preview: {resume_text[:50]}...")

    # 2. (Optional) Intelligent Truncation 
    # Since resumes are long, we focus on the first 500 words or look for "Skills" keyword
    # But for this prototype, let's feed the first 1000 chars to the AI to get the gist
    # OR: If your resumes are standard, the AI often understands the whole context better.
    
    # 3. Create Embedding from Resume Text
    # The AI converts your Resume -> Math Vector
    resume_vec = model.encode([resume_text])
    
    # 4. Find Matching Jobs (Cosine Similarity)
    job_scores = cosine_similarity(resume_vec, job_embeddings)[0]
    top_job_indices = job_scores.argsort()[-10:][::-1] # Top 10
    
    jobs_list = []
    for idx in top_job_indices:
        job = jobs_df.iloc[idx]
        company = job['unified_company']
        logo_text = company[:2].upper() if company and isinstance(company, str) else "CV"

        jobs_list.append({
            'job_id': str(job['unified_id']),
            'title': job['unified_title'],
            'company': company if company else "Confidential",
            'match_score': round(float(job_scores[idx]) * 100, 1),
            'location': "Resume Match",
            'posted': "Best fit for you",
            'logo': logo_text,
            'color': "bg-purple-600 text-white", # Purple for Resume Matches
            'source_type': job['source_type']
        })

    # Return results in the format the frontend expects
    return jsonify({
        'results': jobs_list,
        'extracted_text_preview': resume_text[:200] + "...",
        'extracted_skills': [] # Frontend expects this key, even if empty
    })
if __name__ == "__main__":
    app.run(port=5000, debug=True)