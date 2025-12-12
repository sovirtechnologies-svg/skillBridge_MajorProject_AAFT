# SkillBridge 

SkillBridge is an AI-powered job recommendation and professional networking platform designed to connect candidates with the right opportunities using advanced machine learning.

##  Features

*   **AI-Powered Job Matching**: Uses Sentence Transformers (`all-MiniLM-L6-v2`) to semantically match search queries with job descriptions.
*   **Resume Analysis**: Upload your resume (PDF, DOCX, or TXT) to automatically extract skills and find the best-fitting job opportunities.
*   **Smart Job Feed**: Browse a curated list of jobs with intelligent tagging and UI enhancements.
*   **Community Posts**: A social feature for users to share updates, achievements, and insights (Prototype support for creating and deleting posts).
*   **Candidate Recommendations**: View potential candidates and their skill sets.

##  Tech Stack

*   **Backend**: Python, Flask
*   **Machine Learning**: Scikit-learn, Sentence Transformers, NumPy
*   **Frontend**: HTML5, JavaScript, CSS (Tailwind CSS)
*   **Data Processing**: Pandas, PyPDF, Python-Docx

##  Prerequisites

*   Python 3.8 or higher
*   pip (Python package manager)

##  Installation & Setup

1.  **Clone the Repository**
    ```bash
    git clone https://github.com/sovirtechnologies-svg/skillBridge_MajorProject_AAFT.git/
    
    ```

2.  **Create and Activate Virtual Environment (Optional but Recommended)**
    ```bash
    python -m venv venv
    # Windows
    venv\Scripts\activate
    # macOS/Linux
    source venv/bin/activate
    ```

3.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```
    *If `requirements.txt` is missing or has issues, install core packages manually:*
    ```bash
    pip install flask flask-cors pandas numpy scikit-learn sentence-transformers pypdf python-docx
    ```

4.  **Initialize ML Models**
    Before running the server, you must generate the necessary machine learning models (embeddings).
    ```bash
    python train_model.py
    ```
    This will create a `models/` directory containing the trained pickle files (`candidates.pkl`, `jobs.pkl`, `trainings.pkl`).

5.  **Run the Backend Server**
    ```bash
    python app.py
    ```
    The server will start on `http://localhost:5000`.

6.  **Launch the Frontend**
    *   Navigate to the `frontend` folder.
    *   Open `index.html` in your web browser.
    *   *Tip: For the best experience, use a local development server extension (like Live Server in VS Code) to serve the frontend files.*

## Project Structure

```
skillbridge/
├── app.py                # Main Flask application entry point and API routes
├── train_model.py        # Script to train/generate ML models
├── predict_model.py      # Testing script for model predictions
├── utils.py              # Utility helper functions
├── requirements.txt      # Project dependencies
├── data/                 # Raw data files (CSV, etc.)
├── models/               # Generated ML models (pickle files)
└── frontend/
    ├── index.html        # Main user interface
    ├── app.js            # Frontend logic and API integration
    └── logo.jpg          # Application assets
```

## Troubleshooting

*   **"Models not found" Error**: Ensure you run `python train_model.py` before starting `app.py`.
*   **CORS Issues**: If checking from a different port/frontend server, ensure `Flask-CORS` is enabled (it is by default in `app.py`).


