import os
import json
import numpy as np
import faiss
from database import get_db

# ---------------------------------------------------------------------------
# Offline TF-IDF Vectorizer (Safe for PythonAnywhere Free Tier)
# ---------------------------------------------------------------------------
from sklearn.feature_extraction.text import TfidfVectorizer

# We use a compact vocabulary to keep FAISS fast and memory-efficient
VECTORIZER = TfidfVectorizer(analyzer="char_wb", ngram_range=(2, 4), max_features=512, sublinear_tf=True)
WORD_VECTORIZER = TfidfVectorizer(analyzer="word", ngram_range=(1, 2), max_features=512, sublinear_tf=True, stop_words="english")

SEED_CORPUS = [
    "photosynthesis chlorophyll light energy glucose oxygen plant cell biology",
    "force mass acceleration Newton law motion velocity momentum physics",
    "atom element molecule compound bond ionic covalent chemistry",
    "algebra equation calculus derivative integral math statistics",
    "war revolution civilization ancient history democracy government",
    "algorithm data structure programming code software computer science",
    "supply demand market price inflation economy finance",
    "study question answer explanation concept definition"
]

VECTORIZER.fit(SEED_CORPUS)
WORD_VECTORIZER.fit(SEED_CORPUS)

EMBEDDING_DIM = 1024 # 512 + 512

def get_embedding(text: str) -> np.ndarray:
    char_vec = VECTORIZER.transform([text]).toarray()[0]
    word_vec = WORD_VECTORIZER.transform([text]).toarray()[0]
    combined = np.concatenate([char_vec, word_vec]).astype(np.float32)
    norm = np.linalg.norm(combined)
    if norm > 0:
        combined = combined / norm
    return combined

# ---------------------------------------------------------------------------
# FAISS Index
# ---------------------------------------------------------------------------
index = faiss.IndexFlatIP(EMBEDDING_DIM) 
faiss_id_map = {} 
next_faiss_id = 0

def init_faiss():
    global index, faiss_id_map, next_faiss_id
    index = faiss.IndexFlatIP(EMBEDDING_DIM)
    faiss_id_map = {}
    next_faiss_id = 0
    
    db = get_db()
    try:
        rows = db.execute("SELECT id, text FROM questions").fetchall()
        for row in rows:
            emb = get_embedding(row["text"])
            add_to_faiss(row["id"], emb)
    except Exception as e:
        print(f"FAISS Init Error: {e}")

def add_to_faiss(db_id: int, embedding: np.ndarray):
    global index, faiss_id_map, next_faiss_id
    emb_copy = embedding.copy().reshape(1, -1)
    faiss.normalize_L2(emb_copy)
    index.add(emb_copy)
    faiss_id_map[next_faiss_id] = db_id
    next_faiss_id += 1

TOPICS = {
    "Biology": "cell biology photosynthesis DNA genetics evolution",
    "Physics": "force motion energy gravity velocity acceleration thermodynamics",
    "Chemistry": "atom molecule bond reaction acid base element compound",
    "Mathematics": "algebra calculus geometry trigonometry probability statistics",
    "History": "war revolution civilization ancient medieval colonialism",
    "Literature": "novel poem story author character theme plot Shakespeare",
    "Computer Science": "algorithm data structure programming code software",
    "Economics": "supply demand market price inflation GDP trade",
    "Geography": "continent country capital climate biome population",
    "General": "study question answer explanation concept",
}

TOPIC_EMBEDDINGS = {topic: get_embedding(phrases) for topic, phrases in TOPICS.items()}

def classify_topic(question: str) -> str:
    q_emb = get_embedding(question)
    best_topic, best_score = "General", -1.0
    for topic, t_emb in TOPIC_EMBEDDINGS.items():
        score = np.dot(q_emb, t_emb)
        if score > best_score:
            best_score = score
            best_topic = topic
    return best_topic

def find_similar_questions(embedding: np.ndarray, exclude_user_id: int = None, top_k: int = 5):
    if index.ntotal == 0:
        return []
        
    emb_copy = embedding.copy().reshape(1, -1)
    faiss.normalize_L2(emb_copy)
    
    D, I = index.search(emb_copy, min(index.ntotal, top_k + 2))
    results = []
    db = get_db()
    for i in range(len(I[0])):
        idx = I[0][i]
        score = D[0][i]
        if idx == -1: continue
        db_id = faiss_id_map.get(idx)
        if not db_id: continue
        if score >= 0.99: continue
            
        row = db.execute("SELECT id, text, topic FROM questions WHERE id=?", (db_id,)).fetchone()
        if row:
            results.append({"id": row["id"], "text": row["text"], "topic": row["topic"], "similarity": round(float(score), 3)})
            if len(results) >= top_k: break
    return results

# ---------------------------------------------------------------------------
# Agentic Tutor
# ---------------------------------------------------------------------------
class AgenticTutor:
    def __init__(self):
        self.api_key = os.environ.get("OPENAI_API_KEY")
        
    def generate_response(self, question: str, topic: str, similar_contexts: list) -> str:
        if not self.api_key:
            return self._mock_generation(question, topic, similar_contexts)
        return self._mock_generation(question, topic, similar_contexts)
        
    def _mock_generation(self, question: str, topic: str, contexts: list) -> str:
        response = f"### Concept Analysis: {topic}\n\n"
        response += f"Based on our knowledge base, here is a structured breakdown of your question: '{question}'\n\n"
        response += "**Core Principles:**\n- Understanding the fundamental rules of this topic is key.\n- Look for patterns in how variables interact.\n\n"
        
        if contexts:
            response += "**Related Insights:**\nWe noticed similar questions were asked before:\n"
            for ctx in contexts[:2]:
                response += f"- *{ctx['text']}*\n"
                
        response += "\n**Next Steps:**\nTo master this, try solving a practice problem applying this concept!"
        return response

agent = AgenticTutor()
