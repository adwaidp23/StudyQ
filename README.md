# StudyQ - AI Study Question Finder

StudyQ is a full-stack web application designed for students to ask study questions, auto-tag them to specific academic topics, and automatically find semantically similar past questions using an AI embedding model. 

## Features
- **Secure Authentication**: Sign up and log in via email and password (using `bcrypt` and JWT).
- **Ask & Discover**: Type any study question to instantly see similar questions from the global pool.
- **AI Auto-Tagging**: Questions are automatically categorized into topics (e.g. Biology, Physics, History) using zero-shot semantic matching.
- **Semantic Search**: Uses `sentence-transformers` for calculating dense vector embeddings and cosine similarity to find highly relevant matches.
- **Question History**: View all your previously asked questions and filter them by AI-assigned tags.
- **Stunning UI**: A modern, premium dark-mode interface built with React, Vite, and custom CSS featuring glassmorphism and subtle micro-animations.

---

## Tech Stack
### Frontend
- **Framework**: React (via Vite)
- **Styling**: Vanilla CSS with custom tokens and variables
- **Icons**: Lucide React

### Backend
- **Framework**: Flask (Python)
- **Database**: SQLite
- **Authentication**: Flask-JWT-Extended, bcrypt

### AI / ML Logic
- **Embeddings**: `sentence-transformers` (specifically `all-MiniLM-L6-v2`) computes dense 384-dimensional vector representations for questions.
- **Similarity matching**: We use `scikit-learn` to calculate the `cosine_similarity` between the asked question and all historically stored questions. Results scoring above a certain threshold (or the top K) are shown to the user.
- **Auto-tagging**: The system maintains a predefined list of topics. Each topic is embedded by calculating a centroid embedding of relevant keywords. The user's question is then embedded and compared to these topic embeddings; the topic with the highest cosine similarity is assigned to the question.

---

## How to Run Locally

### 1. Backend Setup
1. Open a terminal and navigate to the `backend/` folder.
2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the Flask application:
   ```bash
   python main.py
   ```
   *The backend will be available at `http://localhost:5000`.*
   *Note: On the first run, it will automatically create `studyq.db` and download the `sentence-transformers` model (approx. 90MB).*

### 2. Frontend Setup
1. Open a new terminal and navigate to the `frontend/` folder.
2. Install Node dependencies:
   ```bash
   npm install
   ```
3. Run the Vite development server:
   ```bash
   npm run dev
   ```
   *The frontend will typically run at `http://localhost:5173` or as shown in your terminal output.*

Open the provided localhost URL in your browser, create an account, and start asking questions!
